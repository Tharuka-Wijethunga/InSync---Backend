from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import getRecordsByUserID
from app.pydantic_models.record import Record
from app.database.database import (
    create_record,
    fetch_record,
    run_aggregation, recordsCollection
)
from app.routers.userAuthentication.security import get_current_userID

router = APIRouter()


@router.post("", response_model=Record)
async def post_record(record: Record, userID: str = Depends(get_current_userID)):
    # Add userID to the record dictionary
    record_dict = record.dict()
    record_dict['userID'] = userID
    response = await create_record(record_dict)
    if response:
        return response
    raise HTTPException(400, "Something went wrong")


@router.get("/{id}", response_model=Record)
async def get_record_id(id: str):
    response = await fetch_record(id)
    if response:
        return response
    raise HTTPException(404, "There is no record as this id")


# @router.get("/records")
# async def get_records():
#     response = await fetch_all_records()
#     return response

@router.get("")
async def get_records(userID: str=Depends(get_current_userID)):
    pipeline = getRecordsByUserID(userID)
    response = await run_aggregation(pipeline, recordsCollection)
    if response:
        return response
    raise HTTPException(404, "No records found for the user")