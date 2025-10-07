"""
Simple helper for multi-page crawling
Giúp tái sử dụng logic chung: collect URLs từ nhiều pages và crawl chúng
"""
from typing import List, Tuple, Optional, Callable, Any
from app.jobs.crawl_strcture.index import crawl_pages
from app.core.config import settings

async def crawl_multi_pages(
    site_name: str,
    fetch_page_urls_func: Callable[[int, dict, bool], Tuple[List[str], Optional[int]]],
    default_num_pages: int,
    id_mongo: str,
    collection_name: str,
    custom_extractor_factory: Any
):
    """
    Helper function để crawl nhiều pages
    
    Args:
        site_name: Tên site (để log)
        fetch_page_urls_func: Function để fetch URLs từ 1 page
            - Input: (page_number, headers, detect_max_pages)
            - Output: (list_of_urls, max_pages)
        default_num_pages: Số pages mặc định nếu không detect được
        id_mongo: ID mongo
        collection_name: Tên collection
        custom_extractor_factory: Factory để tạo custom extractor
    """
    print(f"🚀 Starting {site_name} crawl...")
    
    headers = {"User-Agent": settings.CRAWLER_USER_AGENT}
    all_urls = []
    
    # First page: fetch URLs and detect max pages
    print("📄 Fetching page 1 and detecting pagination...")
    page_urls, detected_max_pages = fetch_page_urls_func(1, headers, True)
    all_urls.extend(page_urls)
    
    # Use detected max pages or fallback to default
    max_pages = detected_max_pages if detected_max_pages else default_num_pages
    print(f"📊 Total pages to crawl: {max_pages}")
    
    # Fetch remaining pages
    for page in range(2, max_pages + 1):
        page_urls, _ = fetch_page_urls_func(page, headers, False)
        all_urls.extend(page_urls)
    
    print(f"✅ Collected {len(all_urls)} total URLs")
    
    if not all_urls:
        print("⚠️ No URLs found to crawl")
        return
    
    # Crawl all collected URLs
    print(f"🎯 Starting to crawl {len(all_urls)} property pages...")
    await crawl_pages(
        urls=all_urls,
        batch_size=settings.BATCH_SIZE,
        id_mongo=id_mongo,
        collection_name=collection_name,
        custom_extractor_factory=custom_extractor_factory
    )
    
    print(f"🎉 {site_name} crawl completed!")