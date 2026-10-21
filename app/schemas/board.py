from pydantic import BaseModel, ConfigDict

class ReadRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idx: int
    title: str
    contents: str
    image_url: str | None = None

class RegisterReq(BaseModel):
    title: str
    contents: str
    image_url: str | None = None

class RegisterRes(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    idx: int
    title: str
    contents: str
    image_url: str | None = None
