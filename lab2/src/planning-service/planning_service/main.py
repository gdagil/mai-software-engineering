from fastapi import FastAPI
from contextlib import asynccontextmanager

from planning_service.config import settings
from planning_service.api import plans_router, transactions_router, analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Planning Service in in-memory mode")
    yield
    print("Shutting down Planning Service")


app = FastAPI(
    title="Planning Service",
    description="Budget Planning Service",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(plans_router)
app.include_router(transactions_router)
app.include_router(analytics_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "planning-service",
        "database_mode": "in-memory"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.planning_service_host,
        port=settings.planning_service_port
    ) 