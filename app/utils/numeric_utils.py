"""
Numeric processing utilities for rent, deposit, key money, etc.
"""
import re

# Negative indicators for all extraction functions
_NEGATIVE_INDICATORS = ('-', 'なし', '無し', '×', '不可', 'ー', '無', 'NO', 'No', 'no')


def _has_negative_indicator(text: str) -> bool:
    """Check if text contains any negative indicator"""
    return any(indicator in text for indicator in _NEGATIVE_INDICATORS)


def extract_numeric_value(text: str) -> int:
    """
    Extract numeric value from Japanese text
    
    Args:
        text: Text containing numeric value (e.g., "1万円", "25.11m²", "1ヶ月")
        
    Returns:
        Numeric value as integer, 0 if not found or contains negative indicators
    """
    if not text or _has_negative_indicator(text):
        return 0
    
    # Extract number with 万 (10,000) multiplier
    if match := re.search(r'(\d+(?:\.\d+)?)万', text):
        return int(float(match.group(1)) * 10000)
    
    # Extract regular numbers
    if match := re.search(r'(\d+(?:\.\d+)?)', text):
        return int(float(match.group(1)))
    
    return 0


def extract_months_multiplier(text: str) -> float:
    """
    Extract months multiplier from text (e.g., "1ヶ月" -> 1.0)
    
    Args:
        text: Text containing months indicator
        
    Returns:
        Months as float, 0 if not found or contains negative indicators
    """
    if not text or _has_negative_indicator(text):
        return 0
    
    if match := re.search(r'(\d+(?:\.\d+)?)ヶ月', text):
        return float(match.group(1))
    
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
        return 0.0
    
    if match := re.search(r'(\d+(?:\.\d+)?)\s*m[\u00B2\u33A1]?', text):
        return float(match.group(1))
    
    return 0.0