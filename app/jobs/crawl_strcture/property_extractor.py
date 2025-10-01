"""
Module chính xử lý extract dữ liệu property
"""

from typing import Dict, Any, Optional, Callable
from crawl4ai import AsyncWebCrawler

from app.models.structure_model import get_empty_property_data
from app.utils.property_utils import PropertyUtils
from app.utils.validation_utils import ValidationUtils
from app.core.config import CrawlerConfig
from .custom_rules import CustomExtractor

class PropertyExtractor:    
    def __init__(self, custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None):
        """
        Initialize PropertyExtractor
        
        Args:
            custom_extractor_factory: Optional factory function to create custom extractor
                                    If None, will use basic extractor
        """
        self.config = CrawlerConfig()
        self.utils = PropertyUtils()
        
        # Use provided factory or create basic extractor
        if custom_extractor_factory:
            self.custom_extractor = custom_extractor_factory()
        else:
            self.custom_extractor = CustomExtractor()  # Basic extractor
    
    async def extract_property_data(self, url: str) -> Dict[str, Any]:
        """
        Extract dữ liệu bất động sản từ URL với đầy đủ thông tin theo PropertyModel
        """
        try:
            async with AsyncWebCrawler(config=self.config.BROWSER_CONFIG) as crawler:
                result = await crawler.arun(
                    url=url,
                    config=self.config.RUN_CONFIG
                )
                
                if result.success:
                    # Extract comprehensive property data
                    extracted_data = self._extract_comprehensive_data(url, result)
                    
                    # Validate data before creating result
                    validated_data = ValidationUtils.validate_property_data(extracted_data)
                    
                    # Log success message
                    PropertyUtils.log_crawl_success(url, validated_data)
                    
                    return PropertyUtils.create_crawl_result(
                        property_data=validated_data,
                    )
                else:
                    error_msg = result.error_message or 'Failed to extract content'
                    PropertyUtils.log_crawl_error(url, error_msg)
                    return PropertyUtils.create_crawl_result(
                        error=error_msg
                    )
                    
        except Exception as e:
            error_msg = str(e)
            PropertyUtils.log_crawl_error(url, error_msg)
            return PropertyUtils.create_crawl_result(
                error=error_msg
            )
    
    def _extract_comprehensive_data(self, url: str, result) -> Dict[str, Any]:
        """
        Extract comprehensive property data từ crawl result
        """
        # Khởi tạo data structure với tất cả fields từ PropertyModel
        extracted_data = get_empty_property_data(url)
        
        # Get content
        html_content = result.html if result.html else ""
        
        # Apply custom rules (this will clean HTML and store it in _html)
        extracted_data = self.custom_extractor.extract_with_rules(html_content, extracted_data)
        
        return extracted_data
    
    def validate_and_create_property_model(self, data: Dict[str, Any]):
        """
        Validate và tạo PropertyModel từ extracted data
        """
        return PropertyUtils.validate_and_create_property_model(data)