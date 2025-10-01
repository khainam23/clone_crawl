"""
Amenities processing utilities
"""
from typing import Dict, Any, List

# Default amenities for Tokyu
DEFAULT_TOKYU_AMENITIES = {
    'credit_card': 'Y',
    'aircon': 'Y',
    'aircon_heater': 'Y',
    'bs': 'Y',
    'cable': 'Y',
    'internet_broadband': 'Y',
    'phoneline': 'Y',
    'flooring': 'Y',
    'system_kitchen': 'Y',
    'bath': 'Y',
    'shower': 'Y',
    'unit_bath': 'Y',
    'western_toilet': 'Y',
}


def get_default_amenities() -> Dict[str, Any]:
    """
    Get default amenities configuration
    
    Returns:
        Dictionary with default amenities
    """
    return DEFAULT_TOKYU_AMENITIES.copy()


def process_amenities_text(amenities_text: str, amenities_mapping: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Process amenities text and map Japanese amenities to field names
    
    Args:
        amenities_text: Raw amenities text from HTML
        amenities_mapping: Dictionary mapping Japanese amenities to field names
        
    Returns:
        List of dictionaries with amenity info
    """
    found_amenities = []
    
    for jp_amenity, field_name in amenities_mapping.items():
        if jp_amenity in amenities_text:
            found_amenities.append({
                'japanese': jp_amenity,
                'field': field_name
            })
    
    return found_amenities


def apply_amenities_to_data(data: Dict[str, Any], found_amenities: List[Dict[str, str]]) -> None:
    """
    Apply found amenities to data dictionary
    
    Args:
        data: Data dictionary to update
        found_amenities: List of found amenities
    """
    for amenity in found_amenities:
        data[amenity['field']] = 'Y'