from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import MatchStatus, NormalizedRow, ReconciliationPair
from app.schemas import NormalizedRowCreate, ReconciliationResultOut, ReconciliationResultSummaryOut
from app.services.reconciliation import build_match_key, normalize_text, reconcile_batches

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])


@router.post("/rows")
def create_normalized_row(payload: NormalizedRowCreate, db: Session = Depends(get_db)):
    row = NormalizedRow(
        batch_id=payload.batch_id,
        raw_row_id=payload.raw_row_id,
        source_type=payload.source_type,
        biz_date=payload.biz_date,
        order_ref=payload.order_ref,
        item_model=payload.item_model,
        item_name=payload.item_name,
        qty=payload.qty,
        amount_tax_incl=payload.amount_tax_incl,
        counterparty_name=payload.counterparty_name,
        normalized_order_ref=normalize_text(payload.order_ref),
        normalized_item_model=normalize_text(payload.item_model),
        match_key=build_match_key(payload.order_ref, payload.item_model),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "match_key": row.match_key}


@router.post("/run")
def run_reconciliation(statement_batch_id: int, inbound_batch_id: int, db: Session = Depends(get_db)):
    job = reconcile_batches(db, statement_batch_id=statement_batch_id, inbound_batch_id=inbound_batch_id)
    return {"job_id": job.id, "job_status": job.job_status}


@router.get("/results", response_model=ReconciliationResultSummaryOut)
def list_reconciliation_results(db: Session = Depends(get_db)):
    pairs = db.query(ReconciliationPair).order_by(ReconciliationPair.id.desc()).all()

    success: list[ReconciliationResultOut] = []
    failed: list[ReconciliationResultOut] = []

    for pair in pairs:
        order_no, item_code = (pair.match_key or "|").split("|", 1)
        result = ReconciliationResultOut(
            match_key=pair.match_key or "",
            order_no=order_no or None,
            item_code=item_code or None,
            statement_qty_sum=pair.statement_qty_sum,
            inbound_qty_sum=pair.inbound_qty_sum,
            statement_amt_sum=pair.statement_amt_sum,
            inbound_amt_sum=pair.inbound_amt_sum,
            qty_diff=pair.qty_diff,
            amt_diff=pair.amt_diff,
            match_status=pair.match_status.value,
            reconciliation_result="success" if pair.match_status == MatchStatus.matched_exact else "failed",
        )
        if pair.match_status == MatchStatus.matched_exact:
            success.append(result)
        else:
            failed.append(result)

    return ReconciliationResultSummaryOut(success=success, failed=failed)
