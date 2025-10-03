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
    
    @staticmethod
    def set_default_amenities(data: Dict[str, Any], default_amenities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set default amenities using provided constants
        
        Args:
            data: Property data dictionary
            default_amenities: Dictionary of default amenity values
            
        Returns:
            Updated data dictionary
        """
        data.update(default_amenities)
        return data
    
    @staticmethod
    def process_pricing(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process pricing calculations with validation
        Calculates total_monthly, numeric_guarantor, and numeric_guarantor_max
        Includes other_subscription_fees (めやす賃料) if available
        
        Args:
            data: Property data dictionary containing monthly_rent, monthly_maintenance,
                  and optionally other_subscription_fees
            
        Returns:
            Updated data dictionary with calculated pricing fields
        """
        if not all(key in data for key in ['monthly_rent', 'monthly_maintenance']):
            return data

        try:
            monthly_rent = data['monthly_rent']
            monthly_maintenance = data['monthly_maintenance']
            total_monthly = data['total_monthly']
            
            # Calculate total including めやす賃料 (estimated rent) if available
            other_subscription_fees = total_monthly - (monthly_rent + monthly_maintenance)

            if total_monthly > 0:
                data.update({
                    "total_monthly": total_monthly,
                    "numeric_guarantor": total_monthly * 50 // 100,
                    "numeric_guarantor_max": total_monthly * 80 // 100,
                    "other_subscription_fees": other_subscription_fees
                })
            else:
                logger.warning(f"Invalid total monthly amount")

        except Exception as e:
            logger.error(f"Error processing pricing: {e}")

        return data
    
    @staticmethod
    def cleanup_temp_fields(data: Dict[str, Any], *field_names: str) -> Dict[str, Any]:
        """
        Remove temporary fields that shouldn't be in final JSON
        
        Args:
            data: Property data dictionary
            *field_names: Variable number of field names to remove (default: '_html')
            
        Returns:
            Updated data dictionary with temporary fields removed
        """
        fields_to_remove = field_names if field_names else ('_html',)
        
        for field in fields_to_remove:
            if field in data:
                del data[field]
                logger.debug(f"Cleaned up temporary field: {field}")
        
        return data