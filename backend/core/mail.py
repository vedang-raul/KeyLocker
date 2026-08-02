import boto3
import os
from fastapi import HTTPException
from itsdangerous import URLSafeTimedSerializer

from schemas.users import UserReg

def get_ses_client():
    """Create the SES client only when an email operation is requested.

    Keeping this out of module import lets health checks and the API service
    start even when email configuration is temporarily unavailable.
    """
    region = os.getenv("AWS_REGION")
    access_key = os.getenv("AWS_ACCESS_KEY")
    secret_key = os.getenv("AWS_SECRET_KEY")

    if not region or not access_key or not secret_key:
        raise RuntimeError("Email service is not configured")

    return boto3.client(
        "ses",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


async def send_test(email_content: UserReg):
    try:
        response = get_ses_client().send_email(
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
        response = get_ses_client().verify_email_address(
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