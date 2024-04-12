from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.dashboard import router as DashboardRouter

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# 2nd comment for Lihaj
# route to dashboard
app.include_router(DashboardRouter, tags=["Dashboard"], prefix="/api/dashboard")

@app.get("/")
async def root():
    return {"message": "Hello World"}
