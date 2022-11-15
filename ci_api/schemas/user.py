from datetime import datetime

from pydantic import BaseModel, validator, EmailStr


class Password(BaseModel):
    password: str
    password2: str

    @validator('password2')
    def password_match(cls, password2, values, **kwargs):
        if 'password' in values and password2 != values['password']:
            raise ValueError('passwords don\'t match')
        return password2


class UserRegistration(Password):
    username: str
    email: EmailStr
    phone: str
    gender: bool

    @validator('phone')
    def check_phone(cls, phone: str, values, **kwargs):
        is_phone_valid: bool = len(phone) == 10
        if not is_phone_valid:
            raise ValueError('phone should be in format 9214442233')
        return phone


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserChangePassword(Password):
    old_password: str


class UserFullData(BaseModel):
    gender: bool
    phone: str
    is_verified: bool = False
    is_admin: bool = False
    is_active: bool = False
    current_complex: int = None
    expired_at: datetime = None


class UserOutput(UserFullData):
    username: str = None
    email: EmailStr = None


class UserProgress(BaseModel):
    level: int
    current_complex: int
