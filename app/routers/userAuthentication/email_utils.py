from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME="devinsightlemon@gmail.com",
    MAIL_PASSWORD="fvgj qctg bvmq zkva",
    MAIL_FROM="InSync@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_verification_email(email: EmailStr, token: str):
    verification_link = f"http://192.168.248.230:8006/verify-email?token={token}"

    # Create an HTML template for the email body
    email_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Credentials</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f6f6f6;
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 15px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            padding: 15px 0;
            background-color: #0053a1;
            color: #ffffff;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }}
        .header img {{
            width: 150px;
            height: auto;
        }}
        .header h1 {{
            margin: 10px 0 0;
            font-size: 24px;
        }}
        .content {{
            padding: 15px;
            text-align: center;
        }}
        .content h2 {{
            font-size: 20px;
            margin-bottom: 15px;
            color: #333333;
        }}
        .content p {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #666666;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #999999;
            background-color: #f6f6f6;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
    </style>
</head>
<body>

<div class="email-container">
    <div class="header">
        <h1>InSync</h1>
    </div>
    <div class="content">
        <h2>Verify Your Email</h2>
        <p>Please click the button below to verify your email address:</p>
        <a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px;">Verify Email</a>
    </div>
    <div class="footer">
        &copy; 2024 InSync. All rights reserved.<br>
    </div>
</div>
</body>
</html>
    """

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=email_body,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)