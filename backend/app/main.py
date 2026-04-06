from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
import logging
from app.core.config import settings
from app.core.database import engine, Base
from app.features.candidates.router import router as candidates_router
from app.features.matching.router import router as matching_router
from app.features.candidates.embedding import load_faiss_index

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _check_schema_sync() -> None:
    """
    On startup, verify that all SQLAlchemy model columns exist in the DB.
    Logs a clear warning if the schema is out of sync so developers know
    to run: alembic upgrade head
    """
    inspector = inspect(engine)
    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            logger.warning("⚠️  Table '%s' missing — run: alembic upgrade head", table_name)
            continue
        db_cols = {col["name"] for col in inspector.get_columns(table_name)}
        model_cols = {col.name for col in table.columns}
        missing = model_cols - db_cols
        if missing:
            logger.warning(
                "⚠️  Schema mismatch on table '%s': missing columns %s — run: alembic upgrade head",
                table_name, missing
            )
        else:
            logger.info("✅ Schema in sync for table '%s'", table_name)


# Run schema check, create any missing tables (safe no-op if already exist)
_check_schema_sync()
Base.metadata.create_all(bind=engine)
load_faiss_index()

app.include_router(candidates_router, prefix="/api/resumes",  tags=["Resumes"])
app.include_router(matching_router,   prefix="/api/matching", tags=["Matching"])


@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "status": "running",
    }
