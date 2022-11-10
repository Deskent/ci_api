import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_session
from models.models import User
from schemas.user import UserRegistration, UserLogin, UserChangePassword, UserOutput
from services.depends import auth_handler, get_logged_user


router = APIRouter(prefix="/auth", tags=['Authorization'])


@router.post("/register", response_model=UserOutput)
async def register(user_data: UserRegistration, session: AsyncSession = Depends(get_session)):
    """
    Create new user in database if not exists

    :param username: string - Username

    :param email: string - E-mail

    :param phone: string - Phone number in format: 9998887766

    :param password: string - Password

    :param password2: string - Repeat Password

    :param gender: bool - True = male, False - female

    :return: User created information as JSON
    """

    if await User.get_user_by_email(session, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User exists')

    user_data.password = auth_handler.get_password_hash(user_data.password)
    expired_at = datetime.datetime.now(tz=None) + datetime.timedelta(days=30)
    user = User(
        **user_data.dict(),
        current_complex=1, is_admin=False, is_active=True, expired_at=expired_at
    )
    session.add(user)
    await session.commit()

    return user


@router.post("/login", response_model=dict)
async def login(user: UserLogin, session: AsyncSession = Depends(get_session)):
    """Get user authorization token

    :param email: string - E-mail

    :param password: string - Password

     :return: Authorization token as JSON
    """

    user_found: User = await User.get_user_by_email(session, user.email)
    if not user_found:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    is_password_correct: bool = auth_handler.verify_password(user.password, user_found.password)
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token: str = auth_handler.encode_token(user_found.id)

    return {"token": token}


@router.put("/change_password", status_code=201)
async def change_password(
        data: UserChangePassword,
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Change password

    :param old_password: string - Old password

    :param password: string - new password

    :param password2: string - Repeat new password
    """

    if not auth_handler.verify_password(data.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    user.password = auth_handler.get_password_hash(data.password)

    session.add(user)
    await session.commit()
