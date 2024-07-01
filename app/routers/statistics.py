from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import sumOfAllExpenses, getGroupCategorySum, DailyRecordsGroupByCategory, \
    GetAllUsersInfo, AllUsersDailyRecordsGroupByCategory
from app.database.database import run_aggregation, get_model_info, create_model_info, update_model_info, \
    run_aggregation_for_users, get_general_model_info, create_general_model_info, update_general_model_info
from datetime import datetime, timedelta

from app.pydantic_models.GeneralModelInfo import GeneralModelInfo
from app.pydantic_models.ModelInfo import ModelInfo
from app.routers.userAuthentication.security import get_current_userID

import pandas as pd
from prophet import Prophet
from joblib import dump, load
from sklearn.preprocessing import LabelEncoder


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

async def trainModel(userID: str) -> Prophet:
    pipeline = DailyRecordsGroupByCategory(userID)
    response = await run_aggregation(pipeline)
    if response:
        df = pd.DataFrame(response)
        df = df.pivot(index='Date', columns='Category', values='Amount').reset_index().fillna(0)
        columns = ['Income', 'Foods & Drinks', 'Shopping', 'Public transport', 'Vehicle', 'Health', 'Bills', 'Loans',
                   'Rent', 'Other']
        for col in columns:
            if col not in df.columns:
                df[col] = 0.0
        df = df[['Date'] + columns]
        df['Date'] = pd.to_datetime(df['Date'])

        # Prepare DataFrame for Prophet
        df = df[['Date', 'Foods & Drinks']]
        df.columns = ['ds', 'y']
        df['ds'] = pd.to_datetime(df['ds'])
        if len(df.dropna()) < 2:
            print("Not enough data to train the model.")
            return None
        model = Prophet()
        model.fit(df)

        # Saving the model file in directory
        model_path = f"app/saveFiles/{userID}_model.pkl"
        dump(model, model_path)

        # Create or update the model info in the database
        model_info = ModelInfo(userID=userID, model_path=model_path, last_trained_day=datetime.now())
        existing_model_info = await get_model_info(userID)
        if existing_model_info is None:
            await create_model_info(model_info)
        else:
            await update_model_info(userID, model_info)

        return model

@router.get("/ForecastNextDay")
async def forecast_next_day(userID: str=Depends(get_current_userID)):
    current_date = datetime.now()
    model_info = await get_model_info(userID)
    if model_info is None or model_info['last_trained_day'].month != current_date.month:
        print("Retraining model...")
        model = await trainModel(userID)
    else:
        print("Using saved model...")
        model = load(model_info['model_path'])

    if model:
        # Make future dataframe
        future = model.make_future_dataframe(periods=10)  # Predict next day

        # Forecast
        forecast = model.predict(future)

        # Return the forecast
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(1).to_dict(orient='records')


