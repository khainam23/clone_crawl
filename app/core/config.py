"""
Settings management (.env)
Tên trong .env phải giống tên trong class Settings vì nó sẽ tự mapping, 
giá trị đang khởi tạo chỉ là giá trị mặc định tránh lỗi
"""
from pydantic_settings import BaseSettings
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

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
        
class CrawlerConfig:
    """Cấu hình cho crawler"""
    
    # Browser configuration
    BROWSER_CONFIG = BrowserConfig(
        headless=True,
        headers={
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
        },
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    # Crawler run configuration
    RUN_CONFIG = CrawlerRunConfig(
        wait_for_images=False,
        scan_full_page=False,
        delay_before_return_html=0.1,
        page_timeout=25000,
        remove_overlay_elements=True
    )
    
    # Valid image extensions
    VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
# Global settings instance
settings = Settings()