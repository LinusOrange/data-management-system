from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SourceType(str, Enum):
    statement = "statement"
    inbound = "inbound"


class ParseStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class ReconciliationStatus(str, Enum):
    pending = "pending"
    done = "done"
    exception = "exception"


class InvoiceStatus(str, Enum):
    not_invoiced = "not_invoiced"
    partially_invoiced = "partially_invoiced"
    invoiced = "invoiced"


class MatchStatus(str, Enum):
    matched_exact = "matched_exact"
    matched_with_diff = "matched_with_diff"
    statement_only = "statement_only"
    inbound_only = "inbound_only"


class ImportBatch(Base):
    __tablename__ = "import_batch"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[str | None] = mapped_column(String(64))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    parse_status: Mapped[ParseStatus] = mapped_column(SAEnum(ParseStatus), default=ParseStatus.pending, nullable=False)
    parse_error: Mapped[str | None] = mapped_column(Text)


class RawRow(Base):
    __tablename__ = "raw_row"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batch.id"), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)
    row_no: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class NormalizedRow(Base):
    __tablename__ = "normalized_row"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("import_batch.id"), nullable=False)
    raw_row_id: Mapped[int] = mapped_column(ForeignKey("raw_row.id"), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)

    biz_date: Mapped[date | None] = mapped_column(Date)
    order_ref: Mapped[str | None] = mapped_column(String(100))
    item_model: Mapped[str | None] = mapped_column(String(100))

    qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    amount_tax_incl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    counterparty_name: Mapped[str | None] = mapped_column(String(255))

    normalized_order_ref: Mapped[str | None] = mapped_column(String(100))
    normalized_item_model: Mapped[str | None] = mapped_column(String(100))
    match_key: Mapped[str | None] = mapped_column(String(220))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ReconciliationJob(Base):
    __tablename__ = "reconciliation_job"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batch.id"))
    inbound_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batch.id"))
    job_status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)


class ReconciliationPair(Base):
    __tablename__ = "reconciliation_pair"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("reconciliation_job.id"), nullable=False)
    statement_row_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    inbound_row_ids: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)
    match_key: Mapped[str | None] = mapped_column(String(220))
    match_status: Mapped[MatchStatus] = mapped_column(SAEnum(MatchStatus), nullable=False)

    statement_qty_sum: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    inbound_qty_sum: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    qty_diff: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    statement_amt_sum: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    inbound_amt_sum: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    amt_diff: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))

    diff_detail: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class PurchaseItem(Base):
    __tablename__ = "purchase_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    statement_row_id: Mapped[int | None] = mapped_column(ForeignKey("normalized_row.id"))
    inbound_row_id: Mapped[int | None] = mapped_column(ForeignKey("normalized_row.id"))

    order_ref: Mapped[str | None] = mapped_column(String(100))
    item_model: Mapped[str | None] = mapped_column(String(100))
    qty: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    amount_tax_incl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))

    reconciliation_status: Mapped[ReconciliationStatus] = mapped_column(
        SAEnum(ReconciliationStatus), default=ReconciliationStatus.pending, nullable=False
    )
    invoice_status: Mapped[InvoiceStatus] = mapped_column(
        SAEnum(InvoiceStatus), default=InvoiceStatus.not_invoiced, nullable=False
    )

    latest_pair_id: Mapped[int | None] = mapped_column(ForeignKey("reconciliation_pair.id"))
    remark: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class StatusEvent(Base):
    __tablename__ = "status_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_item_id: Mapped[int] = mapped_column(ForeignKey("purchase_item.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    old_value: Mapped[str | None] = mapped_column(String(30))
    new_value: Mapped[str | None] = mapped_column(String(30))
    operator: Mapped[str | None] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    before_json: Mapped[dict | None] = mapped_column(JSON)
    after_json: Mapped[dict | None] = mapped_column(JSON)
    operator: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
