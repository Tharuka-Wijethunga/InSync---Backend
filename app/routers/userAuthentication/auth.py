from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.models.userModel import SignupRequest, User
from app.routers.userAuthentication.security import create_access_token, get_current_user, create_refresh_token
from app.database.userDatabase import create_user, authenticate_user

authRouter = APIRouter()


@authRouter.post("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(
        data={"sub": current_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@authRouter.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@authRouter.post("/signup")
async def signup(signup_request: SignupRequest):
    return await create_user(
        signup_request.fullname,
        signup_request.email,
        signup_request.gender,
        signup_request.password,
        signup_request.incomeRange,
        signup_request.car,
        signup_request.bike,
        signup_request.threeWheeler,
        signup_request.none,
        signup_request.loanAmount
    )

@authRouter.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
