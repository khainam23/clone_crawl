"""
Gunicorn/Uvicorn entrypoint
"""
import sys
import asyncio
import platform
from pathlib import Path
import uvicorn

# Fix for Windows ProactorEventLoop issue
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after adding to path
from app.main import app
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.utils import city_utils, prefecture_utils, district_utils

async def startup():
    """Application startup"""
    await connect_to_mongo()
    await city_utils.init()
    await prefecture_utils.init()
    district_utils.ensure_district_index()
    
    # Start scheduler after MongoDB is connected
    from app.core.scheduler import start_scheduler
    await start_scheduler()

async def shutdown():
    """Application shutdown"""
    from app.core.scheduler import stop_scheduler
    stop_scheduler()
    await close_mongo_connection()

# Add startup and shutdown events
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

if __name__ == "__main__": 
    print("============ 😶‍🌫️ START SERVER 😶‍🌫️ ============")   
    # Run with uvicorn
    uvicorn.run(
        "run:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )