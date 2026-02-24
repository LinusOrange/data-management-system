from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ImportBatch
from app.schemas import ImportBatchCreate, ImportBatchOut

router = APIRouter(prefix="/api/imports", tags=["imports"])


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


@router.get("/{batch_id}", response_model=ImportBatchOut)
def get_import_batch(batch_id: int, db: Session = Depends(get_db)):
    return db.get(ImportBatch, batch_id)
