import datetime

from pydantic import BaseModel

class Record(BaseModel):
    type: str
    amount: float
    account: str
    category: str
    date: datetime.date
    time: str