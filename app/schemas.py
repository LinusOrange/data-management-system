from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models import InvoiceStatus, ReconciliationStatus, SourceType


class ImportBatchCreate(BaseModel):
    source_type: SourceType
    file_name: str
    uploaded_by: str | None = None


class ImportBatchOut(BaseModel):
    id: int
    source_type: SourceType
    file_name: str
    uploaded_by: str | None
    parse_status: str
    parse_error: str | None = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class PreviewRowOut(BaseModel):
    row_no: int
    name: str | None
    item_code: str | None
    qty: Decimal | None
    amount: Decimal | None
    order_no: str | None


class PurchaseItemOut(BaseModel):
    id: int
    order_ref: str | None
    item_model: str | None
    item_name: str | None
    qty: Decimal | None
    amount_tax_incl: Decimal | None
    reconciliation_status: ReconciliationStatus
    invoice_status: InvoiceStatus

    class Config:
        from_attributes = True


class PurchaseItemInvoiceUpdate(BaseModel):
    invoice_status: InvoiceStatus
    operator: str | None = None
    note: str | None = None


class PurchaseItemReconciliationUpdate(BaseModel):
    reconciliation_status: ReconciliationStatus
    operator: str | None = None
    note: str | None = None


class DashboardSummary(BaseModel):
    pending_reconciliation_count: int
    pending_invoice_count: int
    reconciliation_exception_count: int
    closed_loop_count: int


class NormalizedRowCreate(BaseModel):
    batch_id: int
    raw_row_id: int
    source_type: SourceType
    biz_date: date | None = None
    order_ref: str | None = None
    item_model: str | None = None
    item_name: str | None = None
    qty: Decimal | None = None
    amount_tax_incl: Decimal | None = None
    counterparty_name: str | None = None


class ManagedParsedRowOut(BaseModel):
    id: int
    batch_id: int
    source_type: SourceType
    row_no: int
    name: str | None
    item_code: str | None
    qty: Decimal | None
    amount: Decimal | None
    order_no: str | None


class ImportManagementOut(BaseModel):
    batches: list[ImportBatchOut]
    inbound_rows: list[ManagedParsedRowOut]
    statement_rows: list[ManagedParsedRowOut]


class ReconciliationResultOut(BaseModel):
    match_key: str
    order_no: str | None
    item_code: str | None
    statement_qty_sum: Decimal | None
    inbound_qty_sum: Decimal | None
    statement_amt_sum: Decimal | None
    inbound_amt_sum: Decimal | None
    qty_diff: Decimal | None
    amt_diff: Decimal | None
    match_status: str
    reconciliation_result: str


class ReconciliationResultSummaryOut(BaseModel):
    success: list[ReconciliationResultOut]
    failed: list[ReconciliationResultOut]
