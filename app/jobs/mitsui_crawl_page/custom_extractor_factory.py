"""
Factory for creating CustomExtractor with all processors
Optimized version with simplified structure
"""
from typing import Dict, Any

from app.jobs.crawl_strcture.custom_rules import CustomExtractor
from app.jobs.mitsui_crawl_page.image_extractor import ImageExtractor
from app.jobs.mitsui_crawl_page.property_data_extractor import PropertyDataExtractor


class CustomExtractorFactory:
    """Factory for creating and configuring CustomExtractor with optimized structure"""
    
    def _create_safe_wrapper(self, callback):
        """Private: Wrapper for safe processing with error handling"""
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
    
    def _store_html(self, html: str, data: Dict[str, Any]) -> tuple:
        """Store HTML in data for post-hooks"""
        data['_html'] = html
        return html, data
    
    def setup_custom_extractor(self) -> CustomExtractor:
        """Setup optimized custom extractor with processing pipeline"""
        # Create new instances for each extractor to avoid shared state in parallel processing
        image_extractor = ImageExtractor()
        property_extractor = PropertyDataExtractor()
        
        extractor = CustomExtractor()
        
        # Pre-processing: Store HTML
        extractor.add_pre_hook(self._store_html)
        
        # Processing pipeline (order matters!)
        processors = [
            image_extractor.extract_images,           # 1. Extract images
            property_extractor.get_static_info,       # 2. Extract all static info
            property_extractor.convert_coordinates,   # 3. Convert coordinates
            property_extractor.set_default_amenities, # 4. Set default amenities
            property_extractor.process_pricing,       # 5. Calculate pricing
            property_extractor.extract_deposit_key_info, # 6. Extract deposit/key (needs total_monthly)
            property_extractor.get_info_district,     # 7. Get district info (needs lat/lng)
            property_extractor.extract_station,      # 8. Extract station service
            property_extractor.cleanup_temp_fields,   # 9. Cleanup temporary fields
        ]
        
        # Add all processors with error handling
        for processor in processors:
            extractor.add_post_hook(self._create_safe_wrapper(processor))
        
        return extractor


def setup_custom_extractor() -> CustomExtractor:
    """Factory function to create configured CustomExtractor"""
    factory = CustomExtractorFactory()
    return factory.setup_custom_extractor()