"""
MongoDB connection
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
        # Test connection
        await mongodb.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    try:
        if mongodb.client:
            mongodb.client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Failed to close MongoDB connection: {e}")

def get_database():
    """Get database instance"""
    return mongodb.database

def get_collection(collection_name: str):
    """Get collection instance"""
    return mongodb.database[collection_name]

# ------------------- Sync -------------------

class MongoDBSync:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.database = self.client[db_name]

    def get_collection(self, name: str):
        return self.database[name]

mongodb_sync = MongoDBSync(settings.MONGODB_URL, settings.DATABASE_NAME)