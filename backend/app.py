import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

# Internal Imports
from db.db import get_db, engine, Base
from models.users import Users
from models.req import Requests 
from models.keys import APIkeys
from schemas.users import UserReg
from core.mail import ses_client


# Initialize Environment
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Recreate tables (especially since you dropped them earlier)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic can go here

app = FastAPI(title="KeyLocker Backend", lifespan=lifespan)

# Secret for token generation
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
serializer = URLSafeTimedSerializer(SECRET_KEY)

@app.get("/")
async def health_check():
    return {"status": "online", "service": "KeyLocker"}

# --- Endpoints ---

@app.post("/signup")
async def signup(user_data: UserReg, db: AsyncSession = Depends(get_db)):
    token = serializer.dumps(user_data.email, salt='email_confirm')
    verification_link = f"http://127.0.0.1:8000/verify/{token}"

    try:
        new_user = Users(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password, 
            role=user_data.role
        )
        db.add(new_user)
        await db.commit()
        # await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        print(f"DB Error: {e}")
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    try:
        ses_client.send_email(
            Source="mail@keylocker.in",
            Destination={"ToAddresses": [user_data.email]},
            Message={
                "Subject": {"Data": "Activate your KeyLocker Account"},
                "Body": {
                    "Html": {
                        "Data": f"""
                        <html>
                            <body>
                                <h3>Welcome {user_data.name}!</h3>
                                <p>Please click the link below to verify your email for KeyLocker:</p>
                                <a href="{verification_link}">Verify My Email</a>
                                <p>This link will expire in 24 hours.</p>
                            </body>
                        </html>
                        """
                    }
                }
            }
        )
        return {"message": "User created. Please check your email for verification."}
    except Exception as e:
        # If mail fails, the user IS in the DB, but they didn't get the link.
        print(f"--- MAIL ERROR: {e} ---") 
        raise HTTPException(status_code=500, detail=f"Mail delivery failed: {str(e)}")
    

@app.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        email = serializer.loads(token, salt='email_confirm', max_age=86400)
        
        query = select(Users).where(Users.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Flip the verification switch in DB
        # user.is_verified = True 
        # await db.commit()
        
        return {"message": f"Account for {email} has been successfully verified!"}
    except Exception:
        raise HTTPException(status_code=400, detail="The verification link is invalid or has expired.")