from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    MatchStatus,
    NormalizedRow,
    PurchaseItem,
    ReconciliationJob,
    ReconciliationPair,
    ReconciliationStatus,
    SourceType,
)


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return "".join(value.strip().upper().split())


def build_match_key(order_ref: str | None, item_model: str | None) -> str:
    return f"{normalize_text(order_ref)}|{normalize_text(item_model)}"


def reconcile_batches(db: Session, statement_batch_id: int, inbound_batch_id: int) -> ReconciliationJob:
    job = ReconciliationJob(statement_batch_id=statement_batch_id, inbound_batch_id=inbound_batch_id)
    db.add(job)
    db.flush()

    stmt_rows = (
        db.query(NormalizedRow)
        .filter(NormalizedRow.batch_id == statement_batch_id, NormalizedRow.source_type == SourceType.statement)
        .all()
    )
    inb_rows = (
        db.query(NormalizedRow)
        .filter(NormalizedRow.batch_id == inbound_batch_id, NormalizedRow.source_type == SourceType.inbound)
        .all()
    )

    stmt_map: dict[str, list[NormalizedRow]] = defaultdict(list)
    inb_map: dict[str, list[NormalizedRow]] = defaultdict(list)

    for row in stmt_rows:
        row.normalized_order_ref = normalize_text(row.order_ref)
        row.normalized_item_model = normalize_text(row.item_model)
        row.match_key = build_match_key(row.order_ref, row.item_model)
        stmt_map[row.match_key].append(row)

    for row in inb_rows:
        row.normalized_order_ref = normalize_text(row.order_ref)
        row.normalized_item_model = normalize_text(row.item_model)
        row.match_key = build_match_key(row.order_ref, row.item_model)
        inb_map[row.match_key].append(row)

    all_keys = set(stmt_map.keys()) | set(inb_map.keys())

    for key in all_keys:
        stmt_group = stmt_map.get(key, [])
        inb_group = inb_map.get(key, [])

        stmt_qty = sum((r.qty or Decimal("0")) for r in stmt_group)
        inb_qty = sum((r.qty or Decimal("0")) for r in inb_group)
        stmt_amt = sum((r.amount_tax_incl or Decimal("0")) for r in stmt_group)
        inb_amt = sum((r.amount_tax_incl or Decimal("0")) for r in inb_group)

        if stmt_group and inb_group:
            qty_diff = stmt_qty - inb_qty
            amt_diff = stmt_amt - inb_amt
            is_exact = qty_diff == 0 and amt_diff == 0
            match_status = MatchStatus.matched_exact if is_exact else MatchStatus.matched_with_diff
            recon_status = ReconciliationStatus.done if is_exact else ReconciliationStatus.exception
        elif stmt_group:
            qty_diff = stmt_qty
            amt_diff = stmt_amt
            match_status = MatchStatus.statement_only
            recon_status = ReconciliationStatus.exception
        else:
            qty_diff = -inb_qty
            amt_diff = -inb_amt
            match_status = MatchStatus.inbound_only
            recon_status = ReconciliationStatus.exception

        pair = ReconciliationPair(
            job_id=job.id,
            statement_row_ids=[r.id for r in stmt_group],
            inbound_row_ids=[r.id for r in inb_group],
            match_key=key,
            match_status=match_status,
            statement_qty_sum=stmt_qty,
            inbound_qty_sum=inb_qty,
            qty_diff=qty_diff,
            statement_amt_sum=stmt_amt,
            inbound_amt_sum=inb_amt,
            amt_diff=amt_diff,
            diff_detail={"qty_diff": str(qty_diff), "amt_diff": str(amt_diff)},
        )
        db.add(pair)
        db.flush()

        if stmt_group:
            for row in stmt_group:
                item = PurchaseItem(
                    statement_row_id=row.id,
                    inbound_row_id=inb_group[0].id if inb_group else None,
                    order_ref=row.order_ref,
                    item_model=row.item_model,
                    item_name=row.item_name,
                    qty=row.qty,
                    amount_tax_incl=row.amount_tax_incl,
                    reconciliation_status=recon_status,
                    latest_pair_id=pair.id,
                )
                db.add(item)

        if inb_group and not stmt_group:
            for row in inb_group:
                item = PurchaseItem(
                    statement_row_id=None,
                    inbound_row_id=row.id,
                    order_ref=row.order_ref,
                    item_model=row.item_model,
                    item_name=row.item_name,
                    qty=row.qty,
                    amount_tax_incl=row.amount_tax_incl,
                    reconciliation_status=recon_status,
                    latest_pair_id=pair.id,
                )
                db.add(item)

    job.job_status = "success"
    job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job
