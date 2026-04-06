from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_TITLE: str = "Resume Matching System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    # SQLite by default; override with PostgreSQL URL in production
    DATABASE_URL: str = "sqlite:///./resume_matching.db"

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g.:
    # ALLOWED_ORIGINS=http://localhost:5173,https://myapp.com
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # ── AI / Embeddings ──────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── File Storage ─────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"

    # ── FAISS Index ──────────────────────────────────────────────────────────
    FAISS_INDEX_PATH: str = "faiss_index.bin"
    FAISS_IDS_PATH: str = "faiss_ids.npy"
    EMBEDDING_DIM: int = 384

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list for CORS middleware."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # ignore unknown env vars


# Single shared instance — import this everywhere
settings = Settings()
