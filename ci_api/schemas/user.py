from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, validator, EmailStr

from config import logger
from exc.exceptions import PhoneNumberError, PasswordMatchError


def slice_phone_to_format(phone: str) -> str:
    """Delete from phone number like `8 (123) 456-7890` or something
    all extra symbols. Return clean phone number like `1234567890`
    """

    phone: str = (
        phone
        .strip()
        .replace('(', '')
        .replace(')', '')
        .replace('-', '')
        .replace(' ', '')[-10:]
    )

    is_phone_valid: bool = len(phone) == 10 and phone.isdigit()
    if not is_phone_valid:
        logger.warning(f"Invalid phone number: {phone}")
        raise PhoneNumberError
    return phone


class PhoneNumber(BaseModel):
    phone: str

    @validator('phone')
    def check_valid_phone(cls, phone: str):
        return slice_phone_to_format(phone)


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


class UserRegistration(Password2, PhoneNumber):
    username: str
    last_name: str = ''
    third_name: str = ''
    email: EmailStr
    gender: bool = True

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


class UserFullData(BaseModel):
    gender: bool
    phone: str
    is_verified: bool = False
    is_active: bool = False
    current_complex: int = None
    expired_at: datetime = None


class UserOutput(UserFullData):
    username: str = None
    email: EmailStr = None


class UserProgress(BaseModel):
    level: int
    current_complex: int


class EmailVerify(BaseModel):
    email: EmailStr
