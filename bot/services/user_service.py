from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.user_repository import UserRepository


async def save_telegram_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
):
    repository = UserRepository(session)

    return await repository.get_or_create(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
