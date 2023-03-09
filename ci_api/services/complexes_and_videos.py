from config import LEVEL_UP_PERCENTS, logger
from database.models import User, Complex, Video, ViewedVideo
from crud_class.crud import CRUD


async def check_level_up(user: User) -> User:
    """Get current percent user progress in current complex"""

    current_complex: Complex = await CRUD.complex.get_by_id(user.current_complex)
    videos: int = len(await CRUD.video.get_all_by_complex_id(current_complex.id))
    if not videos:
        return user
    percent: float = round(1 / videos, 1) * 100
    user.progress = user.progress + percent
    if user.progress >= LEVEL_UP_PERCENTS:
        if user.level < 10:
            user.level = user.level + 1
        user.progress = 0
        await CRUD.viewed_complex.add_viewed(user.id, user.current_complex)
        next_complex: Complex = await CRUD.complex.next_complex(current_complex)
        user.current_complex = next_complex.id
    user: User = await CRUD.user.save(user)
    logger.debug(f"User with id {user.id} viewed video in complex {current_complex.id}")

    return user


async def get_viewed_videos_ids(
        user: User
) -> tuple[int]:
    viewed_videos: list[ViewedVideo] = await CRUD.viewed_video.get_all_viewed_videos(user.id)

    return tuple(elem.video_id for elem in viewed_videos)


async def get_not_viewed_videos_ids(
        videos: list[Video],
        viewed_videos_ids: tuple[int]
) -> tuple[int]:

    return tuple(
        video.id
        for video in videos
        if video.id not in viewed_videos_ids
    )


async def calculate_viewed_videos_duration(
        not_viewed_ids: tuple[int]
) -> int:
    duration: int = await CRUD.video.get_videos_duration(not_viewed_ids)

    return duration


def calculate_videos_to_next_level(user: User, videos: list[Video]):
    if not videos:
        return 0
    return int((LEVEL_UP_PERCENTS - user.progress) / (100 / len(videos)))


async def is_video_viewed_before(
        user: User,
        video_id: int

) -> bool:
    """Check video was viewed, return True if Video was created, False is exists"""

    if await CRUD.viewed_video.add_viewed(user.id, video_id):
        return False
    return True
