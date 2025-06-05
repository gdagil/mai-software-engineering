from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://budget_user:budget_password@postgres:5432/budget_db"
    
    # MongoDB
    mongodb_url: str = os.environ.get("MONGODB_URL", "mongodb://mongodb:27017/transactions_db")
    mongodb_database: str = "transactions_db"
    
    # Redis
    redis_url: str = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    redis_ttl: int = 300  # 5 minutes default TTL
    enable_cache: bool = True
    
    # Planning Service
    planning_service_host: str = "0.0.0.0"
    planning_service_port: int = 8080
    
    # In-memory mode (fallback)
    use_in_memory: bool = False
    
    model_config = ConfigDict(env_file=".env")


settings = Settings() 