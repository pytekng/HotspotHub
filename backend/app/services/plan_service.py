from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.plan_repository import PlanRepository


class PlanService:
    def __init__(self, session: AsyncSession):
        self.repository = PlanRepository(session)

    async def create_plan(
        self,
        name: str,
        description: str | None,
        duration_hours: int,
        price: Decimal,
    ):
        return await self.repository.create(
            name=name,
            description=description,
            duration_hours=duration_hours,
            price=price,
        )

    async def get_plan(self, plan_id: int):
        return await self.repository.get_by_id(plan_id)

    async def get_active_plans(self):
        return await self.repository.get_active_plans()
