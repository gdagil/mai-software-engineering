from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Planning Service
    planning_service_host: str = "0.0.0.0"
    planning_service_port: int = 8080
    
    # In-memory mode (always enabled)
    use_in_memory: bool = True
    
    model_config = ConfigDict(env_file=".env")


settings = Settings() 