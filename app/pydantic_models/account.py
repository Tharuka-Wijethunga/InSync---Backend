from pydantic import BaseModel


class Account(BaseModel):
    userID: str
    type: str
    balance: float


class UpdateBalance(BaseModel):
    amount: float
    type: str


class UpdateBalanceManually(BaseModel):
    balance: float
