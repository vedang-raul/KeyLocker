from sqlalchemy import Column, Integer, String,ForeignKey
from db.db import Base 
from sqlalchemy.orm import relationship

class APIkeys(Base):
    __tablename__="apikeys"

    key_id=Column(Integer,primary_key=True,index=True)

    owner_id=Column(Integer,ForeignKey("users.emp_id",ondelete="CASCADE"))

    encrypted_key=Column(String,unique=True,index=True)
    api_name=Column(String)

    owner=relationship("Users",back_populates="apikey", lazy="selectin")

   