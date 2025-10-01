"""
Factory for creating CustomExtractor with all processors
"""
from typing import Dict, Any

from app.jobs.crawl_strcture.custom_rules import CustomExtractor
from app.utils.html_processor_utils import HtmlProcessor
from app.jobs.mitsui_crawl_page.image_extractor import ImageExtractor
from app.services.station_service import StationService
from app.jobs.mitsui_crawl_page.property_data_extractor import PropertyDataExtractor
from app.jobs.mitsui_crawl_page.property_data_extractor import PropertyDataExtractor


class CustomExtractorFactory:
    """Factory for creating and configuring CustomExtractor"""
    
    def __init__(self):
        self.html_processor = HtmlProcessor()
        self.image_extractor = ImageExtractor()
        self.station_service = StationService()
        self.property_extractor = PropertyDataExtractor()
    
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
            self.property_extractor.get_static_info,
            self.property_extractor.convert_coordinates, 
            self.station_service.set_station_data,
            self.property_extractor.set_default_amenities,
            self.property_extractor.process_pricing,
            self.property_extractor.extract_deposit_key_info, # Vì nó cần giá trị của total_monthly
            self.property_extractor.get_info_district, # cần giá trị lng, lat
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