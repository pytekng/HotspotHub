from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.plan import Plan


class PlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(
        self,
        name: str,
    ) -> Plan | None:
        result = await self.session.execute(
            select(Plan).where(Plan.name == name)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        description: str | None,
        duration_hours: int,
        price: Decimal,
    ) -> Plan:
        existing_plan = await self.get_by_name(name)

        if existing_plan is not None:
            return existing_plan

        plan = Plan(
            name=name,
            description=description,
            duration_hours=duration_hours,
            price=price,
        )

        self.session.add(plan)

        await self.session.commit()
        await self.session.refresh(plan)

        return plan

    async def get_by_id(
        self,
        plan_id: int,
    ) -> Plan | None:
        result = await self.session.execute(
            select(Plan).where(Plan.id == plan_id)
        )

        return result.scalar_one_or_none()

    async def get_active_plans(self) -> list[Plan]:
        result = await self.session.execute(
            select(Plan)
            .where(Plan.is_active.is_(True))
            .order_by(Plan.duration_hours)
        )

        return list(result.scalars().all())
