import re
from typing import Optional, Tuple
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def fetch_coordinates_from_google_maps(address: str) -> Optional[Tuple[float, float]]:
    driver = None
    try:
        encoded_address = quote(address)
        google_maps_url = f"https://www.google.co.jp/maps/place/{encoded_address}"

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")

        service = Service(ChromeDriverManager().install())
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
        print(f"⏱️ Timeout fetching coordinates for: {address}")
        return None
    except Exception as e:
        print(f"❌ Error fetching coordinates: {e}")
        return None
    finally:
        if driver:
            driver.quit()