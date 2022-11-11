import asyncio

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

from config import settings
from models.models import User
from services.auth import AuthHandler


class EmailSchema(BaseModel):
    email: EmailStr
    token: dict


conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_LOGIN,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_LOGIN,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.mail.ru",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=settings.TEMPLATES_DIR
)


async def _send_mail(data: EmailSchema) -> None:

    message = MessageSchema(
        subject="Fastapi-Mail module",
        recipients=[data.email],
        template_body=data.token,
        subtype=MessageType.html
    )

    await FastMail(conf).send_message(message, template_name="email_template.html")


async def send_verification_mail(user: User) -> None:
    token = {"token": AuthHandler().get_email_token(user)}
    data = EmailSchema(email=user.email, token=token)
    await _send_mail(data)


if __name__ == '__main__':
    test_email = 'battenetciz@gmail.com'
    email = EmailSchema(email=[test_email])
    asyncio.run(_send_mail(email))
