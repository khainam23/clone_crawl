"""
Construction date processing utilities
"""
from app.utils.html_processor_utils import HtmlProcessor


def extract_construction_year(construction_text: str) -> int:
    """
    Extract construction year from text
    
    Args:
        construction_text: Raw construction date text from HTML
        
    Returns:
        Construction year as integer, or None if not found
    """
    html_processor = HtmlProcessor()
    
    year_pattern = html_processor.compile_regex(r'(\d{4})年')
    year_match = year_pattern.search(construction_text)
    
    if year_match:
        return int(year_match.group(1))
    
    return None