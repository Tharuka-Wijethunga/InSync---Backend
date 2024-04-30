from fastapi import APIRouter, HTTPException
from app.models.account import Account
from app.models.updateBalance import UpdateBalance
from ..database.aggregations import today_spending

from app.database.database import (
    fetch_balance,
    create_account,
    run_aggregation,
    update_balance
)

router = APIRouter()

@router.get("/account", response_model=float)
async def get_balance(type):
    response = await fetch_balance(type)
    if response:
        return response
    raise HTTPException(404, "There is no account type {type}")


@router.post("/account", response_model=Account)
async def post_account(account: Account):
    response = await create_account(account.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@router.get("/today_spending", response_model=float)
async def get_today_spending():
    response = await run_aggregation(today_spending)
    if response:
        return response[0]['spends']
    raise HTTPException(404, "No expense records found for today")


@router.put("/account/{account}", response_model=Account)
async def put_account(account: str, update: UpdateBalance):
    # Fetch the current balance from the database
    balance = await fetch_balance(account)

    if balance is None:
        raise HTTPException(404, f"There is no account type {account}")

    # Update the balance based on the type of the record
    if update.type == 'expense':
        balance -= update.amount
    else:  # assuming the only other type is 'income'
        balance += update.amount

    # Save the updated balance back to the database
    await update_balance(account, balance)

    return {"type": account, "balance": balance}
