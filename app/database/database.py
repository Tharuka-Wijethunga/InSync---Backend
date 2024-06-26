import motor.motor_asyncio
import pandas as pd
from ..pydantic_models.record import ObjectId
from passlib.context import CryptContext
from app.pydantic_models.userModel import User
from app.pydantic_models.ModelInfo import ModelInfo

client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://tharuka0621:kE3DcROsCHMH8cqH@insync.7taaiij.mongodb.net/')
database = client.InSync
recordsCollection = database.Records
accountCollection = database.Accounts
userCollection = database.Users
saveFilesCollection = database.SaveFiles


async def fetch_balance(type):
    document = await accountCollection.find_one({"type": type})
    balance = document["balance"]
    return balance


async def create_account(account):
    document = account
    result = await accountCollection.insert_one(document)
    return document


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


async def run_aggregation(pipeline: list[dict]):
    result = await recordsCollection.aggregate(pipeline).to_list(None)
    return result


async def update_balance(account_type, new_balance):
    await accountCollection.update_one(
        {'type': account_type},
        {'$set': {'balance': new_balance}}
    )


# userDatabase(login,signup,token)----------------------------------------------------------------------------------

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
    # Append the new user data to the CSV file
    new_user_data = {
        'Age': None,  # Replace with actual age if available
        'Monthly_Total_Income': incomeRange,
        'Gender_Female': gender.lower() == 'female',
        'Gender_Male': gender.lower() == 'male',
        'Occupation_Employee': False,  # Replace with actual occupation if available
        'Occupation_Part_timer': False,  # Replace with actual occupation if available
        'Occupation_Student': False,  # Replace with actual occupation if available
        'Vehicle_you_own_Bike': bike,
        'Vehicle_you_own_Bike_Car': car and bike,
        'Vehicle_you_own_Bike_Three_wheeler': bike and threeWheeler,
        'Vehicle_you_own_Car_Van': car
    }

    df_new_user = pd.DataFrame([new_user_data])
    df_new_user.to_csv('data/Generated.csv', mode='a', header=False, index=False)
    return User(**user, id=str(result.inserted_id))


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return User(**user)


async def get_user_by_id(id: str):
    return await userCollection.find_one({"id": id})


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


async def delete_user_account(email: str):
    user = await get_user(email)
    if not user:
        return False

    await userCollection.delete_one({"email": email})
    await accountCollection.delete_many({"email": email})
    await recordsCollection.delete_many({"userID": str(user["_id"])})
    await saveFilesCollection.delete_many({"userID": str(user["_id"])})

    return True



#Time Series Model---------------------------------------------------------------------------------



async def create_model_info(model_info: ModelInfo):
    document = model_info.dict()
    result = await saveFilesCollection.insert_one(document)
    return document

async def get_model_info(userID: str):
    return await saveFilesCollection.find_one({"userID": userID})

async def update_model_info(userID: str, model_info: ModelInfo):
    await saveFilesCollection.update_one(
        {'userID': userID},
        {'$set': model_info.dict()}
    )


