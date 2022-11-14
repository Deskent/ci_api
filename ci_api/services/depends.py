from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from services.auth import AuthHandler
from database.db import get_session
from models.models import User

auth_handler = AuthHandler()


async def check_user_exists(
        email: EmailStr,
        password: str,
        session: AsyncSession = Depends(get_session)
):
    user: User = await User.get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail='Incorrect username or password')

    is_password_correct: bool = auth_handler.verify_password(password, user.password)
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    return user


async def get_logged_user(
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> User:
    user: User = await session.get(User, logged_user)
    if user:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail='Incorrect username or password')


async def is_user_active(user: User = Depends(get_logged_user)):
    if user.is_active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail='User expired')


# async def check_access(
#         user_id: int,
#         logged_user: int = Depends(auth_handler.auth_wrapper),
#         session: AsyncSession = Depends(get_session)
# ) -> None:
#     user: User = await session.get(User, logged_user)
#     if user.is_admin:
#         print("\nUser:", user.username, "ID:", user.id, "IS ADMIN")
#         return None
#     if user_id != logged_user:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')


async def check_user_is_admin(
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> User:
    user: User = await session.get(User, logged_user)
    print(user.username, user.is_admin)
    if user.is_admin:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied!')

