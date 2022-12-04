import json
from typing import Any

from fastapi import APIRouter, Body, Request

from config import logger, settings

router = APIRouter(prefix="/payments", tags=['Payments'])


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        request: Request,
):
    try:
        data = await request.json()
    except:
        logger.debug("JSON ERROR")
        data = await request.body()
    logger.debug(f"payments data: \n{data}")

    # with open(settings.LOGS_DIR / 'payments.json', 'a', encoding='utf-8') as f:
    #     json.dump(data, f, ensure_ascii=False, indent=4)
