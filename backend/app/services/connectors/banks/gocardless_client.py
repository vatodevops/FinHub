from __future__ import annotations

from datetime import date

import httpx

from app.core.config import settings


class GoCardlessConfigError(RuntimeError):
    pass


class GoCardlessClient:
    def __init__(self) -> None:
        if not settings.gocardless_secret_id or not settings.gocardless_secret_key:
            raise GoCardlessConfigError("Missing GoCardless secret id/key")
        self.base_url = settings.gocardless_base_url.rstrip('/')
        self.secret_id = settings.gocardless_secret_id
        self.secret_key = settings.gocardless_secret_key

    async def _token(self) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            res = await client.post(
                f"{self.base_url}/token/new/",
                json={"secret_id": self.secret_id, "secret_key": self.secret_key},
            )
            res.raise_for_status()
            data = res.json()
            return data["access"]

    async def _request(self, method: str, path: str, **kwargs):
        token = await self._token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        async with httpx.AsyncClient(timeout=45) as client:
            res = await client.request(method, f"{self.base_url}{path}", headers=headers, **kwargs)
            res.raise_for_status()
            if res.status_code == 204:
                return None
            return res.json()

    async def list_institutions(self, country: str = "ES"):
        return await self._request("GET", f"/institutions/?country={country}")

    async def create_requisition(self, institution_id: str, reference: str, user_language: str = "ES"):
        return await self._request(
            "POST",
            "/requisitions/",
            json={
                "redirect": settings.gocardless_redirect_uri,
                "institution_id": institution_id,
                "reference": reference,
                "user_language": user_language,
            },
        )

    async def get_requisition(self, requisition_id: str):
        return await self._request("GET", f"/requisitions/{requisition_id}/")

    async def get_account_details(self, account_id: str):
        return await self._request("GET", f"/accounts/{account_id}/details/")

    async def get_account_balances(self, account_id: str):
        return await self._request("GET", f"/accounts/{account_id}/balances/")

    async def get_account_transactions(self, account_id: str, date_from: date | None = None, date_to: date | None = None):
        qs = []
        if date_from:
            qs.append(f"date_from={date_from.isoformat()}")
        if date_to:
            qs.append(f"date_to={date_to.isoformat()}")
        suffix = f"?{'&'.join(qs)}" if qs else ""
        return await self._request("GET", f"/accounts/{account_id}/transactions/{suffix}")
