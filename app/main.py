import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine, run_startup_migrations
from app.routers.dashboard import router as dashboard_router
from app.routers.imports import router as imports_router
from app.routers.purchases import router as purchases_router
from app.routers.reconciliation import router as reconciliation_router

app = FastAPI(title="Data Reconciliation System")

cors_origins = os.getenv("CORS_ORIGINS", "*")
origins = [o.strip() for o in cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    run_startup_migrations()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(imports_router)
app.include_router(reconciliation_router)
app.include_router(purchases_router)
app.include_router(dashboard_router)
