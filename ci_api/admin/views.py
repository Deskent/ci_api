from fastapi import Request, FastAPI
from sqladmin import Admin
from sqladmin import ModelView, expose, BaseView
from starlette.datastructures import FormData

from admin.auth import authentication_backend
from config import logger, settings
from database.db import engine
from models.models import User, Video, Alarm, Notification, Complex, Rate
from schemas.complexes_videos import VideoUpload
from services.utils import upload_file

ADMIN_URL = "/ci_admin"


class ComplexView(ModelView, model=Complex):
    name_plural = "Комплексы упражнений"
    column_list = [Complex.id, Complex.videos, Complex.description,  Complex.duration,
                   Complex.next_complex_id]
    column_labels = {
        Complex.videos: "Упражнения",
        Complex.description: "Описание комплекса",
        Complex.duration: "Длительность",
        Complex.next_complex_id: "Следующий комплекс"
    }
    form_excluded_columns = [Complex.video_count]


class UserView(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"
    column_details_exclude_list = [User.password]
    form_excluded_columns = [User.password]
    column_list = [
        User.id, User.username, User.email, User.current_complex,
        User.level, User.progress, User.notifications, User.alarms, User.is_admin, User.is_active,
        User.is_verified
    ]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.username]
    can_create = False


# class AlarmView(ModelView, model=Alarm):
#     column_list = [Alarm.id, Alarm.alarm_time, Alarm.text, Alarm.users, Alarm.weekdays]
#     can_create = False
#     can_edit = False
#
#
# class NotificationView(ModelView, model=Notification):
#     column_list = [
#         Notification.id, Notification.notification_time, Notification.notification_time,
#         Notification.users
#     ]
#     can_edit = False
#     can_create = False
#
#
# class VideoView(ModelView, BaseView, model=Video):
#     can_create = False
#     column_list = [
#         Video.id, Video.name, Video.description, Video.file_name, Video.complexes, Video.duration
#     ]


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
    name = "Загрузить видео"

    @expose("/upload", methods=["GET", "POST"])
    async def upload_file(self, request: Request):
        if request.method == "GET":
            return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request},
            )
        form: FormData = await request.form()
        data = VideoUpload(**{k: v for k, v in form.items()})
        logger.debug(f"Load file with data: {data}")
        if video := await upload_file(**data.dict()):
            logger.debug(f"Load file with data: OK")
            return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request, "result": "ok", "video": video},
            )

        logger.debug(f"Load file with data: FAIL")
        return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request, "result": "fail"},
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
    # admin.add_view(VideoView)
    # admin.add_view(AlarmView)
    # admin.add_view(NotificationView)

    return admin
