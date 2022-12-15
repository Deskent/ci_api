import pydantic
from pydantic import EmailStr
from starlette.datastructures import FormData

from config import logger
from exc.exceptions import PasswordMatchError
from exc.register import EmailExistsError, PhoneExistsError, SmsServiceError
from models.models import User, Administrator, Rate, Complex
from schemas.user_schema import UserRegistration, UserLogin, PhoneNumber, UserPhoneLogin
from services.utils import generate_four_random_digits_string
from services.web_context_class import WebContext
from web_service.services.sms_class import sms_service, SMSException


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


async def check_email_and_password_correct(user_data: UserLogin) -> User:
    if user_found := await User.get_by_email(user_data.email):
        if await user_found.is_password_valid(user_data.password):
            return user_found


async def check_email_exists(email: EmailStr) -> bool:
    user: User = await User.get_by_email(email)
    admin: Administrator = await Administrator.get_by_email(email)

    return True if user or admin else False


async def check_user_phone_exists(phone: str | PhoneNumber) -> User:
    if user := await User.get_by_phone(phone):
        return user


async def check_phone_and_password_correct(user_data: UserPhoneLogin) -> User:
    if user_found := await check_user_phone_exists(user_data.phone):
        if await user_found.is_password_valid(user_data.password):
            return user_found


async def validate_logged_user_data(form: FormData) -> tuple[UserLogin | None, dict]:
    try:
        user_data = UserLogin(email=form['email'], password=form['password'])

        return user_data, {}
    except pydantic.error_wrappers.ValidationError as err:
        logger.debug(err)

        return None, {'error': "Invalid email or password"}


async def send_sms(phone: str) -> dict:
    sms_message: str = generate_four_random_digits_string()

    logger.debug(f"Sms message generated: {sms_message}")
    result = {"error": 'Undefined error in _send_sms function'}
    try:
        if await sms_service.send_sms(phone=phone, message=sms_message):
            return {"sms_message": sms_message}
    except SMSException as err:
        logger.error(err)
        result.update(error=err)

    return result


async def register_new_user_web_context(
        context: dict,
        user_data: UserRegistration
):
    web_context = WebContext(context)
    if not user_data:
        web_context.error = 'Пароли не совпадают'
        web_context.template = "registration.html"
        web_context.to_raise = PasswordMatchError
        return web_context

    if await check_email_exists(user_data.email):
        web_context.error = 'Пользователь с таким email уже существует'
        web_context.template = "registration.html"
        web_context.to_raise = EmailExistsError
        return web_context

    if await check_user_phone_exists(user_data.phone):
        web_context.error = 'Пользователь с таким телефоном уже существует'
        web_context.template = "registration.html"
        web_context.to_raise = PhoneExistsError
        return web_context

    data: dict = user_data.dict()
    result: dict = await send_sms(user_data.phone)
    if sms_message := result.get('sms_message'):
        logger.debug(f"Sms_message code: {sms_message}")
        data['sms_message'] = sms_message
    elif error := result.get('error'):
        web_context.error = error
        web_context.template = "registration.html"
        web_context.to_raise = SmsServiceError
        return web_context

    first_complex: Complex = await Complex.get_first()
    if first_complex:
        data['current_complex'] = first_complex.id

    free_rate: Rate = await Rate.get_free()
    if free_rate:
        data['rate_id'] = free_rate.id
    user: User = await User.create(data)

    logger.info(f"User with id {user.id} created. Rate set: {user.rate_id}")
    web_context.context.update(user=user)
    web_context.api_data.update(payload=user)
    web_context.template = "forget2.html"

    return web_context
