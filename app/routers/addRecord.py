from fastapi import APIRouter, HTTPException
from app.models.record import Record

router = APIRouter()

from app.database.database import (
    create_record
)

@router.post("",response_model=Record)
async def post_record(record:Record):
    response = await create_record(record.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")