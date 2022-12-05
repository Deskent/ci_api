def update_context_title(context: dict, key: str) -> dict:
    data = {
        "password_recovery": {
            "title": "Восстановление пароля",
            "head_title": "Восстановление пароля",
        },
        "sms_recovery": {
            "title": "Вход по телефону/sms",
            "head_title": "Вход по телефону/sms",
        },
        "check_email_code": {
            "title": "Верификация почты",
            "head_title": "Верификация почты",
        },
        "profile.html": {
            "title": "Личный кабинет",
            "head_title": "Профиль",
        },
        "entry": {
            "title": "Вход",
            "head_title": "Добро пожаловать",
        },
        "subscribe.html": {
            "title": "Подписка",
            "head_title": "Подписка",
        },
        "cancel_subscribe.html": {
            "title": "Отмена подписка",
            "head_title": "Отмена подписки",
        },

    }
    title: dict = data.get(key)
    if title:
        context.update(title=title['title'], head_title=title['head_title'])

    return context
