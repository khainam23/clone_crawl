"""
Direction processing utilities
"""
from typing import Dict, Any

# Direction mapping
DIRECTION_MAPPING = {
    '北': 'facing_north',
    '北東': 'facing_northeast', 
    '東': 'facing_east',
    '東南': 'facing_southeast',
    '南': 'facing_south',
    '南西': 'facing_southwest',
    '西': 'facing_west',
    '西北': 'facing_northwest',
    '北西': 'facing_northwest'
}


def extract_direction_info(direction_text: str) -> Dict[str, str]:
    """
    Extract apartment facing direction
    
    Args:
        direction_text: Raw direction text from HTML
        
    Returns:
        Dictionary with direction field set to 'Y'
    """
    result = {}
    
    for jp_direction, field_name in DIRECTION_MAPPING.items():
        if jp_direction in direction_text:
            result[field_name] = 'Y'
            break
    
    return result