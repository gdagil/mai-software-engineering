from typing import Optional, Any, Callable, List
from planning_service.database.redis import redis_manager
from planning_service.config import settings
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class CacheService:
    """Сервис для реализации паттернов сквозного чтения и записи"""
    
    def __init__(self):
        self.enabled = settings.enable_cache
    
    def _make_key(self, prefix: str, *args) -> str:
        """Создание ключа кеша с хешированием длинных значений"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key = ":".join(key_parts)
        
        # Если ключ слишком длинный, хешируем его
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key
    
    async def read_through(
        self,
        cache_key: str,
        fetch_function: Callable,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Паттерн сквозного чтения (Read-Through)
        1. Проверяем кеш
        2. Если данных нет, получаем из источника
        3. Сохраняем в кеш
        4. Возвращаем данные
        """
        if not self.enabled:
            return await fetch_function(*args, **kwargs)
        
        # Пытаемся получить из кеша
        cached_data = await redis_manager.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache HIT for key: {cache_key}")
            return cached_data
        
        # Кеш промах - получаем данные из источника
        logger.debug(f"Cache MISS for key: {cache_key}")
        data = await fetch_function(*args, **kwargs)
        
        # Сохраняем в кеш, если данные получены
        if data is not None:
            await redis_manager.set(cache_key, data, ttl)
            logger.debug(f"Data cached for key: {cache_key}")
        
        return data
    
    async def write_through(
        self,
        cache_key: str,
        write_function: Callable,
        data: Any,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Паттерн сквозной записи (Write-Through)
        1. Записываем в основное хранилище
        2. Если запись успешна, обновляем кеш
        3. Возвращаем результат
        """
        if not self.enabled:
            return await write_function(*args, **kwargs)
        
        # Записываем в основное хранилище
        result = await write_function(*args, **kwargs)
        
        # Если запись успешна, обновляем кеш
        if result is not None:
            await redis_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache updated for key: {cache_key}")
        
        return result
    
    async def write_behind(
        self,
        cache_key: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Паттерн отложенной записи (Write-Behind/Write-Back)
        Записываем только в кеш, запись в БД откладывается
        """
        if not self.enabled:
            return False
        
        success = await redis_manager.set(cache_key, data, ttl)
        if success:
            logger.debug(f"Write-behind cache update for key: {cache_key}")
        
        return success
    
    async def invalidate(self, cache_key: str) -> bool:
        """Инвалидация кеша по ключу"""
        if not self.enabled:
            return True
        
        success = await redis_manager.delete(cache_key)
        logger.debug(f"Cache invalidated for key: {cache_key}")
        return success
    
    async def invalidate_pattern(self, pattern: str) -> bool:
        """Инвалидация кеша по паттерну"""
        if not self.enabled:
            return True
        
        success = await redis_manager.delete_pattern(pattern)
        logger.debug(f"Cache invalidated for pattern: {pattern}")
        return success
    
    async def exists(self, cache_key: str) -> bool:
        """Проверка существования ключа в кеше"""
        if not self.enabled:
            return False
        
        return await redis_manager.exists(cache_key)
    
    # Вспомогательные методы для работы с планами
    def make_user_plans_key(self, user_id: str) -> str:
        """Ключ для списка планов пользователя"""
        return self._make_key("plans:user", user_id)
    
    def make_plan_key(self, plan_id: int, user_id: str) -> str:
        """Ключ для конкретного плана"""
        return self._make_key("plan", plan_id, user_id)
    
    def make_user_key(self, user_id: str) -> str:
        """Ключ для пользователя"""
        return self._make_key("user", user_id)
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Инвалидация всего кеша пользователя"""
        patterns = [
            f"plans:user:{user_id}",
            f"plan:*:{user_id}",
            f"user:{user_id}"
        ]
        
        success = True
        for pattern in patterns:
            pattern_success = await self.invalidate_pattern(pattern)
            success = success and pattern_success
        
        return success

# Создаем глобальный экземпляр сервиса кеширования
cache_service = CacheService() 