from fastapi import APIRouter, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from random import randint
from datetime import datetime, timedelta
from app.database.database import get_user_by_email, save_verification_code, verify_user_code, hash_password, update_user_pass
from pydantic import BaseModel, EmailStr

reset_router = APIRouter()



class PasswordResetRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: int

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: int
    new_password: str

# FastMail configuration
conf = ConnectionConfig(
    MAIL_USERNAME="devinsightlemon@gmail.com",
    MAIL_PASSWORD="fvgj qctg bvmq zkva",
    MAIL_FROM="devinsightlemon@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

@reset_router.post("/password-reset/request")
async def request_password_reset(data: PasswordResetRequest):
    user = await get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    verification_code = randint(100000, 999999)  # Generate a 6-digit code
    await save_verification_code(user["_id"], verification_code)  # Save the code in the database with an expiry time

    message = MessageSchema(
        subject="Password Reset Verification Code",
        recipients=[data.email],
        body=f"Your verification code is {verification_code}",
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Verification code sent TOO your email"}

@reset_router.post("/password-reset/verify")
async def verify_code(data: VerifyCodeRequest):
    user = await get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not await verify_user_code(user["_id"], data.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code")

    return {"message": "Verification successful"}

@reset_router.post("/password-reset/reset")
async def reset_password(data: ResetPasswordRequest):
    user = await get_user_by_email(data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not await verify_user_code(user["_id"], data.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification code")

    await update_user_pass(user["_id"], data.new_password)  # Update the user's password in the database

    return {"message": "Password reset successful"}