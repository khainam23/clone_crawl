"""
Settings management (.env)
Tên trong .env phải giống tên trong class Settings vì nó sẽ tự mapping, 
giá trị đang khởi tạo chỉ là giá trị mặc định tránh lỗi
"""
from pydantic_settings import BaseSettings
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

class Settings(BaseSettings):
    # Database settings
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "arealty_crawler"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Scheduler settings
    scheduler_timezone: str = "UTC"
    
    # Crawler settings
    crawler_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    crawler_delay: float = 1.0
    batch_size: int = 10
    
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