"""
EPM — Auth router.
Endpoints: login, logout, me, change-password.
JWT is issued as an httpOnly secure cookie — never in the response body.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import create_access_token, get_current_user, get_session
from app.models import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

COOKIE_NAME = "epm_token"
COOKIE_KWARGS = dict(
    key=COOKIE_NAME,
    httponly=True,
    secure=True,      # HTTPS only — Traefik handles TLS termination
    samesite="strict",
    max_age=60 * 60 * 24 * 30,  # 30 days
)


# ─── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    role: str

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def _envelope(data: object) -> dict:
    return {"data": data, "meta": {}, "error": None}


# ─── POST /api/v1/auth/login ──────────────────────────────────────────────────

@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(User).where(
            User.username == body.username,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
    )
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(user.id, user.role)
    response.set_cookie(value=token, **COOKIE_KWARGS)

    return _envelope(UserOut.model_validate(user).model_dump())


# ─── POST /api/v1/auth/logout ─────────────────────────────────────────────────

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    return {"data": None, "error": None}


# ─── GET /api/v1/auth/me ──────────────────────────────────────────────────────

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return _envelope(UserOut.model_validate(current_user).model_dump())


# ─── POST /api/v1/auth/change-password ───────────────────────────────────────

@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not pwd_context.verify(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = pwd_context.hash(body.new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    session.add(current_user)
    await session.commit()

    return _envelope({"message": "Password updated"})
