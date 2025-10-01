"""
HTTP client utilities for Mitsui crawling
"""
import requests

class HttpClient:
    """Singleton HTTP client for connection pooling"""
    _instance = None
    _session = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._session = requests.Session()
            cls._session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; crawler)'})
        return cls._instance
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request using the session"""
        return self._session.get(url, **kwargs)
    
    def close(self):
        """Close the session"""
        if self._session:
            self._session.close()


# Global client instance
http_client = HttpClient()