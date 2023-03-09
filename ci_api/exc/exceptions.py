from fastapi import HTTPException, status

ApiRequestError = HTTPException(
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    detail="ApiServiceResponser error"
)

UserNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid user or password"
)

UserNotFoundErrorApi = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid user or password"
)

ComplexNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Complex not found"
)

VideoNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Video not found"
)

RateNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Invalid rate id"
)

AlarmNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Alarm not found"
)

NotificationNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Notification not found"
)

FileNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="File not found"
)

PhoneNumberError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid phone number"
)

EmailError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid email"
)

PasswordMatchError = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Passwords does not match"
)

SmsCodeNotValid = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid sms code"
)


class UserNotLoggedError(Exception):
    pass


class ComeTomorrowException(Exception):
    pass
