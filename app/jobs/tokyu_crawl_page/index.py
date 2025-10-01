"""
Tokyu crawl page entry point
"""
import requests
from bs4 import BeautifulSoup

from app.jobs.crawl_strcture.index import crawl_pages
from .custom_extractor_factory import setup_custom_extractor
from .constants import URL_MULTI, ITEM_SELECTOR, NUM_PAGES, BASE_URL
from app.core.config import settings

async def crawl_multi():
    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT
    }
    urls = []

    for page in range(1, NUM_PAGES + 1):
        page_url = f"{URL_MULTI}{page}"
        resp = requests.get(page_url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Lỗi tải trang {page}")
            continue
        
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(ITEM_SELECTOR)
        
        print(f"Trang {page}: tìm thấy {len(items)} items")

        for item in items:
            # Lấy href và ghép với BASE_URL
            href = item.get("href")
            if href:
                # Nếu href đã có http thì dùng luôn, không thì ghép với BASE_URL
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url =  BASE_URL + href
                urls.append(full_url)
            
        
    await crawl_pages(
        urls, 
        batch_size= settings.BATCH_SIZE, 
        id_mongo= settings.ID_MONGO_TOKYU, 
        collection_name= settings.COLLECTION_NAME_TOKYU,
        custom_extractor_factory=setup_custom_extractor  # Pass the factory function
    )