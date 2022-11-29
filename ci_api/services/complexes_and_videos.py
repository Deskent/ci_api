from sqlmodel.ext.asyncio.session import AsyncSession

from config import LEVEL_UP_PERCENTS, logger
from models.models import User, Complex, Video, ViewedVideos, ViewedComplexes


async def check_level_up(session: AsyncSession, user: User) -> User:
    """Get current percent user progress in current complex"""

    current_complex: Complex = await session.get(Complex, user.current_complex)
    videos: int = len(await Video.get_all_by_complex_id(session, current_complex.id))
    if not current_complex.video_count:
        return user
    percent: float = round(1 / videos, 1) * 100
    user.progress = user.progress + percent
    if user.progress >= LEVEL_UP_PERCENTS:
        if user.level < 10:
            user.level = user.level + 1
        user.progress = 0
        await set_complex_viewed(session, user)
        user.current_complex = current_complex.next_complex_id
    await user.save(session)
    logger.debug(f"User with id {user.id} viewed video in complex {current_complex.id}")

    return user


async def get_viewed_videos_ids(
        session: AsyncSession,
        user: User
) -> tuple[int]:
    viewed_videos: list[ViewedVideos] = await ViewedVideos.get_all_viewed_videos(session, user.id)

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
        session: AsyncSession,
        not_viewed_ids: tuple[int]
) -> int:
    duration: int = await Video.get_videos_duration(session, not_viewed_ids)

    return duration


def calculate_videos_to_next_level(user: User, videos: list[Video]):
    return int((LEVEL_UP_PERCENTS - user.progress) / (100 / len(videos)))


async def set_video_viewed(
        session: AsyncSession,
        user: User,
        video_id: int

) -> ViewedVideos:
    return await ViewedVideos.add_viewed(session, user.id, video_id)


async def set_complex_viewed(
        session: AsyncSession,
        user: User

) -> ViewedComplexes:
    return await ViewedComplexes.add_viewed(session, user.id, user.current_complex)
