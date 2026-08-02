import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

raw_url = os.getenv("DATABASE_URL") or os.getenv("DIRECT_URL")

if not raw_url:
    raise RuntimeError(
        "Database configuration is missing. Set DATABASE_URL in Render "
        "(DIRECT_URL is supported as a fallback)."
    )

if raw_url.startswith("postgres://"):
    database_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://"):
    database_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql+asyncpg://"):
    database_url = raw_url
else:
    raise RuntimeError(
        "Database URL must use postgres://, postgresql://, or "
        "postgresql+asyncpg://."
    )

# Creating the engine does not connect to the database. Connections are made
# only when an endpoint needs them, so a temporary DNS/database outage does
# not take down every web worker during deployment.
engine = create_async_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={"timeout": 10},
)

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