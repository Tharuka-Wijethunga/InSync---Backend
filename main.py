from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.dashboard import router as DashboardRouter
from app.routers.onboarding import router as onboarding_router

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
app.include_router(onboarding_router, prefix="/onBoarding")

@app.get("/")
async def root():
    return {"message": "Hello World"}
