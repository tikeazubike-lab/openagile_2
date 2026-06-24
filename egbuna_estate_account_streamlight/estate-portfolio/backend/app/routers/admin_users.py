"""
EPM — Admin Users router.
CRUD operations for user management, admin-guarded.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from passlib.context import CryptContext
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user, get_session, require_admin
from app.models import User

router = APIRouter(prefix="/api/v1", tags=["admin-users"])

# ─── Password Hashing ─────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


# ─── Envelope Helper ──────────────────────────────────────────────────────────

def _envelope(data: object, meta: Optional[dict] = None) -> dict:
    return {"data": data, "meta": meta or {}, "error": None}


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

VALID_ROLES = ("admin", "readonly")


class UserCreate(BaseModel):
    username: str
    name: str
    password: str
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {', '.join(VALID_ROLES)}")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {', '.join(VALID_ROLES)}")
        return v


class PasswordReset(BaseModel):
    new_password: str


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/admin/users")
async def list_users(
    include_inactive: bool = Query(False, alias="include_inactive"),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """List all users. Exclude soft-deleted by default. Optionally include inactive."""
    stmt = select(User).where(User.deleted_at.is_(None))
    if not include_inactive:
        stmt = stmt.where(User.is_active.is_(True))
    result = await session.execute(stmt)
    users = result.scalars().all()

    data = [
        {
            "id": u.id,
            "username": u.username,
            "name": u.name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        }
        for u in users
    ]
    return _envelope(data, meta={"total": len(data)})


@router.post("/admin/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Create a new user. Returns 409 if username already exists."""
    # Check duplicate username
    existing = await session.execute(
        select(User).where(User.username == payload.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    new_user = User(
        username=payload.username,
        name=payload.name,
        hashed_password=_hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return _envelope(
        {
            "id": new_user.id,
            "username": new_user.username,
            "name": new_user.name,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
        }
    )


@router.patch("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Update a user's name, role, or active status."""
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if payload.name is not None:
        user.name = payload.name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    await session.commit()
    await session.refresh(user)

    return _envelope(
        {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
    )


@router.put("/admin/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    payload: PasswordReset,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Reset a user's password."""
    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.hashed_password = _hash_password(payload.new_password)
    await session.commit()

    return _envelope({"id": user.id, "message": "Password reset successfully"})


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Soft delete a user (set deleted_at + is_active=false). Block self-deletion."""
    # Block self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    result = await session.execute(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    now = datetime.now(timezone.utc)
    user.deleted_at = now
    user.is_active = False
    await session.commit()

    return _envelope({"id": user.id, "message": "User deleted successfully"})
