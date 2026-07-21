from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.purchase import Purchase, PurchaseStatus
from backend.app.repositories.plan_repository import PlanRepository
from backend.app.repositories.purchase_repository import PurchaseRepository


class PurchaseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.purchase_repository = PurchaseRepository(session)
        self.plan_repository = PlanRepository(session)

    async def create_purchase(
        self,
        user_id: int,
        plan_id: int,
    ) -> Purchase:
        plan = await self.plan_repository.get_by_id(plan_id)

        if plan is None:
            raise ValueError("Plan not found.")

        if not plan.is_active:
            raise ValueError("This plan is no longer available.")

        purchase = await self.purchase_repository.create(
            user_id=user_id,
            plan_id=plan.id,
            amount=Decimal(plan.price),
        )

        return purchase

    async def get_purchase(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        return await self.purchase_repository.get_by_id(
            purchase_id
        )

    async def get_user_purchases(
        self,
        user_id: int,
    ) -> list[Purchase]:
        return await self.purchase_repository.get_user_purchases(
            user_id
        )

    async def mark_as_paid(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        return await self.purchase_repository.update_status(
            purchase_id=purchase_id,
            status=PurchaseStatus.PAID,
        )

    async def mark_as_failed(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        return await self.purchase_repository.update_status(
            purchase_id=purchase_id,
            status=PurchaseStatus.FAILED,
        )

    async def cancel_purchase(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        return await self.purchase_repository.update_status(
            purchase_id=purchase_id,
            status=PurchaseStatus.CANCELLED,
        )
