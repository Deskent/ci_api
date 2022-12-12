import datetime

from loguru import logger

from exc.exceptions import (
    RateNotFound
)
from exc.payment.pay_exceptions import PaymentServiceError, SubscribeExistsError
from models.models import User, Rate, Payment
from services.rates_cache import RatesCache
from services.web_context_class import WebContext
from services.utils import get_current_datetime
from web_service.services.send_payment_request import get_payment_link
from web_service.utils.get_contexts import present_user_expired_at_day_and_month


async def _get_rate_date(user: User) -> dict:
    rates: list[Rate] = await RatesCache.get_all()
    current_rate: Rate = await RatesCache.get_by_id(user.rate_id)

    return dict(rates=rates, current_rate=current_rate)


async def get_subscribe_context(
        context: dict
) -> WebContext:
    obj = WebContext(context=context)
    user: User = obj.is_user_in_context()
    if not user:
        return obj

    api_data: dict = await _get_rate_date(user)
    obj.context.update(**api_data)
    obj.api_data.update(payload=api_data)
    obj.template = "subscribe.html"

    return obj


async def get_subscribe_by_rate_id(
        context: dict,
        rate_id: int
) -> WebContext:
    obj = WebContext(context=context)
    user: User = obj.is_user_in_context()
    if not user:
        return obj

    api_data = await _get_rate_date(user)
    obj.context.update(**api_data)
    obj.api_data.update(payload=api_data)

    rate: Rate = await RatesCache.get_by_id(rate_id)

    if await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=rate.id):
        obj.error = SubscribeExistsError.detail
        obj.template = "subscribe.html"
        obj.to_raise = SubscribeExistsError

        return obj

    link: str = await get_payment_link(user, rate)
    if not link:
        obj.error = PaymentServiceError.detail
        obj.template = "subscribe.html"
        obj.to_raise = PaymentServiceError

        return obj

    obj.redirect = link
    obj.api_data = dict(payload=link)
    return obj


async def check_payment_result(
        context: dict,
        payform_status: str,
        payform_id: int,
        payform_order_id: int,
        payform_sign: str
) -> WebContext:
    obj = WebContext(context=context)
    user: User = obj.is_user_in_context()
    if not user:
        return obj

    if payform_status != 'success':
        logger.error(
            f"\nPayform status: {payform_status}"
            f"\nPayform id: {payform_id}"
            f"\nPayform order id: {payform_order_id}"
            f"\nPayform status: {payform_sign}"
        )
        obj.error = "При попытке подписки произошла ошибка"
        obj.template = "subscribe.html"
        obj.to_raise = PaymentServiceError

        return obj

    rate_id: int = payform_order_id

    if not await RatesCache.get_by_id(rate_id):
        obj.error = "Тариф не найден",
        obj.template = "subscribe.html",
        obj.to_raise = RateNotFound

        return obj

    if not user.is_active:
        logger.debug(f"Activating user: {user.email}")
        user.rate_id = rate_id
        user.is_active = True
        user.expired_at = get_current_datetime() + datetime.timedelta(days=30)
        await user.save()

        payment: Payment = Payment(
            payment_id=payform_id, payment_sign=payform_sign,
            user_id=user.id, rate_id=user.rate_id
        )
        await payment.save()

    user.expired_at = present_user_expired_at_day_and_month(user.expired_at)
    obj.api_data = dict(payload=user)
    obj.success = "Подписка успешна оформлена"
    obj.template = "profile.html"

    return obj


async def get_cancel_subscribe_context(context: dict) -> WebContext:
    obj = WebContext(context=context)
    user: User = obj.is_user_in_context()
    if not user:
        return obj

    if user.is_active:
        user: User = await user.deactivate()

    payment: Payment = await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=user.rate_id)
    if payment:
        logger.info(f"Payment for {user.email}: {user.rate_id} wille be deleted.")
        await payment.delete()

    free_rate: Rate = await Rate.get_free()
    user.rate_id = free_rate.id
    user.expired_at = None
    user: User = await user.save()

    # TODO отписываться!!!
    obj.template = "cancel_subscribe.html"
    obj.api_data.update(payload=user)

    return obj

