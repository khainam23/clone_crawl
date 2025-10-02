import asyncio

# Chạy: python -m app.tests.mitsui.multi
# Nhớ sửa lại trang là 1 để test

from app.jobs.mitsui_crawl_page.index import crawl_multi
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils import city_utils, prefecture_utils
from app.utils.save_utils import SaveUtils
from app.core.config import settings

async def main():
    """Main function with MongoDB connection setup"""
    try:
        # Initialize MongoDB connection
        print("🔌 Connecting to MongoDB...")
        await connect_to_mongo()
        print("✅ MongoDB connected successfully!")
        
        await city_utils.init()
        await prefecture_utils.init()
        
        await SaveUtils.clean_db(settings.COLLECTION_NAME_MITSUI, auto_backup=True)
        
        # Run the multi-page crawl with Mitsui
        print("🚀 Starting Mitsui multi-page crawl...")
        await crawl_multi()
        print("✅ Crawl completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close MongoDB connection
        print("🔌 Closing MongoDB connection...")
        await close_mongo_connection()
        print("✅ MongoDB connection closed!")

if __name__ == "__main__":
    asyncio.run(main())