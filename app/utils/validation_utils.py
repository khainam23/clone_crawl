"""
Data validation utility functions
"""

import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Setup logger
logger = logging.getLogger(__name__)


class ValidationUtils:
    """Utility functions cho data validation"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Kiểm tra URL có hợp lệ không"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_property_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate và clean property data"""
        validated_data = {}
        
        # Required fields
        required_fields = ['link']
        for field in required_fields:
            if field in data and data[field]:
                validated_data[field] = data[field]
            else:
                logger.warning(f"Missing required field: {field}")
        
        # Optional fields with validation
        if 'building_name_ja' in data:
            name = str(data['building_name_ja']).strip()
            if name:
                validated_data['building_name_ja'] = name
        
        # Numeric fields
        numeric_fields = ['rent', 'management_fee', 'deposit', 'key_money']
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    validated_data[field] = float(data[field])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid numeric value for {field}: {data[field]}")
        
        # Copy other fields as-is
        for key, value in data.items():
            if key not in validated_data and value is not None:
                validated_data[key] = value
        
        return validated_data
    
    @staticmethod
    def validate_urls(urls: List[str]) -> List[str]:
        """Validate danh sách URLs"""
        valid_urls = []
        
        for url in urls:
            if ValidationUtils.is_valid_url(url):
                valid_urls.append(url)
            else:
                logger.warning(f"Invalid URL skipped: {url}")
        
        logger.info(f"Validated {len(valid_urls)}/{len(urls)} URLs")
        return valid_urls