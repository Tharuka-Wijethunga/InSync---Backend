from pydantic import BaseModel

class OnboardingDataModel(BaseModel):
    incomeRange: float
    car: bool
    bike: bool
    threeWheeler: bool
    none: bool
    loanAmount: float
