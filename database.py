from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path

DB_URL = "sqlite+aiosqlite:///./data/snippets.db"

engine = create_async_engine(DB_URL, echo=True)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session