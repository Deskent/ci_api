import datetime
import json
from pathlib import Path
import pydantic
from fastapi import APIRouter, Body

from config import logger, settings

router = APIRouter(prefix="/payments", tags=['Payments'])


class PaymentCheck(pydantic.BaseModel):
    date: datetime.datetime
    order_id: int
    order_num: int
    sum: str
    currency: str
    customer_phone: str
    customer_extra: int
    products: list
    payment_type: str
    payment_status: str

def save_payment(data: dict):
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
    # TODO сделать в БД
    logger.debug(f"payments data_body: \n{data}")
    check = PaymentCheck(**data)
    payments_dir = settings.PAYMENTS_DIR / 'payments' / check.customer_phone
    if not payments_dir.exists():
        payments_dir.mkdir(parents=True)
    with open(payments_dir / f'{check.order_id}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        data: dict = Body()
):
    if data.get('sys') == settings.PRODAMUS_SYS_KEY:
        save_payment(data)
