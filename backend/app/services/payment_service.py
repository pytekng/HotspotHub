import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.integrations.paystack import PaystackClient
from backend.app.models.purchase import Purchase
from backend.app.repositories.purchase_repository import PurchaseRepository


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.paystack = PaystackClient()
        self.purchase_repository = PurchaseRepository(session)

    async def initialize_payment(
        self,
        purchase: Purchase,
        email: str,
    ) -> dict:
        reference = (
            f"hotspothub_{purchase.id}_{uuid.uuid4().hex[:12]}"
        )

        amount_in_kobo = int(purchase.amount * 100)

        result = await self.paystack.initialize_transaction(
            email=email,
            amount=amount_in_kobo,
            reference=reference,
        )

        await self.purchase_repository.update_payment_reference(
            purchase_id=purchase.id,
            payment_reference=reference,
        )

        return {
            "reference": reference,
            "authorization_url": result["data"]["authorization_url"],
            "access_code": result["data"]["access_code"],
        }

    async def verify_payment(
        self,
        reference: str,
    ) -> dict:
        result = await self.paystack.verify_transaction(
            reference=reference,
        )

        return result
