import re
from typing import Optional, Tuple
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import time

def init_chrome_driver() -> webdriver.Chrome:
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
    return driver

def fetch_coordinates(driver: webdriver.Chrome, address: str, retries: int = 2) -> Optional[Tuple[float, float]]:
    encoded_address = quote(address)
    google_maps_url = f"https://www.google.co.jp/maps/place/{encoded_address}"

    for attempt in range(retries):
        try:
            driver.get(google_maps_url)
            wait = WebDriverWait(driver, 10)
            wait.until(lambda d: re.search(r'@-?\d+\.\d+,-?\d+\.\d+', d.current_url))
            match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
            if match:
                return float(match.group(1)), float(match.group(2))
            return None
        except TimeoutException:
            print(f"⏱️ Timeout fetching coordinates for: {address} (retry {attempt+1})")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error fetching coordinates: {address}, {e} (retry {attempt+1})")
            time.sleep(2)
    return None

# Example usage
if __name__ == "__main__":
    addresses = ["神奈川県川崎市中原区木月住吉町１０−１", "東京都千代田区1-1"]
    driver = init_chrome_driver()
    results = []

    try:
        for addr in addresses:
            coords = fetch_coordinates(driver, addr)
            results.append((addr, coords))
    finally:
        driver.quit()

    print(results)
