"""Account API endpoints."""
import io
import math
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.models import get_db
from app.schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountDetailResponse,
    AccountListResponse,
    AccountImportResult,
    TagBrief,
    BatchDeleteRequest,
    BatchTagsRequest,
    BatchUpdateRequest,
)
from app.services.account_service import AccountService
from app.services.crypto_service import crypto_service
from app.utils.security import get_current_user


router = APIRouter(prefix="/accounts", tags=["Accounts"])


def account_to_response(account) -> AccountResponse:
    """Convert Account model to response schema."""
    return AccountResponse(
        id=account.id,
        email=account.email,
        note=account.note,
        sub2api=account.sub2api,
        source=account.source,
        browser=account.browser,
        gpt_membership=account.gpt_membership,
        family_group=account.family_group,
        recovery_email=account.recovery_email,
        has_password=account.password_encrypted is not None,
        has_totp=account.totp_secret_encrypted is not None,
        tags=[TagBrief(id=t.id, name=t.name, color=t.color) for t in account.tags],
        custom_fields=account.custom_fields or {},
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


@router.get("", response_model=AccountListResponse)
async def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE),
    search: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    tag_ids: Optional[str] = Query(None, description="Comma-separated tag IDs"),
    gpt_membership: Optional[str] = Query(None),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated list of accounts."""
    service = AccountService(db)

    # Parse tag_ids
    tag_id_list = None
    if tag_ids:
        tag_id_list = [t.strip() for t in tag_ids.split(",") if t.strip()]

    accounts, total = service.get_accounts(
        page=page,
        page_size=page_size,
        search=search,
        source=source,
        tag_ids=tag_id_list,
        gpt_membership=gpt_membership,
    )

    return AccountListResponse(
        items=[account_to_response(a) for a in accounts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get("/sources", response_model=List[str])
async def get_sources(
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all unique account sources."""
    service = AccountService(db)
    return service.get_sources()


