from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://budget_user:budget_password@postgres:5432/budget_db"
    
    # Planning Service
    planning_service_host: str = "0.0.0.0"
    planning_service_port: int = 8080
    
    # In-memory mode (fallback)
    use_in_memory: bool = False
    
    model_config = ConfigDict(env_file=".env")


settings = Settings() 