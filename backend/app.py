from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import boto3
import os


load_dotenv()

app=FastAPI()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
