from pydantic import BaseModel

class InputData(BaseModel):
    Age: int
    Monthly_Total_Income: float
    Gender_Female: bool
    Gender_Male: bool
    Occupation_Employee: bool
    Occupation_Part_timer: bool
    Occupation_Student: bool
    Vehicle_you_own_Bike: bool
    Vehicle_you_own_Bike_Car: bool
    Vehicle_you_own_Bike_Three_wheeler: bool
    Vehicle_you_own_Car_Van: bool

class PredictionResponse(BaseModel):
    Monthly_Total_Expense: float