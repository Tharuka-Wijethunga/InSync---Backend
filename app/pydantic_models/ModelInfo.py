from pydantic import BaseModel
from datetime import datetime

class ModelInfo(BaseModel):
    userID: str
    category: str
    model_path: str
    last_trained_date: datetime