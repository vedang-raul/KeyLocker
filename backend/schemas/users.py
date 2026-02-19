from pydantic import BaseModel,EmailStr,ConfigDict
from typing import Optional 

class UserReg(BaseModel):
    name : str
    email : EmailStr
    password : str
    role : str ="User"

class UserLogin(BaseModel):
    email : EmailStr
    password : str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    emp_id : int
    email : EmailStr
    role : str