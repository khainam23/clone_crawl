
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
    """
    # Filter urls
    urls, available_ids = await SaveUtils.filter_urls(urls, collection_name, id_mongo)
    
    start = datetime.now()

    # Tracking variables
    total_saved = 0
    saved_batches = []
    id_index = 0  # Index để theo dõi vị trí trong available_ids
    
    # Callback function để lưu sau mỗi batch
    async def save_batch_to_mongo(batch_results: List[Dict[str, Any]], batch_num: int, total_batches: int):
        nonlocal id_index, total_saved
        
        try:
            # Lấy slice của available_ids cho batch này
            batch_size = len(batch_results)
            batch_ids = available_ids[id_index:id_index + batch_size] if id_index < len(available_ids) else []
            
            # Lưu batch vào MongoDB
            result = await SaveUtils.save_db_results(
                batch_results, 
                available_ids=batch_ids, 
                collection_name=collection_name
            )
            
            if result:
                saved_count = len(batch_results)
                total_saved += saved_count
                
                # Hiển thị ID range
                if batch_ids:
                    id_range = f"{min(batch_ids)} - {max(batch_ids)}" if len(batch_ids) > 1 else str(batch_ids[0])
                else:
                    id_range = "auto-generated"
                
                saved_batches.append({
                    'batch_num': batch_num,
                    'saved_count': saved_count,
                    'id_range': id_range
                })
                
                print(f"✅ Batch {batch_num}/{total_batches}: Saved {saved_count} records (IDs: {id_range})")
                
                # Cập nhật id_index cho batch tiếp theo
                id_index += saved_count
            else:
                print(f"⚠️ Batch {batch_num}/{total_batches}: No records saved")
                
        except Exception as e:
            print(f"❌ Error saving batch {batch_num}/{total_batches} to MongoDB: {e}")

    crawler = EnhancedPropertyCrawler(custom_extractor_factory)
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
        Available IDs Used: {id_index}/{len(available_ids)}
        Start: {start:%Y%m%d_%H%M%S} | End: {end:%Y%m%d_%H%M%S} | 🕒 Duration: {duration}
    """)