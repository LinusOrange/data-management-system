from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import PurchaseItem, ReconciliationStatus, StatusEvent
from app.schemas import (
    PurchaseItemInvoiceUpdate,
    PurchaseItemOut,
    PurchaseItemReconciliationUpdate,
)

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


@router.get("", response_model=list[PurchaseItemOut])
def list_purchases(
    reconciliation_status: ReconciliationStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(PurchaseItem)
    if reconciliation_status:
        query = query.filter(PurchaseItem.reconciliation_status == reconciliation_status)
    return query.order_by(PurchaseItem.id.desc()).all()


@router.get("/{item_id}", response_model=PurchaseItemOut)
def get_purchase(item_id: int, db: Session = Depends(get_db)):
    item = db.get(PurchaseItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="purchase item not found")
    return item


@router.patch("/{item_id}/invoice-status", response_model=PurchaseItemOut)
def update_invoice_status(item_id: int, payload: PurchaseItemInvoiceUpdate, db: Session = Depends(get_db)):
    item = db.get(PurchaseItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="purchase item not found")

    event = StatusEvent(
        purchase_item_id=item.id,
        event_type="invoice_update",
        old_value=item.invoice_status.value,
        new_value=payload.invoice_status.value,
        operator=payload.operator,
        note=payload.note,
    )
    item.invoice_status = payload.invoice_status
    db.add(event)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}/reconciliation-status", response_model=PurchaseItemOut)
def update_reconciliation_status(
    item_id: int,
    payload: PurchaseItemReconciliationUpdate,
    db: Session = Depends(get_db),
):
    item = db.get(PurchaseItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="purchase item not found")

    event = StatusEvent(
        purchase_item_id=item.id,
        event_type="reconciliation_update",
        old_value=item.reconciliation_status.value,
        new_value=payload.reconciliation_status.value,
        operator=payload.operator,
        note=payload.note,
    )
    item.reconciliation_status = payload.reconciliation_status
    db.add(event)
    db.commit()
    db.refresh(item)
    return item
