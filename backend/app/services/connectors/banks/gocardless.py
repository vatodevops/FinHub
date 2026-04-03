from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.services.connectors.banks.base import BankConnector, NormalizedAccount, NormalizedTransaction
from app.services.connectors.banks.gocardless_client import GoCardlessClient


class GoCardlessBankConnector(BankConnector):
    provider_name = "gocardless_bad"

    def __init__(self) -> None:
        self.client = GoCardlessClient()

    async def list_accounts(self, connection_ref: str) -> list[NormalizedAccount]:
        requisition = await self.client.get_requisition(connection_ref)
        account_ids = requisition.get("accounts", [])
        out: list[NormalizedAccount] = []
        for account_id in account_ids:
            details = await self.client.get_account_details(account_id)
            account = details.get("account", {})
            out.append(
                NormalizedAccount(
                    external_id=account_id,
                    name=account.get("ownerName") or account.get("resourceId") or f"Account {account_id[:8]}",
                    currency=account.get("currency") or "EUR",
                    kind="checking",
                    iban_masked=_mask_iban(account.get("iban")),
                )
            )
        return out

    async def list_transactions(
        self,
        connection_ref: str,
        account_external_id: str,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[NormalizedTransaction]:
        payload = await self.client.get_account_transactions(account_external_id, from_date=from_date, date_to=to_date)
        booked = payload.get("transactions", {}).get("booked", [])
        pending = payload.get("transactions", {}).get("pending", [])
        all_rows = [*booked, *pending]
        out: list[NormalizedTransaction] = []
        for row in all_rows:
            amount = Decimal(row.get("transactionAmount", {}).get("amount", "0"))
            currency = row.get("transactionAmount", {}).get("currency", "EUR")
            booked_at = _parse_datetime(row.get("bookingDateTime") or row.get("bookingDate"))
            value_date = _parse_date(row.get("valueDate"))
            description = ' | '.join(row.get("remittanceInformationUnstructuredArray") or []) or row.get("remittanceInformationUnstructured")
            merchant = row.get("debtorName") or row.get("creditorName") or description
            channel = _guess_channel(row)
            source_id = row.get("internalTransactionId") or row.get("transactionId") or f"{account_external_id}:{row.get('bookingDate')}:{amount}"
            out.append(
                NormalizedTransaction(
                    source_id=source_id,
                    amount=amount,
                    currency=currency,
                    booked_at=booked_at,
                    value_date=value_date,
                    merchant_raw=merchant,
                    description_raw=description,
                    channel=channel,
                )
            )
        return out


def _mask_iban(iban: str | None) -> str | None:
    if not iban or len(iban) < 4:
        return None
    return f"{iban[:2]}**{iban[-4:]}"


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _guess_channel(row: dict) -> str:
    code = (row.get('bankTransactionCode') or {}).get('code') or ''
    proprietary = row.get('proprietaryBankTransactionCode') or ''
    text = f"{code} {proprietary}".upper()
    if 'PMNT' in text or 'POSD' in text or 'CARD' in text:
        return 'card'
    if 'DDT' in text or 'DIRECT' in text:
        return 'direct_debit'
    if 'XFER' in text or 'TRF' in text or 'TRANSFER' in text:
        return 'transfer'
    return 'other'
