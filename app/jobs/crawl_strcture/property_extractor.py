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
        self.custom_extractor_factory = custom_extractor_factory
    
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
        try:
            
            # Extract và flatten data
            extracted_data = await self._extract_comprehensive_data(url, html_content)
            
            html_content = None
            
            flattened_data = self._flatten_nested_data(extracted_data)
            
            PropertyUtils.log_crawl_success(url, flattened_data)
            return PropertyUtils.create_crawl_result(property_data=flattened_data)
        finally:
            # Đảm bảo nội dung HTML được giải phóng
            html_content = None
            # Bắt buộc garbage collection
            import gc
            gc.collect()
    
    async def _extract_comprehensive_data(self, url: str, html_content: str) -> Dict[str, Any]:
        """Extract comprehensive property data từ HTML content"""
        extracted_data = get_empty_property_data(url)
        # Create a new extractor instance for each request to avoid shared state in parallel processing
        custom_extractor = self.custom_extractor_factory() if self.custom_extractor_factory else CustomExtractor()
        return await custom_extractor.extract_with_rules_async(html_content, extracted_data)
    
    def _flatten_nested_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested data (images, stations) thành các field riêng biệt"""
        def flatten_list(key, items, mapping):
            for i, item in enumerate(data.pop(key, []), 1):
                if isinstance(item, dict):
                    for k, v in mapping.items():
                        if item.get(k) is not None:
                            data[f'{v}_{i}'] = item[k]

        flatten_list('images', data.get('images', []), {
            'url': 'image_url',
            'category': 'image_category'
        })
        flatten_list('stations', data.get('stations', []), {
            'station_name': 'station_name',
            'train_line_name': 'train_line_name',
            'walk_time': 'walk_time'
        })

        # Đảm bảo giá trị số không âm và bỏ None
        return {
            k: (0 if isinstance(v, (int, float)) and v < 0 else v)
            for k, v in data.items() if v is not None
        }
