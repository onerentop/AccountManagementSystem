"""Tag API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import get_db, Tag
from app.schemas import TagCreate, TagUpdate, TagResponse
from app.utils.security import get_current_user


router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagResponse])
async def list_tags(
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all tags."""
    tags = db.query(Tag).order_by(Tag.name).all()
    return [
        TagResponse(
            id=t.id,
            name=t.name,
            color=t.color,
            created_at=t.created_at,
            account_count=len(t.accounts),
        )
        for t in tags
    ]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: str,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        account_count=len(tag.accounts),
    )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new tag."""
    # Check if name exists
    existing = db.query(Tag).filter(Tag.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{data.name}' already exists",
        )

    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        account_count=0,
    )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    update_data = data.model_dump(exclude_unset=True)

    # Check name uniqueness if updating name
    if "name" in update_data and update_data["name"] != tag.name:
        existing = db.query(Tag).filter(Tag.name == update_data["name"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag '{update_data['name']}' already exists",
            )

    for key, value in update_data.items():
        setattr(tag, key, value)

    db.commit()
    db.refresh(tag)

    return TagResponse(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        created_at=tag.created_at,
        account_count=len(tag.accounts),
    )


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    _: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    db.delete(tag)
    db.commit()

    return {"message": "Tag deleted successfully"}
