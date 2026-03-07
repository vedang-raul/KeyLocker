import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

raw_url = os.getenv("DIRECT_URL")

# Safety check for Render's URL format
if raw_url and raw_url.startswith("postgres://"):
    database_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    database_url = raw_url

engine = create_async_engine(database_url)

SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()