"""
Address parsing utilities for Mitsui crawling
"""
import re
from functools import lru_cache


class CoordinateConverter:
    """Handles Japanese address parsing"""
    
    @staticmethod
    def compile_regex(pattern: str, flags: int = re.DOTALL | re.IGNORECASE) -> re.Pattern:
        """Cache compiled regex patterns for better performance"""
        return re.compile(pattern, flags)
    
    @classmethod
    def parse_japanese_address(cls, address: str) -> dict:
        """Parse Japanese address to extract chome_banchi"""
        if not address:
            return {"chome_banchi": None}
        
        # Use cached regex
        pattern = cls.compile_regex(r'^(?:.*?[都道府県])?(?:.*?[市区町村])?(.*)$')
        match = pattern.match(address)
        
        return {
            "chome_banchi": match.group(1).strip() if match else None
        }