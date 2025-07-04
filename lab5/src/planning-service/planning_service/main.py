from fastapi import FastAPI
from contextlib import asynccontextmanager

from planning_service.config import settings
from planning_service.database import connect_db, disconnect_db, create_tables
from planning_service.database.mongodb import mongodb
from planning_service.database.redis import redis_manager
from planning_service.api import plans_router, transactions_router, analytics_router
from planning_service.api.transactions_mongo import router as transactions_mongo_router
from planning_service.api.cache import router as cache_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключение к PostgreSQL
    postgres_connected = False
    try:
        await connect_db()
        create_tables()
        postgres_connected = True
        print("PostgreSQL connected and tables created")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        print("Falling back to in-memory mode for plans")
        settings.use_in_memory = True
    
    # Подключение к MongoDB
    mongodb_connected = False
    try:
        mongodb_connected = mongodb.connect()
        if mongodb_connected:
            print("MongoDB connected successfully")
        else:
            print("MongoDB connection failed")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    # Подключение к Redis
    redis_connected = False
    try:
        redis_connected = await redis_manager.connect()
        if redis_connected:
            print("Redis connected successfully")
        else:
            print("Redis connection failed - caching disabled")
    except Exception as e:
        print(f"Redis connection error: {e}")
    
    yield
    
    # Отключение от баз данных
    if postgres_connected and not settings.use_in_memory:
        await disconnect_db()
        print("PostgreSQL disconnected")
    
    if mongodb_connected:
        mongodb.disconnect()
        print("MongoDB disconnected")
    
    if redis_connected:
        await redis_manager.disconnect()
        print("Redis disconnected")


app = FastAPI(
    title="Planning Service",
    description="Budget Planning Service with PostgreSQL, MongoDB and Redis support",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(plans_router)
app.include_router(transactions_router)
app.include_router(transactions_mongo_router)
app.include_router(analytics_router)
app.include_router(cache_router)


@app.get("/health")
async def health_check():
    mongodb_status = "connected" if mongodb.is_connected() else "disconnected"
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    
    return {
        "status": "healthy", 
        "service": "planning-service",
        "database_mode": "in-memory" if settings.use_in_memory else "postgresql",
        "mongodb_status": mongodb_status,
        "redis_status": redis_status,
        "cache_enabled": settings.enable_cache
    }


@app.get("/db/health")
async def db_health_check():
    """Проверка состояния баз данных"""
    postgres_status = "in-memory" if settings.use_in_memory else "connected"
    mongodb_status = "connected" if mongodb.is_connected() else "disconnected"
    redis_status = "connected" if redis_manager.is_connected() else "disconnected"
    
    return {
        "postgresql": postgres_status,
        "mongodb": mongodb_status,
        "redis": redis_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.planning_service_host,
        port=settings.planning_service_port
    ) 