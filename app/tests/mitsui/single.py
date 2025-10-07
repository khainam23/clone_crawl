import asyncio
import sys
import platform

# Chạy: python -m app.tests.mitsui.single

from app.jobs.crawl_strcture.index import crawl_pages
from app.jobs.mitsui_crawl_page.custom_extractor_factory import setup_custom_extractor
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils import city_utils, prefecture_utils, district_utils

# Fix for Windows ProactorEventLoop issue
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    """Main function with MongoDB connection setup"""
    try:
        # Initialize MongoDB connection
        print("🔌 Connecting to MongoDB...")
        await connect_to_mongo()
        print("✅ MongoDB connected successfully!")
        
        await city_utils.init()
        await prefecture_utils.init()
        district_utils.ensure_district_index()
        
        # Run the crawl with Mitsui custom extractor
        await crawl_pages(
            urls=[
                "https://www.mitsui-chintai.co.jp/rf/tatemono/6764/1102", 
            ],
            batch_size=1,
            id_mongo=0,
            collection_name='mitsui_test',
            custom_extractor_factory=setup_custom_extractor  # Use Mitsui custom extractor
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close MongoDB connection
        print("🔌 Closing MongoDB connection...")
        await close_mongo_connection()
        print("✅ MongoDB connection closed!")

if __name__ == "__main__":
    asyncio.run(main())

