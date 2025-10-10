
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any

from .property_crawler import EnhancedPropertyCrawler
from .custom_rules import CustomExtractor
from app.utils.save_utils import SaveUtils

async def crawl_pages(
    urls: List[str] = [], 
    batch_size: int = 10, 
    id_mongo: int = 0, 
    collection_name: str = 'table_page',
    custom_extractor_factory: Optional[Callable[[], CustomExtractor]] = None,
    max_consecutive_failures: int = 30,
    use_proxy: bool = True
):
    """
    Crawl multiple property pages with batch-wise MongoDB saving
    
    Args:
        urls: List of URLs to crawl
        batch_size: Number of URLs to crawl simultaneously
        id_mongo: MongoDB document ID (starting point)
        collection_name: MongoDB collection name
        custom_extractor_factory: Optional factory function to create custom extractor
        max_consecutive_failures: Maximum consecutive failures before stopping (default: 30)
        use_proxy: Whether to use proxy rotation from http.txt file (default: False)
    """
    # Filter urls
    urls, id_mongo = await SaveUtils.filter_urls(urls, collection_name, id_mongo)
    
    start = datetime.now()

    # Tracking variables
    current_id = id_mongo
    total_saved = 0
    saved_batches = []
    
    # Callback function để lưu sau mỗi batch
    async def save_batch_to_mongo(batch_results: List[Dict[str, Any]], batch_num: int, total_batches: int):
        nonlocal current_id, total_saved
        
        try:
            # Lưu batch vào MongoDB
            result = await SaveUtils.save_db_results(
                batch_results, 
                _id=current_id, 
                collection_name=collection_name
            )
            
            if result:
                saved_count = len(batch_results)
                total_saved += saved_count
                saved_batches.append({
                    'batch_num': batch_num,
                    'saved_count': saved_count,
                    'id_range': f"{current_id + 1} - {current_id + saved_count}"
                })
                
                print(f"✅ Batch {batch_num}/{total_batches}: Saved {saved_count} records (IDs: {current_id + 1} - {current_id + saved_count})")
                
                # Cập nhật current_id cho batch tiếp theo
                current_id += saved_count
            else:
                print(f"⚠️ Batch {batch_num}/{total_batches}: No records saved")
                
        except Exception as e:
            print(f"❌ Error saving batch {batch_num}/{total_batches} to MongoDB: {e}")

    crawler = EnhancedPropertyCrawler(custom_extractor_factory, use_proxy=use_proxy)
    print("\n=== 😶‍🌫️☀️😁😂😑🤷‍♂️ ===")
    
    try:
        # Crawl với callback để lưu sau mỗi batch
        await crawler.crawl_multiple_properties(
            urls, 
            batch_size=batch_size,
            on_batch_complete=save_batch_to_mongo,
            max_consecutive_failures=max_consecutive_failures
        )
        
    except Exception as e:
        print(f"❌ Error during crawling: {e}")
        # In summary ngay cả khi có lỗi
        end = datetime.now()
        duration = end - start
        print(f"""
        === Summary (Interrupted) ===
        Total URLs: {len(urls)}
        Total Saved: {total_saved} records
        Batches Saved: {len(saved_batches)}
        Start: {start:%Y%m%d_%H%M%S} | End: {end:%Y%m%d_%H%M%S} | 🕒 Duration: {duration}
        """)
        return

    end = datetime.now()
    duration = end - start

    print(f"""
        === Summary ===
        Total URLs: {len(urls)}
        Total Saved: {total_saved} records to '{collection_name}'
        Batches Completed: {len(saved_batches)}
        Final ID: {current_id}
        Start: {start:%Y%m%d_%H%M%S} | End: {end:%Y%m%d_%H%M%S} | 🕒 Duration: {duration}
    """)