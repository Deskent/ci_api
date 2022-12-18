from typing import Type

from models.models import (
    User, Avatar, Alarm, Notification, Complex, Video,
    ViewedComplex, ViewedVideo, Administrator,
    Rate, Payment, PaymentCheck
)

TYPES = (
        User | Avatar | Alarm | Notification | Complex | Video | ViewedComplex
        | ViewedVideo | Administrator | Rate | Payment | PaymentCheck
)
MODEL_TYPES = Type[TYPES]
