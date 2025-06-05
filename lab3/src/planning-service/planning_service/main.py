from fastapi import FastAPI
from contextlib import asynccontextmanager

from planning_service.config import settings
from planning_service.database import connect_db, disconnect_db, create_tables
from planning_service.api import plans_router, transactions_router, analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await connect_db()
        create_tables()
        print("Database connected and tables created")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Falling back to in-memory mode")
        settings.use_in_memory = True
    
    yield
    
    if not settings.use_in_memory:
        await disconnect_db()
        print("Database disconnected")


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
        "database_mode": "in-memory" if settings.use_in_memory else "postgresql"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.planning_service_host,
        port=settings.planning_service_port
    ) 