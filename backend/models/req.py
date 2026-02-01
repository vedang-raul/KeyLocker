from sqlalchemy import Column, Integer, String,ForeignKey
from db.db import Base 
from sqlalchemy.orm import relationship

class Requests(Base):
    __tablename__="requests"


    request_id=Column(Integer,primary_key=True,index=True)
    requestee_id=Column(Integer,ForeignKey("users.emp_id",ondelete="CASCADE"))

    api_name=Column(String)
    status=Column(String,default="Pending")

    user=relationship("Users",back_populates="request", lazy="selectin") #Establishes bidirectional relationship with Users model which helps to get into the usersd table