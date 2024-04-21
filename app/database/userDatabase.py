import motor.motor_asyncio
from passlib.context import CryptContext
from app.models.userModel import User

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lihajwicky:InSync1.0@insync.7taaiij.mongodb.net/')
database = client.InSync
UserCollection = database.Users

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user(username: str):
    return await UserCollection.find_one({"username": username})

async def create_user(username: str, email: str, gender: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = {"username": username, "email": email, "gender": gender, "hashed_password": hashed_password}
    result = await UserCollection.insert_one(user)
    return User(**user, id=str(result.inserted_id))

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not pwd_context.verify(password, user["hashed_password"]):
        return False
    return User(**user)
