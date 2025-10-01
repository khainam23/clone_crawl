"""
Property-related utility functions
"""

import logging
from typing import Dict, Any
from app.models.structure_model import PropertyModel

# Setup logger
logger = logging.getLogger(__name__)


class PropertyUtils:
    """Utility functions cho property processing"""
    
    @staticmethod
    def validate_and_create_property_model(data: Dict[str, Any]) -> PropertyModel:
        """
        Validate và tạo PropertyModel từ extracted data
        """
        try:
            # Tạo PropertyModel
            property_model = PropertyModel(**data)
            return property_model
            
        except Exception as e:
            logger.error(f"Error creating PropertyModel: {e}")
            logger.debug(f"Data causing error: {data}")
            
            # Tạo model với dữ liệu cơ bản
            basic_data = {
                'link': data.get('link'),
                'property_csv_id': data.get('property_csv_id'),
                'create_date': data.get('create_date')
            }
            return PropertyModel(**basic_data)
    
    @staticmethod
    def create_crawl_result(property_data: Dict[str, Any] = None, 
                           error: str = None) -> Dict[str, Any]:
        """Tạo cấu trúc kết quả crawl chuẩn"""
        if property_data:
            result = {
                'property_data': property_data,
            }
        else:
            result = {
                'error': error or 'Unknown error'
            }
        
        return result
    
    @staticmethod
    def log_crawl_success(url: str, data: Dict[str, Any]):
        """Log thông báo crawl thành công"""
        title = data.get('building_name_ja', 'N/A')
        logger.info(f"Successfully crawled: {url} - Title: {title}")
        print(f"✅ Successfully crawled: {url}")
        print(f"🔍 Title: {title}")
    
    @staticmethod
    def log_crawl_error(url: str, error: str):
        """Log thông báo crawl lỗi"""
        logger.error(f"Failed to crawl {url}: {error}")
        print(f"❌ Failed to crawl: {url}")
        print(f"🔍 Error: {error}")
    
    # Backward compatibility methods
    @staticmethod
    def print_crawl_success(url: str, data: Dict[str, Any]):
        """Backward compatibility - use log_crawl_success instead"""
        PropertyUtils.log_crawl_success(url, data)
    
    @staticmethod
    def print_crawl_error(url: str, error: str):
        """Backward compatibility - use log_crawl_error instead"""
        PropertyUtils.log_crawl_error(url, error)