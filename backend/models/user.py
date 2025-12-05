from sqlalchemy import Column, Integer, String
from db import Base

class Users(Base):
    __tablename__="users"

    id=Column(Integer,primarry_key=True,index=True)
    email=Column(String,unique=True,index=True)

    