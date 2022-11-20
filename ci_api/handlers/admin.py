from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.db import get_session
from models.models import User
from services.depends import is_user_admin

router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[Depends(is_user_admin)])


@router.get("/", response_model=list[User], dependencies=[Depends(is_user_admin)])
async def get_users(
        session: AsyncSession = Depends(get_session)
):
    """
    Get all users from database. For admins only.

    :return: List of users as JSON
    """

    users = await session.execute(select(User).order_by(User.id))

    return users.scalars().all()
