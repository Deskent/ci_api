import json

from fastapi import APIRouter

from config import logger, settings

router = APIRouter(prefix="/payments", tags=['Payments'])


@router.post(
    "/report",
    status_code=200
)
async def payments(
        data: dict,
):
    logger.debug(f"payments data: {data}")
    with open(settings.LOGS_DIR / 'payments.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
