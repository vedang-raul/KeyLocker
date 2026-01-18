from sqlalchemy import Column, Integer, String,ForeignKey
from db.db import Base 
from sqlalchemy.orm import relationship

class Requests(Base):
    __tablename__="requests"


    RequestID=Column(Integer,primary_key=True,index=True)
    requesteeID=Column(Integer,ForeignKey("users.empID",ondelete="CASCADE"))

    Status=Column(String,default="Active")
    APIname=Column(String)

    user=relationship("Users",back_populates="request") #Establishes bidirectional relationship with Users model which helps to get into the usersd table