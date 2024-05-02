from pydantic import BaseModel

class User(BaseModel):
    fullname: str
    email: str
    gender: str
    hashed_password: str
    incomeRange: float
    car: bool
    bike: bool
    threeWheeler: bool
    none: bool
    loanAmount: float

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
    loanAmount: float