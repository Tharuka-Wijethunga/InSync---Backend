import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends
from app.pydantic_models.account import Account
from app.pydantic_models.account import UpdateBalance
from app.pydantic_models.account import UpdateBalanceManually
from .userAuthentication.security import get_current_userID, get_current_user
from ..database.aggregations import today_spending, getAccountsByUserID
from datetime import datetime, timedelta
from ..pydantic_models.inputData import PredictionResponse, InputData
from app.database.database import (
    fetch_balance,
    create_account,
    run_aggregation,
    update_balance,
    get_user_by_id, recordsCollection
)
from ..pydantic_models.userModel import User

router = APIRouter()

# Load the model and scaler
# model = joblib.load("models/expense_forecasting_model.pkl")
# scaler = joblib.load("models/scaler.pkl")

@router.get("/account", response_model=float)
async def get_balance(type: str, userID: str=Depends(get_current_userID)):
    response = await fetch_balance(type, userID)
    if response:
        return response
    raise HTTPException(404, f"There is no account type {type}")


@router.post("/account", response_model=Account)
async def post_account(account: Account):
    response = await create_account(account.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@router.get("/today_spending", response_model=float)
async def get_today_spending(userID: str=Depends(get_current_userID)):
    now = datetime.now()
    start = now.date()
    end = start + timedelta(days=1)

    # Convert date to string because we store date and time separately, and therefore we have to match the date field correctly
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    pipeline = today_spending(start, end, userID)
    response = await run_aggregation(pipeline, recordsCollection)
    if response:
        return response[0]['spends'] if response else 0
    raise HTTPException(404, "No expense records found for today")


@router.put("/account/{account}", response_model=Account)
async def put_account(account: str, update: UpdateBalance, userID: str = Depends(get_current_userID)):
    # Fetch the current balance from the database
    balance = await fetch_balance(account, userID)

    if balance is None:
        raise HTTPException(404, f"There is no account type {account} for user {userID}")

    if update.type == 'expense':
        balance -= update.amount
    else:
        balance += update.amount

    # Save the updated balance back to the database
    await update_balance(account, balance, userID)

    return {"userID": userID, "type": account, "balance": balance}


@router.put("/account/{account}/manual", response_model=Account)
async def put_account_manual(account: str, update: UpdateBalanceManually, userID: str = Depends(get_current_userID)):
    balance = await fetch_balance(account, userID)

    if balance is None:
        raise HTTPException(404, f"There is no account type {account} for user {userID}")

    balance = update.balance

    await update_balance(account, balance, userID)
    return {"userID": userID, "type": account, "balance": balance}


# @router.get("/predict", response_model=PredictionResponse)
# async def predict_expense(data: List[InputData]):
#     try:
#         input_data = [item.dict() for item in data]
#         predictions = make_prediction(input_data)
#         return [{"Monthly_Total_Expense": pred} for pred in predictions]
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.post("/predict")
# async def predict_expense(current_user: User = Depends(get_current_user)):
#     user_data = current_user
#
#     if not user_data:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     print(user_data)
#
#     # Prepare the data for prediction
#     user_df = pd.DataFrame([{
#         'Age': 23,
#         'Monthly Total Income': user_data.incomeRange,
#         'Gender_Female': 1 if user_data.gender == 'Female' else 0,
#         'Gender_Male': 1 if user_data.gender == 'Male' else 0,
#         'Occupation_Employee': False,
#         'Occupation_Part-timer': False,
#         'Occupation_Student': True,
#         'Vehicle you own_Bike': 1 if user_data.bike == True else 0,
#         'Vehicle you own_Bike, Car': 1 if (user_data.bike == True & user_data.car == True ) else 0,
#         'Vehicle you own_Bike, Three-wheeler': 1 if (user_data.bike == True & user_data.threeWheeler == True ) else 0,
#         'Vehicle you own_Car/Van': 1 if user_data.car == True else 0
#     }])
#
#     # Ensure the feature names match the training phase
#     expected_columns = [
#         'Age', 'Monthly Total Income', 'Gender_Female', 'Gender_Male',
#         'Occupation_Employee', 'Occupation_Part-timer', 'Occupation_Student',
#         'Vehicle you own_Bike', 'Vehicle you own_Bike, Car',
#         'Vehicle you own_Bike, Three-wheeler', 'Vehicle you own_Car/Van'
#     ]
#
#     user_df = user_df.reindex(columns=expected_columns, fill_value=0)
#     # Scale the features
#     user_scaled = scaler.transform(user_df)
#     # Make predictions
#     predictions = model.predict(user_scaled)
#
#     return {"predicted_expense": predictions[0]}


# @router.post("/train")
# async def train_model_endpoint():
#     try:
#         global model, scaler
#         model, scaler = await train_model()
#         return {"message": "Model retrained successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))