from datetime import datetime, timedelta
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import update
from jose import JWTError,jwt
# Internal Imports
from db.db import get_db, engine, Base
from models.users import Users
from models.req import Requests 
from models.keys import APIkeys
from schemas.users import UserReg,UserLogin
from core.mail import ses_client
from core.security import PasswordHasher
from schemas.keys import KeyReg 
from schemas.req import ReqReg


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For testing, allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret for token generation
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
serializer = URLSafeTimedSerializer(SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
@app.get("/")
async def health_check():
    return {"status": "online", "service": "KeyLocker"}

# --- Endpoints ---

@app.post("/signup")
async def signup(user_data: UserReg, db: AsyncSession = Depends(get_db)):
    query = select(Users).where(Users.email == user_data.email)
    existing_user = await db.execute(query)
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Hash the password!
    hashed_pwd = PasswordHasher.hash_password(user_data.password)
    token = serializer.dumps(user_data.email, salt='email_confirm')
    verification_link = f"http://127.0.0.1:8000/verify/{token}"

    try:
        new_user = Users(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pwd, 
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
                                <p>This link will expire in 10 minutes.</p>
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
        email = serializer.loads(token, salt='email_confirm', max_age=600)
        
        query = select(Users).where(Users.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        user.is_verified = True 
        await db.commit()
        
        return {"message": f"Account for {email} has been successfully verified!"}
    except Exception:
        raise HTTPException(status_code=400, detail="The verification link is invalid or has expired.")
@app.post("/login")
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Fetch user from database
    query = select(Users).where(Users.email == credentials.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Validate credentials (Email and Password)
    if not user or not PasswordHasher.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    # 3. STRICT CHECK: Enforce email verification
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account not verified. Please check your email for the activation link."
        )
    
    # 4. Generate JWT for verified users only
    token = create_access_token({"sub": user.email, "role": user.role, "id": user.emp_id})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "emp_id": user.emp_id,
            "role": user.role,
            "name": user.name
        }
    }
@app.patch("/admin/requests/{request_id}/approve")
async def approve_request(request_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Update Request Status
    query = select(Requests).where(Requests.request_id == request_id)
    result = await db.execute(query)
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "Approved"
    
    # 2. Fetch User email for notification
    user_query = select(Users.email).where(Users.emp_id == req.requestee_id)
    user_res = await db.execute(user_query)
    user_email = user_res.scalar()

    try:
        await db.commit()
        
        # 3. Trigger Email Notification
        ses_client.send_email(
            Source="mail@keylocker.in",
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": "KeyLocker: Request Approved!"},
                "Body": {"Html": {"Data": f"Your request for <b>{req.api_name}</b> has been approved. Log in to view your key."}}
            }
        )
        return {"message": "Approved and user notified via email"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/admin/keys")
async def admin_add_key(key_data: KeyReg, db: AsyncSession = Depends(get_db)):
    new_api = APIkeys(
        api_name=key_data.api_name,
        api_key=key_data.api_key,
        owner_id=key_data.owner_id  # Use the ID from the frontend payload
    )
    db.add(new_api)
    await db.commit()
    return {"message": f"Successfully added {key_data.api_name}"}

# Admin: View all requests currently in 'Pending' status
@app.get("/admin/requests")
async def get_all_requests(db: AsyncSession = Depends(get_db)):
    # Join Requests with Users to get the requester's name
    query = select(
        Requests.request_id,
        Requests.api_name,
        Requests.requestee_id,
        Users.name.label("user_name")
    ).join(Users, Requests.requestee_id == Users.emp_id).where(Requests.status == "Pending")
    
    result = await db.execute(query)
    # Convert result to a list of dictionaries for easy JSON serialization
    requests = result.all()
    return [
        {
            "request_id": r.request_id,
            "api_name": r.api_name,
            "requestee_id": r.requestee_id,
            "user_name": r.user_name
        } for r in requests
    ]

# User: See names of APIs available to request (Hides the actual keys)
@app.get("/user/available-apis")
async def get_api_names(db: AsyncSession = Depends(get_db)):
    query = select(APIkeys.api_name).distinct()
    result = await db.execute(query)
    return result.scalars().all()

# User: Submit a request for a specific API
@app.post("/user/request")
async def create_user_request(req_data: ReqReg, db: AsyncSession = Depends(get_db)):
    new_request = Requests(
        api_name=req_data.api_name,
        requestee_id=req_data.requestee_id, # Use the ID from the frontend payload
        status="Pending"
    )
    db.add(new_request)
    await db.commit()
    return {"message": "Request submitted successfully!"}
@app.get("/user/my-keys/{user_id}")
async def get_user_approved_keys(user_id: int, db: AsyncSession = Depends(get_db)):
    # This query joins Requests and APIkeys on the api_name
    # It only returns keys where the specific user's request is 'Approved'
    query = select(APIkeys.api_name, APIkeys.api_key).join(
        Requests, APIkeys.api_name == Requests.api_name
    ).where(
        Requests.requestee_id == user_id,
        Requests.status == "Approved"
    )
    result = await db.execute(query)
    
    # Return a list of dictionaries for the frontend to map
    keys = result.all()
    return [{"api_name": k[0], "api_key": k[1]} for k in keys]
@app.get("/user/my-requests/{user_id}")
async def get_user_requests(user_id: int, db: AsyncSession = Depends(get_db)):
    # Only return API names where the status is currently 'Pending'
    query = select(Requests.api_name).where(
        Requests.requestee_id == user_id,
        Requests.status == "Pending"
    )
    result = await db.execute(query)
    return result.scalars().all()
@app.patch("/user/requests/consume")
async def consume_request(api_name: str, user_id: int, db: AsyncSession = Depends(get_db)):
    # Find the specific approved request
    query = select(Requests).where(
        Requests.api_name == api_name,
        Requests.requestee_id == user_id,
        Requests.status == "Approved"
    )
    result = await db.execute(query)
    db_request = result.scalar_one_or_none()

    if not db_request:
        # If this hits, it means the API name or User ID didn't match an 'Approved' record
        raise HTTPException(status_code=404, detail="Approved request not found")

    db_request.status = "Consumed"
    
    try:
        await db.commit()
        return {"message": "Key burned successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
@app.patch("/admin/requests/{request_id}/reject")
async def reject_request(request_id: int, reason: str, db: AsyncSession = Depends(get_db)):
    # 1. Fetch the request
    query = select(Requests).where(Requests.request_id == request_id)
    result = await db.execute(query)
    req = result.scalar_one_or_none()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # 2. Update status to Rejected
    req.status = "Rejected"
    
    # 3. Get user email for notification
    user_query = select(Users.email).where(Users.emp_id == req.requestee_id)
    user_res = await db.execute(user_query)
    user_email = user_res.scalar()

    try:
        await db.commit()
        
        # 4. Trigger Rejection Email via AWS SES
        ses_client.send_email(
            Source="mail@keylocker.in",
            Destination={"ToAddresses": [user_email]},
            Message={
                "Subject": {"Data": "KeyLocker: Request Denied"},
                "Body": {"Html": {"Data": f"""
                    <h3>Request Update</h3>
                    <p>Your request for <b>{req.api_name}</b> was rejected.</p>
                    <p><b>Reason:</b> {reason}</p>
                    <p>You can try requesting again if you address the reason above.</p>
                """}}
            }
        )
        return {"message": "Rejected and user notified."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/user/stats/{user_id}")
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    # Count Approved keys
    approved_query = select(Requests).where(Requests.requestee_id == user_id, Requests.status == "Approved")
    # Count Consumed keys
    consumed_query = select(Requests).where(Requests.requestee_id == user_id, Requests.status == "Consumed")
    
    approved_res = await db.execute(approved_query)
    consumed_res = await db.execute(consumed_query)
    
    return {
        "approved": len(approved_res.scalars().all()),
        "consumed": len(consumed_res.scalars().all())
    }
@app.post("/forgot-password")
async def forgot_password(email: str, db: AsyncSession = Depends(get_db)):
    query = select(Users).where(Users.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = serializer.dumps(email, salt='password-reset')
    reset_link = f"http://127.0.0.1:8000/reset-password/{token}"

    ses_client.send_email(
        Source="mail@keylocker.in",
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "KeyLocker: Reset Your Password"},
            "Body": {"Html": {"Data": f"Click <a href='{reset_link}'>here</a> to reset your password. Valid for 10 mins."}}
        }
    )
    return {"message": "Reset link sent to your email."}
@app.post("/reset-password-confirm")
async def reset_password_confirm(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=600)
        hashed_pwd = PasswordHasher.hash_password(new_password)
        
        query = update(Users).where(Users.email == email).values(password=hashed_pwd)
        await db.execute(query)
        await db.commit()
        return {"message": "Password updated successfully!"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

@app.delete("/admin/keys/{api_name}")
async def delete_api_key(api_name: str, db: AsyncSession = Depends(get_db)):
    query = select(APIkeys).where(APIkeys.api_name == api_name)
    result = await db.execute(query)
    key = result.scalar_one_or_none()

    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")

    await db.delete(key)
    await db.commit()
    return {"message": f"{api_name} has been purged from the vault."}