titles = {
    ('index.html', 'entry.html', 'entry', 'index'): {
        'title': 'Вход',
        'head_title': 'Добро пожаловать'
    },
    ('profile', 'profile.html'): {
        'title': 'Личный кабинет', 'head_title': 'Профиль'
    },
    ('edit_profile.html', 'edit_profile'): {
        'title': 'Профиль',
        'head_title': 'Редактирование профиля'
    },
    ('check_email_code', 'check_email.html', 'check_email'): {
        'title': 'Верификация почты',
        'head_title': 'Верификация почты'
    },
    ('startCharging.html', 'videos_list.html'): {
        'title': 'Зарядка',
        'head_title': 'Зарядка'
    },
    ('subscribe.html',): {
        'title': 'Подписка', 'head_title': 'Подписка'
    },
    ('cancel_subscribe.html',): {
        'title': 'Отмена подписки',
        'head_title': 'Отмена подписки'
    },
    ('come_tomorrow.html',): {
        'title': 'Приходите завтра',
        'head_title': 'Приходите завтра'
    },
    ('new_level.html',): {
        'title': 'Новый уровень', 'head_title': 'Новый уровень'
    },
    ('complexes_list.html',): {
        'title': 'Комплексы', 'head_title': 'Комплексы'
    },
    ('registration.html',): {
        'title': 'Регистрация', 'head_title': 'Регистрация'
    },
    ('forget_password.html', 'forget_password', 'forget1', 'forget1.html'): {
        'title': 'Забыли пароль', 'head_title': 'Восстановление пароля'
    },
    ('notifications.html',): {
        'title': 'Уведомления', 'head_title': 'Уведомления'
    },
    ('entry_sms.html', 'forget2.html', 'forget3.html'): {
        'title': 'Вход по смс/звонку',
        'head_title': 'Вход по смс/звонку'
    },
    ('payment_report.html',): {
        'title': 'История транзакций',
        'head_title': 'История транзакций'
    },
    ('entry_via_phone.html', 'entry_via_phone.html'): {
        'title': 'Вход по номеру телефона',
        'head_title': 'Вход по номеру телефона'
    },
    ('error_page.html', ): {
        'title': 'Ошибка',
        'head_title': 'Ошибка'
    },
}


def _get_titles(endpoint_name: str) -> dict:
    """Return titles via endpoint name"""

    for names, values in titles.items():
        if endpoint_name in names:
            return values


def get_page_titles(context: dict, endpoint_name: str) -> dict:
    title: dict = _get_titles(endpoint_name)
    if not title:
        title: dict = _get_titles('index.html')

    context.update(title=title['title'], head_title=title['head_title'])

    return context
