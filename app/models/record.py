from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Record(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    type: str
    amount: float
    account: str
    category: str
    date: datetime.date
    time: datetime.time