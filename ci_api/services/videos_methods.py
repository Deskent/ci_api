from exc.exceptions import UserNotFoundError, UserNotFoundErrorApi
from models.models import User, Video, Complex, ViewedComplex
from services.complexes_and_videos import is_video_viewed_before, check_level_up
from services.utils import convert_seconds_to_time
from services.web_context_class import WebContext


async def get_viewed_video_response(user: User, video_id: int, context: dict) -> WebContext:
    obj = WebContext(context=context)
    if not user:
        obj.template = "entry.html"
        obj.to_raise = UserNotFoundErrorApi
        return obj

    current_video: Video = await Video.get_by_id(video_id)
    next_video_id: int = await current_video.next_video_id()

    if not next_video_id:
        obj.template = "come_tomorrow.html"
        obj.api_data.update(payload=dict(result="come tomorrow"))

        return obj

    videos: list[Video] = await Video.get_all_by_complex_id(user.current_complex)
    data = dict(next_video_id=next_video_id, videos=videos)
    obj.context.update(**data)
    obj.api_data.update(payload=data)

    if await is_video_viewed_before(user, video_id):
        obj.redirect = f"/startCharging/{next_video_id}"

        return obj

    old_user_level: int = user.level
    new_user: User = await check_level_up(user)
    current_complex: Complex = await Complex.get_by_id(user.current_complex)
    obj.context.update(current_complex=current_complex)
    if new_user.level <= old_user_level:
        obj.redirect = f"/startCharging/{next_video_id}"
        return obj

    current_complex: Complex = await Complex.get_by_id(user.current_complex)
    obj.context.update(user=new_user, current_complex=current_complex)
    obj.template = "new_level.html"

    return obj


async def get_viewed_complex_response(
        user: User,
        complex_id: int
) -> dict:
    result = {"level_up": False}
    if not await ViewedComplex.is_viewed_complex(user_id=user.id, complex_id=complex_id):
        await ViewedComplex.add_viewed(user_id=user.id, complex_id=complex_id)
        next_complex: Complex = await Complex.get_next_complex(user.current_complex)
        user: User = await user.level_up(next_complex.id)
        next_complex_duration = convert_seconds_to_time(next_complex.duration)
        result.update(
            {
                "level_up": True,
                "new_level": user.level,
                "next_complex_duration": next_complex_duration
            }
        )

    return result
