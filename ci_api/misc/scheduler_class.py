import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import logger, settings
from crud_class.crud import CRUD
from database.models import Alarm, User
from database.models import Notification
from misc.notification_sender import send_push_messages

today = datetime.datetime.today()
NOTIFICATION_TEXT = "Зарядка не выполнена, не забудьте выполнить упражнения"


async def _get_notifications_for_create(users: list[int]) -> list[Notification]:
    """Return notifications list for users without notifications"""

    return [
        Notification(user_id=user, created_at=today, text=NOTIFICATION_TEXT)
        for user in users
    ]


async def _get_notifications_for_update(
        users: list[int]
) -> list[Notification]:
    """Return updated notifications list without add to database"""

    for_update: list[Notification] = []
    for user in users:
        notifications: list = await CRUD.notification.get_all_by_user_id(user)
        for notification in notifications:
            notification.text = NOTIFICATION_TEXT
            notification.created_at = today
            for_update.append(notification)

    return for_update


async def create_notifications_for_not_viewed_users():
    """Create notifications for user not viewed complex today"""

    users_ids_for_notification: list[int] = await CRUD.user.get_users_ids_for_create_notifications()
    logger.info(
        f"Create notifications for next users [{len(users_ids_for_notification)}]: "
        f"\n{users_ids_for_notification}"
    )

    users_for_update: list[int] = await CRUD.user.get_users_have_notification(
        users_ids_for_notification
    )
    logger.debug(f"users_ids_for_notification: {users_for_update}")

    users_for_create: list[int] = [
        user_id
        for user_id in users_ids_for_notification
        if user_id not in users_for_update
    ]
    notifications_for_create: list[Notification] = await _get_notifications_for_create(
        users_for_create
    )

    notifications_for_update: list[
        Notification] = await _get_notifications_for_update(users_for_update)
    notifications_for_update.extend(notifications_for_create)

    await CRUD.notification.create_and_update_notifications(notifications_for_update)
    user_tokens: list[str] = await CRUD.user.get_tokens_for_send_notification_push()
    logger.info(f"Tokens for pushing messages [{len(user_tokens)}]: {user_tokens}")
    result: list = await send_push_messages(message=NOTIFICATION_TEXT, tokens=user_tokens)
    logger.info(f"Notifications send: [{len(result)}]")


async def send_alarm_push(user_id: int, text: str):
    user: User = await CRUD.user.get_by_id(user_id)
    result: list = await send_push_messages(message=text, tokens=[user.push_token])
    logger.info(f"Alarms send: [{len(result)}]")


class CiScheduler:

    def __init__(self, scheduler: AsyncIOScheduler = None):
        self.scheduler: AsyncIOScheduler = scheduler

    async def add_alarm(self, alarm: Alarm) -> None:
        if alarm.weekdays == 'all' or str(today.weekday()) in alarm.weekdays:
            logger.debug(f"Today alarm job added: {alarm}")
            self.scheduler.add_job(
                send_alarm_push,
                'cron',
                hour=alarm.alarm_time.hour,
                minute=alarm.alarm_time.minute,
                replace_existing=True,
                timezone=datetime.timezone(datetime.timedelta(hours=3)),
                kwargs={'text': alarm.text, 'user_id': alarm.user_id}
            )

    async def create_notifications(self):
        self.scheduler.add_job(
            create_notifications_for_not_viewed_users,
            'cron',
            hour=settings.NOTIFICATION_HOUR,
            minute=00,
            replace_existing=True,
            timezone=datetime.timezone(datetime.timedelta(hours=3))
        )

    async def create_alarms(self):
        alarms: list[Alarm] = await CRUD.alarm.get_all_active_alarms()
        for alarm in alarms:
            await self.add_alarm(alarm)

    async def update_alarms(self):
        self.scheduler.add_job(
            self.create_alarms,
            'cron',
            hour=00,
            minute=1,
            replace_existing=True,
            timezone=datetime.timezone(datetime.timedelta(hours=3))
        )

    async def run(self):
        """Add scheduler job for create notifications.
        Add scheduler job for create alarms.
        Add scheduler job for update alarms at 00:01 every day
        """

        await self.create_notifications()
        await self.create_alarms()
        await self.update_alarms()

    def start(self):
        return self.scheduler.start()

    def shutdown(self):
        return self.scheduler.shutdown()


ci_scheduler = CiScheduler(AsyncIOScheduler())


if __name__ == '__main__':
    print(today.weekday())
