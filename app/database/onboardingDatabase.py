import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://lihajwicky:InSync1.0@insync.7taaiij.mongodb.net/')
database = client.InSync
Onboardingcollection = database.Onboarding

async def create_onboarding_data(data):
    document = data
    result = await Onboardingcollection.insert_one(document)
    return document


