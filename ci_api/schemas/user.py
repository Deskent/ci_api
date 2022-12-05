from datetime import datetime

from fastapi import Form
from pydantic import BaseModel, validator, EmailStr

from config import logger


class PhoneNumber(BaseModel):
    phone: str

    @validator('phone')
    def check_phone(cls, phone: str):
        phone: str = (
            phone
            .strip()
            .replace('(', '')
            .replace(')', '')
            .replace('-', '')
            .replace(' ', '')[-10:]
        )

        is_phone_valid: bool = len(phone) == 10
        if not is_phone_valid:
            logger.warning(f"Invalid phone number: {phone}")
            raise ValueError('Phone should be in format 9214442233')
        return phone


class Password(BaseModel):
    password: str
    password2: str

    @validator('password2')
    def password_match(cls, password2, values, **kwargs):
        if 'password' in values and password2 != values['password']:
            logger.warning("Passwords dont match")
            raise ValueError('passwords don\'t match')
        return password2


class UserRegistration(Password, PhoneNumber):
    username: str
    last_name: str = ''
    third_name: str = ''
    rate_id: int = 1
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
        if password != password2:
            return
        return cls(
            username=username,
            last_name=last_name,
            third_name=third_name,
            phone=phone,
            rate_id=1,
            email=email,
            gender=True if gender == 'male' else False,
            password=password,
            password2=password2,
        )


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    def as_form(
            cls,
            email: EmailStr = Form(...),
            password: str = Form(...),
    ):
        return cls(
            email=email,
            password=password)


class UserChangePassword(Password):
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
