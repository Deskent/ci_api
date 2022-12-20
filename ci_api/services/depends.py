from fastapi import HTTPException, status, Depends
from fastapi import Request

from models.models import User, Administrator
from schemas.user_schema import UserLogin
from services.auth import auth_handler
from crud_class.crud import CRUD


async def get_logged_user(
        logged_user: int = Depends(auth_handler.auth_wrapper),
) -> User:
    """Returns authenticated with Bearer user instance"""

    if user := await CRUD.user.get_by_id(logged_user):
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail='Incorrect username or password')


async def check_admin_credentials(user_data: UserLogin) -> Administrator:
    """Check user and password is correct. Return user instance"""

    admin: Administrator = await CRUD.admin.get_by_email(user_data.email)
    if not admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail='Incorrect username or password')

    is_password_correct: bool = await CRUD.admin.is_password_valid(admin, user_data.password)
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')

    return admin


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

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='User is not verified yet.'
    )


async def get_context_with_request(
        request: Request
) -> dict:
    return {"request": request}
