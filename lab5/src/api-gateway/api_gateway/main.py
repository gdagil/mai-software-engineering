from fastapi import FastAPI

from api_gateway.config import settings
from api_gateway.api import auth_router, proxy_router

app = FastAPI(
    title="API Gateway", 
    description="Budget Planning System API Gateway", 
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(proxy_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.api_gateway_host, 
        port=settings.api_gateway_port
    ) 