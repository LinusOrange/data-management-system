from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ImportBatch, NormalizedRow, ParseStatus, RawRow, SourceType
from app.schemas import ImportBatchCreate, ImportBatchOut, ImportManagementOut, ManagedParsedRowOut, PreviewRowOut
from app.services.file_parser import parse_file_to_preview_rows
from app.services.reconciliation import build_match_key, normalize_text

router = APIRouter(prefix="/api/imports", tags=["imports"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("", response_model=ImportBatchOut)
def create_import_batch(payload: ImportBatchCreate, db: Session = Depends(get_db)):
    record = ImportBatch(
        source_type=payload.source_type,
        file_name=payload.file_name,
        uploaded_by=payload.uploaded_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/upload", response_model=ImportBatchOut)
async def upload_import_file(
    source_type: SourceType = Form(...),
    uploaded_by: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix
    safe_name = f"{uuid4().hex}{suffix}"
    save_path = UPLOAD_DIR / safe_name

    content = await file.read()
    save_path.write_bytes(content)

    record = ImportBatch(
        source_type=source_type,
        file_name=str(save_path),
        uploaded_by=uploaded_by,
        parse_status=ParseStatus.pending,
    )
    db.add(record)
    db.flush()

    try:
        parsed_rows = parse_file_to_preview_rows(save_path, source_type)
        existing_keys = {
            (order_ref, item_model)
            for order_ref, item_model in (
                db.query(NormalizedRow.normalized_order_ref, NormalizedRow.normalized_item_model)
                .filter(
                    NormalizedRow.source_type == source_type,
                    NormalizedRow.normalized_order_ref.is_not(None),
                    NormalizedRow.normalized_item_model.is_not(None),
                )
                .all()
            )
        }

        for parsed in parsed_rows:
            normalized_order_ref = normalize_text(parsed.order_no)
            normalized_item_model = normalize_text(parsed.item_code)
            dedup_key = (normalized_order_ref, normalized_item_model)

            if normalized_order_ref and normalized_item_model and dedup_key in existing_keys:
                continue

            raw_row = RawRow(
                batch_id=record.id,
                source_type=source_type,
                row_no=parsed.row_no,
                raw_json=parsed.raw,
            )
            db.add(raw_row)
            db.flush()

            norm_row = NormalizedRow(
                batch_id=record.id,
                raw_row_id=raw_row.id,
                source_type=source_type,
                order_ref=parsed.order_no,
                item_model=parsed.item_code,
                item_name=parsed.name,
                qty=parsed.qty,
                amount_tax_incl=parsed.amount,
                normalized_order_ref=normalized_order_ref,
                normalized_item_model=normalized_item_model,
                match_key=build_match_key(parsed.order_no, parsed.item_code),
            )
            db.add(norm_row)

            if normalized_order_ref and normalized_item_model:
                existing_keys.add(dedup_key)

        record.parse_status = ParseStatus.success
        record.parse_error = None
    except Exception as exc:  # noqa: BLE001
        record.parse_status = ParseStatus.failed
        record.parse_error = str(exc)

    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[ImportBatchOut])
def list_import_batches(db: Session = Depends(get_db)):
    return db.query(ImportBatch).order_by(ImportBatch.id.desc()).all()


@router.get("/{batch_id}", response_model=ImportBatchOut)
def get_import_batch(batch_id: int, db: Session = Depends(get_db)):
    return db.get(ImportBatch, batch_id)


@router.get("/{batch_id}/preview", response_model=list[PreviewRowOut])
def preview_import_rows(batch_id: int, db: Session = Depends(get_db)):
    batch = db.get(ImportBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="batch not found")

    rows = (
        db.query(NormalizedRow)
        .filter(NormalizedRow.batch_id == batch_id)
        .order_by(NormalizedRow.id.asc())
        .all()
    )

    raw_rows = db.query(RawRow).filter(RawRow.batch_id == batch_id).all()
    row_no_map = {raw.id: raw.row_no for raw in raw_rows}

    return [
        {
            "row_no": row_no_map.get(row.raw_row_id, row.raw_row_id),
            "name": row.item_name,
            "item_code": row.item_model,
            "qty": row.qty,
            "amount": row.amount_tax_incl,
            "order_no": row.order_ref,
        }
        for row in rows
    ]


@router.get("/manage/overview", response_model=ImportManagementOut)
def get_import_management_data(db: Session = Depends(get_db)):
    batches = db.query(ImportBatch).order_by(ImportBatch.id.desc()).all()

    normalized_rows = (
        db.query(NormalizedRow, RawRow.row_no)
        .join(RawRow, RawRow.id == NormalizedRow.raw_row_id)
        .order_by(NormalizedRow.id.desc())
        .all()
    )

    inbound_rows: list[ManagedParsedRowOut] = []
    statement_rows: list[ManagedParsedRowOut] = []

    for norm, row_no in normalized_rows:
        item = ManagedParsedRowOut(
            id=norm.id,
            batch_id=norm.batch_id,
            source_type=norm.source_type,
            row_no=row_no,
            name=norm.item_name,
            item_code=norm.item_model,
            qty=norm.qty,
            amount=norm.amount_tax_incl,
            order_no=norm.order_ref,
        )
        if norm.source_type == SourceType.inbound:
            inbound_rows.append(item)
        else:
            statement_rows.append(item)

    return ImportManagementOut(
        batches=batches,
        inbound_rows=inbound_rows,
        statement_rows=statement_rows,
    )


@router.delete("/{batch_id}")
def delete_import_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.get(ImportBatch, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="batch not found")

    db.query(NormalizedRow).filter(NormalizedRow.batch_id == batch_id).delete(synchronize_session=False)
    db.query(RawRow).filter(RawRow.batch_id == batch_id).delete(synchronize_session=False)
    db.delete(batch)
    db.commit()
    return {"ok": True}
