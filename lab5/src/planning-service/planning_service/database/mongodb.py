from pymongo import MongoClient
from planning_service.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        try:
            self._client = MongoClient(settings.mongodb_url)
            self._database = self._client[settings.mongodb_database]
            # Проверяем подключение
            self._client.admin.command('ismaster')
            logger.info("MongoDB connected successfully")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    def disconnect(self):
        if self._client:
            self._client.close()
            logger.info("MongoDB disconnected")
    
    @property
    def database(self):
        if self._database is None:
            raise Exception("MongoDB not connected")
        return self._database
    
    @property
    def transactions_collection(self):
        return self.database.transactions
    
    def is_connected(self):
        try:
            if self._client:
                self._client.admin.command('ismaster')
                return True
        except:
            pass
        return False


# Глобальный экземпляр MongoDB
mongodb = MongoDB() 