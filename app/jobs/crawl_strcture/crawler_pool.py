"""
HTTP Session Pool - Quản lý pool các HTTP sessions để tránh overhead
"""

import asyncio
import aiohttp
from typing import Optional, Callable, List
from app.core.config import CrawlerConfig
from .custom_rules import CustomExtractor

class CrawlerPool:
    """
    Pool quản lý các aiohttp ClientSession instances để tái sử dụng
    Giúp tránh overhead khi khởi tạo session mới cho mỗi request
    """
    
    def __init__(
        self, 
        pool_size: int,
        custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None
    ):
        """
        Initialize CrawlerPool (HTTP Session Pool)
        
        Args:
            pool_size: Số lượng session instances trong pool (thường bằng BATCH_SIZE)
            custom_extractor_factory: Optional factory function to create custom extractor
        """
        self.pool_size = pool_size
        self.config = CrawlerConfig()
        self.custom_extractor_factory = custom_extractor_factory
        
        # Pool của các HTTP sessions
        self._sessions: List[aiohttp.ClientSession] = []
        self._available_sessions: asyncio.Queue = asyncio.Queue()
        self._initialized = False
        self._lock = asyncio.Lock()
        self._connector: Optional[aiohttp.TCPConnector] = None
        
    async def initialize(self):
        """
        Khởi tạo pool với số lượng HTTP session instances
        """
        async with self._lock:
            if self._initialized:
                return
                
            print(f"🔧 Initializing HTTP session pool with {self.pool_size} instances...")
            
            # Tạo connector với connection pooling
            self._connector = aiohttp.TCPConnector(
                limit=self.pool_size * 2,  # Tổng số connections
                limit_per_host=self.pool_size,  # Connections per host
                ttl_dns_cache=300,  # DNS cache 5 phút
                force_close=False,  # Giữ connections alive
            )
            
            # Tạo timeout config
            timeout = aiohttp.ClientTimeout(
                total=self.config.get_timeout(),
                connect=10,
                sock_read=self.config.get_timeout()
            )
            
            for i in range(self.pool_size):
                try:
                    session = aiohttp.ClientSession(
                        headers=self.config.get_headers(),
                        connector=self._connector,
                        timeout=timeout,
                        connector_owner=False  # Connector được quản lý bởi pool
                    )
                    self._sessions.append(session)
                    await self._available_sessions.put(session)
                    print(f"✅ Session {i+1}/{self.pool_size} initialized")
                except Exception as e:
                    print(f"❌ Failed to initialize session {i+1}: {e}")
                    
            self._initialized = True
            print(f"🎉 HTTP session pool initialized with {len(self._sessions)} instances")
    
    async def acquire(self) -> aiohttp.ClientSession:
        """
        Lấy một HTTP session instance từ pool
        Nếu pool đang trống, sẽ đợi cho đến khi có session available
        
        Returns:
            aiohttp.ClientSession instance
        """
        if not self._initialized:
            await self.initialize()
            
        session = await self._available_sessions.get()
        return session
    
    async def release(self, session: aiohttp.ClientSession):
        """
        Trả HTTP session instance về pool sau khi sử dụng xong
        
        Args:
            session: aiohttp.ClientSession instance to release
        """
        await self._available_sessions.put(session)
    
    async def close(self):
        """
        Đóng tất cả HTTP session instances trong pool
        """
        async with self._lock:
            if not self._initialized:
                return
                
            print(f"🔒 Closing HTTP session pool...")
            
            # Đóng tất cả sessions
            for i, session in enumerate(self._sessions):
                try:
                    await session.close()
                    print(f"✅ Session {i+1}/{len(self._sessions)} closed")
                except Exception as e:
                    print(f"⚠️ Error closing session {i+1}: {e}")
            
            self._sessions.clear()
            
            # Đóng connector
            if self._connector:
                try:
                    await self._connector.close()
                    print(f"✅ Connector closed")
                except Exception as e:
                    print(f"⚠️ Error closing connector: {e}")
            
            # Clear queue
            while not self._available_sessions.empty():
                try:
                    self._available_sessions.get_nowait()
                except asyncio.QueueEmpty:
                    break
                    
            self._initialized = False
            print(f"🎉 HTTP session pool closed")
    
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