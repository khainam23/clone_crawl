import re
import time
from typing import Optional, Tuple, List
from urllib.parse import quote
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
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")

        service = Service("/usr/bin/chromedriver")
        _driver_instance = webdriver.Chrome(service=service, options=chrome_options)
        _driver_instance.set_page_load_timeout(15)
    return _driver_instance

def fetch_coordinates_from_google_maps(address: str, retries: int = 2, delay_between_retries: float = 2.0) -> Optional[Tuple[float, float]]:
    """
    Lấy tọa độ từ Google Maps.
    Chỉ mở 1 Chrome duy nhất, sử dụng nhiều tab cho nhiều địa chỉ.
    """
    driver = _init_driver()

    for attempt in range(1, retries + 1):
        try:
            if attempt > 1:
                time.sleep(delay_between_retries)

            encoded_address = quote(address)
            google_maps_url = f"https://www.google.co.jp/maps/place/{encoded_address}"

            # Mở tab mới
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(google_maps_url)

            wait = WebDriverWait(driver, 10)
            wait.until(lambda d: re.search(r'@-?\d+\.\d+,-?\d+\.\d+', d.current_url))

            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
            coords = (float(match.group(1)), float(match.group(2))) if match else None

            # Đóng tab sau khi lấy xong
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return coords

        except TimeoutException:
            print(f"⏱️ Timeout fetching coordinates for: {address} (attempt {attempt}/{retries})")
        except WebDriverException as e:
            print(f"❌ WebDriver error for {address} (attempt {attempt}/{retries}): {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {address} (attempt {attempt}/{retries}): {e}")

    print(f"⚠️ Failed to fetch coordinates for: {address} after {retries} attempts")
    return None
