import os
from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import DailyRecordsGroupByCategory, AllUsersID
from app.database.database import run_aggregation, get_model_info, create_model_info, update_model_info, recordsCollection
from datetime import datetime, timedelta

from app.pydantic_models.ModelInfo import ModelInfo
from app.routers.userAuthentication.security import get_current_userID

import pandas as pd
from prophet import Prophet
from joblib import dump, load
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

router = APIRouter()
scheduler = AsyncIOScheduler()


@router.get("/ForecastNextDay")
async def forecast_next_day(userID: str = Depends(get_current_userID)):
    categories = ['Income', 'Foods & Drinks', 'shopping', 'Public transport', 'Vehicle', 'Health', 'Bills', 'Loans',
                  'Rent', 'Other']
    forecasts = {}
    total_amount = 0

    for category in categories:
        model_info = await get_model_info(userID, category)
        if not model_info:
            raise HTTPException(status_code=404, detail=f"No model found for category '{category}' for user '{userID}'")

        # Load the model
        model_path = model_info.model_path
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail=f"Model file '{model_path}' not found for user '{userID}'")

        model = load(model_path)

        # Make future dataframe
        # future = model.make_future_dataframe(periods=1)  # Predict next day

        # Get tomorrow's date
        tomorrow = datetime.now().date() + timedelta(days=1)
        # Create future dataframe with only tomorrow's date
        future = pd.DataFrame({'ds': [tomorrow]})

        # Forecast
        forecast = model.predict(future)

        # Get the forecasted value and date
        forecast_record = forecast[['ds', 'yhat']].tail(1).to_dict(orient='records')[0]
        forecast_record['yhat'] = max(0, forecast_record['yhat'])  # Ensure yhat is not negative

        # Apply Rent category condition
        if category == "Rent" and forecast_record['yhat'] < 1000:
            forecast_record['yhat'] = 0


        # Format the forecast record
        formatted_forecast = {
            "Date": forecast_record['ds'].strftime('%Y-%m-%d'),  # Format date as 'YYYY-MM-DD'
            "Amount": int(forecast_record['yhat'])
        }

        # Store the formatted forecast for the category
        forecasts[category] = formatted_forecast

        # Add to total amount
        total_amount += formatted_forecast['Amount']

        # Calculate 'Value' for each category
    for category in forecasts:
        forecasts[category]['Value'] = round((forecasts[category]['Amount'] / total_amount) * 100, 2)

        # Add total amount to the response
    response = {"Total": total_amount}
    response.update(forecasts)

    return response

async def trainModel(userID: str) -> None:
    pipeline = DailyRecordsGroupByCategory(userID)
    response = await run_aggregation(pipeline, recordsCollection)
    if response:
        df = pd.DataFrame(response)
        df = df.pivot(index='Date', columns='Category', values='Amount').reset_index().fillna(0)
        columns = ['Income', 'Foods & Drinks', 'shopping', 'Public transport', 'Vehicle', 'Health', 'Bills', 'Loans',
                   'Rent', 'Other']
        for col in columns:
            if col not in df.columns:
                df[col] = 0.0
        df = df[['Date'] + columns]
        df['Date'] = pd.to_datetime(df['Date'])

        print(df)

        for category in columns:
            category_df = df[['Date', category]].copy()
            category_df.columns = ['ds', 'y']
            category_df['ds'] = pd.to_datetime(category_df['ds'])

            if len(category_df.dropna()) < 2:
                print(f"{userID} Not enough data to train the model for {category}.")
                continue

            print(f"Training model for {category} for {userID}.")
            model = Prophet()
            model.fit(category_df)

            model_path = f"app/userTimeSeriesModel/{userID}_{category}_model.pkl"
            dump(model, model_path)
            print(f"Model for {category} saved as {model_path}")

            model_info = ModelInfo(
                userID=userID,
                category=category,
                model_path=model_path,
                last_trained_date=datetime.now()
            )
            existing_model_info = await get_model_info(userID, category)
            if existing_model_info is None:
                await create_model_info(model_info)
            else:
                await update_model_info(userID, category, model_info)

async def trainModelsForAllUsers():
    pipeline = AllUsersID()
    response = await run_aggregation(pipeline, recordsCollection)

    if response:
        for user in response:
            userID = user.get("userID")
            if userID:
                await trainModel(userID)

@router.on_event("startup")
async def startup_event():
    scheduler.start()
    scheduler.add_job(trainModelsForAllUsers, CronTrigger(hour=0, minute=10))


