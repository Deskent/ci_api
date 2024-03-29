import aiosmtplib
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr, BaseModel

from config import settings, logger
from services.utils import generate_four_random_digits_string


class EmailException(Exception):
    pass


class EmailSchema(BaseModel):
    email: EmailStr
    payload: dict


conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_LOGIN,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_LOGIN,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=settings.TEMPLATES_DIR / 'send_email'
)


async def _send_mail(email: EmailStr, payload: dict) -> None:
    logger.debug(f"Sending email for {email}")

    data = EmailSchema(email=email, payload=payload)

    message = MessageSchema(
        subject="Ci service mailing",
        recipients=[data.email],
        template_body=data.payload,
        subtype=MessageType.html
    )
    try:
        await FastMail(conf).send_message(message, template_name="email_sending.html")
    except ConnectionErrors as err:
        logger.exception(f"Email sending error: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            detail="Invalid mailing credentials"
        )
    except (
            aiosmtplib.errors.SMTPRecipientsRefused,
            aiosmtplib.errors.SMTPDataError
    ) as err:
        logger.exception(f"Email sending error: {str(err)}")
        raise EmailException("Invalid email address")


async def send_verification_mail(
        email: EmailStr
) -> str:
    # token: str = AuthHandler().get_email_token(user)
    code: str = generate_four_random_digits_string()
    payload = {
        'data': {
            'title': 'Токен валидации',
            'body': 'Ваш токен для валидации:',
            'message': code
        }
    }
    logger.debug(f'Email token for {email}: {code}')
    await _send_mail(email, payload)

    return code


async def send_email_message(email: EmailStr, message: str):
    payload = {
        'data': {
            'title': 'Новый пароль',
            'body': 'Ваш новый пароль:',
            'message': message
        }
    }

    await _send_mail(email, payload)
