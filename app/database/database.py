import motor.motor_asyncio
import pandas as pd

from ..pydantic_models.record import Record, ObjectId
from passlib.context import CryptContext
from app.pydantic_models.userModel import User

client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://tharuka0621:kE3DcROsCHMH8cqH@insync.7taaiij.mongodb.net/')
database = client.InSync
recordsCollection = database.Records
accountCollection = database.Accounts
userCollection = database.Users


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
                      threeWheeler: bool, none: bool, loanAmount: float):
    hashed_password = pwd_context.hash(password)
    user = {"fullname": fullname, "email": email, "gender": gender, "hashed_password": hashed_password,
            "incomeRange": incomeRange, "car": car, "bike": bike, "threeWheeler": threeWheeler, "none": none,
            "loanAmount": loanAmount}
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