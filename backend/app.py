from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
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


