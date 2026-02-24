from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import NormalizedRow
from app.schemas import NormalizedRowCreate
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
