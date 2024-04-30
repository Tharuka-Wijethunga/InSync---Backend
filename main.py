from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.dashboard import router as dashboard_router
from app.routers.addRecord import router as add_record_router

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
app.include_router(dashboard_router, tags=["Dashboard"], prefix="/api/dashboard")
app.include_router(add_record_router, tags=["Add Record"], prefix="/api/addrecord")


@app.get("/")
async def root():
    return {"message": "Welcome to InSync"}