@router.get("/stats")
async def get_stats(
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get account statistics."""
    service = AccountService(db)
    return service.get_stats()


# =====================
# Batch Operations (must be before /{account_id} routes)
# =====================

@router.post("/batch/delete")
async def batch_delete_accounts(
    request: BatchDeleteRequest,
    hard: bool = Query(False, description="Permanently delete"),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete multiple accounts at once."""
    service = AccountService(db)
    deleted = 0
    failed = 0

    for account_id in request.account_ids:
        if service.delete_account(account_id, hard_delete=hard):
            deleted += 1
        else:
            failed += 1

    return {"deleted": deleted, "failed": failed}


@router.post("/batch/tags")
async def batch_update_tags(
    request: BatchTagsRequest,
    action: str = Query("add", pattern=r"^(add|remove|set)$"),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update tags for multiple accounts.

    Actions:
    - add: Add tags to accounts (keep existing)
    - remove: Remove tags from accounts
    - set: Replace all tags with given tags
    """
    service = AccountService(db)
    updated = 0
    failed = 0

    for account_id in request.account_ids:
        try:
            account = service.get_account_by_id(account_id)
            if not account:
                failed += 1
                continue

            current_tag_ids = [t.id for t in account.tags]

            if action == "add":
                new_tag_ids = list(set(current_tag_ids + request.tag_ids))
            elif action == "remove":
                new_tag_ids = [t for t in current_tag_ids if t not in request.tag_ids]
            else:  # set
                new_tag_ids = request.tag_ids

            service.update_account(account_id, AccountUpdate(tag_ids=new_tag_ids))
            updated += 1
        except Exception:
            failed += 1

    return {"updated": updated, "failed": failed}


@router.post("/batch/update")
async def batch_update_accounts(
    request: BatchUpdateRequest,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update multiple accounts with the same data."""
    service = AccountService(db)
    updated = 0
    failed = 0

    # Extract update data from request (excluding account_ids)
    update_data = AccountUpdate(
        email=request.email,
        note=request.note,
        sub2api=request.sub2api,
        source=request.source,
        browser=request.browser,
        gpt_membership=request.gpt_membership,
        family_group=request.family_group,
        recovery_email=request.recovery_email,
        tag_ids=request.tag_ids,
    )

    for account_id in request.account_ids:
        try:
            if service.update_account(account_id, update_data):
                updated += 1
            else:
                failed += 1
        except Exception:
            failed += 1

    return {"updated": updated, "failed": failed}


# =====================
# Single Account Operations
# =====================

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get account by ID."""
    service = AccountService(db)
    account = service.get_account_by_id(account_id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account_to_response(account)


@router.get("/{account_id}/password")
async def get_account_password(
    account_id: str,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get decrypted password for an account."""
    service = AccountService(db)
    password = service.get_decrypted_password(account_id)

    if password is None:
        account = service.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return {"password": None}

    return {"password": password}


@router.get("/{account_id}/totp")
async def get_account_totp(
    account_id: str,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get decrypted TOTP secret for an account."""
    service = AccountService(db)
    totp = service.get_decrypted_totp(account_id)

    if totp is None:
        account = service.get_account_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        return {"totp_secret": None}

    return {"totp_secret": totp}


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    data: AccountCreate,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new account."""
    service = AccountService(db)

    try:
        account = service.create_account(data)
        return account_to_response(account)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    data: AccountUpdate,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing account."""
    service = AccountService(db)
    account = service.update_account(account_id, data)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account_to_response(account)


@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    hard: bool = Query(False, description="Permanently delete"),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an account."""
    service = AccountService(db)
    success = service.delete_account(account_id, hard_delete=hard)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return {"message": "Account deleted successfully"}


@router.post("/import", response_model=AccountImportResult)
async def import_accounts(
    file: UploadFile = File(...),
    conflict_strategy: str = Query("skip", pattern=r"^(skip|overwrite|merge)$"),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Import accounts from Excel file."""
    import pandas as pd

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are supported",
        )

    try:
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read Excel file: {str(e)}",
        )

    service = AccountService(db)

    # Column mapping
    column_map = {
        "账号": "email",
        "密码": "password",
        "备注": "note",
        "sub2api": "sub2api",
        "来源": "source",
        "登录浏览器": "browser",
        "是否是gpt会员": "gpt_membership",
        "所属家庭": "family_group",
        "辅助邮箱": "recovery_email",
        "2fa": "totp_secret",
    }

    imported = 0
    skipped = 0
    errors = []

    for idx, row in df.iterrows():
        try:
            # Map columns
            data = {}
            for cn_name, en_name in column_map.items():
                if cn_name in df.columns:
                    value = row[cn_name]
                    if pd.notna(value):
                        if en_name == "sub2api":
                            data[en_name] = str(value).strip() == "有"
                        else:
                            data[en_name] = str(value).strip()

            if "email" not in data:
                errors.append(f"Row {idx + 2}: Missing email")
                continue

            # Check if exists
            existing = service.get_account_by_email(data["email"])

            if existing:
                if conflict_strategy == "skip":
                    skipped += 1
                    continue
                elif conflict_strategy == "overwrite":
                    # Update existing
                    update_data = AccountUpdate(**data)
                    service.update_account(existing.id, update_data)
                    imported += 1
                elif conflict_strategy == "merge":
                    # Only update empty fields
                    update_dict = {}
                    for key, value in data.items():
                        if key == "email":
                            continue
                        current = getattr(existing, key if key not in ("password", "totp_secret") else f"{key}_encrypted")
                        if current is None or current == "":
                            update_dict[key] = value
                    if update_dict:
                        service.update_account(existing.id, AccountUpdate(**update_dict))
                    imported += 1
            else:
                # Create new
                create_data = AccountCreate(**data)
                service.create_account(create_data)
                imported += 1

        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")

    return AccountImportResult(
        total=len(df),
        imported=imported,
        skipped=skipped,
        errors=errors[:10],  # Limit error messages
    )


@router.get("/export/download")
async def export_accounts(
    format: str = Query("excel", pattern=r"^(excel|csv|json)$"),
    include_password: bool = Query(False),
    account_ids: Optional[str] = Query(None, description="Comma-separated account IDs"),
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export accounts to file."""
    import pandas as pd
    import json

    service = AccountService(db)

    # Get accounts
    if account_ids:
        id_list = [i.strip() for i in account_ids.split(",")]
        accounts = [service.get_account_by_id(i) for i in id_list]
        accounts = [a for a in accounts if a]
    else:
        accounts, _ = service.get_accounts(page=1, page_size=10000)

    # Build data
    data = []
    # Collect all custom field keys for column headers
    all_custom_keys = set()
    for acc in accounts:
        if acc.custom_fields:
            all_custom_keys.update(acc.custom_fields.keys())
    all_custom_keys = sorted(all_custom_keys)

    for acc in accounts:
        row = {
            "账号": acc.email,
            "备注": acc.note,
            "sub2api": "有" if acc.sub2api else "",
            "来源": acc.source,
            "登录浏览器": acc.browser,
            "是否是gpt会员": acc.gpt_membership,
            "所属家庭": acc.family_group,
            "辅助邮箱": acc.recovery_email,
        }

        if include_password:
            row["密码"] = service.get_decrypted_password(acc.id) or ""
            row["2fa"] = service.get_decrypted_totp(acc.id) or ""
        else:
            row["密码"] = "******" if acc.password_encrypted else ""
            row["2fa"] = "******" if acc.totp_secret_encrypted else ""

        # Add custom fields as additional columns
        for key in all_custom_keys:
            row[f"自定义_{key}"] = (acc.custom_fields or {}).get(key, "")

        data.append(row)

    if format == "json":
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=accounts.json"},
        )

    df = pd.DataFrame(data)

    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=accounts.csv"},
        )

    # Excel
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=accounts.xlsx"},
    )
