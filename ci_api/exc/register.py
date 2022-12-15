from fastapi import HTTPException, status

EmailExistsError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Email exists"
)
PhoneExistsError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Phone exists"
)

SmsServiceError = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Sms service error"
)
