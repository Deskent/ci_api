import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import EmailStr

from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from database.db import get_session
from models.models import User, UserUpdate, Alarm, Notification, Video, UserInput, UserLogin, UserOutput
from services.depends import check_access, auth_handler, check_user_is_admin
from services.utils import get_data_for_update

router = APIRouter(prefix="/users", tags=['Users'])


@router.get("/", response_model=list[User], dependencies=[Depends(check_user_is_admin)])
async def get_users(session: AsyncSession = Depends(get_session)):
    """
    Get all users from database. For admin only.

    :return: List of users as JSON
    """

    users = await session.execute(select(User).order_by(User.id))

    return users.scalars().all()

# TODO сделать GetMe endpoint ,


@router.get("/{user_id}", response_model=UserOutput)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user by user_id

    :param user_id: int - User database ID

    :return: User information as JSON
    """

    if not (user := await User.get_user_by_id(session, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.post("/get_id")
async def get_user_id_by_email(email: EmailStr, session: AsyncSession = Depends(get_session)):
    """Get user_id by email

    :param email: string - User email

    :return: User id
    """

    if not (user := await User.get_user_by_email(session, email)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user.id


@router.post("/", response_model=UserOutput, tags=['Authentication'])
async def create_user(user: UserInput, session: AsyncSession = Depends(get_session)):
    """
    Create new user in database if not exists

    :param username: string - Username

    :param email: string - E-mail

    :param password: string - Password

    :param password2: string - Repeat Password

    :return: User created information as JSON
    """

    if await User.get_user_by_email(session, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User exists')

    user.password = auth_handler.get_password_hash(user.password)
    expired_at = datetime.datetime.now(tz=None) + datetime.timedelta(days=30)
    verified_user: dict = user.dict()
    user = User(**verified_user, current_video=1, is_admin=False, is_active=True, expired_at=expired_at)
    session.add(user)
    await session.commit()

    return user


@router.post("/get_token", response_model=dict, tags=['Authentication'])
async def get_token(user: UserLogin, session: AsyncSession = Depends(get_session)):
    """Get user authorization token

    :param email: string - E-mail

    :param password: string - Password

     :return: Authorization token as JSON
    """

    user_found: User = await User.get_user_by_email(session, user.email)
    if not user_found:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    is_password_correct: bool = auth_handler.verify_password(user.password, user_found.password)
    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token: str = auth_handler.encode_token(user_found.id)

    return {"token": token}


@router.put(
    path="/{user_id}",
    response_model=UserOutput,
    dependencies=[Depends(check_access), Depends(check_user_is_admin)]
)
async def update_user(
        user_id: int,
        data: UserUpdate,
        session: AsyncSession = Depends(get_session),
):
    """
    Update user in database from optional parameters.
    For user self and admins only.

    :param username: string - Username

    :param email: string - E-mail (Unique)

    :param password: string - Password

    :param expired_at: string - Date subscribe expiration in format "2022-11-30[T]09:20[:31.777132]"

    :param is_admin: bool - Flag is user admin

    :param is_active: bool - Flag is user have active subscibe

    :param current_video: int - ID next video in database

    :return: User updated information as JSON
    """

    if not (user := await session.get(User, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_data: dict = await get_data_for_update(data.dict())

    if updated_data.get('expired_at'):
        updated_data['expired_at'] = updated_data['expired_at'].replace(tzinfo=None)

    password: str = updated_data.get('password')
    if password:
        updated_data['password'] = auth_handler.get_password_hash(password)

    email: EmailStr = updated_data.get('email')
    if email:
        if await User.get_user_by_email(session, email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    if updated_data.get('current_video') == 0:
        updated_data['current_video'] = user.current_video

    await session.execute(update(User).where(User.id == user_id).values(**updated_data))
    session.add(user)
    await session.commit()

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Delete user by user_id

    :param user_id: int - User database ID

    :return: None
    """

    if not (user := await session.get(User, user_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()

    return None


@router.get("/{user_id}/alarms", response_model=list[Alarm])
async def get_user_alarms(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get all user alarms

    :return List of alarms as JSON
    """

    alarms: Row = await session.execute(select(Alarm).join(User).where(User.id == user_id))

    return alarms.scalars().all()


@router.get("/{user_id}/notifications", response_model=list[Notification])
async def get_user_notifications(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get all user notifications

    :return List of notifications
    """

    notifications: Row = await session.execute(select(Notification).join(User).where(User.id == user_id))

    return notifications.scalars().all()


@router.get("/{user_id}/get_current_video")
async def get_user_current_video(user_id: int, session: AsyncSession = Depends(get_session)):
    """

    :param user_id: int - User database ID

    :return: User video file

    """
    user: User = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    video: Video = await session.get(Video, user.current_video)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    return FileResponse(path=video.path, media_type='video/mp4')
