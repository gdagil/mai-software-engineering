from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Planning Service
    planning_service_url: str = "http://planning-service:8080"
    
    # API Gateway
    api_gateway_host: str = "0.0.0.0"
    api_gateway_port: int = 8000
    
    model_config = ConfigDict(env_file=".env")


settings = Settings() 