    /api/v1

    GET /profiles - список профилей ?
    POST /profiles - создать профиль пользователя
    GET /profiles/{id} - получить профиль пользователя
    PUT /profiles/{id} - обновить профиль пользователя
    DELETE /profiles/{id} - удалить профиль пользователя


    /api/v1/profiles/{id}

    GET /alarms - получить список алармов пользователя
    POST /alarms - создать аларм для пользователя
    GET /alarms/{id} - получить аларм пользователя
    PUT /alarms/{id} - обновить аларм пользователя
    DELETE /alarms/{id} - удалить аларм пользователя


    /api/v1/profiles/{id}

    GET /videos - список видео
    GET /videos/next - пометить что видео просмотрено
    POST /videos - создать видео пользователя
    GET /videos/{id} - получить видео пользователя
    PUT /videos/{id} - обновить видео пользователя
    DELETE /videos/{id} - удалить видео пользователя



    OLD
    Get Post /api/v1/myProfiles/ — профили пользователей
    Get Put /api/v1/me/1/ — мой профиль
    Get Post /api/v1/notifications/ — уведомления
    Get /api/v1/notification/1/ — уведомление
    Get Post /api/v1/chargers/ — зарядки
    Get Post /api/v1/charger/1/ — зарядка
    Get Post Put /api/v1/alarm/1/ — будильник
    Get Delete /api/v1/alarm_delete/1/ — будильник удаление
