from pydantic import BaseModel

class Account(BaseModel):
    type: str
    balance: float