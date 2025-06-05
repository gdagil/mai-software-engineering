import databases
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base

from planning_service.config import settings

# Database setup
DATABASE_URL = settings.database_url

metadata = MetaData()
database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))

# SQLAlchemy Base class for models
Base = declarative_base()


async def connect_db():
    """Подключение к базе данных"""
    await database.connect()


async def disconnect_db():
    """Отключение от базы данных"""
    await database.disconnect()


def create_tables():
    """Создание таблиц в базе данных"""
    from planning_service.models.database_models import Base
    Base.metadata.create_all(bind=engine) 