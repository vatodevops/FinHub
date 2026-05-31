"""SimpleFIN Bridge connector for FinHub.

SimpleFIN (https://www.simplefin.org) is a read-only financial interchange
protocol. The user gets a Setup Token from a SimpleFIN server (typically the
SimpleFIN Bridge at https://bridge.simplefin.org), pastes it into FinHub,
and FinHub claims an Access URL that embeds Basic Auth credentials. From then
on, ``GET {access_url}/accounts?version=2`` returns accounts + transactions
+ holdings in a single JSON document.

The protocol is intentionally simple: there is no OAuth dance, no widget, no
on-demand refresh, no MFA. Every read goes to the bridge, which pulls from
the bank on its own schedule.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import httpx

from app.services.connectors.banks.base import BankConnector, NormalizedAccount, NormalizedTransaction

logger = logging.getLogger("finhub")

SIMPLEFIN_MAX_WINDOW_DAYS = 90
SIMPLEFIN_DEFAULT_HISTORY_DAYS = 90
SIMPLEFIN_INITIAL_HISTORY_DAYS = 365
SIMPLEFIN_HTTP_TIMEOUT = 60.0

_REAUTH_ERROR_CODES = frozenset({"gen.auth", "con.auth"})


def _decode_setup_token(raw: str) -> str:
    """Decode a SimpleFIN Setup Token (Base64-encoded URL)."""
    cleaned = "".join(raw.split())
    if not cleaned:
        raise ValueError("SimpleFIN setup token is empty")
    padding = (-len(cleaned)) % 4
    cleaned = cleaned + ("=" * padding)
    try:
        decoded = base64.b64decode(cleaned, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError("SimpleFIN setup token is not valid base64") from exc
    if not decoded.startswith(("http://", "https://")):
        raise ValueError("SimpleFIN setup token did not decode to a URL")
    return decoded


def _epoch_to_date(value: Any) -> Optional[date]:
    if value is None or value == "":
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc).date()
    except (ValueError, TypeError, OSError):
        return None


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _surface_errors(errlist: list[dict], context: str) -> None:
    """Log SimpleFIN warnings; reauth errors are logged but not raised."""
    if not errlist:
        return
    reauth = [e for e in errlist if (e.get("code") or "").lower() in _REAUTH_ERROR_CODES]
    for entry in errlist:
        code = entry.get("code", "")
        msg = entry.get("msg") or entry.get("message", "")
        if code.lower() in _REAUTH_ERROR_CODES:
            logger.warning("SimpleFIN %s REAUTH: code=%s msg=%s", context, code, msg)
        else:
            logger.warning("SimpleFIN %s warning code=%s msg=%s", context, code, msg)


class SimpleFINBankConnector(BankConnector):
    """SimpleFIN Bridge connector."""

    provider_name = "simplefin"

    def __init__(self) -> None:
        self._access_url: Optional[str] = None

    # ----- credential handling -----------------------------------------------

    @staticmethod
    def _decode_setup_token(raw: str) -> str:
        return _decode_setup_token(raw)

    async def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=SIMPLEFIN_HTTP_TIMEOUT,
            headers={
                "Accept": "application/json",
                "User-Agent": "FinHub/0.1",
            },
        )

    async def _fetch_accounts(
        self,
        *,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None,
        pending: bool = True,
    ) -> dict:
        if not self._access_url:
            raise RuntimeError("SimpleFIN access URL is missing")
        params: dict[str, Any] = {"version": "2"}
        if pending:
            params["pending"] = "1"
        if start_date:
            params["start-date"] = str(int(datetime.combine(
                start_date, datetime.min.time(), tzinfo=timezone.utc,
            ).timestamp()))
        if end_date:
            params["end-date"] = str(int(datetime.combine(
                end_date, datetime.min.time(), tzinfo=timezone.utc,
            ).timestamp()))
        if account_id:
            params["account"] = account_id
        async with await self._client() as client:
            resp = await client.get(f"{self._access_url}/accounts", params=params)
        if resp.status_code in (401, 403):
            raise RuntimeError(f"SimpleFIN refused the request ({resp.status_code})")
        resp.raise_for_status()
        return resp.json() or {}

    # ----- connection flow ---------------------------------------------------

    async def claim_access_url(self, setup_token: str) -> tuple[str, str, list[NormalizedAccount]]:
        """Claim a SimpleFIN Access URL from a Setup Token.

        Returns (access_url, external_connection_id, accounts).
        """
        claim_url = self._decode_setup_token(setup_token)
        async with await self._client() as client:
            claim_resp = await client.post(
                claim_url, headers={"Content-Length": "0"}
            )
        if claim_resp.status_code == 403:
            raise RuntimeError(
                "SimpleFIN setup token has already been used or expired. "
                "Generate a fresh token from the SimpleFIN Bridge."
            )
        if claim_resp.status_code >= 400:
            raise RuntimeError(
                f"SimpleFIN claim returned {claim_resp.status_code}: "
                f"{claim_resp.text[:200]}"
            )
        access_url = (claim_resp.text or "").strip().strip('"')
        if not access_url.startswith(("http://", "https://")):
            raise RuntimeError("SimpleFIN claim did not return a URL")

        self._access_url = access_url

        # Pull the account list once so we can return accounts immediately
        payload = await self._fetch_accounts(pending=False)
        _surface_errors(payload.get("errlist") or [], context="claim")
        conn_id = self._stable_external_id(payload, claim_url)
        institution_name, accounts = self._parse_accounts(payload)
        return access_url, conn_id, accounts

    @staticmethod
    def _stable_external_id(payload: dict, claim_url: str) -> str:
        """Produce a stable external id for this connection."""
        conns = payload.get("connections") or []
        if conns and conns[0].get("conn_id"):
            return str(conns[0]["conn_id"])
        for acc in payload.get("accounts") or []:
            if acc.get("conn_id"):
                return str(acc["conn_id"])
        return "simplefin-" + hashlib.sha256(claim_url.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _parse_accounts(payload: dict) -> tuple[str, list[NormalizedAccount]]:
        connections = payload.get("connections") or []
        institution_name = (
            connections[0].get("name") if connections else "SimpleFIN Connection"
        )
        accounts: list[NormalizedAccount] = []
        for raw in payload.get("accounts") or []:
            account_id = str(raw.get("id") or "")
            if not account_id:
                continue
            name = raw.get("name") or "Account"
            accounts.append(
                NormalizedAccount(
                    external_id=account_id,
                    name=name,
                    currency=raw.get("currency") or "EUR",
                    kind="checking",
                )
            )
        return institution_name or "SimpleFIN Connection", accounts

    # ----- BankConnector interface -------------------------------------------

    async def list_accounts(self, connection_ref: str) -> list[NormalizedAccount]:
        """Fetch accounts for a connection (uses stored access URL)."""
        payload = await self._fetch_accounts(pending=False)
        _surface_errors(payload.get("errlist") or [], context="list_accounts")
        _, accounts = self._parse_accounts(payload)
        return accounts

    async def list_transactions(
        self,
        connection_ref: str,
        account_external_id: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[NormalizedTransaction]:
        """Fetch transactions for an account with 90-day chunking."""
        end_date = to_date or date.today()
        start_date = from_date or (end_date - timedelta(days=SIMPLEFIN_INITIAL_HISTORY_DAYS))

        transactions: list[NormalizedTransaction] = []
        seen_ids: set[str] = set()
        cursor = start_date

        while cursor <= end_date:
            chunk_end = min(cursor + timedelta(days=SIMPLEFIN_MAX_WINDOW_DAYS), end_date)
            payload = await self._fetch_accounts(
                start_date=cursor,
                end_date=chunk_end + timedelta(days=1),
                account_id=account_external_id,
                pending=True,
            )
            _surface_errors(payload.get("errlist") or [], context="get_transactions")
            for raw_acc in payload.get("accounts") or []:
                if str(raw_acc.get("id") or "") != account_external_id:
                    continue
                for raw_txn in raw_acc.get("transactions") or []:
                    parsed = self._build_transaction(raw_txn)
                    if parsed and parsed.source_id not in seen_ids:
                        seen_ids.add(parsed.source_id)
                        transactions.append(parsed)
            cursor = chunk_end + timedelta(days=1)

        return transactions

    @staticmethod
    def _build_transaction(raw: dict) -> Optional[NormalizedTransaction]:
        txn_id = str(raw.get("id") or "")
        if not txn_id:
            return None
        amount_raw = _to_decimal(raw.get("amount"))
        if amount_raw is None:
            return None
        amount = amount_raw.copy_abs()
        posted = _epoch_to_date(raw.get("posted"))
        transacted = _epoch_to_date(raw.get("transacted_at"))
        txn_date = posted or transacted
        if not txn_date:
            return None
        description = (
            raw.get("description")
            or raw.get("payee")
            or raw.get("memo")
            or "Transaction"
        ).strip()[:500]
        channel = "other"
        if raw.get("pending"):
            channel = "transfer"
        return NormalizedTransaction(
            source_id=txn_id,
            amount=amount,
            currency=raw.get("currency") or "EUR",
            booked_at=datetime.combine(txn_date, datetime.min.time(), tzinfo=timezone.utc),
            value_date=txn_date,
            merchant_raw=(raw.get("payee") or "").strip() or None,
            description_raw=description,
            channel=channel,
        )

    async def refresh_credentials(self, credentials: dict) -> dict:
        return credentials
