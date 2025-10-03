"""
Coordinate conversion utilities for Mitsui crawling
"""
import re
from typing import Tuple
from functools import lru_cache
from pyproj import CRS, Transformer

from app.jobs.mitsui_crawl_page.constants import COORDINATE_OFFSET_LAT, COORDINATE_OFFSET_LON, DEFAULT_ZONE


class CoordinateConverter:
    """Handles coordinate conversion from XY to lat/lon"""
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_transformer(zone: int = DEFAULT_ZONE) -> Transformer:
        """Get cached coordinate transformer for better performance"""
        epsg_code = 30160 + zone
        crs_xy = CRS.from_epsg(epsg_code)
        crs_wgs84 = CRS.from_epsg(4326)
        return Transformer.from_crs(crs_xy, crs_wgs84, always_xy=True)
    
    @classmethod
    def xy_to_latlon_tokyo(cls, x: float, y: float, zone: int = DEFAULT_ZONE) -> Tuple[float, float]:
        """
        Convert XY coordinates to lat/lon with Tokyo offset
        """
        transformer = cls.get_transformer(zone)
        lon, lat = transformer.transform(x, y)
        return lat + COORDINATE_OFFSET_LAT, lon + COORDINATE_OFFSET_LON
    
    @staticmethod
    @lru_cache(maxsize=128)
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