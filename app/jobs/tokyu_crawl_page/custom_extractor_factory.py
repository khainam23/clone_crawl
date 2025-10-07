"""
Factory for creating CustomExtractor with all processors for Tokyu
Optimized version with clear processing pipeline
"""
from typing import Dict, Any

from app.jobs.crawl_strcture.custom_rules import CustomExtractor
from app.jobs.tokyu_crawl_page.image_extractor import ImageExtractor
from app.jobs.tokyu_crawl_page.map_extractor import MapExtractor
from app.jobs.tokyu_crawl_page.property_data_extractor import PropertyDataExtractor


class CustomExtractorFactory:
    """Factory for creating and configuring CustomExtractor with optimized pipeline"""
    
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
        """
        Setup optimized custom extractor with clear processing pipeline
        
        Processing Order (13 steps):
        1. Store HTML in _html field
        2. Extract images from page
        3. Extract building information (name, type, structure, address, year)
        4. Extract unit information (unit_no, floor, size, direction)
        5. Extract rental costs (monthly_rent, monthly_maintenance)
        6. Extract other fees (cleaning fee, other expenses)
        7. Extract unit description (pet info, remarks)
        8. Extract deposits and fees (deposit, key money, renewal)
        9. Extract amenities from 設備・条件 section
        10. Extract pet policy from 敷金積増 section
        11. Set default amenities
        12. Calculate financial info (guarantor, agency, insurance, discount, availability)
        13. Extract map coordinates
        14. Cleanup temporary fields (_html)
        """
        # Create new instances for each extractor to avoid shared state in parallel processing
        image_extractor = ImageExtractor()
        property_extractor = PropertyDataExtractor()
        map_extractor = MapExtractor()
        
        extractor = CustomExtractor()
        
        # Pre-processing: Store HTML
        extractor.add_pre_hook(self._store_html)
        
        # Define processing pipeline in order
        processors = [
            image_extractor.extract_images,              # 1. Extract images
            property_extractor.extract_building_info,    # 2. Building info
            property_extractor.extract_unit_info,        # 3. Unit info
            property_extractor.extract_rental_costs,     # 4. Rental costs
            property_extractor.extract_other_fee,        # 5. Other fees
            property_extractor.extract_unit_description, # 6. Unit description
            property_extractor.extract_deposits_and_fees,# 7. Deposits & fees
            property_extractor.extract_future,           # 8. Amenities
            property_extractor.extract_is_pets,          # 9. Pet policy
            property_extractor.set_default_amenities,    # 10. Default amenities
            property_extractor.extract_money,            # 11. Financial calculations
            map_extractor.extract_map,                   # 12. Map coordinates
            # property_extractor.extract_station,          # 13. Station info
            property_extractor.cleanup_temp_fields,      # 14. Cleanup
        ]
        
        # Add all processors with error handling
        for processor in processors:
            extractor.add_post_hook(self._create_safe_wrapper(processor))
        
        return extractor


def setup_custom_extractor() -> CustomExtractor:
    """
    Factory function to create configured CustomExtractor
    """
    factory = CustomExtractorFactory()
    return factory.setup_custom_extractor()