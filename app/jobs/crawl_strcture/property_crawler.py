"""
Enhanced Property Crawler - Class chính
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable

from .property_extractor import PropertyExtractor
from .custom_rules import CustomExtractor
from .crawler_pool import CrawlerPool
from app.core.config import settings

class EnhancedPropertyCrawler:
    def __init__(self, custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None):
        """
        Initialize EnhancedPropertyCrawler
        
        Args:
            custom_extractor_factory: Optional factory function to create custom extractor
                                    If None, will use basic extractor
        """
        self.extractor = PropertyExtractor(custom_extractor_factory)
        self.custom_extractor_factory = custom_extractor_factory
        self.pool: Optional[CrawlerPool] = None

    async def _crawl_single_property(self, url: str, verbose: bool = True, pool: Optional[CrawlerPool] = None) -> Dict[str, Any]:
        """
        Private method để crawl một property
        
        Args:
            url: URL to crawl
            verbose: Whether to print progress messages (default: True)
            pool: Optional CrawlerPool instance to use
        """
        if verbose:
            print(f"🚀 Crawling: {url}")
        
        crawler = None
        try:
            # Nếu có pool, lấy crawler từ pool
            if pool:
                crawler = await pool.acquire()
                result = await self.extractor.extract_property_data(url, crawler=crawler)
            else:
                # Fallback: không dùng pool
                result = await self.extractor.extract_property_data(url)
            
            # Trả về trực tiếp property_data đã được flatten trong extractor
            return result.get('property_data', result)
            
        except Exception as e:
            error_result = {
                'error': str(e),
            }
            if verbose:
                print(f"❌ Exception crawling {url}: {e}")
            return error_result
        finally:
            # Trả crawler về pool nếu đã lấy từ pool
            if pool and crawler:
                await pool.release(crawler)

    async def crawl_multiple_properties(
        self, 
        urls: List[str], 
        batch_size: int = 10,
        on_batch_complete: Optional[Callable[[List[Dict[str, Any]], int, int], Any]] = None,
        max_consecutive_failures: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Crawl nhiều properties với batch processing và crawler pool để tránh timeout và overhead
        
        Args:
            urls: List of URLs to crawl
            batch_size: Number of URLs to crawl simultaneously (default: 10)
            on_batch_complete: Optional callback function được gọi sau mỗi batch
                             Nhận params: (batch_results, batch_num, total_batches)
            max_consecutive_failures: Maximum consecutive failures before stopping (default: 30)
        """
        print(f"🏘️ Crawling {len(urls)} properties in batches of {batch_size}...")
        
        all_results = []
        consecutive_failures = 0
        
        # Khởi tạo HTTP session pool với kích thước bằng batch_size
        async with CrawlerPool(pool_size=batch_size, custom_extractor_factory=self.custom_extractor_factory) as pool:
            # Chia URLs thành các batches
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(urls) + batch_size - 1) // batch_size
                
                print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_urls)} URLs)...")
                
                # Tạo tasks cho batch hiện tại với pool
                tasks = [self._crawl_single_property(url, pool=pool) for url in batch_urls]
                
                # Chạy parallel với error handling cho batch này
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Xử lý exceptions cho batch và đếm consecutive failures
                processed_batch_results = []
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        processed_batch_results.append({
                            'error': str(result),
                            'url': batch_urls[j]
                        })
                        consecutive_failures += 1
                    else:
                        # Kiểm tra nếu result có 'error' key (crawl failed)
                        if isinstance(result, dict) and 'error' in result:
                            consecutive_failures += 1
                        else:
                            # Reset counter chỉ khi có success thật sự
                            if consecutive_failures > 0:
                                print(f"✅ Success after {consecutive_failures} consecutive failures - counter reset")
                            consecutive_failures = 0
                        
                        processed_batch_results.append(result)
                    
                    # Kiểm tra threshold sau mỗi result
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"🛑 Stopping crawl: {consecutive_failures} consecutive failures reached!")
                        print(f"⚠️ Crawled {len(all_results)} out of {len(urls)} URLs before stopping")
                        return all_results
                    elif consecutive_failures > 0 and consecutive_failures % 5 == 0:
                        print(f"⚠️ Warning: {consecutive_failures} consecutive failures (max: {max_consecutive_failures})")
                
                all_results.extend(processed_batch_results)
                
                # Gọi callback sau khi hoàn thành batch (nếu có)
                if on_batch_complete:
                    try:
                        await on_batch_complete(processed_batch_results, batch_num, total_batches)
                    except Exception as e:
                        print(f"⚠️ Error in batch callback: {e}")
                
                # Thêm delay giữa các batches để tránh quá tải server
                if i + batch_size < len(urls):  # Không delay sau batch cuối
                    print(f"⏳ Waiting {settings.CRAWLER_DELAY} seconds before next batch...")
                    await asyncio.sleep(settings.CRAWLER_DELAY)
        
        print(f"✅ Completed crawling all {len(urls)} properties!")
        return all_results