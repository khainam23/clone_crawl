"""
Numeric processing utilities for rent, deposit, key money, etc.
"""
import re
from app.utils.html_processor_utils import HtmlProcessor


def extract_numeric_value(text: str) -> int:
    """
    Extract numeric value from Japanese text
    
    Args:
        text: Text containing numeric value (e.g., "1万円", "25.11m²", "1ヶ月")
        
    Returns:
        Numeric value as integer, 0 if not found or contains negative indicators
    """
    if not text:
        return 0
    
    # Check for negative indicators
    negative_indicators = ['-', 'なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no']
    if any(indicator in text for indicator in negative_indicators):
        return 0
    
    html_processor = HtmlProcessor()
    
    # Extract number with 万 (10,000) multiplier
    man_pattern = html_processor.compile_regex(r'(\d+(?:\.\d+)?)万')
    man_match = man_pattern.search(text)
    if man_match:
        return int(float(man_match.group(1)) * 10000)
    
    # Extract regular numbers
    number_pattern = html_processor.compile_regex(r'(\d+(?:\.\d+)?)')
    number_match = number_pattern.search(text)
    if number_match:
        return int(float(number_match.group(1)))
    
    return 0


def extract_months_multiplier(text: str) -> float:
    """
    Extract months multiplier from text (e.g., "1ヶ月" -> 1.0)
    
    Args:
        text: Text containing months indicator
        
    Returns:
        Months as float, 0 if not found or contains negative indicators
    """
    if not text:
        return 0
    
    # Check for negative indicators
    negative_indicators = ['-', 'なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no']
    if any(indicator in text for indicator in negative_indicators):
        return 0
    
    html_processor = HtmlProcessor()
    
    # Extract months
    months_pattern = html_processor.compile_regex(r'(\d+(?:\.\d+)?)ヶ月')
    months_match = months_pattern.search(text)
    if months_match:
        return float(months_match.group(1))
    
    return 0


def extract_area_size(text: str) -> float:
    """
    Extract area size from text (e.g., "25.11m²" -> 25.11)
    
    Args:
        text: Text containing area size
        
    Returns:
        Area size as float, 0 if not found
    """
    if not text:
        return 0
    
    html_processor = HtmlProcessor()
    
    # Extract area size
    area_pattern = html_processor.compile_regex(r'(\d+(?:\.\d+)?)m²')
    area_match = area_pattern.search(text)
    if area_match:
        return float(area_match.group(1))
    
    return 0