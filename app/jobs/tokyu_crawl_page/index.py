"""
Tokyu crawl page entry point
"""
import requests
from bs4 import BeautifulSoup

from app.jobs.crawl_strcture.index import crawl_pages
from .custom_extractor_factory import setup_custom_extractor
from . import constants as config

async def crawl_multi():
    url = config.url_multi
    item_selector = config.item_selector
    num_page = 30

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    urls = []

    for page in range(1, num_page + 1):
        page_url = f"{url}{page}"
        resp = requests.get(page_url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Lỗi tải trang {page}")
            continue
        
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(item_selector)
        
        print(f"Trang {page}: tìm thấy {len(items)} items")

        for item in items:
            # Lấy href và ghép với BASE_URL
            href = item.get("href")
            if href:
                # Nếu href đã có http thì dùng luôn, không thì ghép với BASE_URL
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = config.BASE_URL + href
                urls.append(full_url)
            
        
    await crawl_pages(
        urls, 
        batch_size=config.batch_size, 
        id_mongo=config.ID_MONGO, 
        collection_name=config.COLLECTION_NAME,
        custom_extractor_factory=setup_custom_extractor  # Pass the factory function
    )