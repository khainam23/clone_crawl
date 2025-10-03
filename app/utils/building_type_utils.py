"""
Building type processing utilities
"""
import difflib

from app.utils.html_processor_utils import HtmlProcessor

# Building type mapping
BUIDING_TYPE_MAPPING = {
    "マンション・ビル": "mansion",
    "分譲マンション": "mansion",
    "アパート・コーポ": "apartment",
    "テナントビル": "office",
    "駐車場": "other",
    "戸建て": "house",
}


def extract_building_type(building_type_texts: str) -> str:
    """
    Extract and map building type information
    
    Args:
        building_type_texts: Raw building type text from HTML
        
    Returns:
        Mapped building type
    """
    html_processor = HtmlProcessor()
    
    def map_building_type(original_type: str) -> str:
        if not original_type:
            return "other"
        
        keys = list(BUIDING_TYPE_MAPPING.keys())
        # Tìm key giống nhất, cutoff = 0.5 để tránh match lung tung
        matches = difflib.get_close_matches(original_type, keys, n=1, cutoff=0.5)
        
        if matches:
            return BUIDING_TYPE_MAPPING[matches[0]]
        return "other"
    
    # Clean and extract building type from text
    if not building_type_texts:
        return "other"
    
    # Strip whitespace and extract the building type
    cleaned_text = building_type_texts.strip()
    
    # Try direct mapping first
    if cleaned_text in BUIDING_TYPE_MAPPING:
        return BUIDING_TYPE_MAPPING[cleaned_text]
    
    # Use fuzzy matching for similar strings
    return map_building_type(cleaned_text)