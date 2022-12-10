import datetime
import json
from typing import Any

from fastapi import APIRouter, Body, Request, Query

from config import logger, settings
from exc.payment.pay_exceptions import PaymentServiceError
from models.models import PaymentCheck, User

router = APIRouter(prefix="/payments", tags=['Payments'])


async def save_payment(data: dict) -> PaymentCheck:
    """
    {
    'date': '2022-12-06T18:21:06+03:00', 'order_id': '7975674', 'order_num': '2',
    'domain': 'box.payform.ru', 'sum': '999.00', 'currency': 'rub', 'customer_phone': '+1234567890',
    'customer_extra': '1', 'payment_type': 'Оплата картой, выпущенной в РФ', 'commission': '2.9',
    'commission_sum': '28.97', 'attempt': '1', 'sys': 'ci_api_prodamus_key', 'callbackType': 'json',
    'acquiring': 'sbrf', 'demo_mode': '1',
    'products': [
        {'name': 'Солнце', 'price': '999.00', 'quantity': '1', 'sum': '999.00'}],
    'payment_status': 'success', 'payment_status_description': 'Успешная оплата', 'payment_init': 'manual'
    }
    :param data:
    :return:
    """

    user_id = int(data.pop('customer_extra'))
    if not user_id:
        raise PaymentServiceError
    user: User = await User.get_by_id(user_id)
    data['user_id'] = user.id
    if not data.get('customer_email'):
        data['customer_email'] = user.email
    data['rate_id'] = int(data.pop('order_num'))
    check = await PaymentCheck().create(data)
    logger.debug(f"Check created: {check.dict()}")
    user.expired_at = check.date
    await user.save()

    return check

def save_to_file(data: dict):
    current_date = datetime.datetime.now(tz=None).date()
    payments_dir = settings.PAYMENTS_DIR / data['customer_phone'] / str(current_date)
    if not payments_dir.exists():
        payments_dir.mkdir(parents=True)
    with open(payments_dir / f'{data["order_id"]}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.get(
    "/report",
    status_code=200
)
def payments_report_get(
        args: list = Query(...)
):
    logger.debug(*args)


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        data: dict = Body(...)
):
    data_str = '\n'.join(f"{k}: {v}" for k, v in data.items())
    logger.debug(f"Payments data: \n{data_str}")
    if data.get('sys') == settings.PRODAMUS_SYS_KEY:
        await save_payment(data)
        save_to_file(data)
