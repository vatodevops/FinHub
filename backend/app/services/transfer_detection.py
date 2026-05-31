from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import LinkType, Transaction, TransactionLink


def detect_transfer_pairs(
    session: Session,
    user_id: str,
    candidate_ids: list[str] | None = None,
    date_tolerance_days: int = 2,
) -> int:
    """Detect and create transfer pairs for a user.

    Algorithm: for each unpaired debit, find a matching unpaired credit with:
    - Same user_id
    - Different account
    - Same absolute amount
    - Date within ±tolerance days

    Greedy closest-date-first matching, each tx can only pair once.

    Returns the number of pairs created.
    """
    now = datetime.now(UTC)
    window_start = now - timedelta(days=date_tolerance_days * 2)

    # Base query for candidate transactions
    tx_query = (
        select(Transaction)
        .where(
            Transaction.user_id == user_id,
            Transaction.status == "booked",
            Transaction.booked_at.isnot(None),
        )
    )

    if candidate_ids:
        tx_query = tx_query.where(Transaction.id.in_(candidate_ids))

    all_txs = session.scalars(tx_query).all()

    # Filter to only debit/credit pairs (non-zero amounts)
    txs = [tx for tx in all_txs if tx.amount != 0]

    # Find already-paired transaction IDs
    existing_links = (
        session.query(TransactionLink)
        .where(
            TransactionLink.user_id == user_id,
            TransactionLink.link_type == LinkType.transfer_pair,
        )
        .all()
    )
    paired_ids: set[str] = set()
    for link in existing_links:
        paired_ids.add(str(link.left_transaction_id))
        paired_ids.add(str(link.right_transaction_id))

    # Separate into debits (negative) and credits (positive)
    debits = [tx for tx in txs if tx.amount < 0 and str(tx.id) not in paired_ids]
    credits = [tx for tx in txs if tx.amount > 0 and str(tx.id) not in paired_ids]

    # Build a lookup for credits by account for quick filtering
    credit_map: dict[str, list[Transaction]] = {}
    for credit in credits:
        acc_key = str(credit.account_id)
        if acc_key not in credit_map:
            credit_map[acc_key] = []
        credit_map[acc_key].append(credit)

    # Sort debits by booked_at for greedy closest-date-first matching
    debits.sort(key=lambda tx: tx.booked_at or datetime.min.replace(tzinfo=UTC))

    used_credit_ids: set[str] = set()
    pairs_created = 0

    for debit in debits:
        debit_amount = abs(debit.amount)
        debit_date = debit.booked_at or datetime.min.replace(tzinfo=UTC)
        debit_account = str(debit.account_id)

        # Find matching credits: different account, same absolute amount, within date window
        candidates: list[Transaction] = []
        for credit in credits:
            credit_id = str(credit.id)
            if credit_id in used_credit_ids:
                continue
            if credit.account_id == debit.account_id:
                continue
            if abs(float(credit.amount) - float(debit_amount)) > 0.001:
                continue

            credit_date = credit.booked_at or datetime.min.replace(tzinfo=UTC)
            date_diff = abs((credit_date - debit_date).days)
            if date_diff <= date_tolerance_days:
                candidates.append(credit)

        if not candidates:
            continue

        # Sort by closest date
        candidates.sort(key=lambda tx: abs((tx.booked_at or datetime.min.replace(tzinfo=UTC)) - debit_date))

        # Pick the closest match
        best = candidates[0]
        best_id = str(best.id)

        # Create the link
        link = TransactionLink(
            user_id=user_id,
            left_transaction_id=debit.id,
            right_transaction_id=best.id,
            link_type=LinkType.transfer_pair,
        )
        session.add(link)
        used_credit_ids.add(best_id)
        paired_ids.add(str(debit.id))
        paired_ids.add(best_id)
        pairs_created += 1

    session.commit()
    return pairs_created
