from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
from itsdangerous import URLSafeTimedSerializer
import boto3
import os



load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")


app=FastAPI()

ses_client=boto3.client(
    'ses',
    region_name = AWS_REGION,
    aws_access_key_id = AWS_ACCESS_KEY,
    aws_secret_access_key = AWS_SECRET_KEY
)

class EmailContent(BaseModel):
    EmailAddress : List[str]
    message:str = "Hello this is a test message from keylocker.in"


@app.get("/")
async def root():
    return {"Message" : "Backend is Live"}

@app.post("/send_mail")
async def send_test(email_content:EmailContent):
    try:
        response = ses_client.send_email(
            Source = "mail@keylocker.in",
            Destination = {
                "ToAddresses" : email_content.EmailAddress
            },
            Message = {
                        "Subject" : {"Data" : "Test email from keylocker"},
                        "Body" : {
                                    "Text" : 
                                    {
                                    "Data" : email_content.message
                                    } 
                                }
                    }
        )
        return {"Message" : "Email sent !"}
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/verify_mail")
async def verify_mail(email_content : EmailContent):
    try:
        responses = []
        for email in email_content.EmailAddress:
            response = ses_client.verify_email_address(EmailAddress = email)
            responses.append(response)
            return {
                "Message" : "Verification Email sent !",
                "Response" : responses
                    }
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
        


@app.post("/verify_email")
async def verify(email_content=EmailContent):
    try:
        secret_key=os.getenv("SECRET_KEY")
        serializer=URLSafeTimedSerializer(secret_key)

        user_id = email_content.EmailAddress
        token = serializer.dumps(user_id,salt='email_confirm')

        verification_link = f"https://yourdomain.com/verify_email/{token}"
        print(f"verification Link: {verification_link}")

        try: 
            data = serializer.load(token, salt='email_confirm',max_age="8400")
            print(f"Verified user ID: {data}")
        except Exception as e:
            print(f"Token invalid or expired: {e}")
    except Exception as e:
        raise HTTPException(status_code=400,detail=(e))
    