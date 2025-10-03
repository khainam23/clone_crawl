"""
Mitsui crawling entry point
Optimized version with better error handling and structure
Using lxml for faster HTML parsing
"""
import requests
from lxml import html
from typing import List, Tuple, Optional

from app.jobs.crawl_strcture.index import crawl_pages
from app.core.config import settings
from .custom_extractor_factory import setup_custom_extractor
from .constants import URL_MULTI, ITEM_SELECTOR, DEFAULT_NUM_PAGES, ID_MONGO, COLLECTION_NAME, ITEM_MAX_NUM_PAGE

def _fetch_page_urls(page: int, headers: dict, detect_max_pages: bool = False) -> Tuple[List[str], Optional[int]]:
    """
    Fetch URLs from a single page
    
    Args:
        page: Page number to fetch
        headers: Request headers
        detect_max_pages: If True, also detect maximum pages from pagination
        
    Returns:
        Tuple of (urls, max_pages) where max_pages is None unless detect_max_pages=True
    """
    urls = []
    max_pages = None
    
    try:
        params = {"page": page}
        resp = requests.get(URL_MULTI, params=params, headers=headers, timeout=30)
        
        if resp.status_code != 200:
            print(f"❌ Failed to load page {page}: HTTP {resp.status_code}")
            return urls, max_pages
        
        # Parse HTML with lxml (faster than BeautifulSoup)
        tree = html.fromstring(resp.content)
        
        # Extract items using CSS selector
        items = tree.cssselect(ITEM_SELECTOR)
        print(f"📄 Page {page}: Found {len(items)} items")
        
        for item in items:
            link = item.get("data-js-room-link")
            if link:
                urls.append(link)
        
        # Detect max pages if requested (only on first page)
        if detect_max_pages:
            pagination_links = tree.cssselect(ITEM_MAX_NUM_PAGE)
            
            if pagination_links:
                last_link = pagination_links[-1]
                href = last_link.get("href", "")
                
                if "page=" in href:
                    try:
                        max_pages = int(href.split("page=")[-1].split("&")[0])
                        print(f"✅ Detected maximum pages: {max_pages}")
                    except ValueError:
                        print(f"⚠️ Could not parse page number from: {href}")
            
            if max_pages is None:
                print(f"⚠️ Could not detect max pages, will use default: {DEFAULT_NUM_PAGES}")
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout loading page {page}")
    except Exception as e:
        print(f"❌ Error loading page {page}: {e}")
    
    return urls, max_pages


async def crawl_multi():
    """
    Main crawling function for Mitsui properties
    Fetches property URLs from multiple pages and crawls them
    """
    print(f"🚀 Starting Mitsui crawl...")
    
    headers = {
        "User-Agent": settings.CRAWLER_USER_AGENT
    }
    
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
        print("⚠️ No URLs found to crawl")
        return
    
    # Crawl all collected URLs
    await crawl_pages(
        urls=all_urls,
        batch_size=settings.BATCH_SIZE,
        id_mongo=ID_MONGO,
        collection_name=COLLECTION_NAME,
        custom_extractor_factory=setup_custom_extractor
    )
    
    print(f"🎉 Mitsui crawl completed!")