import json
import aioredis
from typing import Optional, Any
from planning_service.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.connected = False

    async def connect(self):
        """Подключение к Redis"""
        if not settings.enable_cache:
            logger.info("Redis cache is disabled")
            return False
            
        try:
            self.redis_client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Проверяем подключение
            await self.redis_client.ping()
            self.connected = True
            logger.info("Redis connected successfully")
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
            logger.info("Redis disconnected")

    def is_connected(self) -> bool:
        """Проверка подключения к Redis"""
        return self.connected and self.redis_client is not None

    async def get(self, key: str) -> Optional[Any]:
        """Получение данных из кеша"""
        if not self.is_connected():
            return None
            
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранение данных в кеш"""
        if not self.is_connected():
            return False
            
        try:
            ttl = ttl or settings.redis_ttl
            data = json.dumps(value, default=str)  # default=str для обработки datetime
            await self.redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаление данных из кеша"""
        if not self.is_connected():
            return False
            
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> bool:
        """Удаление данных по паттерну"""
        if not self.is_connected():
            return False
            
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis delete pattern error for pattern {pattern}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Проверка существования ключа"""
        if not self.is_connected():
            return False
            
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    def make_cache_key(self, prefix: str, *args) -> str:
        """Создание ключа кеша"""
        parts = [prefix] + [str(arg) for arg in args]
        return ":".join(parts)

# Создаем глобальный экземпляр менеджера Redis
redis_manager = RedisManager() 