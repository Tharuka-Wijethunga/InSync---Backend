from fastapi import APIRouter, HTTPException
from app.database.aggregations import sumOfAllExpenses,getGroupCategorySum
from app.database.database import run_aggregation
from datetime import datetime, timedelta

router = APIRouter()
@router.get("/thisMonthTotal")
async def getThisMonthTotal(userID: str):
    currentMonth = datetime.now().strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/thisMonthStat")
async def getThisMonthStat(userID: str):
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
    raise HTTPException(404, "this month expense does not exist")



@router.get("/previousMonthTotal")
async def getPreviousMonthTotal(userID: str):
# Get the previous month
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")
    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response[0]['totalAmount']
    raise HTTPException(404, "this month total does not exist")

@router.get("/previousMonthStat")
async def getPreviousMonthStat(userID: str):
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
    raise HTTPException(404, "this month expense does not exist")

