
from datetime import datetime
from typing import List, Optional, Callable

from .property_crawler import EnhancedPropertyCrawler
from .custom_rules import CustomExtractor
from app.utils.save_utils import SaveUtils

async def crawl_pages(
    urls: List[str] = [], 
    batch_size: int = 5, 
    id_mongo: int = 0, 
    collection_name: str = 'table_page',
    custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None
):
    """
    Crawl multiple property pages
    
    Args:
        urls: List of URLs to crawl
        batch_size: Number of URLs to crawl simultaneously
        id_mongo: MongoDB document ID
        collection_name: MongoDB collection name
        custom_extractor_factory: Optional factory function to create custom extractor
    """
    start = datetime.now()

    crawler = EnhancedPropertyCrawler(custom_extractor_factory)
    print("\n=== 😶‍🌫️☀️😁😂😑🤷‍♂️ ===")
    try:
        results = await crawler.crawl_multiple_properties(urls, batch_size = batch_size)
        json_file = await SaveUtils.save_db_results(results, _id = id_mongo, collection_name = collection_name)
    except Exception as e:
        print(e)
        return

    end = datetime.now()
    duration = end - start

    print(f"""
        === Summary ===
        Total URLs: {len(urls)}
        MongoDB saved: {json_file or "None"}
        Start: {start:%Y%m%d_%H%M%S} | End: {end:%Y%m%d_%H%M%S} | 🕒 Duration: {duration}
    """)