from sqlmodel.ext.asyncio.session import AsyncSession

from config import LEVEL_UP_PERCENTS, logger
from models.models import User, Complex, Video


async def check_level_up(user: User, session: AsyncSession) -> User:
    """Get current percent user progress in current complex"""

    current_complex: Complex = await session.get(Complex, user.current_complex)
    videos: list[Video] = await Video.get_all_by_complex_id(session, user.current_complex)
    if not videos:
        return user
    percent: float = round(1 / len(videos), 1) * 100
    user.progress = user.progress + percent
    if user.progress >= LEVEL_UP_PERCENTS:
        if user.level < 10:
            user.level = user.level + 1
        user.progress = 0
        user.current_complex = current_complex.next_complex_id
    await user.save(session)
    logger.debug(f"User with id {user.id} viewed video in complex {current_complex.id}")

    return user
