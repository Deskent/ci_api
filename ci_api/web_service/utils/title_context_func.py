# TODO отрефакторить (убрать классы, сделать словарь с туплом names)

class WebTitle:
    def __init__(self, name: str, title: str, head_title: str):
        self.name: str = name
        self.title: str = title
        self.head_title: str = head_title
        self.names: list[str] = [name]

    def add_name(self, value: str) -> 'WebTitle':
        self.names.append(value)
        return self

    def add_names(self, *args) -> 'WebTitle':
        self.names.extend(list(args))
        return self


class TitleStorage:
    """Singleton"""

    __INSTANCE: 'TitleStorage' = None
    __titles: list[WebTitle] = []

    def __new__(cls, *args, **kwargs) -> 'TitleStorage':
        if cls.__INSTANCE is None:
            cls.__INSTANCE = super().__new__(cls)

        return cls.__INSTANCE

    @classmethod
    def add_title(cls, title: WebTitle):
        cls.__titles.append(title)

    @classmethod
    def get_title(cls, name: str) -> WebTitle:
        for title in cls.__titles:
            if name in title.names:
                return title


index = WebTitle(
    name="index.html",
    title="Вход",
    head_title="Добро пожаловать"
).add_names("entry.html", "entry", "index")

profile = WebTitle(
    name="profile",
    title="Личный кабинет",
    head_title="Профиль"
).add_name("profile.html")

check_email = WebTitle(
    name="check_email_code",
    title="Верификация почты",
    head_title="Верификация почты"
).add_names("check_email.html", "check_email")

charge = WebTitle(
    name="startCharging.html",
    title="Зарядка",
    head_title="Зарядка"
).add_name("videos_list.html")

subscribe = WebTitle(
    name="subscribe.html",
    title="Подписка",
    head_title="Подписка"
)
cancel_subscribe = WebTitle(
    name="cancel_subscribe.html",
    title="Отмена подписки",
    head_title="Отмена подписки"
)

come_tomorrow = WebTitle(
    name="come_tomorrow.html",
    title="Приходите завтра",
    head_title="Приходите завтра"
)

new_level = WebTitle(
    name="new_level.html",
    title="Новый уровень",
    head_title="Новый уровень"
)

complexes_list = WebTitle(
    name="complexes_list.html",
    title="Комплексы",
    head_title="Комплексы"
)

register = WebTitle(
    name="registration.html",
    title="Регистрация",
    head_title="Регистрация"
)

edit_profile = WebTitle(
    name="edit_profile.html",
    title="Профиль",
    head_title="Редактирование профиля"
).add_name('edit_profile')

forget_password = WebTitle(
    name="forget_password.html",
    title="Забыли пароль",
    head_title="Восстановление пароля"
).add_names('forget_password', 'forget1', 'forget1.html')

notifications = WebTitle(
    name="notifications.html",
    title="Уведомления",
    head_title="Уведомления"
)

entry_sms = WebTitle(
    name="entry_sms.html",
    title="Вход по смс/звонку",
    head_title="Вход по смс/звонку"
).add_names("forget2.html", "forget3.html")

entry_via_phone = WebTitle(
    name="entry_via_phone.html",
    title="Вход по номеру телефона",
    head_title="Вход по номеру телефона"
).add_name("entry_via_phone.html")

payment_report = WebTitle(
    name="payment_report.html",
    title="История транзакций",
    head_title="История транзакций"
)


titles: tuple[WebTitle, ...] = (
    index,
    profile,
    edit_profile,
    check_email,
    charge,
    subscribe,
    cancel_subscribe,
    come_tomorrow,
    new_level,
    complexes_list,
    register,
    forget_password,
    notifications,
    entry_sms,
    payment_report,
    entry_via_phone,
)


def create_titles():
    for elem in titles:
        TitleStorage.add_title(elem)


def update_title(context: dict, key: str) -> dict:
    web_title: WebTitle = TitleStorage.get_title(key)
    if web_title:
        context.update(title=web_title.title, head_title=web_title.head_title)

    return context


create_titles()
