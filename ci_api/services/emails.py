from fastapi_mail.errors import ConnectionErrors
import jwt
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

from config import settings, logger
from models.models import User
from services.auth import AuthHandler


class EmailSchema(BaseModel):
    email: EmailStr
    token: dict


conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_LOGIN,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_LOGIN,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=settings.TEMPLATES_DIR
)


async def _send_mail(data: EmailSchema) -> None:
    logger.debug(f"Sending email for {data.email}")

    message = MessageSchema(
        subject="Ci service mailing",
        recipients=[data.email],
        template_body=data.token,
        subtype=MessageType.html
    )
    try:
        await FastMail(conf).send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        logger.error(f"Email sending error: {str(err)}")
        raise HTTPException(status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
                            detail="Invalid mailing credentials")


async def send_verification_mail(user: User) -> None:
    token = {"token": AuthHandler().get_email_token(user)}
    data = EmailSchema(email=user.email, token=token)
    await _send_mail(data)


async def verify_token_from_email(token: str) -> str:
    logger.debug(f"Verify email token...")

    try:
        payload = AuthHandler().verify_email_token(token)
        return payload["id"]
    except jwt.exceptions.DecodeError as err:
        logger.error(f"Email token verify: {str(err)}")
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid token")
