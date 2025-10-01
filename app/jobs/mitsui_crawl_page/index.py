import requests
from bs4 import BeautifulSoup

from app.jobs.crawl_strcture.index import crawl_pages
from app.core.config import settings
from .custom_extractor_factory import setup_custom_extractor
from .constants import URL_MULTI, ITEM_SELECTOR, NUM_PAGES, ID_MONGO, COLLECTION_NAME

async def crawl_multi():
    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT
    }
    urls = []

    for page in range(1, NUM_PAGES + 1):
        params = {"page": page}
        resp = requests.get(URL_MULTI, params=params, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Lỗi tải trang {page}")
            continue
        
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(ITEM_SELECTOR)
        
        print(f"Trang {page}: tìm thấy {len(items)} items")

        for item in items:
            link = item.get("data-js-room-link")
            urls.append(link)
            
        
    await crawl_pages(
        urls, 
        batch_size=settings.BATCH_SIZE, 
        id_mongo=ID_MONGO, 
        collection_name=COLLECTION_NAME,
        custom_extractor_factory=setup_custom_extractor
    )