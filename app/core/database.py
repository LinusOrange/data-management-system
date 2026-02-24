import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/reconciliation.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_startup_migrations():
    """Lightweight auto-migration for sqlite local/dev compatibility."""
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        # normalized_row.item_name
        norm_cols = {row[1] for row in conn.execute(text("PRAGMA table_info('normalized_row')")).fetchall()}
        if "item_name" not in norm_cols:
            conn.execute(text("ALTER TABLE normalized_row ADD COLUMN item_name VARCHAR(255)"))

        # purchase_item.item_name
        purchase_cols = {row[1] for row in conn.execute(text("PRAGMA table_info('purchase_item')")).fetchall()}
        if "item_name" not in purchase_cols:
            conn.execute(text("ALTER TABLE purchase_item ADD COLUMN item_name VARCHAR(255)"))
