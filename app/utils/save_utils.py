"""
File operation utility functions
"""
import logging, time, json, os
from typing import List, Dict, Any, Optional

from app.db.mongodb import get_collection

# Setup logger
logger = logging.getLogger(__name__)

class SaveUtils:
    """Utility functions cho file operations"""
    
    @staticmethod
    def _ensure_directory(directory: str) -> None:
        """Đảm bảo thư mục tồn tại, tạo nếu cần thiết"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def _prepare_documents(results: List[Dict[str, Any]], start_id: int = 0) -> List[Dict[str, Any]]:
        """Chuẩn bị documents với ID và timestamp"""
        documents = []
        current_time = time.time()
        
        for i, result in enumerate(results):
            document = {
                **result,
                "created_at": current_time,
                "_id": start_id + i + 1
            }
            documents.append(document)
        
        return documents
    
    @staticmethod
    async def backup_db(collection_name: str = "crawl_results") -> Optional[str]:
        """Backup MongoDB collection ra file JSON trước khi thực hiện thao tác"""
        try:
            collection = get_collection(collection_name)
            
            # Đếm số lượng documents
            count = await collection.count_documents({})
            
            if count == 0:
                logger.info(f"No data to backup in collection: {collection_name}")
                print(f"ℹ️ No data to backup in collection: {collection_name}")
                return None
            
            # Lấy tất cả documents từ collection
            cursor = collection.find({})
            documents = await cursor.to_list(length=None)
            
            # Tạo thư mục backup nếu chưa tồn tại
            backup_dir = "data/backups"
            SaveUtils._ensure_directory(backup_dir)
            
            # Tạo tên file backup với timestamp
            timestamp = int(time.time())
            filename = f"{backup_dir}/{collection_name}_backup_{timestamp}.json"
            
            # Lưu vào file JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Backed up {count} documents from collection '{collection_name}' to: {filename}")
            print(f"💾 Backed up {count} documents from collection '{collection_name}' to: {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error backing up MongoDB collection {collection_name}: {e}")
            print(f"❌ Error backing up MongoDB collection {collection_name}: {e}")
            return None
    
    @staticmethod
    async def clean_db(collection_name: str = "crawl_results", auto_backup: bool = True) -> Optional[int]:
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
    async def save_db_results(
        results: List[Dict[str, Any]], 
        collection_name: str = "crawl_results", 
        _id: int = 0
    ) -> Optional[str]:
        """Lưu kết quả vào MongoDB"""        
        try:
            if not results:
                logger.warning("No results to save")
                print("⚠️ No results to save")
                return None
                
            collection = get_collection(collection_name)
            documents = SaveUtils._prepare_documents(results, _id)
            
            # Insert vào MongoDB
            insert_result = await collection.insert_many(documents)
            inserted_count = len(insert_result.inserted_ids)
            
            logger.info(f"Saved {inserted_count} results to MongoDB collection: {collection_name}")
            print(f"💾 Saved {inserted_count} results to MongoDB collection: {collection_name}")
            return collection_name
            
        except Exception as e:
            logger.error(f"Error saving to MongoDB collection {collection_name}: {e}")
            print(f"❌ Error saving to MongoDB: {e}")
            return None
        
    @staticmethod
    async def save_json_results(
        results: List[Dict[str, Any]], 
        collection_name: str = "crawl_results", 
        _id: int = 0
    ) -> Optional[str]:
        """Lưu kết quả vào file JSON"""
        try:
            if not results:
                logger.warning("No results to save")
                print("⚠️ No results to save")
                return None
                
            # Tạo thư mục data nếu chưa tồn tại
            data_dir = "data"
            SaveUtils._ensure_directory(data_dir)
            
            # Tạo tên file dựa trên collection_name và timestamp
            timestamp = int(time.time())
            filename = f"{data_dir}/{collection_name}_{timestamp}.json"
            
            # Chuẩn bị documents và lưu vào file JSON
            documents = SaveUtils._prepare_documents(results, _id)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2, default=str)
            
            saved_count = len(documents)
            logger.info(f"Saved {saved_count} results to JSON file: {filename}")
            print(f"💾 Saved {saved_count} results to JSON file: {filename}")
            return filename
                
        except Exception as e:
            logger.error(f"Error saving to JSON file: {e}")
            print(f"❌ Error saving to JSON file: {e}")
            return None