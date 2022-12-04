import json

import requests
from fastapi import Depends
from loguru import logger

from config import settings
from exc.payment.exceptions import PaymentServiceError, UserNotFoundError, RateNotFound
from models.models import User, Rate, Payment
from web_service.utils import get_full_context


async def subscribe_context(
        context: dict = Depends(get_full_context),

):
    if not (user := context.get('user')):
        context.update(template="entry.html", to_raise=UserNotFoundError)
        return context

    rates: list[Rate] = await Rate.get_all()
    current_rate: Rate = await Rate.get_by_id(user.rate_id)
    api_data = dict(rates=rates, current_rate=current_rate)
    context.update(template="subscribe.html", **api_data, api_data=api_data)

    return context


async def get_subscribe_by_rate_id(
        rate_id: int,
        context: dict = Depends(get_full_context),
):
    user: User = context['user']
    rate: Rate = await Rate.get_by_id(rate_id)

    if await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=rate.id):
        context.update(
            error=PaymentServiceError.detail,
            template="subscribe.html",
            to_raise=PaymentServiceError
        )

        return context
    link: str = get_payment_link(user, rate)
    if link:
        context.update(redirect=link, api_data=dict(payload=link))
        return context
    context.update(
        error=PaymentServiceError.detail,
        template="subscribe.html",
        to_raise=PaymentServiceError
    )

    return context


async def check_payment_result(
        context: dict = Depends(get_full_context),
        _payform_status: str = None,
        _payform_id: int = None,
        _payform_order_id: int = None,
        _payform_sign: str = None
):

    if _payform_status != 'success':
        logger.error(
            f"\nPayform status: {_payform_status}"
            f"\nPayform id: {_payform_id}"
            f"\nPayform order id: {_payform_order_id}"
            f"\nPayform status: {_payform_sign}"
        )
        context.update(
            error="При попытке подписки произошла ошибка",
            template="subscribe.html",
            to_raise=PaymentServiceError
        )
        return context
    rate_id: int = _payform_order_id

    if not await Rate.get_by_id(rate_id):
        context.update(
            error="Тариф не найден",
            template="subscribe.html",
            to_raise=RateNotFound
        )
        return context

    user: User = context['user']
    if not user.is_active:
        logger.debug(f"Activating user: {user.email}")
        user.rate_id = rate_id
        user.is_active = True
        await user.save()

        payment: Payment = Payment(
            payment_id=_payform_id, payment_sign=_payform_sign,
            user_id=user.id, rate_id=user.rate_id
        )
        await payment.save()

    api_data = dict(payload=user)
    context.update(
        success="Подписка успешна оформлена",
        template="profile.html",
        api_data=api_data
    )
    return context


def get_payment_link(user: User, rate: Rate) -> str:
    params: str = (
        f"&order_id={rate.id}"
        f"&customer_phone={user.phone}"
        f"&customer_extra={user.id}"
        f"&order_sum={rate.price}"
        f"&products[0][price]={rate.price}"
        f"&products[0][quantity]=1"
        f"&products[0][name]={rate.name}"
        f"&demo_mode=1"  # TODO  <- ТЕСТОВЫЙ РЕЖИМ!
    )

    url = (
        f"https://box.payform.ru/?"
        f"do=link"
        f"&type=json"
        f"&callbackType=json"
        f"&currency=rub"
        f"&acquiring=sbrf"
        f"&sys={settings.PRODAMUS_SYS_KEY}"
    )
    url += params
    headers = {
        "Content-type": "text/plain",
        "charset": "utf-8"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data: dict = response.json()
            return data['payment_link']
        except json.JSONDecodeError as err:
            logger.error(f"Json error: {err}")

    return ''
