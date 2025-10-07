"""
Settings management (.env)
Tên trong .env phải giống tên trong class Settings vì nó sẽ tự mapping, 
giá trị đang khởi tạo chỉ là giá trị mặc định tránh lỗi
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE SETTINGS
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "arealty_crawler"
        
    # API SETTINGS
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
        
    # SCHEDULER SETTINGS
    SCHEDULER_TIMEZONE: str = "UTC"
        
    # CRAWLER SETTINGS
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    CRAWLER_DELAY: float = 1.0
    BATCH_SIZE: int = 10
    CRAWLER_TIMEOUT: int = 30  # HTTP request timeout in seconds
    LAST_UPDATED: int = 172800 # About 2 days
        
    # FOR IMAGE
    MAX_IMAGES: int = 16
    GALLERY_TIMEOUT: int = 10
        
    # FOR MONGO
    ID_MONGO_MITSUI: int = 11000000
    COLLECTION_NAME_MITSUI: str = 'room_mitsui'
    ID_MONGO_TOKYU: int = 12000000
    COLLECTION_NAME_TOKYU: str = 'room_tokyu'
        
    # STATION
    STATION_URL: str = 'https://bmatehouse.com/api/routes/get_by_position'
    MAX_STATIONS: int = 5

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields not defined in the model
  
# Global settings instance
settings = Settings()
        
class CrawlerConfig:
    """Cấu hình cho HTTP crawler với BeautifulSoup"""
    
    @staticmethod
    def get_headers() -> dict:
        """
        Trả về HTTP headers cho requests
        """
        return {
            "User-Agent": settings.CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    @staticmethod
    def get_timeout() -> int:
        """Trả về timeout cho HTTP requests"""
        return settings.CRAWLER_TIMEOUT