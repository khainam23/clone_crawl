import re
import time
from typing import Optional, Tuple
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

def fetch_coordinates_from_google_maps(address: str, retries: int = 2, delay_between_retries: float = 2.0) -> Optional[Tuple[float, float]]:
    """
    Lấy tọa độ từ Google Maps.
    Mỗi lần chạy tạo một Chrome mới.
    Có retry và delay để tránh crash/disconnect trên Kaggle.
    """
    for attempt in range(1, retries + 1):
        driver = None
        try:
            # Delay nếu là retry
            if attempt > 1:
                time.sleep(delay_between_retries)

            encoded_address = quote(address)
            google_maps_url = f"https://www.google.co.jp/maps/place/{encoded_address}"

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
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(15)
            driver.get(google_maps_url)

            wait = WebDriverWait(driver, 10)
            wait.until(lambda d: re.search(r'@-?\d+\.\d+,-?\d+\.\d+', d.current_url))

            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
            if match:
                return float(match.group(1)), float(match.group(2))
            return None

        except TimeoutException:
            print(f"⏱️ Timeout fetching coordinates for: {address} (attempt {attempt}/{retries})")
        except WebDriverException as e:
            print(f"❌ WebDriver error for {address} (attempt {attempt}/{retries}): {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {address} (attempt {attempt}/{retries}): {e}")
        finally:
            if driver:
                driver.quit()

    print(f"⚠️ Failed to fetch coordinates for: {address} after {retries} attempts")
    return None
