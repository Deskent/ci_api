import json

from fastapi import APIRouter

from config import logger, settings

router = APIRouter(prefix="/payments", tags=['Payments'])


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        data: dict,
):
    logger.debug(f"payments data: {data}")
    with open(settings.LOGS_DIR / 'payments.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.post(
    "/report_fail",
    status_code=200
)
async def report_fail(
        data: dict,
):
    logger.debug(f"payments data: {data}")
    with open(settings.LOGS_DIR / 'payments_fail.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
