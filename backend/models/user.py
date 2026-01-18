from sqlalchemy import Column, Integer, String
from db.db import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__="users"

    empID=Column(Integer,primary_key=True,index=True)

    email=Column(String,unique=True,index=True)
    hashedPassword=Column(String)
    Role=Column(String)
    
    
    request=relationship("Requests",back_populates="user")#Establishes bidirectional relationship with APIkeys model which helps to get into the APIkeys table
    apikey=relationship("APIkeys",back_populates="owner")