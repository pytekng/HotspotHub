import asyncio

from backend.app.db.database import AsyncSessionLocal
from backend.app.services.purchase_service import PurchaseService


async def test_purchase():
    async with AsyncSessionLocal() as session:
        service = PurchaseService(session)

        purchase = await service.create_purchase(
            user_id=1,
            plan_id=3,
        )

        print("Purchase created successfully!")
        print(f"Purchase ID: {purchase.id}")
        print(f"User ID: {purchase.user_id}")
        print(f"Plan ID: {purchase.plan_id}")
        print(f"Amount: ₦{purchase.amount}")
        print(f"Status: {purchase.status}")


if __name__ == "__main__":
    asyncio.run(test_purchase())
