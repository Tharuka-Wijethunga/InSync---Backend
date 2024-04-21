from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    gender: str
    hashed_password: str

class TokenRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    username: str
    email: str
    gender: str
    password: str