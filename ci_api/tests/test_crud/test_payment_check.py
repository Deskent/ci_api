import pytest

from api.payments import save_payment
from models.models import PaymentCheck

@pytest.mark.skip("Manual")
async def test_save_payment():
    data = {
        'date': '2022-12-06T18:21:06+03:00', 'order_id': '7975674', 'order_num': '2',
        'domain': 'box.payform.ru', 'sum': '999.00', 'currency': 'rub',
        'customer_phone': '+1234567890',
        'customer_extra': '1', 'payment_type': 'Оплата картой, выпущенной в РФ',
        'commission': '2.9',
        'commission_sum': '28.97', 'attempt': '1', 'sys': 'ci_api_prodamus_key',
        'callbackType': 'json',
        'acquiring': 'sbrf', 'demo_mode': '1',
        'products': [
            {'name': 'Солнце', 'price': '999.00', 'quantity': '1', 'sum': '999.00'}],
        'payment_status': 'success', 'payment_status_description': 'Успешная оплата',
        'payment_init': 'manual'
    }
    check = await save_payment(data)
    assert check is not None


@pytest.mark.skip("Manual")
async def test_get_all_checks_by_user_id():
    user_id = 1
    checks: list[PaymentCheck] = await PaymentCheck.get_all_by_user_id(user_id)
    assert checks is not None
