import datetime
import json

from fastapi import APIRouter, Body, Request

from config import logger, settings, prodamus
from exc.payment.pay_exceptions import PaymentServiceError
from models.models import PaymentCheck, User

router = APIRouter(prefix="/payments", tags=['Payments'])


async def save_payment(data: dict) -> PaymentCheck:
    """
{
    "date": "2022-12-06T18:21:06+03:00", "order_id": "7975674", "order_num": "2",
    "domain": "box.payform.ru", "sum": "999.00", "currency": "rub", "customer_phone": "+1234567890",
    "customer_extra": "1", "payment_type": "Оплата картой, выпущенной в РФ", "commission": "2.9",
    "commission_sum": "28.97", "attempt": "1", "sys": "ci_api_prodamus_key", "callbackType": "json",
    "acquiring": "sbrf", "demo_mode": "1",
    "products": [
        {"name": "Солнце", "price": "999.00", "quantity": "1", "sum": "999.00"}],
    "payment_status": "success", "payment_status_description": "Успешная оплата",
    "payment_init": "manual"
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
async def payments_report_get(
        request: Request,
):
    body = await request.body()
    dec_body = body.decode()
    logger.debug(dec_body)


@router.post(
    "/report",
    status_code=200
)
async def payments_report(
        request: Request,
        data: dict = Body(...)
):
    body = await request.body()
    dec_body = body.decode()
    logger.debug(f"Body: {dec_body}")

    data_str = '\n'.join(f"{k}: {v}" for k, v in data.items())
    logger.debug(f"Payments data: \n{data_str}")
    if data.get('sys') == prodamus.PRODAMUS_SYS_KEY:
        await save_payment(data)
        save_to_file(data)


# if __name__ == '__main__':
#     a = "date=2022-12-11T00%3A00%3A00%2B03%3A00&order_id=1&order_num=test&domain=box.payform.ru&sum=1000.00&customer_phone=%2B79999999999&customer_email=email%40domain.com&customer_extra=%D1%82%D0%B5%D1%81%D1%82&payment_type=%D0%9F%D0%BB%D0%B0%D1%81%D1%82%D0%B8%D0%BA%D0%BE%D0%B2%D0%B0%D1%8F+%D0%BA%D0%B0%D1%80%D1%82%D0%B0+Visa%2C+MasterCard%2C+%D0%9C%D0%98%D0%A0&commission=3.5&commission_sum=35.00&attempt=1&sys=test&products%5B0%5D%5Bname%5D=%D0%94%D0%BE%D1%81%D1%82%D1%83%D0%BF+%D0%BA+%D0%BE%D0%B1%D1%83%D1%87%D0%B0%D1%8E%D1%89%D0%B8%D0%BC+%D0%BC%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%B0%D0%BB%D0%B0%D0%BC&products%5B0%5D%5Bprice%5D=1000.00&products%5B0%5D%5Bquantity%5D=1&products%5B0%5D%5Bsum%5D=1000.00&payment_status=success&payment_status_description=%D0%A3%D1%81%D0%BF%D0%B5%D1%88%D0%BD%D0%B0%D1%8F+%D0%BE%D0%BF%D0%BB%D0%B0%D1%82%D0%B0"

