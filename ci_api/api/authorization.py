from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from pydantic import EmailStr

from config import logger
from exc.exceptions import UserNotFoundErrorApi
from models.models import User
from schemas.user_schema import UserPhoneCode, TokenUser, UserOutput, UserSchema
from schemas.user_schema import UserRegistration, UserPhoneLogin, UserChangePassword
from services.depends import get_logged_user
from services.models_cache.crud import CRUD
from services.user import register_new_user_web_context
from services.web_context_class import WebContext
from web_service.handlers.common import user_login_via_phone
from web_service.handlers.enter_with_sms import approve_sms_code

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

    :param rate_id: int - Rate id (тариф)

    :param gender: bool - True = male, False - female

    :return: User created information as JSON
    """
    web_context: WebContext = await register_new_user_web_context(context={}, user_data=user_data)
    return web_context.api_render()


@router.get("/verify_email", status_code=status.HTTP_202_ACCEPTED, response_model=UserOutput)
async def verify_email_token(
        token: str,
        email: EmailStr,
):
    """Verify user via email code (not using)

    :param email: string - Email

    :param code: string - Code from sms

     :return: User data as JSON

    """

    user: User = await CRUD.user.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.email_code != token:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid token")

    if user and not user.is_verified:
        user.is_verified = True
        user.email_code = None
        await CRUD.user.save(user)
        logger.info(f"User with id {user.id} verified")
    logger.debug(f"Verify email token: OK")

    return user


@router.post("/verify_sms_code", status_code=status.HTTP_202_ACCEPTED, response_model=UserOutput)
async def verify_sms_code(
        request: Request,
        data: UserPhoneCode
):

    """Verify user via sms code

    :param phone: string - phone number in format: 9998887766

    :param code: string - Code from sms

     :return: User data as JSON

    """

    web_context: WebContext = await approve_sms_code(request=request,
        context={}, phone=data.phone, code=data.code)
    return web_context.api_render()



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
    if web_context.to_raise:
        raise web_context.to_raise

    user: User = web_context.api_data['payload']
    token: str = await CRUD.user.get_user_token(user)
    logger.info(f"User with id {user.id} got Bearer token")
    return TokenUser(token=token, user=user.dict())


@router.put("/change_password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
        data: UserChangePassword,
        user: User = Depends(get_logged_user),
):
    """
    Change password

    :param old_password: string - Old password

    :param password: string - new password

    :param password2: string - Repeat new password

    :return: None
    """
    if not await CRUD.user.is_password_valid(user, data.old_password):
        raise UserNotFoundErrorApi
    user.password = await CRUD.user.get_hashed_password(data.password)
    await CRUD.user.save(user)
    logger.info(f"User with id {user.id} change password")



@router.put("/set_push_token", status_code=status.HTTP_202_ACCEPTED)
async def set_push_token(
        push_token: str = Body(...),
        user: User = Depends(get_logged_user),
):
    """Get and save token to user

    :return None
    """

    user.push_token = push_token
    await CRUD.user.save(user)
