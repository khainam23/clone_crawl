"""
File operation utility functions
"""
import logging, time
from typing import List, Dict, Any, Optional
import logging, time, json, os

from app.db.mongodb import get_collection

# Setup logger
logger = logging.getLogger(__name__)

class SaveUtils:
    """Utility functions cho file operations"""
    
    @staticmethod
    async def backup_db(collection_name: Optional[str] = "crawl_results") -> Optional[str]:
        """Backup MongoDB collection ra file JSON trước khi thực hiện thao tác"""
        try:
            collection = get_collection(collection_name)
            
            # Đếm số lượng documents
            count = await collection.count_documents({})
            
            if count == 0:
                logger.info(f"No data to backup in collection: {collection_name}")
                return None
            
            # Lấy tất cả documents từ collection
            cursor = collection.find({})
            documents = await cursor.to_list(length=None)
            
            # Tạo thư mục backup nếu chưa tồn tại
            backup_dir = "data/backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Tạo tên file backup với timestamp
            timestamp = int(time.time())
            filename = f"{backup_dir}/{collection_name}_backup_{timestamp}.json"
            
            # Lưu vào file JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Backed up {count} documents from collection '{collection_name}' to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error backing up MongoDB collection {collection_name}: {e}")
            print(f"❌ Error backing up MongoDB collection {collection_name}: {e}")
            return None
    
    @staticmethod
    async def clean_db(collection_name: Optional[str] = "crawl_results", auto_backup: bool = True):
        """Làm rỗng database theo collection_name"""
        try:
            # Tự động backup trước khi xóa (nếu auto_backup=True)
            if auto_backup:
                backup_file = await SaveUtils.backup_db(collection_name)
                if backup_file:
                    print(f"✅ Backup completed before cleaning")
            
            collection = get_collection(collection_name)
            
            # Xóa tất cả documents trong collection
            delete_result = await collection.delete_many({})
            deleted_count = delete_result.deleted_count
            
            logger.info(f"Cleaned {deleted_count} documents from MongoDB collection: {collection_name}")
            print(f"🧹 Cleaned {deleted_count} documents from MongoDB collection: {collection_name}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning MongoDB collection {collection_name}: {e}")
            print(f"❌ Error cleaning MongoDB collection {collection_name}: {e}")
            return None
        
    @staticmethod
    async def filter_urls(urls: List[str], collection_name: Optional[str] = "crawl_results", id_fallback: Optional[int] = 0) -> tuple[List[str], int]:
        """
        Lọc ra các URLs chưa tồn tại trong collection và lấy ID lớn nhất
        
        Args:
            urls: Danh sách URLs cần kiểm tra
            collection_name: Tên collection cần kiểm tra
            
        Returns:
            Tuple gồm (danh sách URLs chưa tồn tại, ID MongoDB lớn nhất hiện tại)
        """
        try:
            collection = get_collection(collection_name)
            
            # Lấy ID lớn nhất hiện tại trong collection
            max_id_doc = await collection.find_one(
                sort=[("_id", -1)],
                projection={"_id": 1}
            )
            max_id = max_id_doc["_id"] if max_id_doc else id_fallback
            
            if not urls:
                return [], max_id
            
            # Tạo index cho field 'link' nếu chưa có (để tăng tốc độ query)
            try:
                await collection.create_index("link")
            except Exception as e:
                logger.warning(f"Index creation skipped or failed: {e}")
            
            # Tìm các URLs đã tồn tại trong collection
            existing_urls = await collection.distinct("link", {"link": {"$in": urls}})
            existing_urls_set = set(existing_urls)
            
            # Lọc ra các URLs chưa tồn tại
            new_urls = [url for url in urls if url not in existing_urls_set]
            
            logger.info(f"Filtered URLs: {len(urls)} total, {len(existing_urls_set)} existing, {len(new_urls)} new | Max ID: {max_id}")
            print(f"🔍 Filtered URLs: {len(urls)} total, {len(existing_urls_set)} existing, {len(new_urls)} new | Max ID: {max_id}")
            
            return new_urls, max_id
            
        except Exception as e:
            logger.error(f"Error filtering URLs from collection {collection_name}: {e}")
            print(f"❌ Error filtering URLs: {e}")
            # Trả về tất cả URLs và ID = 0 nếu có lỗi (fail-safe)
            return urls, id_fallback
    
    @staticmethod
    async def save_db_results(results: List[Dict[str, Any]], collection_name: Optional[str] = "crawl_results", _id: Optional[int] = 0) -> Optional[str]:
        """Lưu kết quả vào MongoDB"""        
        try:
            collection = get_collection(collection_name)
        
            # Chuẩn bị documents để insert
            documents = []
            for i, result in enumerate(results):
                document = {
                    **result,
                    "created_date": time.time(),
                    "_id": _id + i + 1
                }
                
                documents.append(document)
            
            # Insert vào MongoDB
            if documents:
                insert_result = await collection.insert_many(documents)
                inserted_count = len(insert_result.inserted_ids)
                
                logger.info(f"Saved {inserted_count} results to MongoDB collection: {collection_name}")
                print(f"💾 Saved {inserted_count} results to MongoDB collection: {collection_name}")
                return f"{collection_name}"
            else:
                logger.warning("No results to save")
                print("⚠️ No results to save")
                return None
            
        except Exception as e:
            logger.error(f"Error saving to MongoDB collection {collection_name}: {e}")
            print(f"❌ Error saving to MongoDB: {e}")
            return None
        
    @staticmethod
    async def save_json_results(results: List[Dict[str, Any]], collection_name: Optional[str] = "crawl_results", _id: Optional[int] = 0) -> Optional[str]:
        try:
            # Tạo thư mục data nếu chưa tồn tại
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Tạo tên file dựa trên collection_name và timestamp
            timestamp = int(time.time())
            filename = f"{data_dir}/{collection_name}_{timestamp}.json"
            
            # Chuẩn bị documents để lưu
            documents = []
            for i, result in enumerate(results):
                document = {
                    **result,
                    "created_date": time.time(),
                    "_id": str(_id + i + 1)
                }
                documents.append(document)
            
            # Lưu vào file JSON
            if documents:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(documents, f, ensure_ascii=False, indent=2)
                
                saved_count = len(documents)
                logger.info(f"Saved {saved_count} results to JSON file: {filename}")
                print(f"💾 Saved {saved_count} results to JSON file: {filename}")
                return filename
            else:
                logger.warning("No results to save")
                print("⚠️ No results to save")
                return None
                
        except Exception as e:
            logger.error(f"Error saving to JSON file: {e}")
            print(f"❌ Error saving to JSON file: {e}")
            return None
        