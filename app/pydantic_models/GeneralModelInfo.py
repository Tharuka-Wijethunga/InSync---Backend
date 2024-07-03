from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Define your Pydantic model for ModelInfo
class GeneralModelInfo(BaseModel):
    modelID: str
    model_path: str
    last_trained_day: Optional[datetime]