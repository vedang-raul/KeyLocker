from sqlalchemy import Column, Integer, String,Boolean
from db.db import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__="users"

    emp_id=Column(Integer,primary_key=True,index=True)

    name=Column(String)
    email=Column(String,unique=True,index=True)
    password=Column(String)
    role=Column(String)
    is_verified=Column(Boolean,default=False)
    
    
    request=relationship("Requests",back_populates="user", lazy="selectin")#Establishes bidirectional relationship with APIkeys model which helps to get into the APIkeys table
    apikey=relationship("APIkeys",back_populates="owner", lazy="selectin")