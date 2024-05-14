from fastapi import APIRouter, HTTPException
from app.database.aggregations import sumOfAllExpenses
from app.database.database import run_aggregation
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/thisMonthStat")
async def getThisMonthStat(userID: str):

    currentMonth = datetime.now().strftime("-%m-")
    print(currentMonth)

    pipeline = sumOfAllExpenses(userID,currentMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response
    raise HTTPException(404, "this month expense does not exist")

@router.get("/previousMonthStat")
async def getPreviousMonthStat(userID: str):

    # Get the previous month as a string in the "-MM-" format
    previousMonth = datetime.now().replace(day=1) - timedelta(days=1)
    previousMonth = previousMonth.strftime("-%m-")
    print(previousMonth)

    pipeline = sumOfAllExpenses(userID,previousMonth)
    response = await run_aggregation(pipeline)
    if response:
        return response
    raise HTTPException(404, "previous month expense does not exist")
