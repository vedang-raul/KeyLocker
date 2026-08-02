from fastapi import HTTPException
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from pydantic import BaseModel, EmailStr
import boto3
import os

from models.users import Users
from schemas.users import UserReg


load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")

ses_client = boto3.client(
    'ses',
    region_name=AWS_REGION,
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY
)


async def send_test(email_content: UserReg):
    try:
        response = ses_client.send_email(
            Source = "mail@keylocker.in",
            Destination = {
                "ToAddresses" : [email_content.email]
            },
            Message = {
                        "Subject" : {"Data" : "Test email from keylocker"},
                        "Body" : {
                                    "Text" : 
                                    {
                                    "Data" : "Testing email from keylocker.in"
                                    } 
                                }
                    }
        )
        return {"Message" : "Email sent !"}
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

async def verify_mail(email_content: UserReg):
    try:
        response = ses_client.verify_email_address(
            EmailAddress=email_content.email  
        )
        return {
            "Message": f"AWS Sandbox verification sent to {email_content.email}!",
            "Response": response
        }
    except Exception as e:
        # This will catch if the email is invalid or AWS keys are wrong
        raise HTTPException(status_code=400, detail=str(e))
    
async def verify(email_content=UserReg):
    try:
        secret_key = os.getenv("SECRET_KEY")
        serializer = URLSafeTimedSerializer(secret_key)

        email_to_verify = email_content.email 
        token = serializer.dumps(email_to_verify, salt='email_confirm')

        verification_link = f"https://keylocker.in/verify_email/{token}"
        print(f"Verification Link: {verification_link}")

        # Testing the verification logic immediately
        try: 
            # Changed .load() to .loads()
            # Note: max_age must be an integer (8400), not a string ("8400")
            data = serializer.loads(token, salt='email_confirm', max_age=8400)
            print(f"Verified email from token: {data}")
        except Exception as e:
            print(f"Token invalid or expired: {e}")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))