from fastapi import APIRouter, Depends
from planning_service.services.cache_service import cache_service
from planning_service.database.redis import redis_manager
from planning_service.dependencies import get_current_user
import time

router = APIRouter(prefix="/cache", tags=["cache"])

@router.get("/health")
async def cache_health():
    """Проверка состояния кеша"""
    return {
        "redis_connected": redis_manager.is_connected(),
        "cache_enabled": cache_service.enabled
    }

@router.post("/invalidate/{user_id}")
async def invalidate_user_cache(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    """Инвалидация кеша пользователя (только для администратора или самого пользователя)"""
    if current_user != "admin" and current_user != user_id:
        return {"error": "Access denied"}
    
    success = await cache_service.invalidate_user_cache(user_id)
    return {
        "message": f"Cache invalidated for user {user_id}",
        "success": success
    }

@router.post("/clear")
async def clear_all_cache(current_user: str = Depends(get_current_user)):
    """Очистка всего кеша (только для администратора)"""
    if current_user != "admin":
        return {"error": "Access denied - admin only"}
    
    if not redis_manager.is_connected():
        return {"error": "Redis not connected"}
    
    try:
        await redis_manager.redis_client.flushdb()
        return {"message": "All cache cleared successfully"}
    except Exception as e:
        return {"error": f"Failed to clear cache: {e}"}

@router.get("/stats")
async def cache_stats(current_user: str = Depends(get_current_user)):
    """Статистика кеша (только для администратора)"""
    if current_user != "admin":
        return {"error": "Access denied - admin only"}
    
    if not redis_manager.is_connected():
        return {"error": "Redis not connected"}
    
    try:
        info = await redis_manager.redis_client.info("memory")
        stats = {
            "used_memory": info.get("used_memory", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "used_memory_peak": info.get("used_memory_peak", 0),
            "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
            "connected_clients": info.get("connected_clients", 0)
        }
        return stats
    except Exception as e:
        return {"error": f"Failed to get cache stats: {e}"}

@router.get("/test/performance")
async def test_cache_performance(
    iterations: int = 100,
    current_user: str = Depends(get_current_user)
):
    """Тест производительности кеша vs прямого доступа к БД"""
    if current_user != "admin":
        return {"error": "Access denied - admin only"}
    
    from planning_service.services import plans_service
    
    # Измеряем время с кешем
    start_time = time.time()
    for i in range(iterations):
        await plans_service.get_plans(current_user)
    cached_time = time.time() - start_time
    
    # Очищаем кеш для честного теста
    await cache_service.invalidate_user_cache(current_user)
    
    # Временно отключаем кеш
    original_enabled = cache_service.enabled
    cache_service.enabled = False
    
    # Измеряем время без кеша
    start_time = time.time()
    for i in range(iterations):
        await plans_service.get_plans(current_user)
    uncached_time = time.time() - start_time
    
    # Восстанавливаем настройку кеша
    cache_service.enabled = original_enabled
    
    return {
        "iterations": iterations,
        "cached_time": round(cached_time, 4),
        "uncached_time": round(uncached_time, 4),
        "speedup": round(uncached_time / cached_time, 2) if cached_time > 0 else "N/A",
        "cache_enabled": original_enabled
    } 