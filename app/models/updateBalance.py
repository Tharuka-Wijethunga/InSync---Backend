from pydantic import BaseModel


class UpdateBalance(BaseModel):
    amount: float
    type: str
