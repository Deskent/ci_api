import pydantic
from pydantic import EmailStr
from starlette.datastructures import FormData

from config import logger
from exc.exceptions import PasswordMatchError
from exc.register import EmailExistsError, PhoneExistsError, SmsServiceError
from database.models import User, Administrator, Rate, Complex, Video, Mood
from schemas.user_schema import UserRegistration, UserLogin, PhoneNumber, UserPhoneLogin, \
    EntryModalWindow
from crud_class.crud import CRUD
from services.utils import generate_four_random_digits_string
from misc.web_context_class import WebContext
from misc.sms_class import sms_service, SMSException


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


async def check_email_and_password_correct(user_data: UserLogin) -> User:
    if user_found := await CRUD.user.get_by_email(user_data.email):
        if await CRUD.user.is_password_valid(user_found, user_data.password):
            return user_found


async def check_email_exists(email: EmailStr) -> bool:
    user: User = await CRUD.user.get_by_email(email)
    admin: Administrator = await CRUD.admin.get_by_email(email)

    return True if user or admin else False


async def check_user_phone_exists(phone: str | PhoneNumber) -> User:
    if user := await CRUD.user.get_by_phone(phone):
        return user


async def check_phone_and_password_correct(user_data: UserPhoneLogin) -> User:
    if user_found := await check_user_phone_exists(user_data.phone):
        if await CRUD.user.is_password_valid(user_found, user_data.password):
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
        logger.exception(err)
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
    if user_data.test:
        data['sms_message'] = "1234"
    else:
        result: dict = await send_sms(user_data.phone)
        if sms_message := result.get('sms_message'):
            logger.debug(f"Sms_message code: {sms_message}")
            data['sms_message'] = sms_message
        elif error := result.get('error'):
            web_context.error = error
            web_context.template = "registration.html"
            web_context.to_raise = SmsServiceError
            return web_context

    first_complex: Complex = await CRUD.complex.get_first()
    if first_complex:
        data['current_complex'] = first_complex.id

    free_rate: Rate = await CRUD.rate.get_free()
    if free_rate:
        data['rate_id'] = free_rate.id
    user: User = await CRUD.user.create(data)

    logger.info(f"User with id {user.id} created. Rate set: {user.rate_id}")
    web_context.context.update(user=user)
    web_context.api_data.update(payload=user)
    web_context.template = "forget2.html"

    return web_context


async def get_modal_window_first_entry(user: User) -> EntryModalWindow:
    """Check what modal window need to return if user first entry today"""

    if await CRUD.user.is_new_user(user):
        user: User = await CRUD.user.set_last_entry_today(user)
        await CRUD.user.set_subscribe_to(days=7, user=user)
        hello_video: Video = await CRUD.video.get_hello_video()

        return EntryModalWindow(user=user, new_user=True, hello_video=hello_video)

    if await CRUD.user.is_first_entry_today(user):
        user: User = await CRUD.user.set_last_entry_today(user)
        if not await CRUD.user.check_is_active(user):
            return EntryModalWindow(user=user, is_expired=True)
        elif user.level > 6:
            emojies: list[Mood] = await CRUD.mood.get_all()

            return EntryModalWindow(
                user=user, emojies=emojies, today_first_entry=True)

    return EntryModalWindow(user=user)
