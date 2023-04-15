import pydantic
from fastapi import Request, FastAPI
from sqladmin import Admin
from sqladmin import ModelView, expose, BaseView
from starlette.datastructures import FormData

from admin.auth import authentication_backend
from admin.utils import upload_file
from config import logger, settings
from crud_class.crud import CRUD
from database.db import engine
from database.models import (
    User, Video, Complex, Rate, Administrator, Payment, PaymentCheck, Avatar, Mood
)
from schemas.complexes_videos import VideoUpload
from services.utils import convert_seconds_to_time


def date_format(value):
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else "Нет подписки"


class MoodView(ModelView, model=Mood):
    name = "Настроение"
    name_plural = "Настроения"
    column_list = [
        Mood.id, Mood.name, Mood.code
    ]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class PaymentView(ModelView, model=Payment):
    name = "Платеж"
    name_plural = "Платежи"
    column_list = [
        Payment.payment_id, Payment.user_id, Payment.rate_id, Payment.payment_sign
    ]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = False
    can_export = True


class PaymentCheckView(ModelView, model=PaymentCheck):
    name = "Чек"
    name_plural = "Чеки"
    column_list = [
        PaymentCheck.customer_phone, PaymentCheck.user_id, PaymentCheck.rate_id, PaymentCheck.date
    ]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = False
    can_export = True


class ComplexView(ModelView, model=Complex):
    name = "Комплекс упражнений"
    name_plural = "Комплексы упражнений"
    column_list = [
        Complex.id, Complex.number, Complex.description, Complex.duration,
        Complex.videos
    ]
    column_labels = {
        Complex.id: "ID",
        Complex.number: "Порядковый номер",
        Complex.name: "Название комплекса",
        Complex.description: "Описание комплекса",
        Complex.duration: "Длительность",
        Complex.videos: "Упражнения",
    }
    column_formatters = {
        Complex.duration: lambda m, a: convert_seconds_to_time(m.duration),
    }
    form_excluded_columns = [Complex.video_count]
    column_details_exclude_list = [Complex.video_count]
    column_default_sort = [(Complex.number, False)]


class UserView(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_details_exclude_list = [User.password, User.progress]
    column_list = [
        User.id, User.email, User.phone, User.level, User.is_active, User.is_verified,
        User.sms_message, User.push_token, User.last_entry, User.expired_at, User.username,
        User.third_name, User.last_name, User.sms_call_code, User.email_code, User.avatar,
        User.created_at, User.mood, User.rate_id,
    ]
    column_labels = {
        User.username: "Имя",
        User.third_name: "Отчество",
        User.last_name: "Фамилия",
        User.email: "Е-мэйл",
        User.phone: "Телефон",
        User.expired_at: "Дата окончания подписки",
        User.level: "Прогресс",
        User.created_at: "Дата регистрации",
        User.last_entry: "Последний вход",
        User.is_active: "Подписан",
        User.is_verified: "Подтвержден",
        User.rate_id: "Тариф",
        User.mood: "Настроение",
        User.gender: "Пол",
        User.alarms: "Будильники",
        User.notifications: "Оповещения",
        User.current_complex: "Текущий комплекс",
        User.avatar: "ID аватара",
    }
    column_formatters = {
        User.expired_at: lambda m, a: date_format(m.expired_at),
        User.created_at: lambda m, a: date_format(m.created_at),
        User.last_entry: lambda m, a: date_format(m.last_entry),
        User.gender: lambda m, a: "Male" if m.gender else "Female"
    }
    column_formatters_detail = column_formatters
    form_columns = [*column_labels.keys(), User.gender, User.avatar]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id, User.username, User.expired_at]
    column_default_sort = [(User.expired_at, True), (User.id, True)]
    can_create = False
    # TODO дописать функцию обработки пароля после создания


class AdminView(ModelView, model=Administrator):
    name = "Администратор"
    name_plural = "Администраторы"

    column_details_exclude_list = [Administrator.password]
    column_list = [
        Administrator.id, Administrator.username, Administrator.email
    ]

    column_labels = {
        User.username: "Имя",
        User.email: "Е-мэйл",
    }
    column_sortable_list = [Administrator.id, Administrator.username, Administrator.email]
    column_default_sort = [(Administrator.id, False)]
    can_create = False
    # TODO дописать функцию обработки пароля после создания


class VideoView(ModelView, model=Video):
    name = "Упражнение"
    name_plural = "Упражнения"

    can_create = False
    column_list = [
        Video.number, Video.name, Video.description, Video.file_name,
        Video.duration
    ]
    column_labels = {
        Video.number: "Порядковый номер",
        Video.name: "Название",
        Video.description: "Описание",
        Video.file_name: "Имя файла",
        Video.complexes: "Комплекс",
        Video.duration: "Длительность",
    }
    column_formatters = {
        Video.duration: lambda m, a: convert_seconds_to_time(m.duration)
    }

    async def on_model_delete(self, model: Video):
        return await CRUD.video.delete(model)


class RateView(ModelView, model=Rate):
    name = "Тариф"
    name_plural = "Тарифы"
    column_list = [
        Rate.id, Rate.name, Rate.price, Rate.duration
    ]
    column_labels = {
        Rate.name: "Название тарифа",
        Rate.price: "Цена",
        Rate.duration: "Длительность (дней)",
    }


class AvatarView(ModelView, model=Avatar):
    name = "Аватар"
    name_plural = "Аватары"
    column_list = [
        Avatar.id, Avatar.file_name
    ]


class UploadVideo(BaseView):
    name = "Загрузить видео упражнения"

    @expose("/upload", methods=["GET", "POST"])
    async def upload_file(
            self,
            request: Request
    ):
        context = {"request": request}
        if request.method == "GET":
            # TODO разобраться с формами
            # TODO в выбор комплекс_ид вывести список всех комплексов

            return self.templates.TemplateResponse(
                "upload_video.html",
                context=context,
            )

        context.update({"result": "fail"})
        try:
            form: FormData = await request.form()
            data = VideoUpload(**{k: v for k, v in form.items()})
            logger.debug(f"Load file with data: {data}")
            if video := await upload_file(file_form=data):
                logger.debug("Load file with data: OK")
                context.update(result="ok", video=video)

        except pydantic.error_wrappers.ValidationError as err:
            logger.exception(err)
            logger.debug("Load file with data: FAIL")
        return self.templates.TemplateResponse(
            "upload_video.html",
            context=context
        )


def add_admin_views(app: FastAPI) -> None:
    admin = Admin(
        app,
        engine,
        base_url=settings.ADMIN_URL,
        authentication_backend=authentication_backend,
        templates_dir=settings.TEMPLATES_DIR / 'admin'
    )

    admin.add_view(AdminView)
    admin.add_view(UserView)
    admin.add_view(ComplexView)
    admin.add_view(VideoView)
    admin.add_view(UploadVideo)
    admin.add_view(RateView)
    admin.add_view(AvatarView)
    admin.add_view(MoodView)
    admin.add_view(PaymentView)
    admin.add_view(PaymentCheckView)
