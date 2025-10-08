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

# Lấy link của nhà trong trang
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
        
        for i, item in enumerate(items):
            if i >= 3:
                break
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
    from app.jobs.crawl_strcture.handle_multi_crawl_url import crawl_multi_pages
    
    await crawl_multi_pages(
        site_name="Mitsui",
        fetch_page_urls_func=_fetch_page_urls,
        default_num_pages=DEFAULT_NUM_PAGES,
        id_mongo=ID_MONGO,
        collection_name=COLLECTION_NAME,
        custom_extractor_factory=setup_custom_extractor
    )