"""Auto backup service for scheduled account exports."""
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from app.config import settings
from app.models import SessionLocal
from app.services.account_service import AccountService

logger = logging.getLogger(__name__)


class BackupService:
    """Service for automatic account backups."""

    def __init__(self):
        self._timer: Optional[threading.Timer] = None
        self._running = False

    def start(self):
        """Start the backup scheduler."""
        if not settings.AUTO_BACKUP_ENABLED:
            logger.info("Auto backup is disabled")
            return

        self._running = True
        self._schedule_next_backup()
        logger.info(
            f"Auto backup started: interval={settings.AUTO_BACKUP_INTERVAL_HOURS}h, "
            f"keep={settings.AUTO_BACKUP_KEEP_COUNT}, format={settings.AUTO_BACKUP_FORMAT}"
        )

    def stop(self):
        """Stop the backup scheduler."""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        logger.info("Auto backup stopped")

    def _schedule_next_backup(self):
        """Schedule the next backup."""
        if not self._running:
            return

        interval_seconds = settings.AUTO_BACKUP_INTERVAL_HOURS * 3600
        self._timer = threading.Timer(interval_seconds, self._run_backup)
        self._timer.daemon = True
        self._timer.start()

    def _run_backup(self):
        """Execute backup and schedule next one."""
        try:
            self.backup_now()
        except Exception as e:
            logger.error(f"Auto backup failed: {e}")
        finally:
            self._schedule_next_backup()

    def backup_now(self, include_password: bool = True) -> Optional[Path]:
        """
        Execute backup immediately.
        
        Args:
            include_password: Whether to include decrypted passwords in backup
            
        Returns:
            Path to the backup file, or None if failed
        """
        db = SessionLocal()
        try:
            service = AccountService(db)
            accounts, _ = service.get_accounts(page=1, page_size=100000)

            if not accounts:
                logger.info("No accounts to backup")
                return None

            # Collect all custom field keys
            all_custom_keys = set()
            for acc in accounts:
                if acc.custom_fields:
                    all_custom_keys.update(acc.custom_fields.keys())
            all_custom_keys = sorted(all_custom_keys)

            # Build data
            data = []
            for acc in accounts:
                row = {
                    "id": acc.id,
                    "账号": acc.email,
                    "备注": acc.note or "",
                    "sub2api": "有" if acc.sub2api else "",
                    "来源": acc.source or "",
                    "登录浏览器": acc.browser or "",
                    "是否是gpt会员": acc.gpt_membership or "",
                    "所属家庭": acc.family_group or "",
                    "辅助邮箱": acc.recovery_email or "",
                    "标签": ",".join([t.name for t in acc.tags]),
                    "创建时间": acc.created_at.isoformat() if acc.created_at else "",
                    "更新时间": acc.updated_at.isoformat() if acc.updated_at else "",
                }

                if include_password:
                    row["密码"] = service.get_decrypted_password(acc.id) or ""
                    row["2fa"] = service.get_decrypted_totp(acc.id) or ""

                # Add custom fields
                for key in all_custom_keys:
                    row[f"自定义_{key}"] = (acc.custom_fields or {}).get(key, "")

                data.append(row)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_format = settings.AUTO_BACKUP_FORMAT.lower()

            if backup_format == "json":
                filename = f"backup_{timestamp}.json"
                filepath = settings.BACKUP_DIR / filename
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            elif backup_format == "csv":
                filename = f"backup_{timestamp}.csv"
                filepath = settings.BACKUP_DIR / filename
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, encoding="utf-8-sig")

            else:  # excel
                filename = f"backup_{timestamp}.xlsx"
                filepath = settings.BACKUP_DIR / filename
                df = pd.DataFrame(data)
                df.to_excel(filepath, index=False, engine="openpyxl")

            logger.info(f"Backup created: {filepath} ({len(accounts)} accounts)")

            # Cleanup old backups
            self._cleanup_old_backups()

            return filepath

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
        finally:
            db.close()

    def _cleanup_old_backups(self):
        """Remove old backup files, keeping only the configured number."""
        try:
            backup_files = sorted(
                settings.BACKUP_DIR.glob("backup_*.*"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )

            # Keep only the configured number of backups
            files_to_delete = backup_files[settings.AUTO_BACKUP_KEEP_COUNT:]
            for f in files_to_delete:
                f.unlink()
                logger.info(f"Deleted old backup: {f.name}")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def get_backups(self) -> list:
        """Get list of available backups."""
        backups = []
        for f in sorted(
            settings.BACKUP_DIR.glob("backup_*.*"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        ):
            backups.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
        return backups


# Global backup service instance
backup_service = BackupService()
