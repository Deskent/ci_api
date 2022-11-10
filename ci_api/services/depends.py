from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth import AuthHandler
from database.db import get_session
from models.models import User

auth_handler = AuthHandler()


async def get_logged_user(
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> User:

    user: User = await session.get(User, logged_user)
    if user:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='Incorrect username or password')


async def check_access(
        user_id: int,
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> None:

    user: User = await session.get(User, logged_user)
    if user.is_admin:
        print("\nUser:", user.username, "ID:", user.id, "IS ADMIN")
        return None
    if user_id != logged_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')


async def check_user_is_admin(
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> None:
    user: User = await session.get(User, logged_user)
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied!')

