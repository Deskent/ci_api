import pydantic
from fastapi import Request, FastAPI
from sqladmin import Admin
from sqladmin import ModelView, expose, BaseView
from starlette.datastructures import FormData

from admin.auth import authentication_backend
from config import logger, settings
from database.db import engine
from models.models import User, Video, Complex, Rate
from schemas.complexes_videos import VideoUpload
from services.utils import upload_file, convert_seconds_to_time

ADMIN_URL = "/ci_admin"


def date_format(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")


class ComplexView(ModelView, model=Complex):
    name = "Комплекс упражнений"
    name_plural = "Комплексы упражнений"
    column_list = [Complex.id, Complex.videos, Complex.description, Complex.duration,
                   Complex.next_complex_id]
    column_labels = {
        Complex.next_complex_id: "Следующий комплекс",
        Complex.name: "Название комплекса",
        Complex.videos: "Упражнения",
        Complex.description: "Описание комплекса",
        Complex.duration: "Длительность",
    }
    form_excluded_columns = [Complex.video_count, Complex.duration]
    column_details_exclude_list = [Complex.video_count]


class UserView(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_details_exclude_list = [User.password, User.progress]
    column_list = [
        User.id, User.username, User.third_name, User.last_name, User.email, User.phone,
        User.expired_at, User.level, User.created_at, User.is_admin, User.is_active,
        User.is_verified
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
        User.is_admin: "Админ",
        User.is_active: "Подписан",
        User.is_verified: "Подтвержден",
        User.rate_id: "Тариф",
        User.gender: "Пол",
        User.alarms: "Будильники",
        User.notifications: "Оповещения",
        User.current_complex: "Текущий комплекс",
    }
    column_formatters = {
        User.expired_at: lambda m, a: date_format(m.expired_at),
        User.created_at: lambda m, a: date_format(m.expired_at),
        User.gender: lambda m, a: "Male" if m.gender else "Female"
    }
    column_formatters_detail = column_formatters
    form_columns = [*column_labels.keys(), User.gender]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.username]
    column_default_sort = [(User.expired_at, True), (User.id, True)]
    can_create = True


# class AlarmView(ModelView, model=Alarm):
#     column_list = [Alarm.id, Alarm.alarm_time, Alarm.text, Alarm.users, Alarm.weekdays]
#     can_create = False
#     can_edit = False
#
#     column_type_formatters = dict(ModelView.column_type_formatters, alarm_time=date_format)


# class NotificationView(ModelView, model=Notification):
#     column_list = [
#         Notification.id, Notification.notification_time, Notification.notification_time,
#         Notification.users
#     ]
#     can_edit = False
#     can_create = False
#
#
class VideoView(ModelView, BaseView, model=Video):
    name = "Упражнение"
    name_plural = "Упражнения"

    can_create = False
    can_edit = False
    column_list = [
        Video.id, Video.name, Video.description, Video.file_name,
        Video.complexes, Video.duration
    ]
    column_labels = {
        Video.name: "Название",
        Video.description: "Описание",
        Video.file_name: "Имя файла",
        Video.complexes: "Комплекс",
        Video.duration: "Длительность",
    }
    column_formatters = {
        Video.duration: lambda m, a: convert_seconds_to_time(m.duration)
    }


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


class UploadVideo(BaseView):
    name = "Загрузить видео упражнения"

    @expose("/upload", methods=["GET", "POST"])
    async def upload_file(self, request: Request):
        if request.method == "GET":
            # TODO разобраться с формами
            # data = dict(
            #     filename={
            #         "title": "Имя файла",
            #         "value": "123.mp3"
            #     },
            #     name="namename",
            #     description="descr1",
            #     complex_id=1
            # )
            # form = FormData(data)
            return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request},
            )
        context = {"request": request, "result": "fail"}
        try:
            form: FormData = await request.form()
            data = VideoUpload(**{k: v for k, v in form.items()})
            logger.debug(f"Load file with data: {data}")
            if video := await upload_file(**data.dict()):
                logger.debug(f"Load file with data: OK")
                context.update(result="ok", video=video)

        except pydantic.error_wrappers.ValidationError as err:
            logger.error(err)

        logger.debug(f"Load file with data: FAIL")
        return self.templates.TemplateResponse(
            "upload_video.html",
            context=context,
        )


def get_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        base_url=ADMIN_URL,
        authentication_backend=authentication_backend,
        templates_dir=settings.TEMPLATES_DIR
    )

    admin.add_view(ComplexView)
    admin.add_view(UploadVideo)
    admin.add_view(RateView)
    admin.add_view(UserView)
    admin.add_view(VideoView)
    # admin.add_view(AlarmView)
    # admin.add_view(NotificationView)

    return admin
