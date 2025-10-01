"""
Factory for creating CustomExtractor with all processors for Tokyu
"""
from typing import Dict, Any

from app.jobs.crawl_strcture.custom_rules import CustomExtractor
from app.utils.html_processor_utils import HtmlProcessor
from app.jobs.tokyu_crawl_page.image_extractor import ImageExtractor
from app.jobs.tokyu_crawl_page.map_extractor import MapExtractor
from app.jobs.tokyu_crawl_page.property_data_extractor import PropertyDataExtractor


class CustomExtractorFactory:
    """Factory for creating and configuring CustomExtractor"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.image_extractor = ImageExtractor()
        self.property_extractor = PropertyDataExtractor()
        self.map_extractor = MapExtractor()
    
    def create_safe_wrapper(self, callback):
        """Wrapper for safe processing with error handling"""
        def wrapper_func(data: Dict[str, Any]) -> Dict[str, Any]:
            html = data.get('_html', '')
            if not html:
                return data
            
            try:
                return callback(data, html)
            except Exception as e:
                print(f"❌ Error in {callback.__name__}: {e}")
                return data
        
        return wrapper_func
    
    def pass_html(self, html: str, data: Dict[str, Any]) -> tuple:
        """Clean HTML before processing with cached regex"""
        cleaned_html = self.html_processor.clean_html_before_processing(html)
        data['_html'] = cleaned_html
        return cleaned_html, data
    
    def setup_custom_extractor(self) -> CustomExtractor:
        """
        Setup optimized custom extractor with better performance and structure
        """
        extractor = CustomExtractor()
        
        # Setup hooks
        extractor.add_pre_hook(self.pass_html)
        
        # Add processors in order
        processors = [
            self.image_extractor.extract_images,
            self.property_extractor.extract_building_info,
            self.property_extractor.extract_unit_info,
            self.property_extractor.extract_rental_costs,
            self.property_extractor.extract_other_fee,
            self.property_extractor.extract_unit_description,
            self.property_extractor.extract_deposits_and_fees,
            self.property_extractor.extract_future,
            self.property_extractor.extract_is_pets,
            self.property_extractor.set_default_amenities,
            self.property_extractor.extract_money,
            self.map_extractor.extract_map,
            self.property_extractor.extract_station,
            self.property_extractor.cleanup_temp_fields,
        ]
        
        for processor in processors:
            extractor.add_post_hook(self.create_safe_wrapper(processor))
        
        return extractor


def setup_custom_extractor() -> CustomExtractor:
    """
    Factory function to create configured CustomExtractor
    """
    factory = CustomExtractorFactory()
    return factory.setup_custom_extractor()