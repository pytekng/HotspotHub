from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.purchase import Purchase, PurchaseStatus


class PurchaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        plan_id: int,
        amount: Decimal,
    ) -> Purchase:
        purchase = Purchase(
            user_id=user_id,
            plan_id=plan_id,
            amount=amount,
            status=PurchaseStatus.PENDING,
        )

        self.session.add(purchase)

        await self.session.commit()
        await self.session.refresh(purchase)

        return purchase

    async def get_by_id(
        self,
        purchase_id: int,
    ) -> Purchase | None:
        result = await self.session.execute(
            select(Purchase).where(
                Purchase.id == purchase_id
            )
        )

        return result.scalar_one_or_none()

    async def get_user_purchases(
        self,
        user_id: int,
    ) -> list[Purchase]:
        result = await self.session.execute(
            select(Purchase)
            .where(Purchase.user_id == user_id)
            .order_by(Purchase.created_at.desc())
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        purchase_id: int,
        status: PurchaseStatus,
    ) -> Purchase | None:
        purchase = await self.get_by_id(purchase_id)

        if purchase is None:
            return None

        purchase.status = status

        if status == PurchaseStatus.PAID:
            purchase.paid_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(purchase)

        return purchase
