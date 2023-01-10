import re
from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, validator, EmailStr

from config import logger, MAX_LEVEL
from exc.exceptions import PhoneNumberError, PasswordMatchError, SmsCodeNotValid


def slice_phone_to_format(phone: str) -> str:
    """Delete from phone number like `8 (123) 456-7890` or something
    all extra symbols. Return clean phone number like `1234567890`
    """
    pattern = r'[^\d]'
    phone: str = re.sub(pattern, '', phone)[-10:]

    is_phone_valid: bool = len(phone) == 10 and phone.isdigit()
    if not is_phone_valid:
        logger.warning(f"Invalid phone number: {phone}")
        raise PhoneNumberError
    return phone


class PhoneNumber(BaseModel):
    phone: str

    _normalize_name = validator('phone', allow_reuse=True)(slice_phone_to_format)


class Password(BaseModel):
    password: str


class Password2(Password):
    password2: str

    @validator('password')
    def password_match(cls, password, values):
        if 'password2' in values and password != values['password2']:
            logger.warning("Passwords dont match")
            raise PasswordMatchError
        return password


class MaxLevel(BaseModel):
    max_level: int = MAX_LEVEL


class UserEditProfile(PhoneNumber):
    phone: str = ''
    username: str = ''
    last_name: str = ''
    third_name: str = ''
    email: EmailStr = ''


class NewProfile(PhoneNumber):
    username: str
    last_name: str = 'Connor'
    third_name: str = 'Sara'
    email: EmailStr


class UserRegistration(Password2, NewProfile):
    gender: bool = True
    test: bool = False

    @classmethod
    def as_form(
            cls,
            username: str = Form(...),
            last_name: str = Form(...),
            third_name: str = Form(...),
            phone: str = Form(...),
            email: EmailStr = Form(...),
            gender: str = Form(...),
            password: str = Form(...),
            password2: str = Form(...),
            test: bool = False
    ):
        if password == password2:
            return cls(
                username=username,
                last_name=last_name,
                third_name=third_name,
                phone=phone,
                email=email,
                gender=True if gender == 'male' else False,
                password=password,
                password2=password2,
                test=test
            )


class UserLogin(Password):
    email: EmailStr

    @classmethod
    def as_form(
            cls,
            email: EmailStr = Form(...),
            password: str = Form(...),
    ):
        return cls(
            email=email,
            password=password)


class SmsCode(BaseModel):
    code: str

    @validator('code')
    def password_match(cls, code, values):
        if len(code) != 4:
            logger.warning(SmsCodeNotValid.detail)
            raise SmsCodeNotValid
        return code


class UserPhoneCode(PhoneNumber, SmsCode):
    pass


class UserPhoneLogin(Password, PhoneNumber):
    pass

    @classmethod
    def as_form(
            cls,
            phone: str = Form(...),
            password: str = Form(...),
    ):
        return cls(
            phone=phone,
            password=password)


class UserChangePassword(Password2):
    old_password: str


class UserSchema(MaxLevel):
    id: int
    username: str
    last_name: str
    third_name: str
    phone: str
    email: EmailStr
    gender: bool
    level: int
    current_complex: int
    expired_at: datetime | None = None
    avatar: int = None
    mood: int = None
    rate_id: int = None
    is_email_verified = False
    is_verified: bool = False
    is_active: bool = False


class UserFullData(MaxLevel):
    gender: bool
    phone: str
    level: int
    is_email_verified = False
    is_verified: bool = False
    is_active: bool = False
    current_complex: int = None
    expired_at: datetime = None


class UserOutput(UserFullData):
    username: str = None
    email: EmailStr = None


class UserProgress(MaxLevel):
    level: int
    current_complex: int


class EmailVerify(BaseModel):
    email: EmailStr


class TokenUser(BaseModel):
    token: str
    user: UserSchema


class UserMood(BaseModel):
    mood_id: int


class EntryModalWindow(BaseModel):
    user: dict
    emojies: list[dict] = []
    new_user: bool = False
    hello_video: dict = {}
    today_first_entry: bool = False
    is_expired: bool = False
