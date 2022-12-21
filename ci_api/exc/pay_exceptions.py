from fastapi import HTTPException
from starlette import status

PaymentServiceError = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Ошибка ответа сервиса оплаты"
)
SubscribeExistsError = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Вы уже подписаны на этот тариф"
)
