from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import InvoiceStatus, PurchaseItem, ReconciliationStatus
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    pending_reconciliation_count = (
        db.query(func.count(PurchaseItem.id))
        .filter(PurchaseItem.reconciliation_status == ReconciliationStatus.pending)
        .scalar()
    )
    pending_invoice_count = (
        db.query(func.count(PurchaseItem.id))
        .filter(PurchaseItem.invoice_status.in_([InvoiceStatus.not_invoiced, InvoiceStatus.partially_invoiced]))
        .scalar()
    )
    reconciliation_exception_count = (
        db.query(func.count(PurchaseItem.id))
        .filter(PurchaseItem.reconciliation_status == ReconciliationStatus.exception)
        .scalar()
    )
    closed_loop_count = (
        db.query(func.count(PurchaseItem.id))
        .filter(
            PurchaseItem.reconciliation_status == ReconciliationStatus.done,
            PurchaseItem.invoice_status == InvoiceStatus.invoiced,
        )
        .scalar()
    )

    return DashboardSummary(
        pending_reconciliation_count=pending_reconciliation_count or 0,
        pending_invoice_count=pending_invoice_count or 0,
        reconciliation_exception_count=reconciliation_exception_count or 0,
        closed_loop_count=closed_loop_count or 0,
    )
