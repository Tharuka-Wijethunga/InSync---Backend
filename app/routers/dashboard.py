from fastapi import APIRouter,HTTPException
from app.models.account import Account

router = APIRouter()

from app.database.database import (
    fetch_balance,
    create_account
)

@router.get("/account",response_model=float)
async def get_balance(type):
    response = await fetch_balance(type)
    if response:
        return response
    raise HTTPException(404, "There is no account type {type}")

@router.post("/account",response_model=Account)
async def post_account(account:Account):
    response = await create_account(account.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")