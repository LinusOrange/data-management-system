from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ImportBatch, SourceType
from app.schemas import ImportBatchCreate, ImportBatchOut

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
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=list[ImportBatchOut])
def list_import_batches(db: Session = Depends(get_db)):
    return db.query(ImportBatch).order_by(ImportBatch.id.desc()).all()


@router.get("/{batch_id}", response_model=ImportBatchOut)
def get_import_batch(batch_id: int, db: Session = Depends(get_db)):
    return db.get(ImportBatch, batch_id)
