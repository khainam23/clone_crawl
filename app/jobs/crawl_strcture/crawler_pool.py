"""
Crawler Pool - Quản lý pool các crawler instances để tránh overhead
"""

import asyncio
from typing import Optional, Callable, List
from crawl4ai import AsyncWebCrawler
from app.core.config import CrawlerConfig
from .custom_rules import CustomExtractor


class CrawlerPool:
    """
    Pool quản lý các AsyncWebCrawler instances để tái sử dụng
    Giúp tránh overhead khi khởi tạo crawler mới cho mỗi request
    """
    
    def __init__(
        self, 
        pool_size: int,
        custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None
    ):
        """
        Initialize CrawlerPool
        
        Args:
            pool_size: Số lượng crawler instances trong pool (thường bằng BATCH_SIZE)
            custom_extractor_factory: Optional factory function to create custom extractor
        """
        self.pool_size = pool_size
        self.config = CrawlerConfig()
        self.custom_extractor_factory = custom_extractor_factory
        
        # Pool của các crawler instances
        self._crawlers: List[AsyncWebCrawler] = []
        self._available_crawlers: asyncio.Queue = asyncio.Queue()
        self._initialized = False
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """
        Khởi tạo pool với số lượng crawler instances
        """
        async with self._lock:
            if self._initialized:
                return
                
            print(f"🔧 Initializing crawler pool with {self.pool_size} instances...")
            
            for i in range(self.pool_size):
                try:
                    crawler = AsyncWebCrawler(config=self.config.BROWSER_CONFIG)
                    await crawler.__aenter__()  # Initialize crawler context
                    self._crawlers.append(crawler)
                    await self._available_crawlers.put(crawler)
                    print(f"✅ Crawler {i+1}/{self.pool_size} initialized")
                except Exception as e:
                    print(f"❌ Failed to initialize crawler {i+1}: {e}")
                    
            self._initialized = True
            print(f"🎉 Crawler pool initialized with {len(self._crawlers)} instances")
    
    async def acquire(self) -> AsyncWebCrawler:
        """
        Lấy một crawler instance từ pool
        Nếu pool đang trống, sẽ đợi cho đến khi có crawler available
        
        Returns:
            AsyncWebCrawler instance
        """
        if not self._initialized:
            await self.initialize()
            
        crawler = await self._available_crawlers.get()
        return crawler
    
    async def release(self, crawler: AsyncWebCrawler):
        """
        Trả crawler instance về pool sau khi sử dụng xong
        
        Args:
            crawler: AsyncWebCrawler instance to release
        """
        await self._available_crawlers.put(crawler)
    
    async def close(self):
        """
        Đóng tất cả crawler instances trong pool
        """
        async with self._lock:
            if not self._initialized:
                return
                
            print(f"🔒 Closing crawler pool...")
            
            # Đóng tất cả crawlers
            for i, crawler in enumerate(self._crawlers):
                try:
                    await crawler.__aexit__(None, None, None)
                    print(f"✅ Crawler {i+1}/{len(self._crawlers)} closed")
                except Exception as e:
                    print(f"⚠️ Error closing crawler {i+1}: {e}")
            
            self._crawlers.clear()
            
            # Clear queue
            while not self._available_crawlers.empty():
                try:
                    self._available_crawlers.get_nowait()
                except asyncio.QueueEmpty:
                    break
                    
            self._initialized = False
            print(f"🎉 Crawler pool closed")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    def get_custom_extractor(self) -> CustomExtractor:
        """
        Tạo custom extractor instance
        
        Returns:
            CustomExtractor instance
        """
        if self.custom_extractor_factory:
            return self.custom_extractor_factory()
        else:
            return CustomExtractor()