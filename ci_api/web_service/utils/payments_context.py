import datetime

from loguru import logger

from exc.exceptions import RateNotFound
from exc.payment.pay_exceptions import PaymentServiceError, SubscribeExistsError
from models.models import User, Rate, Payment
from services.models_cache.crud import CRUD
from services.utils import get_current_datetime
from services.web_context_class import WebContext
from web_service.services.send_payment_request import get_payment_link
from web_service.utils.get_contexts import present_user_expired_at_day_and_month


async def _get_rate_date(user: User) -> dict:
    rates: list[Rate] = await CRUD.rate.get_all()
    current_rate: Rate = await CRUD.rate.get_by_id(user.rate_id)

    return dict(rates=rates, current_rate=current_rate)


async def get_subscribe_context(
        context: dict
) -> WebContext:
    web_context = WebContext(context=context)
    user: User = web_context.is_user_in_context()
    if not user:
        return web_context

    api_data: dict = await _get_rate_date(user)
    web_context.context.update(**api_data)
    web_context.api_data.update(payload=api_data)
    web_context.template = "subscribe.html"

    return web_context


async def get_subscribe_by_rate_id(
        context: dict,
        rate_id: int
) -> WebContext:
    web_context = WebContext(context=context)
    user: User = web_context.is_user_in_context()
    if not user:
        return web_context

    api_data: dict = await _get_rate_date(user)
    web_context.context.update(**api_data)
    web_context.api_data.update(payload=api_data)

    rate: Rate = await CRUD.rate.get_by_id(rate_id)

    if await Payment.get_by_user_and_rate_id(user_id=user.id, rate_id=rate.id):
        web_context.error = SubscribeExistsError.detail
        web_context.template = "subscribe.html"
        web_context.to_raise = SubscribeExistsError

        return web_context

    link: str = await get_payment_link(user, rate)
    if not link:
        web_context.error = PaymentServiceError.detail
        web_context.template = "subscribe.html"
        web_context.to_raise = PaymentServiceError

        return web_context

    web_context.redirect = link
    web_context.api_data.update(payload=dict(link=link))
    return web_context


async def check_payment_result(
        context: dict,
        payform_status: str,
        payform_id: int,
        payform_order_id: int,
        payform_sign: str
) -> WebContext:
    web_context = WebContext(context=context)
    user: User = web_context.is_user_in_context()
    if not user:
        return web_context

    if payform_status != 'success':
        logger.error(
            f"\nPayform status: {payform_status}"
            f"\nPayform id: {payform_id}"
            f"\nPayform order id: {payform_order_id}"
            f"\nPayform status: {payform_sign}"
        )
        web_context.error = "При попытке подписки произошла ошибка"
        web_context.template = "subscribe.html"
        web_context.to_raise = PaymentServiceError

        return web_context

    rate_id: int = payform_order_id

    if not await CRUD.rate.get_by_id(rate_id):
        web_context.error = "Тариф не найден",
        web_context.template = "subscribe.html",
        web_context.to_raise = RateNotFound

        return web_context

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
    web_context.api_data.update(payload=user)
    web_context.success = "Подписка успешна оформлена"
    web_context.template = "profile.html"

    return web_context


async def get_cancel_subscribe_context(context: dict) -> WebContext:
    web_context = WebContext(context=context)
    user: User = web_context.is_user_in_context()
    if not user:
        return web_context

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
    web_context.template = "cancel_subscribe.html"
    web_context.api_data.update(payload=user)

    return web_context

