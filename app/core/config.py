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
    USE_GPU: bool = False
        
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
    """Cấu hình cho crawler"""
    
    @staticmethod
    def get_browser_config(use_gpu: bool = None) -> BrowserConfig:
        """
        Trả về browser config dựa theo GPU setting
        
        Args:
            use_gpu: True/False để bật/tắt GPU. Nếu None thì lấy từ settings.USE_GPU
        """
        # Nếu không truyền vào thì lấy từ settings
        if use_gpu is None:
            use_gpu = settings.USE_GPU
            
        if use_gpu:
            extra_args = [
                "--enable-gpu",
                "--use-gl=desktop",
                "--enable-accelerated-2d-canvas",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
            ]
        else:
            extra_args = [
                "--disable-gpu",
                "--disable-software-rasterizer",
            ]

        return BrowserConfig(
            headless=True,
            headers={
                "Accept-Encoding": "gzip, deflate",
                "Cache-Control": "no-cache",
            },
            user_agent=settings.CRAWLER_USER_AGENT,
            extra_args=extra_args,
        )
    
    # Crawler run configuration
    RUN_CONFIG = CrawlerRunConfig(
        wait_for_images=False,
        scan_full_page=False,
        delay_before_return_html=0.1,
        page_timeout=25000,
        remove_overlay_elements=True
    )