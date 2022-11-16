from fastapi import Request
from sqladmin import ModelView, expose, BaseView
from starlette.datastructures import FormData

from models.models import User, Video, Alarm, Notification, Complex
from services.utils import upload_file
from schemas.complexes_videos import VideoUpload
from config import logger


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


class AlarmView(ModelView, model=Alarm):
    column_list = [Alarm.id, Alarm.alarm_time, Alarm.text, Alarm.users, Alarm.weekdays]
    can_create = False
    can_edit = False


class NotificationView(ModelView, model=Notification):
    column_list = [
        Notification.id, Notification.notification_time, Notification.notification_time,
        Notification.users
    ]
    can_edit = False
    can_create = False


class ComplexView(ModelView, model=Complex):
    name_plural = "Комплексы"
    column_list = [Complex.id, Complex.name, Complex.videos, Complex.description,
                   Complex.next_complex_id]
    column_labels = {Complex.name: "Name"}


class VideoView(ModelView, BaseView, model=Video):
    can_create = False
    column_list = [
        Video.id, Video.name, Video.description, Video.file_name, Video.complexes, Video.duration
    ]


class UploadVideo(BaseView):
    name = "Upload Video"

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
        if await upload_file(**data.dict()):
            logger.debug(f"Load file with data: OK")
            return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request, "result": "ok"},
            )

        logger.debug(f"Load file with data: FAIL")
        return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request, "result": "fail"},
            )
