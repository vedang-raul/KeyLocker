import fastapi as FastAPI
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(os.getenv("DIRECT_URL"))


SessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base=declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            # You must await the close in an async setup
            await db.close()