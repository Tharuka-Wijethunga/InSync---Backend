import motor.motor_asyncio
from app.models.record import Record
from app.models.account import Account

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://tharuka0621:kE3DcROsCHMH8cqH@insync.7taaiij.mongodb.net/')
database = client.InSync
recordsCollection = database.Records
accountCollection = database.Accounts

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
