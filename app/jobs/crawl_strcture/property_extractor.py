"""Module chính xử lý extract dữ liệu property với BeautifulSoup"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, Callable

from app.models.structure_model import get_empty_property_data
from app.utils.property_utils import PropertyUtils
from app.core.config import CrawlerConfig
from .custom_rules import CustomExtractor

class PropertyExtractor:
    def __init__(self, custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None):
        self.config = CrawlerConfig()
        self.custom_extractor = custom_extractor_factory() if custom_extractor_factory else CustomExtractor()
    
    async def _fetch_html(self, url: str, session: aiohttp.ClientSession) -> tuple[bool, str, str]:
        """Fetch HTML từ URL (không retry). Returns: (success, html_content, error_message)"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return (True, await response.text(), "")
                return (False, "", f"HTTP {response.status}")
        except asyncio.TimeoutError:
            return (False, "", "Request timeout")
        except aiohttp.ClientError as e:
            return (False, "", f"Client error: {str(e)}")
        except Exception as e:
            return (False, "", f"Unexpected error: {str(e)}")
    
    async def extract_property_data(self, url: str, crawler: Optional[aiohttp.ClientSession] = None) -> Dict[str, Any]:
        """Extract dữ liệu bất động sản từ URL với đầy đủ thông tin theo PropertyModel"""
        try:
            # Sử dụng session từ pool hoặc tạo mới
            if crawler:
                return await self._process_url(url, crawler)
            
            # Tạo session mới nếu không có từ pool
            timeout = aiohttp.ClientTimeout(
                total=self.config.get_timeout(),
                connect=10,
                sock_read=self.config.get_timeout()
            )
            async with aiohttp.ClientSession(headers=self.config.get_headers(), timeout=timeout) as session:
                return await self._process_url(url, session)
                    
        except Exception as e:
            error_msg = str(e)
            PropertyUtils.log_crawl_error(url, error_msg)
            return PropertyUtils.create_crawl_result(error=error_msg)
    
    async def _process_url(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Xử lý fetch và extract data từ URL"""
        success, html_content, error_msg = await self._fetch_html(url, session)
        
        if not success:
            PropertyUtils.log_crawl_error(url, error_msg)
            return PropertyUtils.create_crawl_result(error=error_msg)
        
        # Extract và flatten data
        extracted_data = self._extract_comprehensive_data(url, html_content)
        flattened_data = self._flatten_nested_data(extracted_data)
        
        PropertyUtils.log_crawl_success(url, flattened_data)
        return PropertyUtils.create_crawl_result(property_data=flattened_data)
    
    def _extract_comprehensive_data(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract comprehensive property data từ HTML content"""
        extracted_data = get_empty_property_data(url)
        return self.custom_extractor.extract_with_rules(html_content, extracted_data)
    
    def _flatten_nested_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested data (images, stations) thành các field riêng biệt"""
        # Flatten images
        if 'images' in data and isinstance(data['images'], list):
            for i, img in enumerate(data.pop('images', []), 1):
                if isinstance(img, dict):
                    if img.get('url'):
                        data[f'image_url_{i}'] = img['url']
                    if img.get('category'):
                        data[f'image_category_{i}'] = img['category']
        
        # Flatten stations
        if 'stations' in data and isinstance(data['stations'], list):
            for i, station in enumerate(data.pop('stations', []), 1):
                if isinstance(station, dict):
                    if station.get('station_name'):
                        data[f'station_name_{i}'] = station['station_name']
                    if station.get('train_line_name'):
                        data[f'train_line_name_{i}'] = station['train_line_name']
                    if station.get('walk_time') is not None:
                        data[f'walk_time_{i}'] = station['walk_time']
        
        # Loại bỏ các field None
        return {k: v for k, v in data.items() if v is not None}