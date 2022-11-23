from fastapi import HTTPException, status, Depends
from pydantic import EmailStr
from sqlalchemy import select

from database.db import get_session, AsyncSession
from services.auth import auth_handler
from models.models import User, Administrator


async def get_logged_user(
        logged_user: int = Depends(auth_handler.auth_wrapper),
        session: AsyncSession = Depends(get_session)
) -> User:
    """Returns authenticated with Bearer user instance"""

    if user := await session.get(User, logged_user):
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='Incorrect username or password')


async def check_admin_credentials(
        email: EmailStr,
        password: str
) -> Administrator:
    """Check user and password is correct. Return user instance"""

    async for session in get_session():
        query = select(Administrator).where(Administrator.email == email)
        response = await session.execute(query)
        user = response.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Incorrect username or password')

        is_password_correct: bool = auth_handler.verify_password(password, user.password)
        if not is_password_correct:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

        return user


async def is_user_active(
        user: User = Depends(get_logged_user)
) -> User:
    """Check user have active subscribe in database"""

    if user.is_active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='User expired.')


async def is_user_verified(
        user: User = Depends(get_logged_user)
) -> User:
    """Check user email is verified in database"""

    if user.is_verified:
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is not verified yet.')
