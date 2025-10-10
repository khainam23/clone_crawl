"""
Proxy Manager - Quản lý danh sách proxy từ file
"""

import random
from typing import Optional, List
from pathlib import Path


class ProxyManager:
    """
    Quản lý danh sách proxy và cung cấp proxy rotation
    """
    
    def __init__(self, proxy_file: str = None):
        """
        Initialize ProxyManager
        
        Args:
            proxy_file: Path to file containing proxy list (format: ip:port)
        """
        if proxy_file is None:
            # Default path
            proxy_file = Path(__file__).parent / "http.txt"
        
        self.proxy_file = proxy_file
        self.proxies: List[str] = []
        self.current_proxy: Optional[str] = None
        self.current_index: int = -1
        self._load_proxies()
    
    def _load_proxies(self):
        """
        Load danh sách proxy từ file
        """
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                # Đọc và lọc các dòng trống
                self.proxies = [line.strip() for line in f if line.strip()]
            
            print(f"✅ Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            
            if not self.proxies:
                print("⚠️ Warning: No proxies found in file!")
        except FileNotFoundError:
            print(f"❌ Proxy file not found: {self.proxy_file}")
            self.proxies = []
        except Exception as e:
            print(f"❌ Error loading proxies: {e}")
            self.proxies = []
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Lấy proxy tiếp theo trong danh sách (round-robin)
        
        Returns:
            Proxy string in format "http://ip:port" or None if no proxies available
        """
        if not self.proxies:
            return None
        
        # Chuyển sang proxy tiếp theo
        self.current_index = (self.current_index + 1) % len(self.proxies)
        self.current_proxy = f"http://{self.proxies[self.current_index]}"
        
        print(f"🔄 Switched to proxy [{self.current_index + 1}/{len(self.proxies)}]: {self.proxies[self.current_index]}")
        return self.current_proxy
    
    def get_random_proxy(self) -> Optional[str]:
        """
        Lấy một proxy ngẫu nhiên từ danh sách
        
        Returns:
            Proxy string in format "http://ip:port" or None if no proxies available
        """
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        self.current_proxy = f"http://{proxy}"
        
        print(f"🎲 Selected random proxy: {proxy}")
        return self.current_proxy
    
    def get_current_proxy(self) -> Optional[str]:
        """
        Lấy proxy hiện tại đang sử dụng
        
        Returns:
            Current proxy string or None
        """
        return self.current_proxy
    
    def reload_proxies(self):
        """
        Reload danh sách proxy từ file
        """
        print("🔄 Reloading proxy list...")
        self._load_proxies()
        self.current_index = -1
        self.current_proxy = None
    
    def has_proxies(self) -> bool:
        """
        Kiểm tra xem có proxy nào available không
        
        Returns:
            True if proxies are available, False otherwise
        """
        return len(self.proxies) > 0
    
    def get_proxy_count(self) -> int:
        """
        Lấy số lượng proxy trong danh sách
        
        Returns:
            Number of proxies
        """
        return len(self.proxies)