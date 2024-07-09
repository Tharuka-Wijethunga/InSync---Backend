from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from starlette import status
from fastapi.responses import HTMLResponse

from app.pydantic_models.userModel import SignupRequest, User
from app.routers.userAuthentication.email_utils import send_verification_email
from app.routers.userAuthentication.security import create_access_token, get_current_user, create_refresh_token,create_verification_token
from app.database.database import create_user, authenticate_user, get_user, verify_user_email, get_user_verify_info, \
    delete_user_verify_info

authRouter = APIRouter()

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
        signup_request.occupation
    )

@authRouter.post("/checkMail")
async def checkMail(email: str):
    user = await get_user(email)
    if user:
        return {"exists": True}
    else:
        return {"exists": False}

@authRouter.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@authRouter.post("/send-verification-email")
async def send_verify_email(email: str):
    # Generate verification token
    token = create_verification_token(email)

    # Send verification email
    await send_verification_email(email, token)

    return {"msg": "verification email sent"}


@authRouter.get("/verify-email", response_class=HTMLResponse)
async def verify_email(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            return HTMLResponse(
                content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Email Verification</title>
                </head>
                <body>
                    <h1>Invalid token</h1>
                    <p>The token provided is invalid. Please request a new verification email.</p>
                </body>
                </html>
                """,
                status_code=status.HTTP_400_BAD_REQUEST
            )
    except JWTError:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Email Verification</title>
            </head>
            <body>
                <h1>Token expired</h1>
                <p>The token provided has expired. Please request a new verification email.</p>
            </body>
            </html>
            """,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    await verify_user_email(email)

    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verification</title>
        </head>
        <body>
            <h1>Email successfully verified</h1>
            <p>Your email has been successfully verified. You can now close this page and continue using the app.</p>
        </body>
        </html>
        """,
        status_code=status.HTTP_200_OK
    )
@authRouter.get("/check-verification-status")
async def check_verification_status(email: str):
    user = await get_user_verify_info(email)
    if user and user.get("verified"):
        return {"verified": True}
    return {"verified": False}

@authRouter.delete("/delete-verification-info")
async def delete_user(email: str):
    user = await get_user_verify_info(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email verification info not found",
        )
    await delete_user_verify_info(email)
    return {"msg": "Email verification info deleted"}

