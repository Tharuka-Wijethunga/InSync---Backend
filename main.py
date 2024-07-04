from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.dashboard import router as DashboardRouter
from app.routers.userAuthentication.auth import authRouter as auth_router
from app.routers.addRecord import router as add_record_router
from app.routers.statistics import router as statistics_router
from app.routers.user_info import user_info_router
from app.routers.generalTimeSeriesModel import router as general_model_router
from app.routers.userTimeSeriesModel import router as user_time_series_router


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(DashboardRouter, tags=["Dashboard"], prefix="/api/dashboard")
app.include_router(auth_router, tags=["Auth"])
app.include_router(add_record_router, tags=["Add Record"], prefix="/api/addrecord")
app.include_router(statistics_router, tags=["statistics"], prefix="/api/statistics")
app.include_router(general_model_router, tags=["Model"],prefix="/api/generalModel")
app.include_router(user_time_series_router, tags=["Model"],prefix="/api/userModel")
app.include_router(user_info_router, tags=["User Info"], prefix="/api/user")





@app.get("/")
async def root():
    return {"message": "Welcome to InSync"}
