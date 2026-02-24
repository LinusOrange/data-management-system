from fastapi import FastAPI

from app.core.database import Base, engine
from app.routers.dashboard import router as dashboard_router
from app.routers.imports import router as imports_router
from app.routers.purchases import router as purchases_router
from app.routers.reconciliation import router as reconciliation_router

app = FastAPI(title="Data Reconciliation System")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(imports_router)
app.include_router(reconciliation_router)
app.include_router(purchases_router)
app.include_router(dashboard_router)
