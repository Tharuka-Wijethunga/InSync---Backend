from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import sumOfAllExpenses, getGroupCategorySum
from app.database.database import run_aggregation, recordsCollection
from datetime import datetime, timedelta
from app.routers.userAuthentication.security import get_current_userID

from fastapi.responses import JSONResponse
import pandas as pd

router = APIRouter()

@router.get("/thisMonthTotal")
async def get_this_month_total(userID: str=Depends(get_current_userID)):
    currentMonth = datetime.now().strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/thisMonthStat")
async def get_this_month_stat(userID: str=Depends(get_current_userID)):
    currentMonth = datetime.now().strftime("-%m-")

#get the totalAmount
    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        totalAmount = response[0]['totalAmount']


#rearange each category as this format {'value': 19.15, 'category': 'Rent', 'sum': 5000.0}
    pipeline = getGroupCategorySum(userID,currentMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        for item in response:
            item['value'] = round((item['sum'] / totalAmount) * 100, 2)

    if response:
        return response
    raise HTTPException(404, "Wallet's quiet this month. Let's fill it up!")

@router.get("/previousMonthTotal")
async def get_previous_month_total(userID: str=Depends(get_current_userID)):
# Get the previous month
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/previousMonthStat")
async def get_previous_month_stat(userID: str=Depends(get_current_userID)):
# Get the previous month
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")

#get the totalAmount
    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        totalAmount = response[0]['totalAmount']

#rearange each category as this format {'value': 19.15, 'category': 'Rent', 'sum': 5000.0}
    pipeline = getGroupCategorySum(userID,previousMonth)
    response = await run_aggregation(pipeline,recordsCollection)
    if response:
        for item in response:
            item['value'] = round((item['sum'] / totalAmount) * 100, 2)

    if response:
        return response
    raise HTTPException(404, "Looks like your wallet was quiet last month!")


def inflationData():
    url = 'https://www.cbsl.gov.lk/cbsl_custom/inflation/inflationwindow.php'
    tables = pd.read_html(url)
    tables[1] = tables[1].drop([0, 1])
    df = pd.concat([tables[0], tables[1]], ignore_index=True)

    # Find the indices where the year changes
    year_indices = df[df[0].notna() & df[0].str.isnumeric()].index

    # Create an empty dataframe to hold all the data
    all_data = pd.DataFrame()

    # Iterate over the indices
    for i in range(len(year_indices)-1):
        year = df.iloc[year_indices[i]][0]
        year_data = df.iloc[year_indices[i]+1:year_indices[i+1]].reset_index(drop=True)
        year_data['Year'] = year
        all_data = pd.concat([all_data, year_data])

    # Add the last year
    year = df.iloc[year_indices[-1]][0]
    year_data = df.iloc[year_indices[-1]+1:].reset_index(drop=True)
    year_data['Year'] = year
    all_data = pd.concat([all_data, year_data])

    # Format the date column
    all_data['Date'] = pd.to_datetime(all_data['Year'] + '-' + all_data[0] + '-1')

    # Drop the old month and year columns
    all_data.drop(columns=[0, 'Year'], inplace=True)

    # Rename the columns
    all_data.columns = ['CCPI H Inflation', 'CCPI C Inflation', 'NCPI H Inflation', 'NCPI C Inflation', 'Date']

    # Sort the dataframe by Date in descending order
    all_data = all_data.sort_values(by='Date', ascending=False).reset_index(drop=True)

    # Format the Date column to 'MMM yy'
    all_data['Date'] = all_data['Date'].dt.strftime('%b %y')

    # Reorder the columns to make 'Date' the first column
    all_data = all_data[['Date', 'CCPI H Inflation']]

    # Get the latest 12 rows and reverse the order
    yearlyDf = all_data.head(12).iloc[::-1].reset_index(drop=True)

    return yearlyDf

@router.get("/inflation")
def get_inflation_data():
    df = inflationData()
    return JSONResponse(content=df.to_dict(orient="records"))