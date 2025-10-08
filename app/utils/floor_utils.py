"""
Floor information processing utilities
"""
from typing import Dict
from app.utils.html_processor_utils import HtmlProcessor


def extract_floor_info(floor_text: str) -> Dict[str, int]:
    """
    Extract floor information from text (e.g., "1階/7階建" -> {"floor_no": 1, "floors": 7})
    
    Args:
        floor_text: Text containing floor information
        
    Returns:
        Dictionary with floor_no and floors
    """
    result = {'floor_no': 0, 'floors': 1}
    
    if not floor_text:
        return result
    
    html_processor = HtmlProcessor()
    
    # Pattern for "X階/Y階建" (full format)
    full_pattern = html_processor.compile_regex(r'(\d+)階/(\d+)階建')
    match = full_pattern.search(floor_text)
    
    if match:
        result['floor_no'] = int(match.group(1))
        result['floors'] = int(match.group(2))
        return result
    
    # Pattern for "-/Y階建" or missing floor_no
    floors_only_pattern = html_processor.compile_regex(r'[-/]+(\d+)階建')
    match = floors_only_pattern.search(floor_text)
    
    if match:
        result['floors'] = int(match.group(1))
        return result
    
    # Pattern for "X階" only (floor number without total floors)
    floor_only_pattern = html_processor.compile_regex(r'(\d+)階')
    match = floor_only_pattern.search(floor_text)
    
    if match:
        result['floor_no'] = int(match.group(1))
        return result
    
    return result


