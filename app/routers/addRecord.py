from fastapi import APIRouter, HTTPException
from app.models.record import Record
from app.database.database import (
    create_record,
    fetch_record,
    fetch_all_records
)

router = APIRouter()


@router.post("", response_model=Record)
async def post_record(record: Record):
    response = await create_record(record.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@router.get("/{id}", response_model=Record)
async def get_record_id(id: str):
    response = await fetch_record(id)
    if response:
        return response
    raise HTTPException(404, "There is no record as this id")


@router.get("")
async def get_records():
    response = await fetch_all_records()
    return response
