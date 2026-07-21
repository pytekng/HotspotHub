import asyncio
from decimal import Decimal

from backend.app.db.database import AsyncSessionLocal
from backend.app.repositories.plan_repository import PlanRepository


PLANS = [
    {
        "name": "1 Hour",
        "description": "Perfect for quick browsing.",
        "duration_hours": 1,
        "price": Decimal("100.00"),
    },
    {
        "name": "3 Hours",
        "description": "Great for a few hours of browsing.",
        "duration_hours": 3,
        "price": Decimal("250.00"),
    },
    {
        "name": "24 Hours",
        "description": "Enjoy hotspot access for a full day.",
        "duration_hours": 24,
        "price": Decimal("500.00"),
    },
    {
        "name": "7 Days",
        "description": "Stay connected for the entire week.",
        "duration_hours": 168,
        "price": Decimal("2000.00"),
    },
]


async def seed_plans():
    async with AsyncSessionLocal() as session:
        repository = PlanRepository(session)

        for plan_data in PLANS:
            existing_plan = await repository.get_by_name(
                plan_data["name"]
            )

            if existing_plan is not None:
                print(
                    f"Plan already exists: "
                    f"{existing_plan.name}"
                )
                continue

            plan = await repository.create(**plan_data)

            print(
                f"Created plan: "
                f"{plan.name} - "
                f"₦{plan.price}"
            )


if __name__ == "__main__":
    asyncio.run(seed_plans())
