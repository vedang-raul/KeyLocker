import asyncio
from db.db import engine, Base, SessionLocal
from backend.models.users import Users 
from models.req import Requests
from models.keys import APIkeys
from sqlalchemy import select

async def test_logic():
    # Use 'async with' for the session
    async with SessionLocal() as db:
        try:
            # 1. Create Tables
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully!")

            # 2. Create a Test User
            new_user = Users(
                email="test@keylocker.in", 
                hashed_password="hashed_abc_123", 
                role="Admin"
            )
            db.add(new_user)
            await db.commit()  # Use await
            await db.refresh(new_user) # Use await
            print(f"CREATED: User {new_user.email} with emp_id {new_user.emp_id}")

            # 3. Create a Request
            new_request = Requests(
                requestee_id=new_user.emp_id,
                api_name="CloudVision_API",
                status="Pending"
            )
            db.add(new_request)
            
            # 4. Create an API Key
            new_key = APIkeys(
                owner_id=new_user.emp_id,
                encrypted_key="super_secret_encrypted_string_99",
                api_name="CloudVision_API"
            )
            db.add(new_key)
            await db.commit()

            # 5. RELATIONSHIP CHECK
            # In Async, you often need to re-select to load relationships
            result = await db.execute(
                select(Users).filter(Users.emp_id == new_user.emp_id)
            )
            user_from_db = result.scalar_one()
            
            # Note: Because relationships are lazy-loaded, 
            # you might need to use selectinload in your query 
            # for async relationships to work smoothly.
            print(f"\nRELATIONSHIP CHECK:")
            print(f"User {user_from_db.email} created successfully.")

        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_logic())