async def trainGeneralModel() -> Prophet:
    recordPipeline = AllUsersDailyRecordsGroupByCategory()
    response = await run_aggregation(recordPipeline)
    if response:
        # Convert the response to a DataFrame
        record_df = pd.DataFrame(response)

        # Pivot the DataFrame to include userID, Date, and Category
        df_pivot = record_df.pivot_table(index=['userID', 'Date'], columns='Category', values='Amount', fill_value=0).reset_index()

        # Define the columns to ensure they are present in the DataFrame
        columns = ['Income', 'Foods & Drinks', 'Shopping', 'Public transport', 'Vehicle', 'Health', 'Bills', 'Loans', 'Rent', 'Other']

        # Add missing columns with 0.0 as default value
        for col in columns:
            if col not in df_pivot.columns:
                df_pivot[col] = 0.0

        # Ensure the final DataFrame has the desired order of columns
        record_df = df_pivot[['userID', 'Date'] + columns]

        # Convert Date to datetime format
        record_df['Date'] = pd.to_datetime(record_df['Date'])

    userPipeline = GetAllUsersInfo()
    response = await run_aggregation_for_users(userPipeline)
    if response:
        user_df = pd.DataFrame(response)

        # Transform gender column to Male and Female
        user_df['Male'] = (user_df['gender'] == 'Male').astype(int)
        user_df['Female'] = (user_df['gender'] == 'Female').astype(int)

        # Transform boolean columns to 1 and 0
        user_df['Car'] = user_df['car'].astype(int)
        user_df['Bike'] = user_df['bike'].astype(int)
        user_df['ThreeWheeler'] = user_df['threeWheeler'].astype(int)
        user_df['None'] = user_df['none'].astype(int)

        # Transform occupation column to separate columns
        user_df['Student'] = (user_df['occupation'] == 'Student').astype(int)
        user_df['Employee (Full Time)'] = (user_df['occupation'] == 'Employee (Full Time)').astype(int)
        user_df['Employee (Part Time)'] = (user_df['occupation'] == 'Employee (Part Time)').astype(int)

        # Drop the original boolean and gender columns
        user_df = user_df.drop(columns=['gender', 'car', 'bike', 'threeWheeler', 'none', 'occupation'])

        # Reorder the columns
        user_df = user_df[['userID', 'Male', 'Female', 'incomeRange', 'Car', 'Bike', 'ThreeWheeler', 'None', 'Student', 'Employee (Full Time)', 'Employee (Part Time)']]

        # Merge the DataFrames on userID with an inner join
        combined_df = pd.merge(record_df, user_df, on='userID', how='inner')

        # Save the new data to newData.csv
        new_data_path = 'app/generalModel/csvFiles/newData.csv'
        combined_df.to_csv(new_data_path, index=False)

        # Load the existing generalData.csv
        general_data_path = 'app/generalModel/csvFiles/generalData.csv'
        general_df = pd.read_csv(general_data_path)

        # Convert Date columns to string to avoid timestamps
        combined_df['Date'] = combined_df['Date'].dt.strftime('%Y-%m-%d')
        general_df['Date'] = pd.to_datetime(general_df['Date']).dt.strftime('%Y-%m-%d')

        # Append the new data to the general data
        combined_general_df = pd.concat([general_df, combined_df], ignore_index=True)

        # Save the combined data to a new file
        combined_data_path = 'app/generalModel/csvFiles/combinedData.csv'
        combined_general_df.to_csv(combined_data_path, index=False)





    df = pd.read_csv('app/generalModel/csvFiles/combinedData.csv')

    # Convert UserID to numerical using LabelEncoder
    label_encoder = LabelEncoder()
    df['userID'] = label_encoder.fit_transform(df['userID'])

    # Create a dictionary to map encoded values to userIDs
    label_mapping = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))

    # Print the mapping of userID to encoded values
    print("UserID to Encoded Values Mapping:")
    for user_id, encoded_value in label_mapping.items():
        print(f"{user_id}: {encoded_value}")

    # Prepare DataFrame for Prophet
    df = df[['Date', 'Foods & Drinks', 'userID', 'Male', 'Female', 'incomeRange', 'Car', 'Bike', 'ThreeWheeler', 'None',
             'Student', 'Employee (Full Time)', 'Employee (Part Time)']]
    df.columns = ['ds', 'y', 'userID', 'Male', 'Female', 'incomeRange', 'Car', 'Bike', 'ThreeWheeler', 'None',
                  'Student', 'Employee (Full Time)', 'Employee (Part Time)']
    df['ds'] = pd.to_datetime(df['ds'])

    model = Prophet()
    model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    model.add_regressor('userID')
    model.add_regressor('Male')
    model.add_regressor('Female')
    model.add_regressor('incomeRange')
    model.add_regressor('Car')
    model.add_regressor('Bike')
    model.add_regressor('ThreeWheeler')
    model.add_regressor('None')
    model.add_regressor('Student')
    model.add_regressor('Employee (Full Time)')
    model.add_regressor('Employee (Part Time)')
    model.fit(df)

    # Saving the model file in directory
    model_path = f"app/generalModel/trainedModels/model.pkl"
    dump((model,df['cap'].iloc[0]), model_path)

    # Create or update the model info in the database
    model_info = GeneralModelInfo(modelID="general_model", model_path=model_path, last_trained_day=datetime.now())
    existing_model_info = await get_general_model_info("general_model")
    if existing_model_info is None:
        await create_general_model_info(model_info)
    else:
        await update_general_model_info("general_model", model_info)

    return model


@router.get("/ForecastNextDay_GeneralModel")
async def get_forecast_next_day():
    current_date = datetime.now()
    model_info = await get_general_model_info("general_model")
    if model_info is None or model_info['last_trained_day'].month != current_date.month:
        print("Retraining model...")
        model = await trainGeneralModel()
    else:
        print("Using saved model...")
        model = load(model_info['model_path'])

    if model:
        # Make future dataframe
        future = model.make_future_dataframe(periods=1)  # Predict next day

        future['userID'] = 2
        future['Male'] = 1
        future['Female'] = 0
        future['incomeRange'] = 25000
        future['Car'] = 1
        future['Bike'] = 0
        future['ThreeWheeler'] = 0
        future['None'] = 0
        future['Student'] = 1
        future['Employee (Full Time)'] = 0
        future['Employee (Part Time)'] = 0
        # Forecast
        forecast = model.predict(future)

        # Return the forecast
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(1).to_dict(orient='records')