"""Backup API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.services.backup_service import backup_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.get("/list")
async def list_backups(_: str = Depends(get_current_user)):
    """Get list of available backups."""
    return {
        "backups": backup_service.get_backups(),
        "config": {
            "enabled": settings.AUTO_BACKUP_ENABLED,
            "interval_hours": settings.AUTO_BACKUP_INTERVAL_HOURS,
            "keep_count": settings.AUTO_BACKUP_KEEP_COUNT,
            "format": settings.AUTO_BACKUP_FORMAT,
        },
    }


@router.post("/now")
async def backup_now(_: str = Depends(get_current_user)):
    """Trigger immediate backup."""
    try:
        filepath = backup_service.backup_now()
        if filepath:
            return {
                "success": True,
                "message": "备份成功",
                "filename": filepath.name,
            }
        return {
            "success": True,
            "message": "没有账户需要备份",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"备份失败: {str(e)}")


@router.get("/download/{filename}")
async def download_backup(
    filename: str,
    _: str = Depends(get_current_user),
):
    """Download a backup file."""
    # Validate filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    filepath = settings.BACKUP_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete("/delete/{filename}")
async def delete_backup(
    filename: str,
    _: str = Depends(get_current_user),
):
    """Delete a backup file."""
    # Validate filename to prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    filepath = settings.BACKUP_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="备份文件不存在")

    try:
        filepath.unlink()
        return {"success": True, "message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
