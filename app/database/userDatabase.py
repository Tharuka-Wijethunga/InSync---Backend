import motor.motor_asyncio
from passlib.context import CryptContext
from app.models.userModel import User

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lihajwicky:InSync1.0@insync.7taaiij.mongodb.net/')
database = client.InSync
UserCollection = database.Users

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(email: str):
    return await UserCollection.find_one({"email": email})

async def create_user(fullname: str, email: str, gender: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = {"fullname": fullname, "email": email, "gender": gender, "hashed_password": hashed_password}
    result = await UserCollection.insert_one(user)
    return User(**user, id=str(result.inserted_id))

async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return User(**user)
