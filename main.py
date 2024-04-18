from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.dashboard import router as DashboardRouter
from app.routers.addRecord import router as AddRecordRouter

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# routers
app.include_router(DashboardRouter, tags=["Dashboard"], prefix="/api/dashboard")
app.include_router(AddRecordRouter, tags=["Add Record"], prefix="/api/addrecord")

@app.get("/")
async def root():
    return {"message": "Welcome to InSync"}
