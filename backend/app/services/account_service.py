"""Account service for CRUD operations."""
from typing import List, Optional, Tuple

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Account, Tag
from app.schemas import AccountCreate, AccountUpdate
from app.services.crypto_service import crypto_service


class AccountService:
    """Service for account operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_accounts(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        source: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        gpt_membership: Optional[str] = None,
    ) -> Tuple[List[Account], int]:
        """Get paginated list of accounts with optional filters."""
        query = self.db.query(Account).filter(Account.is_deleted == False)

        # Apply search filter
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Account.email.ilike(search_pattern),
                    Account.note.ilike(search_pattern),
                )
            )

        # Apply source filter
        if source:
            query = query.filter(Account.source == source)

        # Apply GPT membership filter
        if gpt_membership:
            query = query.filter(Account.gpt_membership == gpt_membership)

        # Apply tag filter
        if tag_ids:
            query = query.filter(Account.tags.any(Tag.id.in_(tag_ids)))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        accounts = query.order_by(Account.created_at.desc()).offset(offset).limit(page_size).all()

        return accounts, total

    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        return self.db.query(Account).filter(
            Account.id == account_id,
            Account.is_deleted == False
        ).first()

    def get_account_by_email(self, email: str) -> Optional[Account]:
        """Get account by email."""
        return self.db.query(Account).filter(
            Account.email == email,
            Account.is_deleted == False
        ).first()

    def create_account(self, data: AccountCreate) -> Account:
        """Create a new account."""
        # Check if email already exists
        existing = self.get_account_by_email(data.email)
        if existing:
            raise ValueError(f"Account with email {data.email} already exists")

        # Encrypt sensitive fields
        password_encrypted = None
        if data.password:
            password_encrypted = crypto_service.encrypt(data.password)

        totp_encrypted = None
        if data.totp_secret:
            totp_encrypted = crypto_service.encrypt(data.totp_secret)

        # Create account
        account = Account(
            email=data.email,
            password_encrypted=password_encrypted,
            note=data.note,
            sub2api=data.sub2api,
            source=data.source,
            browser=data.browser,
            gpt_membership=data.gpt_membership,
            family_group=data.family_group,
            recovery_email=data.recovery_email,
            totp_secret_encrypted=totp_encrypted,
            custom_fields=data.custom_fields or {},
        )

        # Add tags
        if data.tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
            account.tags = tags

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def update_account(self, account_id: str, data: AccountUpdate) -> Optional[Account]:
        """Update an existing account."""
        account = self.get_account_by_id(account_id)
        if not account:
            return None

        # Update fields
        update_data = data.model_dump(exclude_unset=True)

        # Handle password encryption
        if "password" in update_data:
            password = update_data.pop("password")
            if password:
                account.password_encrypted = crypto_service.encrypt(password)
            else:
                account.password_encrypted = None

        # Handle TOTP encryption
        if "totp_secret" in update_data:
            totp = update_data.pop("totp_secret")
            if totp:
                account.totp_secret_encrypted = crypto_service.encrypt(totp)
            else:
                account.totp_secret_encrypted = None

        # Handle tags
        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
                account.tags = tags

        # Update other fields
        for key, value in update_data.items():
            setattr(account, key, value)

        self.db.commit()
        self.db.refresh(account)

        return account

    def delete_account(self, account_id: str, hard_delete: bool = False) -> bool:
        """Delete an account (soft or hard delete)."""
        account = self.get_account_by_id(account_id)
        if not account:
            return False

        if hard_delete:
            self.db.delete(account)
        else:
            account.is_deleted = True

        self.db.commit()
        return True

    def get_decrypted_password(self, account_id: str) -> Optional[str]:
        """Get decrypted password for an account."""
        account = self.get_account_by_id(account_id)
        if not account or not account.password_encrypted:
            return None

        return crypto_service.decrypt(account.password_encrypted)

    def get_decrypted_totp(self, account_id: str) -> Optional[str]:
        """Get decrypted TOTP secret for an account."""
        account = self.get_account_by_id(account_id)
        if not account or not account.totp_secret_encrypted:
            return None

        return crypto_service.decrypt(account.totp_secret_encrypted)

    def get_sources(self) -> List[str]:
        """Get all unique sources."""
        result = self.db.query(Account.source).filter(
            Account.is_deleted == False,
            Account.source.isnot(None)
        ).distinct().all()
        return [r[0] for r in result if r[0]]

    def get_stats(self) -> dict:
        """Get account statistics."""
        total = self.db.query(Account).filter(Account.is_deleted == False).count()
        with_gpt = self.db.query(Account).filter(
            Account.is_deleted == False,
            Account.gpt_membership.isnot(None)
        ).count()
        by_source = self.db.query(
            Account.source,
            func.count(Account.id)
        ).filter(
            Account.is_deleted == False
        ).group_by(Account.source).all()

        return {
            "total": total,
            "with_gpt_membership": with_gpt,
            "by_source": {s or "unknown": c for s, c in by_source},
        }
