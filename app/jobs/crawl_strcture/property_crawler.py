"""
Enhanced Property Crawler - Class chính
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable

from .property_extractor import PropertyExtractor
from .custom_rules import CustomExtractor

class EnhancedPropertyCrawler:
    def __init__(self, custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None):
        """
        Initialize EnhancedPropertyCrawler
        
        Args:
            custom_extractor_factory: Optional factory function to create custom extractor
                                    If None, will use basic extractor
        """
        self.extractor = PropertyExtractor(custom_extractor_factory)

    async def _crawl_single_property(self, url: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Private method để crawl một property
        
        Args:
            url: URL to crawl
            verbose: Whether to print progress messages (default: True)
        """
        if verbose:
            print(f"🚀 Crawling: {url}")
        
        try:
            # Extract dữ liệu bằng crawl4ai
            result = await self.extractor.extract_property_data(url)
            
            # Validate và tạo PropertyModel
            property_model = self.extractor.validate_and_create_property_model(
                result['property_data']
            )
            
            # Convert về dict để serialize JSON
            property_dict = property_model.dict(exclude_none=True)
            
            # Chuyển đổi images thành các field riêng biệt
            if 'images' in property_dict and isinstance(property_dict['images'], list):
                images_list = property_dict.pop('images', [])
                for i, img in enumerate(images_list):
                    img_num = i + 1
                    if isinstance(img, dict):
                        if 'url' in img:
                            property_dict[f'image_url_{img_num}'] = img['url']
                        if 'category' in img:
                            property_dict[f'image_category_{img_num}'] = img['category']
                            
            # Chuyển đổi station thành các field riêng biệt
            if 'stations' in property_dict and isinstance(property_dict['stations'], list):
                stations_list = property_dict.pop('stations', [])
                for i, station in enumerate(stations_list):
                    station_num = i + 1
                    if isinstance(station, dict):
                        if 'station_name' in station:
                            property_dict[f'station_name_{station_num}'] = station['station_name']
                        if 'train_line_name' in station:
                            property_dict[f'train_line_name_{station_num}'] = station['train_line_name']
            
            result['property_data'] = property_dict
            
            return result['property_data']
            
        except Exception as e:
            error_result = {
                'error': str(e),
            }
            if verbose:
                print(f"❌ Exception crawling {url}: {e}")
            return error_result

    async def crawl_multiple_properties(self, urls: List[str], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Crawl nhiều properties với batch processing để tránh timeout
        
        Args:
            urls: List of URLs to crawl
            batch_size: Number of URLs to crawl simultaneously (default: 5)
        """
        print(f"🏘️ Crawling {len(urls)} properties in batches of {batch_size}...")
        
        all_results = []
        
        # Chia URLs thành các batches
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(urls) + batch_size - 1) // batch_size
            
            print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_urls)} URLs)...")
            
            # Tạo tasks cho batch hiện tại
            tasks = [self._crawl_single_property(url) for url in batch_urls]
            
            # Chạy parallel với error handling cho batch này
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Xử lý exceptions cho batch
            processed_batch_results = []
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    processed_batch_results.append({
                        'error': str(result),
                        'url': batch_urls[j]
                    })
                else:
                    processed_batch_results.append(result)
            
            all_results.extend(processed_batch_results)
            
            # Thêm delay giữa các batches để tránh quá tải server
            if i + batch_size < len(urls):  # Không delay sau batch cuối
                print(f"⏳ Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)
        
        print(f"✅ Completed crawling all {len(urls)} properties!")
        return all_results