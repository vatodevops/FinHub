from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class NormalizedAccount:
    external_id: str
    name: str
    currency: str
    kind: str
    iban_masked: str | None = None


@dataclass
class NormalizedTransaction:
    source_id: str
    amount: Decimal
    currency: str
    booked_at: datetime | None
    value_date: date | None
    merchant_raw: str | None
    description_raw: str | None
    channel: str


class BankConnector(ABC):
    provider_name: str

    @abstractmethod
    async def list_accounts(self, connection_ref: str) -> list[NormalizedAccount]:
        raise NotImplementedError

    @abstractmethod
    async def list_transactions(
        self,
        connection_ref: str,
        account_external_id: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[NormalizedTransaction]:
        raise NotImplementedError
