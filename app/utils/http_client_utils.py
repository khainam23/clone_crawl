"""
HTTP client utilities for Mitsui crawling
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class HttpClient:
    """Singleton HTTP client with optimized connection pooling"""
    _instance = None
    _session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._session = cls._create_optimized_session()
        return cls._instance
    
    @staticmethod
    def _create_optimized_session() -> requests.Session:
        """Create session with optimized settings for batch crawling"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=2,  # Reduced retries for faster failure
            backoff_factor=0.3,  # Quick backoff
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        # Configure adapter with larger pool
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,  # Increased for batch processing
            pool_maxsize=50,      # Match pool_connections
            pool_block=False      # Don't block when pool is full
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; crawler)',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate'
        })
        
        return session
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request using the optimized session"""
        return self._session.get(url, **kwargs)
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()


# Global client instance
http_client = HttpClient()