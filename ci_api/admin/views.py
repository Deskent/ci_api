from fastapi import Request, UploadFile, File
from sqladmin import ModelView, expose, BaseView
from starlette.datastructures import FormData

from models.models import User, Video, Alarm, Notification, Complex
from services.utils import upload_file
from schemas.complexes_videos import VideoUpload


class UserView(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    column_details_exclude_list = [User.password]
    column_list = [
        User.id, User.username, User.email, User.current_complex,
        User.level, User.progress, User.notifications, User.alarms, User.is_admin, User.is_active,
        User.is_verified
    ]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.username]


class AlarmView(ModelView, model=Alarm):
    column_list = [Alarm.id, Alarm.alarm_time, Alarm.text, Alarm.users, Alarm.weekdays]


class NotificationView(ModelView, model=Notification):
    column_list = [
        Notification.id, Notification.notification_time, Notification.notification_time,
        Notification.users
    ]


class ComplexView(ModelView, model=Complex):
    column_list = [Complex.id, Complex.name, Complex.videos, Complex.description,
                   Complex.next_complex_id]


class VideoView(ModelView, BaseView, model=Video):
    can_create = False
    column_list = [Video.id, Video.name, Video.description, Video.file_name, Video.complexes]


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
        if await upload_file(**data.dict()):
            # TODO сделать темплейт что удачно загружено.
            return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request},
            )
        return self.templates.TemplateResponse(
                "upload_video.html",
                context={"request": request},
            )
