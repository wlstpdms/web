from pydantic import BaseModel, ConfigDict

class ReadRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idx: int
    title: str
    contents: str

class RegisterReq(BaseModel):
    title: str
    contents: str

class RegisterRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idx: int
    title: str
    contents: str
