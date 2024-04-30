from fastapi import APIRouter, HTTPException
from app.models.onboardingModel import OnboardingDataModel
from app.database.onboardingDatabase import create_onboarding_data

router = APIRouter()

@router.post("/data/", response_model=OnboardingDataModel)
async def post_income(data: OnboardingDataModel):
    response = await create_onboarding_data(data.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")
