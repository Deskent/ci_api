from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTasks

from config import logger
from database.db import get_db_session
from models.models import User
from schemas.user import UserRegistration, UserLogin, UserChangePassword
from services.depends import get_logged_user
from services.emails import verify_token_from_email
from services.user import register_new_user

router = APIRouter(prefix="/auth", tags=['Authorization'])


@router.post("/register", response_model=User)
async def register(
        user_data: UserRegistration,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Create new user in database if not exists

    :param username: string - Username

    :param last_name: Optional[string] - User last name

    :param third_name: Optional[string] - User middle name (Отчество)

    :param email: string - E-mail

    :param phone: string - Phone number in format: 9998887766

    :param password: string - Password

    :param password2: string - Repeat Password

    :param rate_id: int - Rate id (тариф)

    :param gender: bool - True = male, False - female

    :return: User created information as JSON
    """

    user, errors = await register_new_user(session, user_data)
    if user:
        return user
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors['error']
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='New user registration unrecognized error'
    )


@router.get("/verify_email", status_code=status.HTTP_202_ACCEPTED)
async def verify_email_token(
        token: str,
        session: AsyncSession = Depends(get_db_session)
):
    user_id: str = await verify_token_from_email(token=token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid token")
    user: User = await session.get(User, user_id)
    if user and not user.is_verified:
        user.is_verified = True
        await user.save(session)
        logger.info(f"User with id {user.id} verified")
    logger.debug(f"Verify email token: OK")

    return user


@router.post("/login", response_model=dict)
async def login(
        user: UserLogin,
        session: AsyncSession = Depends(get_db_session)
):
    """Get user authorization token

    :param email: string - E-mail

    :param password: string - Password

     :return: Authorization token as JSON
    """
    user_found: User = await User.get_by_email(session, user.email)
    if not user_found:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    if not await user_found.is_password_valid(user.password):
        logger.info(f"User with email {user.email} type wrong password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    token: str = await user_found.get_user_token()
    logger.info(f"User with id {user_found.id} got Bearer token")

    return {"token": token}


@router.put("/change_password", status_code=status.HTTP_202_ACCEPTED)
async def change_password(
        data: UserChangePassword,
        user: User = Depends(get_logged_user),
        session: AsyncSession = Depends(get_db_session)
):
    """
    Change password

    :param old_password: string - Old password

    :param password: string - new password

    :param password2: string - Repeat new password

    :return: None
    """
    if not await user.is_password_valid(data.old_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    user.password = await user.get_hashed_password(data.password)
    await user.save(session)
    logger.info(f"User with id {user.id} change password")
