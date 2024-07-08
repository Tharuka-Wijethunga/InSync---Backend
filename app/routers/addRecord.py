from bson import ObjectId
from bson.errors import InvalidId
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
async def get_records(userID: str = Depends(get_current_userID)):
    pipeline = getRecordsByUserID(userID)
    response = await run_aggregation(pipeline, recordsCollection)
    if response:
        # Convert ObjectId to string for each record
        for record in response:
            record['_id'] = str(record['_id'])
        return response
    raise HTTPException(404, "No records found for the user")


@router.delete("/{record_id}")
async def delete_record_endpoint(record_id: str, userID: str = Depends(get_current_userID)):
    try:
        # Try to delete using the string ID first
        result = await recordsCollection.delete_one({"id": record_id, "userID": userID})

        # If no document was deleted, try with ObjectId
        if result.deleted_count == 0:
            try:
                object_id = ObjectId(record_id)
                result = await recordsCollection.delete_one({"_id": object_id, "userID": userID})
            except:
                # If conversion to ObjectId fails, it's definitely not found
                raise HTTPException(status_code=404,
                                    detail="Record not found or you don't have permission to delete it")

        if result.deleted_count == 1:
            return {"success": True, "message": "Record deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Record not found or you don't have permission to delete it")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
