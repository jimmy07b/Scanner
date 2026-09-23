import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "RootLayer"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database: Supports SQLite (default local) or PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite+aiosqlite:///{BASE_DIR / 'aegis_scan.db'}"
    )
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "aegis_super_secret_jwt_key_startup_mvp_2026_change_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ADMIN_DEFAULT_EMAIL: str = os.getenv("ADMIN_EMAIL", os.getenv("ADMIN_DEFAULT_EMAIL", "admin@rootlayer.io"))
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_PASSWORD", os.getenv("ADMIN_DEFAULT_PASSWORD", "AegisScan2026!Secure"))
    
    # File Storage & Limits
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    RETENTION_HOURS: int = 24  # Privacy first auto-purge
    
    # Pricing
    ADVANCED_AUDIT_PRICE_INR: int = 1999
    
    # Allowed CORS Origins (Configurable for production domains e.g. Vercel, custom domain)
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
        ).split(",")
        if origin.strip()
    ]

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
