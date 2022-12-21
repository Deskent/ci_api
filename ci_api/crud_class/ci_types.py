from typing import Type

from database.models import (
    User, Avatar, Alarm, Notification, Complex, Video,
    ViewedComplex, ViewedVideo, Administrator,
    Rate, Payment, PaymentCheck, Mood
)

TYPES = (
        User | Avatar | Alarm | Notification | Complex | Video | ViewedComplex
        | ViewedVideo | Administrator | Rate | Payment | PaymentCheck | Mood
)
MODEL_TYPES = Type[TYPES]
