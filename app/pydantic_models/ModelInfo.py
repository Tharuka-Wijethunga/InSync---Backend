from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelInfo(BaseModel):
    userID: str
    model_path: str
    last_trained_day: Optional[datetime]


