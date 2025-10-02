"""
Tokyu crawl page entry point
Optimized version with better error handling and logging
"""
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import re

from app.jobs.crawl_strcture.index import crawl_pages
from .custom_extractor_factory import setup_custom_extractor
from .constants import URL_MULTI, ITEM_SELECTOR, DEFAULT_NUM_PAGES, BASE_URL, ITEM_MAX_NUM_PAGE
from app.core.config import settings


def _fetch_page_urls(page: int, headers: dict, detect_max_pages: bool = False) -> Tuple[List[str], Optional[int]]:
    """
    Fetch property URLs from a single listing page
    
    Args:
        page: Page number to crawl
        headers: Request headers
        detect_max_pages: If True, also detect maximum pages from pagination
        
    Returns:
        Tuple of (urls, max_pages) where max_pages is None unless detect_max_pages=True
    """
    urls = []
    max_pages = None
    page_url = f"{URL_MULTI}{page}"
    
    try:
        resp = requests.get(page_url, headers=headers, timeout=30)
        
        if resp.status_code != 200:
            print(f"❌ Error loading page {page}: HTTP {resp.status_code}")
            return urls, max_pages
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract items
        items = soup.select(ITEM_SELECTOR)
        print(f"📄 Page {page}: Found {len(items)} items")

        for item in items:
            href = item.get("href")
            if href:
                # Build full URL
                full_url = href if href.startswith('http') else BASE_URL + href
                urls.append(full_url)
        
        # Detect max pages if requested (only on first page)
        if detect_max_pages:
            pagination_links = soup.select(ITEM_MAX_NUM_PAGE)
            
            if pagination_links:
                last_link = pagination_links[-1]
                href = last_link.get("href", "")
                
                # Extract page number from href like 'rent_search/埼玉県-千葉県-東京都-神奈川県/limit:50/page:30'
                if "page:" in href:
                    try:
                        # Use regex to extract the number after 'page:'
                        match = re.search(r'page:(\d+)', href)
                        if match:
                            max_pages = int(match.group(1))
                            print(f"✅ Detected maximum pages: {max_pages}")
                        else:
                            print(f"⚠️ Could not parse page number from: {href}")
                    except ValueError:
                        print(f"⚠️ Could not parse page number from: {href}")
            
            if max_pages is None:
                print(f"⚠️ Could not detect max pages, will use default: {DEFAULT_NUM_PAGES}")
                
    except requests.Timeout:
        print(f"⚠️ Timeout loading page {page}")
    except Exception as e:
        print(f"❌ Error processing page {page}: {e}")
    
    return urls, max_pages


async def crawl_multi():
    """Main entry point for Tokyu multi-page crawling"""
    print("🏢 Starting Tokyu property crawl...")
    
    headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
    
    # Collect all URLs from all pages
    all_urls = []
    
    # First page: fetch URLs and detect max pages
    print("📄 Fetching page 1 and detecting pagination...")
    page_urls, detected_max_pages = _fetch_page_urls(1, headers, detect_max_pages=True)
    all_urls.extend(page_urls)
    
    # Use detected max pages or fallback to DEFAULT_NUM_PAGES
    max_pages = detected_max_pages if detected_max_pages else DEFAULT_NUM_PAGES
    print(f"📊 Total pages to crawl: {max_pages}")
    
    # Fetch remaining pages
    for page in range(2, max_pages + 1):
        page_urls, _ = _fetch_page_urls(page, headers)
        all_urls.extend(page_urls)
    
    print(f"✅ Collected {len(all_urls)} total URLs")
    
    if not all_urls:
        print("⚠️ No URLs collected. Exiting...")
        return
    
    # Crawl all property pages
    print(f"🎯 Starting to crawl {len(all_urls)} property pages...")
    await crawl_pages(
        all_urls, 
        batch_size=settings.BATCH_SIZE, 
        id_mongo=settings.ID_MONGO_TOKYU, 
        collection_name=settings.COLLECTION_NAME_TOKYU,
        custom_extractor_factory=setup_custom_extractor
    )
    
    print("🎉 Tokyu crawl completed!")