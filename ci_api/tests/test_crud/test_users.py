import datetime

from crud_class.crud import CRUD
from database.models import User, Alarm, Avatar


async def test_crud_get_user_by_id(get_user):
    user: User = await CRUD.user.get_by_id(get_user.id)
    assert user.id == get_user.id


async def test_crud_get_user_by_id_user_not_exists():
    user: User = await CRUD.user.get_by_id(-1)
    assert user is None


async def test_crud_get_all_users(get_user):
    users: list[User] = await CRUD.user.get_all()
    assert users[0].email is not None


async def test_crud_get_user_by_phone(get_user, user_data):
    user: User = await CRUD.user.get_by_phone(user_data['phone'])
    assert user.phone == user_data['phone']


async def test_crud_activate_user(get_user):
    user: User = await CRUD.user.activate(get_user)
    assert user.is_active is True
    user: User = await CRUD.user.deactivate(id_=user.id)
    assert user.is_active is False


async def test_crud_get_alarm_by_id(get_user, get_user_alarm):
    alarm: Alarm = await CRUD.user.get_alarm_by_alarm_id(get_user, get_user_alarm.id)
    assert alarm.id is not None


async def test_crud_set_subscribe_to(get_user):
    user: User = await CRUD.user.set_subscribe_to(5, get_user)
    assert user.expired_at.date() == (
            datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=5)).date()


async def test_crud_set_last_entry_today(get_user):
    user: User = await CRUD.user.set_last_entry_today(get_user)
    assert user.last_entry.day == datetime.datetime.now().day


async def test_user_level_up(get_user):
    user: User = get_user
    first_level = user.level
    user: user = await CRUD.user.level_up(user)
    assert user.level == first_level + 1


async def test_user_set_avatar(get_user):
    avatars: list[Avatar] = await CRUD.avatar.get_all()
    avatar = avatars[0]
    user: User = await CRUD.user.set_avatar(avatar.id, get_user)
    assert user.avatar == avatar.id


async def test_check_is_active(get_user):
    user: User = await CRUD.user.set_subscribe_to(-1, user=get_user)
    assert await CRUD.user.check_is_active(user) is False


async def test_user_is_first_entry_today(get_user):
    assert await CRUD.user.is_first_entry_today(get_user) is True


async def test_user_is_new_user(get_user):
    assert await CRUD.user.is_new_user(get_user) is True


async def test_get_tokens_for_send_notification_push():
    tokens: list[str] = await CRUD.user.get_tokens_for_send_notification_push()
    assert tokens is not None


async def test_get_users_ids_for_create_notifications():
    users_ids: list[int] = await CRUD.user.get_users_ids_for_create_notifications()
    assert users_ids is not None


async def test_get_users_have_notification():
    users_ids: list[int] = await CRUD.user.get_users_ids_for_create_notifications()
    assert users_ids is not None
    users_for_update: list[int] = await CRUD.user.get_users_have_notification(users_ids)
    assert users_for_update is not None
