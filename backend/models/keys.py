from sqlalchemy import Column, Integer, String,ForeignKey
from db.db import Base 
from sqlalchemy.orm import relationship

class APIkeys(Base):
    __tablename__="apikeys"

    KeyID=Column(Integer,primary_key=True,index=True)

    ownerID=Column(Integer,ForeignKey("users.empID",ondelete="CASCADE"))

    EncryptedKey=Column(String,unique=True,index=True)
    APIName=Column(String)

    owner=relationship("Users",back_populates="apikey")

   