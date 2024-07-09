import motor.motor_asyncio
import pandas as pd
from typing import Optional

from ..pydantic_models.GeneralModelInfo import GeneralModelInfo

from .aggregations import getAccountsByUserID
from ..pydantic_models.record import ObjectId
from passlib.context import CryptContext
from app.pydantic_models.userModel import User
from app.pydantic_models.ModelInfo import ModelInfo
from datetime import datetime, timedelta

client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://tharuka0621:kE3DcROsCHMH8cqH@insync.7taaiij.mongodb.net/')
database = client.InSync
recordsCollection = database.Records
accountCollection = database.Accounts
userCollection = database.Users
emailVerificationsCollection = database.EmailVerifications
generalModelCollection= database.GeneralModel
timeSeriesModelCollection= database.TimeSeriesModel


# DashBoard & Add Records -------------------------------------------------------------------------------------<Tharuka>
async def fetch_balance(account: str, userID: str):
    pipeline = getAccountsByUserID(userID)
    result = await run_aggregation(pipeline, accountCollection)
    for account_data in result:
        if account_data['type'] == account:
            return account_data['balance']
    return None

async def create_account(user_id):
    document = {"userID":user_id, "type":"bank", "balance": 0}
    result = await accountCollection.insert_one(document)

    document = {"userID": user_id, "type": "cash", "balance": 0}
    result = await accountCollection.insert_one(document)
    return {"Two Accounts are Successfully Created"}


async def create_record(record):
    document = record
    result = await recordsCollection.insert_one(document)
    return document


async def fetch_record(id):
    document = await recordsCollection.find_one({"_id": ObjectId(id)})
    # Handle missing 'date' and 'time' fields
    document.setdefault('date', None)
    document.setdefault('time', None)

    return document


# async def fetch_all_records():
#     records = []
#     cursor = recordsCollection.find({})
#     async for document in cursor:
#         # Handle missing 'date' and 'time' fields
#         document.setdefault('date', None)
#         document.setdefault('time', None)
#
#         records.append((Record(**document)))
#     return records


async def run_aggregation(pipeline: list[dict], collection):
    result = await collection.aggregate(pipeline).to_list(None)
    return result

async def update_balance(account_type, new_balance, user_id):
    await accountCollection.update_one(
        {'type': account_type, 'userID': user_id},
        {'$set': {'balance': new_balance}}
    )

async def get_user_by_id(id: str):
    return await userCollection.find_one({"id": id})

# userDatabase(login,signup,token)-------------------------------------------------------------------------------<lihaj>

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(email: str):
    return await userCollection.find_one({"email": email})

async def create_user(fullname: str, email: str, gender: str, password: str, incomeRange: float, car: bool, bike: bool,
                      threeWheeler: bool, none: bool, occupation: str):
    hashed_password = pwd_context.hash(password)
    user = {"fullname": fullname, "email": email, "gender": gender, "hashed_password": hashed_password,
            "incomeRange": incomeRange, "car": car, "bike": bike, "threeWheeler": threeWheeler, "none": none,
            "occupation": occupation}
    result = await userCollection.insert_one(user)

    #Account creation
    user_id=str(result.inserted_id)
    await create_account(user_id)

    return User(**user, id=str(result.inserted_id))

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return User(**user)


# Email Verification --------------------------------------------------------------------------------------------<lihaj>
async def verify_user_email(email: str):
    await emailVerificationsCollection.insert_one({"email": email,"verified": True})
async def get_user_verify_info(email: str):
    return await emailVerificationsCollection.find_one({"email": email})
async def delete_user_verify_info(email: str):
    await emailVerificationsCollection.delete_one({"email": email})



#Time Series Model---------------------------------------------------------------------------------------------<Lihaj>

async def get_model_info(userID: str, category: str) -> Optional[ModelInfo]:
    result = await timeSeriesModelCollection.find_one({"userID": userID, "category": category})
    if result:
        return ModelInfo(**result)
    return None

async def create_model_info(model_info: ModelInfo) -> None:
    await timeSeriesModelCollection.insert_one(model_info.dict())

async def update_model_info(userID: str, category: str, model_info: ModelInfo) -> None:
    await timeSeriesModelCollection.update_one(
        {"userID": userID, "category": category},
        {"$set": model_info.dict()}
    )

# General Time Series Model---------------------------------------------------------------------------------------<Lihaj>
async def create_general_model_info(model_info: GeneralModelInfo):
    document = model_info.dict()
    result = await generalModelCollection.insert_one(document)
    return document

async def get_general_model_info(modelID: str):
    return await generalModelCollection.find_one({"modelID": modelID})

async def update_general_model_info(modelID: str, model_info: GeneralModelInfo):
    await generalModelCollection.update_one(
        {'modelID': modelID},
        {'$set': model_info.dict()}
    )

# User Profile -------------------------------------------------------------------------------------------------<Panchu>
async def update_user_details(email: str, fullname: str):
    result = await userCollection.update_one(
        {'email': email},
        {'$set': {'fullname': fullname}}
    )
    if result.matched_count == 0:
        return None
    return await get_user(email)


async def update_user_email(email: str, new_email: str):
    result = await userCollection.update_one(
        {'email': email},
        {'$set': {'email': new_email}}
    )
    if result.matched_count == 0:
        return None
    return await get_user(new_email)


async def update_user_password(email: str, new_password: str):
    hashed_password = pwd_context.hash(new_password)
    result = await userCollection.update_one(
        {'email': email},
        {'$set': {'hashed_password': hashed_password}}
    )
    if result.matched_count == 0:
        return None
    return await get_user(email)


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def delete_user_account(email: str):
    user = await get_user(email)
    if not user:
        return False

    await userCollection.delete_one({"email": email})
    await accountCollection.delete_many({"userID": str(user["_id"])})
    await recordsCollection.delete_many({"userID": str(user["_id"])})

    return True

# Reset password  -------------------------------------------------------------------------------------------------<Panchu>


async def get_user_by_email(email: str):
    user = await userCollection.find_one({"email": email})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
    return user


async def save_verification_code(user_id: str, code: int):
    expiration_time = datetime.utcnow() + timedelta(minutes=10)
    await userCollection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password_reset_code': code, 'password_reset_expiration': expiration_time}}
    )

async def verify_user_code(user_id: str, code: int):
    user = await userCollection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False
    if user.get('password_reset_code') != code:
        return False
    if user.get('password_reset_expiration') < datetime.utcnow():
        return False
    return True

def hash_password(password: str):
    return pwd_context.hash(password)

async def update_user_pass(user_id: str, new_password: str):
    try:
        hashed_password = hash_password(new_password)
        result = await userCollection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'hashed_password': hashed_password}}
        )
        if result.modified_count == 0:
            return None
        return await get_user_by_id(user_id)
    except Exception as e:
        print(f"An error occurred during password update: {e}")
        return None

async def get_user_by_idd(user_id: str):
    user = await userCollection.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
    return user

