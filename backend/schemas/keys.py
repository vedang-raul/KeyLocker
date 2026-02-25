from pydantic import BaseModel,ConfigDict

class KeyReg(BaseModel):
    api_key : str
    api_name : str
    owner_id: int

class Keyresponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key_id : int
    owner_id : int
    api_key : str
    api_name : str 