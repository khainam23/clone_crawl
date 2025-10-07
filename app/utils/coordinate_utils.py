import re
import time
import atexit
from typing import Optional, Tuple, List
from urllib.parse import quote
from functools import lru_cache
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

# --- Khởi tạo 1 browser toàn cục
_driver_instance = None

def _init_driver() -> webdriver.Chrome:
    global _driver_instance
    if _driver_instance is None:
        chrome_options = Options()
        chrome_options.binary_location = "/usr/local/bin/chrome/chrome"
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--hide-scrollbars")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--safebrowsing-disable-auto-update")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=800,600")  # Giảm từ 1920x1080
        chrome_options.add_argument("--single-process")  # Chạy single process để giảm RAM/CPU
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-notifications")
        
        # Tắt hình ảnh để tải nhanh hơn và giảm CPU
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service("/usr/bin/chromedriver")
        _driver_instance = webdriver.Chrome(service=service, options=chrome_options)
        _driver_instance.set_page_load_timeout(10)  # Giảm từ 15s
        
        # Đăng ký cleanup khi thoát
        atexit.register(_cleanup_driver)
    return _driver_instance

def _cleanup_driver():
    """Đóng browser khi thoát chương trình"""
    global _driver_instance
    if _driver_instance:
        try:
            _driver_instance.quit()
        except Exception:
            pass
        _driver_instance = None

def _reset_driver():
    """Reset driver nếu gặp lỗi nghiêm trọng"""
    global _driver_instance
    _cleanup_driver()
    _driver_instance = None

@lru_cache(maxsize=1000)
def _fetch_coordinates_cached(address: str) -> Optional[Tuple[float, float]]:
    """
    Hàm nội bộ để fetch tọa độ (được cache).
    Chỉ nhận address làm tham số để cache hiệu quả.
    """
    driver = _init_driver()
    
    try:
        encoded_address = quote(address)
        google_maps_url = f"https://www.google.co.jp/maps/place/{encoded_address}"

        # Mở tab mới
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(google_maps_url)

        wait = WebDriverWait(driver, 8)
        wait.until(lambda d: re.search(r'@-?\d+\.\d+,-?\d+\.\d+', d.current_url))

        match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
        coords = (float(match.group(1)), float(match.group(2))) if match else None

        # Đóng tab sau khi lấy xong
        driver.close()
        if driver.window_handles:
            driver.switch_to.window(driver.window_handles[0])
        return coords

    except TimeoutException:
        # Đóng tab nếu timeout
        try:
            driver.close()
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])
        except Exception:
            pass
        raise  # Re-raise để retry logic xử lý
    except WebDriverException as e:
        # Reset driver nếu lỗi nghiêm trọng
        if "chrome not reachable" in str(e).lower() or "session deleted" in str(e).lower():
            _reset_driver()
        raise  # Re-raise để retry logic xử lý
    except Exception:
        try:
            driver.close()
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])
        except Exception:
            pass
        raise  # Re-raise để retry logic xử lý


def fetch_coordinates_from_google_maps(address: str, retries: int = 2, delay_between_retries: float = 1.5) -> Optional[Tuple[float, float]]:
    """
    Lấy tọa độ từ Google Maps.
    Chỉ mở 1 Chrome duy nhất, sử dụng nhiều tab cho nhiều địa chỉ.
    Kết quả được cache để tránh tra cứu lại.
    
    Args:
        address: Địa chỉ cần tra cứu
        retries: Số lần thử lại nếu thất bại (mặc định: 2)
        delay_between_retries: Thời gian chờ giữa các lần thử (mặc định: 1.5s)
    
    Returns:
        Tuple (latitude, longitude) hoặc None nếu không tìm thấy
    """
    for attempt in range(1, retries + 1):
        try:
            if attempt > 1:
                time.sleep(delay_between_retries)
            
            # Gọi hàm cached
            return _fetch_coordinates_cached(address)
            
        except TimeoutException:
            print(f"⏱️ Timeout fetching coordinates for: {address} (attempt {attempt}/{retries})")
        except WebDriverException as e:
            print(f"❌ WebDriver error for {address} (attempt {attempt}/{retries}): {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {address} (attempt {attempt}/{retries}): {e}")

    print(f"⚠️ Failed to fetch coordinates for: {address} after {retries} attempts")
    return None


def clear_cache():
    """Xóa cache địa chỉ đã tra cứu"""
    _fetch_coordinates_cached.cache_clear()


def cleanup_browser():
    """Đóng browser thủ công nếu cần"""
    _cleanup_driver()
