"""
District utilities for geospatial queries

Thực hiện tính toán bằng chuyển đội tọa độ không gian
"""
from typing import List, Optional
from app.db.mongodb import mongodb_sync
from pymongo.errors import OperationFailure
import logging

logger = logging.getLogger(__name__)

def ensure_district_index() -> bool:
    """
    Tạo 2dsphere index cho collection district.
    Hàm này nên được gọi 1 lần khi khởi động ứng dụng.
    
    Returns:
        bool: True nếu index đã tồn tại hoặc tạo thành công, False nếu có lỗi
    """
    try:
        districts_collection = mongodb_sync.get_collection('district')
        
        # Kiểm tra xem index đã tồn tại chưa
        indexes = districts_collection.index_information()
        if 'location_2dsphere' in indexes:
            logger.info("✅ Index 'location_2dsphere' đã tồn tại")
            return True
        
        # Tạo index mới
        districts_collection.create_index([("location", "2dsphere")], name='location_2dsphere')
        logger.info("✅ Đã tạo index 'location_2dsphere' thành công")
        return True
        
    except OperationFailure as e:
        logger.error(f"❌ Lỗi khi tạo index: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Lỗi không xác định khi tạo index: {e}")
        return False


def get_district(lat: float, lng: float) -> List[Optional[str]]:
    """
    Tìm district gần nhất dựa trên tọa độ.
    
    Args:
        lat: Latitude (vĩ độ)
        lng: Longitude (kinh độ)
    
    Returns:
        List[Optional[str]]: [name, prefecture, city] hoặc [None, None, None] nếu không tìm thấy
    
    Note:
        Đảm bảo đã gọi ensure_district_index() trước khi sử dụng hàm này
    """
    try:
        # Get districts collection (sync version)
        districts_collection = mongodb_sync.get_collection('district')

        # MongoDB uses [longitude, latitude] order for GeoJSON
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(lng), float(lat)]
                    }
                }
            }
        }

        # Find the nearest district
        district = districts_collection.find_one(query)
        
        if district:
            return [
                district.get('name'),
                district.get('prefecture'), 
                district.get('city')
            ]
        else:
            return [None, None, None]

    except (ValueError, TypeError) as e:
        logger.error(f"❌ Invalid coordinates: lat={lat}, lng={lng}, error={e}")
        return [None, None, None]
    except Exception as e:
        logger.error(f"❌ Error getting district: {e}")
        return [None, None, None]
