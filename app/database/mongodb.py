import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger("krishimitra.database")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    try:
        db_instance.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=3000
        )
        db_instance.db = db_instance.client[settings.MONGODB_DB_NAME]
        # Quick ping test
        await db_instance.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas / Local MongoDB!")

        # Create indexes
        await db_instance.db.users.create_index("email", unique=True)
        await db_instance.db.chat_history.create_index([("user_id", 1), ("updated_at", -1)])
        await db_instance.db.documents.create_index([("user_id", 1)])
        await db_instance.db.disease_reports.create_index([("user_id", 1)])
        await db_instance.db.notifications.create_index([("user_id", 1), ("read", 1)])

    except Exception as e:
        logger.warning(f"MongoDB connection failed: {e}. App will proceed with in-memory / fallback data mode if needed.")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_instance.db
