from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import sumOfAllExpenses, getGroupCategorySum, DailyRecordsGroupByCategory
from app.database.database import run_aggregation, get_model_info, create_model_info, update_model_info
from datetime import datetime, timedelta
from app.pydantic_models.ModelInfo import ModelInfo
from app.routers.userAuthentication.security import get_current_userID

# import pandas as pd
# from prophet import Prophet
# from joblib import dump, load


router = APIRouter()
@router.get("/thisMonthTotal")
async def getThisMonthTotal(userID: str=Depends(get_current_userID)):
    currentMonth = datetime.now().strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/thisMonthStat")
async def getThisMonthStat(userID: str=Depends(get_current_userID)):
    currentMonth = datetime.now().strftime("-%m-")

#get the totalAmount
    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline)
    if response:
        totalAmount = response[0]['totalAmount']


#rearange each category as this format {'value': 19.15, 'category': 'Rent', 'sum': 5000.0}
    pipeline = getGroupCategorySum(userID,currentMonth)
    response = await run_aggregation(pipeline)
    if response:
        for item in response:
            item['value'] = round((item['sum'] / totalAmount) * 100, 2)

    if response:
        return response
    raise HTTPException(404, "Wallet's quiet this month. Let's fill it up!")

@router.get("/previousMonthTotal")
async def getPreviousMonthTotal(userID: str=Depends(get_current_userID)):
# Get the previous month
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/previousMonthStat")
async def getPreviousMonthStat(userID: str=Depends(get_current_userID)):
# Get the previous month
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")

#get the totalAmount
    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline)
    if response:
        totalAmount = response[0]['totalAmount']

#rearange each category as this format {'value': 19.15, 'category': 'Rent', 'sum': 5000.0}
    pipeline = getGroupCategorySum(userID,previousMonth)
    response = await run_aggregation(pipeline)
    if response:
        for item in response:
            item['value'] = round((item['sum'] / totalAmount) * 100, 2)

    if response:
        return response
    raise HTTPException(404, "Looks like your wallet was quiet last month!")

# async def trainModel(userID: str) -> Prophet:
#     pipeline = DailyRecordsGroupByCategory(userID)
#     response = await run_aggregation(pipeline)
#     if response:
#         df = pd.DataFrame(response)
#         df = df.pivot(index='Date', columns='Category', values='Amount').reset_index().fillna(0)
#         columns = ['Income', 'Foods & Drinks', 'Shopping', 'Public transport', 'Vehicle', 'Health', 'Bills', 'Loans',
#                    'Rent', 'Other']
#         for col in columns:
#             if col not in df.columns:
#                 df[col] = 0.0
#         df = df[['Date'] + columns]
#         df['Date'] = pd.to_datetime(df['Date'])
#
#         # Prepare DataFrame for Prophet
#         df = df[['Date', 'Foods & Drinks']]
#         df.columns = ['ds', 'y']
#         df['ds'] = pd.to_datetime(df['ds'])
#         if len(df.dropna()) < 2:
#             print("Not enough data to train the model.")
#             return None
#         model = Prophet()
#         model.fit(df)
#
#         # Saving the model file in directory
#         model_path = f"app/saveFiles/{userID}_model.pkl"
#         dump(model, model_path)
#
#         # Create or update the model info in the database
#         model_info = ModelInfo(userID=userID, model_path=model_path, last_trained_day=datetime.now())
#         existing_model_info = await get_model_info(userID)
#         if existing_model_info is None:
#             await create_model_info(model_info)
#         else:
#             await update_model_info(userID, model_info)
#
#         return model
#
# @router.get("/ForecastNextDay")
# async def forecast_next_day(userID: str=Depends(get_current_userID)):
#     current_date = datetime.now()
#     model_info = await get_model_info(userID)
#     if model_info is None or model_info['last_trained_day'].month != current_date.month:
#         print("Retraining model...")
#         model = await trainModel(userID)
#     else:
#         print("Using saved model...")
#         model = load(model_info['model_path'])
#
#     if model:
#         # Make future dataframe
#         future = model.make_future_dataframe(periods=10)  # Predict next day
#
#         # Forecast
#         forecast = model.predict(future)
#
#         # Return the forecast
#         return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(1).to_dict(orient='records')