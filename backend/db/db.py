import fastapi as FastAPI
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os

engine=create_async_engine(os.getenv("DIRECT_URL"))


SessionLocal=sessionmaker(bind=engine)

Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
