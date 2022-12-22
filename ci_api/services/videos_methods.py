from exc.exceptions import UserNotFoundErrorApi
from database.models import User, Video, Complex
from services.complexes_and_videos import is_video_viewed_before, check_level_up
from crud_class.crud import CRUD
from services.utils import convert_to_minutes
from misc.web_context_class import WebContext


async def get_viewed_video_response(user: User, video_id: int, context: dict) -> WebContext:
    web_context = WebContext(context=context)
    if not user:
        web_context.template = "entry.html"
        web_context.to_raise = UserNotFoundErrorApi
        return web_context

    current_video: Video = await CRUD.video.get_by_id(video_id)
    next_video_id: int = await CRUD.video.next_video_id(current_video)

    if not next_video_id:
        web_context.template = "come_tomorrow.html"
        web_context.api_data.update(payload=dict(result="come tomorrow"))

        return web_context

    videos: list[Video] = await CRUD.video.get_all_by_complex_id(user.current_complex)
    data = dict(next_video_id=next_video_id, videos=videos)
    web_context.context.update(**data)
    web_context.api_data.update(payload=data)

    if await is_video_viewed_before(user, video_id):
        web_context.redirect = f"/startCharging/{next_video_id}"

        return web_context

    old_user_level: int = user.level
    new_user: User = await check_level_up(user)
    if new_user.level <= old_user_level:
        current_complex: Complex = await CRUD.complex.get_by_id(user.current_complex)
        web_context.context.update(current_complex=current_complex)
        web_context.redirect = f"/startCharging/{next_video_id}"
        return web_context

    current_complex: Complex = await CRUD.complex.get_by_id(user.current_complex)
    web_context.context.update(user=new_user, current_complex=current_complex)
    web_context.template = "new_level.html"

    return web_context


async def get_viewed_complex_response(
        user: User,
        complex_id: int
) -> dict:
    result = {"level_up": False}
    if not await CRUD.viewed_complex.is_viewed_complex(user_id=user.id, complex_id=complex_id):
        await CRUD.viewed_complex.add_viewed(user_id=user.id, complex_id=complex_id)
        next_complex: Complex = await CRUD.complex.next_complex(user.current_complex)
        user: User = await CRUD.user.level_up(user)
        next_complex_duration: int = convert_to_minutes(next_complex.duration)
        result.update(
            {
                "level_up": True,
                "new_level": user.level,
                "next_complex_duration": next_complex_duration
            }
        )

    return result
