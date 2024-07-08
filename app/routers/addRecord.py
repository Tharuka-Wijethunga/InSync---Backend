from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Depends
from app.database.aggregations import getRecordsByUserID
from app.pydantic_models.record import Record, RecordId
from app.database.database import (
    create_record,
    fetch_record,
    run_aggregation,
    delete_record,
    recordsCollection
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


@router.get("")
async def get_records(userID: str=Depends(get_current_userID)):
    pipeline = getRecordsByUserID(userID)
    response = await run_aggregation(pipeline, recordsCollection)
    if response:
        return response
    raise HTTPException(404, "No records found for the user")


@router.get("/{id}", response_model=Record)
async def get_record_id(id: str):
    response = await fetch_record(id)
    if response:
        return response
    raise HTTPException(404, "There is no record as this id")


@router.delete("/{record_id}")
async def delete_record_by_id(record_id: str, userID: str = Depends(get_current_userID)):
    print(f"Received delete request for record_id: {record_id}")
    result = await delete_record(recordsCollection, record_id, userID)
    if result:
        return {"success": True, "message": "Record deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Record not found or you don't have permission to delete it")