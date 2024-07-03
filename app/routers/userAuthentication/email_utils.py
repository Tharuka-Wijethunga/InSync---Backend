from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

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

async def send_verification_email(email: EmailStr, token: str):
    verification_link = f"http://192.168.248.230:8005/verify-email?token={token}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Please click the following link to verify your email: {verification_link}",
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
