"""
File operation utility functions
"""
import logging, time
from typing import List, Dict, Any, Optional
import logging, time, json, os
from app.core.config import settings

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
    async def filter_urls(urls: List[str], collection_name: Optional[str] = "crawl_results", id_fallback: Optional[int] = 0) -> tuple[List[str], List[int]]:
        """
        Lọc ra các URLs chưa tồn tại trong collection hoặc đã quá hạn cập nhật và lấy danh sách ID khả dụng
        
        Ngoài ra phải loại bỏ các url trong collection không còn tồn tại khi trong các url crawl về tránh tình trạng nhà đã được đóng
        
        Args:
            urls: Danh sách URLs cần kiểm tra
            collection_name: Tên collection cần kiểm tra
            id_fallback: ID mặc định nếu collection rỗng
            
        Returns:
            Tuple gồm (danh sách URLs chưa tồn tại hoặc cần cập nhật, danh sách ID khả dụng để sử dụng)
        """
        try:
            collection = get_collection(collection_name)
            
            # Lấy ID lớn nhất hiện tại trong collection
            max_id_doc = await collection.find_one(
                sort=[("_id", -1)],
                projection={"_id": 1}
            )
            # Convert string _id to int if needed
            if max_id_doc:
                max_id = int(max_id_doc["_id"]) if isinstance(max_id_doc["_id"], str) else max_id_doc["_id"]
            else:
                max_id = id_fallback
            
            if not urls:
                return [], []
            
            # Tạo index cho field 'link' nếu chưa có (để tăng tốc độ query)
            try:
                await collection.create_index("link")
            except Exception as e:
                logger.warning(f"Index creation skipped or failed: {e}")
            
            # Tính thời gian hiện tại
            current_time = time.time()
            cutoff_time = current_time - settings.LAST_UPDATED
            
            # Tìm các URLs đã tồn tại và còn mới (created_date > cutoff_time)
            # Chỉ lấy những URLs còn fresh, không cần cập nhật
            fresh_urls = await collection.distinct(
                "link", 
                {
                    "link": {"$in": urls},
                    "created_date": {"$gt": cutoff_time}
                }
            )
            fresh_urls_set = set(fresh_urls)
            
            # Lọc ra các URLs chưa tồn tại hoặc đã quá hạn
            new_urls = [url for url in urls if url not in fresh_urls_set]
            
            # Xóa các URLs trong collection không còn tồn tại trong danh sách crawl
            # (Tránh tình trạng nhà đã được đóng nhưng vẫn còn trong DB)
            urls_set = set(urls)
            delete_result = await collection.delete_many({
                "link": {"$nin": urls}  # URLs không có trong danh sách crawl
            })
            deleted_count = delete_result.deleted_count
            
            if deleted_count > 0:
                logger.info(f"Removed {deleted_count} URLs no longer available in crawl results")
                print(f"🗑️ Removed {deleted_count} closed/unavailable listings from collection")
            
            # Tìm các ID gaps (ID bị thiếu) để tái sử dụng
            available_ids = []
            if len(new_urls) > 0:
                existing_ids = await collection.distinct("_id")
                existing_ids_set = set(int(i) for i in existing_ids)

                max_id = max(existing_ids_set) if existing_ids_set else id_fallback
                needed = len(new_urls)

                # Tìm các ID còn trống (gap)
                all_ids = set(range(id_fallback, max_id + 1))
                available_ids = list(all_ids - existing_ids_set)

                # Cắt vừa đủ số lượng cần thiết
                available_ids = available_ids[:needed]

                # Nếu chưa đủ, thêm các ID mới
                if len(available_ids) < needed:
                    available_ids.extend(range(max_id + 1, max_id + 1 + (needed - len(available_ids))))
            
            gaps_count = len([id for id in available_ids if id <= max_id])
            new_ids_count = len([id for id in available_ids if id > max_id])
            
            print(f"🔍 Filtered URLs: {len(urls)} total, {len(fresh_urls_set)} fresh, {len(new_urls)} to process | 🆔 Available IDs: {gaps_count} gaps + {new_ids_count} new")
            
            return new_urls, available_ids
            
        except Exception as e:
            logger.error(f"Error filtering URLs from collection {collection_name}: {e}")
            print(f"❌ Error filtering URLs: {e}")
            # Trả về tất cả URLs và danh sách ID rỗng nếu có lỗi (fail-safe)
            return urls, []
    
    @staticmethod
    async def save_db_results(results: List[Dict[str, Any]], collection_name: Optional[str] = "crawl_results", available_ids: Optional[List[int]] = None) -> Optional[str]:
        """Lưu kết quả vào MongoDB - Insert mới hoặc Update nếu URL đã tồn tại"""        
        try:
            collection = get_collection(collection_name)
            
            inserted_count = 0
            updated_count = 0
            # Sử dụng danh sách ID khả dụng hoặc tạo mới nếu không có
            if available_ids is None:
                available_ids = []
            
            id_index = 0  # Index để lấy ID từ available_ids
            
            required_field = [
                'link',
                'room_type', 
                'map_lat', 
                'map_lng', 
                'image_url_3', 
                'image_category_1',
                'image_category_2',
                'station_name_1',
                'floors', 
                'floor_no'
            ]
            
            for result in results:
                missing = [f for f in required_field if f not in result]
                if missing:
                    print(f"Bỏ qua vì thiếu các field: {missing}")
                    continue
                
                if result['map_lat'] <= 0 or result['map_lng'] <= 0:
                    print(f"Bỏ qua vì vị trí không hợp lệ: {result['link']}")
                    continue
                
                link = result.get("link")
                
                # Kiểm tra URL đã tồn tại chưa
                existing_doc = await collection.find_one({"link": link})
                
                if existing_doc:
                    # URL đã tồn tại → UPDATE (giữ nguyên _id cũ)
                    existing_id = str(existing_doc["_id"])
                    document = {
                        **result,
                        "created_date": time.time(),
                        "_id": existing_id   # Giữ nguyên _id cũ
                    }
                    await collection.replace_one({"_id": existing_id}, document)
                    updated_count += 1
                else:
                    # URL mới → INSERT với _id từ available_ids
                    if id_index < len(available_ids):
                        new_id = available_ids[id_index]
                        id_index += 1
                    else:
                        # Fallback: nếu hết available_ids, tìm max_id và tăng dần
                        max_id_doc = await collection.find_one(
                            sort=[("_id", -1)],
                            projection={"_id": 1}
                        )
                        if max_id_doc:
                            max_id = int(max_id_doc["_id"]) if isinstance(max_id_doc["_id"], str) else max_id_doc["_id"]
                            new_id = max_id + 1
                        else:
                            new_id = 1
                    
                    document = {
                        **result,
                        "created_date": time.time(),
                        "_id": str(new_id)  # Convert to string for MongoDB
                    }
                    await collection.insert_one(document)
                    inserted_count += 1
            
            total_count = inserted_count + updated_count
            if total_count > 0:
                logger.info(f"Saved {total_count} results to MongoDB collection '{collection_name}' (Inserted: {inserted_count}, Updated: {updated_count})")
                print(f"💾 Saved {total_count} results to '{collection_name}' (✨ New: {inserted_count}, 🔄 Updated: {updated_count})")
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
        