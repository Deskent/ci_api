from fastapi import APIRouter, status, Request

from config import logger
from crud_class.crud import CRUD
from database.models import User
from exc.exceptions import UserNotFoundError, EmailError
from misc.web_context_class import WebContext
from schemas.user_schema import UserPhoneCode, TokenUser, UserSchema, PhoneNumber, UserEmail
from schemas.user_schema import UserRegistration, UserPhoneLogin
from services.emails import send_email_message, EmailException
from services.user import register_new_user_web_context
from services.utils import generate_random_password
from web_service.handlers.common import user_login_via_phone
from web_service.handlers.enter_with_sms import approve_sms_code_or_call_code, \
    update_user_token_to_web_context, entry_via_sms_or_call

router = APIRouter(prefix="/auth", tags=['Authorization'])


@router.post("/register", response_model=UserSchema)
async def register(
        user_data: UserRegistration,
):
    """
    Create new user in database if not exists

    :param username: string - Username

    :param last_name: Optional[string] - User last name

    :param third_name: Optional[string] - User middle name (Отчество)

    :param email: string - E-mail

    :param phone: string - Phone number in format: 9998887766

    :param password: string - Password

    :param password2: string - Repeat Password

    :param gender: bool - True = male, False - female

    :param is_registered: bool - False - Ss user registered flag

    :return: User created information as JSON
    """

    web_context: WebContext = await register_new_user_web_context(context={}, user_data=user_data)

    return web_context.api_render()


# @router.get("/verify_email", status_code=status.HTTP_202_ACCEPTED, response_model=UserOutput)
# async def verify_email_token(
#         token: str,
#         email: EmailStr,
# ):
#     """Verify user via email code (not using)
#
#     :param email: string - Email
#
#     :param code: string - Code from sms
#
#      :return: User data as JSON
#
#     """
#
#     user: User = await CRUD.user.get_by_email(email)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     if user.email_code != token:
#         raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid token")
#
#     if user and not user.is_verified:
#         user.is_verified = True
#         user.email_code = None
#         await CRUD.user.save(user)
#         logger.info(f"User with id {user.id} verified")
#     logger.debug(f"Verify email token: OK")
#
#     return user


@router.post("/login", response_model=TokenUser)
async def login(
        user_data: UserPhoneLogin
):
    """Get user authorization token

    :param phone: string - phone number in format: 9998887766

    :param password: string - Password

     :return: Authorization token as JSON and user as JSON
    """

    web_context: WebContext = await user_login_via_phone(context={}, form_data=user_data)
    web_context: WebContext = await update_user_token_to_web_context(web_context)

    return web_context.api_render()


@router.post(
    "/login_via_sms",
    status_code=status.HTTP_204_NO_CONTENT
)
async def login_via_sms(
        user_phone: PhoneNumber
):
    """Login user via sms

    :param phone: string - phone number in format: 9998887766

     :return: None
    """
    web_context: WebContext = await entry_via_sms_or_call(
        context={}, sms_send_to="sms", phone=user_phone.phone
    )

    return web_context.api_render()


@router.post(
    "/login_via_call",
    status_code=status.HTTP_204_NO_CONTENT
)
async def login_via_call(
        user_phone: PhoneNumber
):
    """Login user via phone call

    :param phone: string - phone number in format: 9998887766

     :return: None
    """
    web_context: WebContext = await entry_via_sms_or_call(
        context={}, sms_send_to="call", phone=user_phone.phone
    )

    return web_context.api_render()


@router.post(
    "/verify_sms_code",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TokenUser
)
async def verify_sms_code(
        request: Request,
        data: UserPhoneCode
):
    """Verify user via sms code

    :param phone: string - phone number in format: 9998887766

    :param code: string - Code from sms

     :return: Authorization token as JSON and user as JSON
    """

    web_context: WebContext = await approve_sms_code_or_call_code(
        request=request, context={}, phone=data.phone, code=data.code)
    return web_context.api_render()


@router.post(
    "/verify_call_code",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TokenUser)
async def verify_call_code(
        request: Request,
        data: UserPhoneCode
):
    """Verify user via call code

    :param phone: string - phone number in format: 9998887766

    :param code: string - Code from phone call

     :return: Authorization token as JSON and user as JSON
    """

    web_context: WebContext = await approve_sms_code_or_call_code(
        request=request, context={}, phone=data.phone, code=data.code, check_call=True
    )
    return web_context.api_render()


@router.post("/restore_password", response_model=UserSchema)
async def restore_password(
        user_email: UserEmail
):
    """
    Send new password to user email.

    :return: User as JSON if email correct
    """
    user: User = await CRUD.user.get_by_email(user_email.email)
    if not user:
        raise UserNotFoundError

    new_password: str = generate_random_password()
    try:
        await send_email_message(user.email, new_password)
    except EmailException:
        raise EmailError

    logger.debug(f"New password: {new_password}")
    user.password = await CRUD.user.get_hashed_password(new_password)
    await CRUD.user.save(user)

    return user
