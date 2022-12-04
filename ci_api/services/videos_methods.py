from exc.payment.exceptions import UserNotFoundError
from models.models import User, Video, Complex
from services.complexes_and_videos import is_video_viewed, check_level_up
from services.response_manager import WebContext


async def get_viewed_video_response(user: User, video_id: int, context: dict) -> WebContext:
    obj = WebContext(context=context)
    if not user:
        obj.template = "entry.html"
        obj.to_raise = UserNotFoundError
        return obj

    current_video: Video = await Video.get_by_id(video_id)
    next_video_id: int = await current_video.next_video_id()

    if not next_video_id:
        obj.template = "come_tomorrow.html"
        obj.api_data = dict(payload="come tomorrow")

        return obj
    videos: list[Video] = await Video.get_all_by_complex_id(user.current_complex)
    api_data = dict(next_video_id=next_video_id, user=user, videos=videos)
    obj.context.update(api_data)
    obj.api_data['payload'] = api_data

    if not await is_video_viewed(user, video_id):
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
