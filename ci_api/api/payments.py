import datetime
import json
from pathlib import Path

from fastapi import APIRouter, Body

from config import logger, settings, prodamus
from crud_class.crud import CRUD
from exc.pay_exceptions import PaymentServiceError
from database.models import PaymentCheck, User
from services.utils import get_current_datetime

router = APIRouter(prefix="/payments", tags=['Payments'])


async def save_payment(data: dict) -> PaymentCheck:
    """
    Add to payment_check data user.id, user.email and rate.it.
    Save payment_check to DB. Return instance.

    """

    user_id = int(data.pop('customer_extra'))
    if not user_id:
        raise PaymentServiceError
    user: User = await CRUD.user.get_by_id(user_id)
    data['user_id'] = user.id
    if not data.get('customer_email'):
        data['customer_email'] = user.email
    data['rate_id'] = int(data.pop('order_num'))
    check = await CRUD.payment_check.create(data)
    logger.debug(f"Check created: {check.dict()}")
    user.expired_at = check.date
    await CRUD.user.save(user)

    return check


def save_payment_check_to_json(data: dict):
    """Save payment check to json file"""

    current_date: datetime.date = get_current_datetime().date()
    payments_dir: Path = settings.PAYMENTS_DIR / data['customer_phone'] / str(current_date)
    if not payments_dir.exists():
        payments_dir.mkdir(parents=True)
    with open(payments_dir / f'{data["order_id"]}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        data: dict = Body(...)
):
    data_str = '\n'.join(f"{k}: {v}" for k, v in data.items())
    logger.debug(f"Payments data: \n{data_str}")
    if data.get('sys') == prodamus.PRODAMUS_SYS_KEY:
        await save_payment(data)
        save_payment_check_to_json(data)
