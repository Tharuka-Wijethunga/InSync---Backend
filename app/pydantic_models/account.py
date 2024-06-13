from pydantic import BaseModel


class Account(BaseModel):
    type: str
    balance: float


class UpdateBalance(BaseModel):
    amount: float
    type: str


class UpdateBalanceManually(BaseModel):
    balance: float
