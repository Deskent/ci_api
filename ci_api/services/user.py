import pydantic
from pydantic import EmailStr
from starlette.datastructures import FormData

from config import logger
from models.models import User, Administrator, Rate, Complex
from schemas.user import UserRegistration, UserLogin
from services.utils import generate_four_random_digits_string
from web_service.services.sms_class import sms_service, SMSException


def get_bearer_header(token: str) -> dict[str, str]:
    return {'Authorization': f"Bearer {token}"}


async def user_login(user_data: UserLogin) -> User:
    if user_found := await User.get_by_email(user_data.email):
        if await user_found.is_password_valid(user_data.password):
            return user_found


async def check_email_exists(email: EmailStr) -> bool:
    user: User = await User.get_by_email(email)
    admin: Administrator = await Administrator.get_by_email(email)

    return True if user or admin else False


async def check_user_phone_exists(phone: str) -> User:
    if user := await User.get_by_phone(phone):
        return user


async def register_new_user(user_data: UserRegistration) -> tuple[User | None, dict]:
    errors = {}
    if await check_email_exists(user_data.email):
        errors = {'error': 'Пользователь с таким email уже существует'}
        return None, errors

    if await check_user_phone_exists(user_data.phone):
        errors = {'error': 'Пользователь с таким телефоном уже существует'}
        return None, errors

    data: dict = user_data.dict()
    result: dict = await send_sms(user_data.phone)
    if sms_message := result.get('sms_message'):
        logger.debug(f"Sms_message code: {sms_message}")
        data['sms_message'] = sms_message
    elif result.get('error'):
        errors.update(**result)
        return None, errors

    # except EmailException:
    #     logger.warning(f"Wrong email {user_data.email}")
    #     errors = {'error': "Неверный адрес почты"}
    #     return None, errors
    first_complex: Complex = await Complex.get_first()
    if first_complex:
        data['current_complex'] = first_complex.id

    free_rate: Rate = await Rate.get_free()
    if free_rate:
        data['rate_id'] = free_rate.id
    user: User = await User.create(data)

    logger.info(f"User with id {user.id} created. Rate set: {user.rate_id}")

    return user, errors


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
