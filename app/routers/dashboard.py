from fastapi import APIRouter, HTTPException, Depends
from app.pydantic_models.account import Account
from app.pydantic_models.account import UpdateBalance
from app.pydantic_models.account import UpdateBalanceManually
from .userAuthentication.security import get_current_userID
from ..database.aggregations import today_spending
from datetime import datetime, timedelta
from app.database.database import (
    fetch_balance,
    create_account,
    run_aggregation,
    update_balance,
    recordsCollection
)

router = APIRouter()

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

