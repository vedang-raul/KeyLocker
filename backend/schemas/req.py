from pydantic import BaseModel,ConfigDict

class ReqReg(BaseModel):
    api_name : str
    requestee_id: int
    status : str = "Pending"

class ReqResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    request_id : int
    requestee_id : int
    api_name : str
    status : str