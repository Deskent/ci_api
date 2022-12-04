import json

from fastapi import APIRouter, Body

from config import logger, settings

router = APIRouter(prefix="/payments", tags=['Payments'])


async def save_payment(data):
    logger.debug(f"payments data_body: \n{data}")
    order_id = data['order_id']
    payments_dir = settings.LOGS_DIR / 'payments'
    if not payments_dir.exists():
        payments_dir.mkdir()
    with open(payments_dir / f'payments_{order_id}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        data: dict = Body()
):
    if data.get('sys') == settings.PRODAMUS_SYS_KEY:
        await save_payment(data)

