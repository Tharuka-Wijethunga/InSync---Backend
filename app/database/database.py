import motor.motor_asyncio
from ..models.record import Record, ObjectId

client = motor.motor_asyncio.AsyncIOMotorClient(
    'mongodb+srv://tharuka0621:kE3DcROsCHMH8cqH@insync.7taaiij.mongodb.net/')
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


async def fetch_record(id):
    document = await recordsCollection.find_one({"_id": ObjectId(id)})
    # Handle missing 'date' and 'time' fields
    document.setdefault('date', None)
    document.setdefault('time', None)

    return document


async def fetch_all_records():
    records = []
    cursor = recordsCollection.find({})
    async for document in cursor:
        # Handle missing 'date' and 'time' fields
        document.setdefault('date', None)
        document.setdefault('time', None)

        records.append((Record(**document)))
    return records


async def run_aggregation(pipeline: list[dict]):
    result = await recordsCollection.aggregate(pipeline).to_list(None)
    return result


async def update_balance(account_type, new_balance):
    await accountCollection.update_one(
        {'type': account_type},
        {'$set': {'balance': new_balance}}
    )
