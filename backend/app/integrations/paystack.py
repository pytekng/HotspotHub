import httpx

from backend.app.core.config import settings


class PaystackClient:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.paystack_secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self,
        email: str,
        amount: int,
        reference: str,
        callback_url: str | None = None,
    ) -> dict:
        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
        }

        if callback_url:
            payload["callback_url"] = callback_url

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/transaction/initialize",
                json=payload,
                headers=self.headers,
                timeout=30.0,
            )

        response.raise_for_status()

        return response.json()

    async def verify_transaction(
        self,
        reference: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/transaction/verify/{reference}",
                headers=self.headers,
                timeout=30.0,
            )

        response.raise_for_status()

        return response.json()
