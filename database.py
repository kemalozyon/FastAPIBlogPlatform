from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

## Changing the url is the only thing that we need to change when we need to change our db
SQLALHEMY_DATABASE_URL = settings.database_url

## we dont use using same thread is false since we are using postgresql right now
engine = create_async_engine(
    SQLALHEMY_DATABASE_URL
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session