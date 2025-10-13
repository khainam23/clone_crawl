"""
Tokyu crawl page entry point
Optimized version with better error handling and logging
Using lxml for faster HTML parsing
"""
from typing import List, Tuple, Optional
import requests
from lxml import html
import re

from app.jobs.crawl_strcture.index import crawl_pages
from .custom_extractor_factory import setup_custom_extractor
from .constants import URL_MULTI, ITEM_SELECTOR, DEFAULT_NUM_PAGES, BASE_URL, ITEM_MAX_NUM_PAGE
from app.core.config import settings

# Lấy link của nhà trong trang
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
        
        # Parse HTML with lxml (faster than BeautifulSoup)
        tree = html.fromstring(resp.content)
        
        # Extract items using CSS selector
        items = tree.cssselect(ITEM_SELECTOR)
        print(f"📄 Page {page}: Found {len(items)} items")

        for i, a_tag in enumerate(items):
            if a_tag is None or not a_tag.get("href"):
                continue

            href = a_tag.get("href")
            full_url = href if href.startswith("http") else BASE_URL + href
            urls.append(full_url)
                
        # Detect max pages if requested (only on first page)
        if detect_max_pages:
            pagination_links = tree.cssselect(ITEM_MAX_NUM_PAGE)
            
            if pagination_links:
                last_link = pagination_links[-1]
                href = last_link.get("href", "")
                
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
    from app.jobs.crawl_strcture.handle_multi_crawl_url import crawl_multi_pages
    
    await crawl_multi_pages(
        site_name="Tokyu",
        fetch_page_urls_func=_fetch_page_urls,
        default_num_pages=DEFAULT_NUM_PAGES,
        id_mongo=settings.ID_MONGO_TOKYU,
        collection_name=settings.COLLECTION_NAME_TOKYU,
        custom_extractor_factory=setup_custom_extractor
    )