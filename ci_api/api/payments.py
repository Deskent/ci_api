import json

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from database.db import get_db_session

router = APIRouter(prefix="/payments", tags=['Payments'])


@router.post(
    "/",
    status_code=200
)
async def payments(
        data: dict,
        session: AsyncSession = Depends(get_db_session)
):
    logger.debug(f"payments data: {data}")
    with open('payments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

