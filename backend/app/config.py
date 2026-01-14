"""Application configuration settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Account Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_PATH: Path = DATA_DIR / "accounts.db"
    BACKUP_DIR: Path = DATA_DIR / "backups"

    # Security - Use a fixed secret key or load from env, otherwise JWT tokens will invalidate on restart
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "account-management-system-secret-key-2024-please-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    MASTER_PASSWORD_MIN_LENGTH: int = 8

    # Clipboard
    CLIPBOARD_CLEAR_SECONDS: int = 30

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Auto Backup
    AUTO_BACKUP_ENABLED: bool = True
    AUTO_BACKUP_INTERVAL_HOURS: int = 24  # 备份间隔（小时）
    AUTO_BACKUP_KEEP_COUNT: int = 7  # 保留备份数量
    AUTO_BACKUP_FORMAT: str = "json"  # 备份格式: json, csv, excel

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
