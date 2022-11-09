from datetime import datetime, time

from pydantic import BaseModel, EmailStr, validator


class AlarmBase(BaseModel):
    alarm_time: time
    text: str = None


class AlarmCreate(AlarmBase):
    user_id: int = None


class AlarmUpdate(AlarmCreate):
    pass


class NotificationBase(BaseModel):
    notification_time: time
    text: str = ''


class NotificationCreate(NotificationBase):
    user_id: int = None


class NotificationUpdate(NotificationCreate):
    pass


class VideoBase(BaseModel):
    path: str
    name: str = ''
    description: str = ''
    previous_id: int = None
    next_id: int


class VideoCreate(VideoBase):
    pass


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserInput(UserCreate):
    password2: str

    @validator('password2')
    def password_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords don\'t match')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserFullData(BaseModel):
    is_admin: bool = False
    is_active: bool = False
    current_video: int = None
    expired_at: datetime = None


class UserUpdate(UserFullData):
    username: str = None
    email: EmailStr = None
    password: str = None


class UserOutput(UserFullData):
    username: str = None
    email: EmailStr = None
