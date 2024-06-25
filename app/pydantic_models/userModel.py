from typing import Optional
from pydantic import BaseModel, BeforeValidator,Field
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    fullname: str
    email: str
    gender: str
    hashed_password: str
    incomeRange: float
    car: bool
    bike: bool
    threeWheeler: bool
    none: bool
    occupation: str

class TokenRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    fullname: str
    email: str
    gender: str
    password: str
    incomeRange: float
    car: bool
    bike: bool
    threeWheeler: bool
    none: bool
    occupation: str


class FullUpdateRequest(BaseModel):
    fullname: Optional[str]
    new_email: Optional[str]
    new_password: Optional[str]
    confirm_password: Optional[str]




