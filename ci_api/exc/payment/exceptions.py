from fastapi import HTTPException, status

ApiRequestError = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="ApiServiceResponser error"
)


PaymentServiceError = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Ошибка ответа сервиса оплаты"
)

SubscribeExistsError = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Вы уже подписаны на этот тариф"
)


UserNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid user or password"
)


RateNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid rate id"

)
