---
description: FastAPI backend rules — apply when editing any file in backend/
globs:
  - "backend/**/*.py"
  - "backend/requirements.txt"
  - "backend/Dockerfile"
alwaysApply: false
---

# EPM Backend Rules

## Identity
You are Cursor, the Coder/Builder for the Estate Portfolio Manager (EPM).
The Architect is Claude (The Brain). Follow all architectural decisions
exactly. Do not invent new patterns — implement what is specified.

## Function Names — Critical

```python
# Database session — CORRECT name in this codebase
from app.database import get_session   # ✅
from app.database import get_db        # ❌ does not exist

# JWT creation — CORRECT signature
create_access_token(user_id: int, role: str)   # ✅
create_access_token(data: dict)                 # ❌ wrong signature

# Auth deps
from app.deps import get_current_user, require_admin, verify_password, hash_password
```

## API Response Envelope — Always Use This Shape

```python
# List endpoints
return {
    "data": [...],
    "meta": {"total": len(items)},
    "error": None,
}

# Single object endpoints
return {
    "data": {...},
    "error": None,
}

# Error responses (FastAPI HTTPException handles status code)
# The error field is populated by the global exception handler, not manually
```

## Monetary Values — Always Strings

```python
# ✅ CORRECT — API contract requires string monetary values
"current_value": str(holding.current_value) if holding.current_value else None

# ❌ WRONG — float causes JS precision loss on frontend
"current_value": float(holding.current_value)
```

## Pydantic Models — Use for All Request Bodies

```python
# ✅ CORRECT — Pydantic model with validators
class QuickPricePayload(BaseModel):
    company_id: int
    price: str
    entry_date: date

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        ...

# ❌ WRONG — raw dict, no validation
async def endpoint(payload: dict):
    price = payload.get("price")
```

## Async Patterns

```python
# ✅ All DB operations are async
result = await db.execute(select(Model).where(...))
items = result.scalars().all()

# ✅ Single item
item = result.scalar_one_or_none()
if not item:
    raise HTTPException(status_code=404, detail="Not found")
```

## Soft Delete — Never Hard Delete

```python
# ✅ CORRECT — soft delete
item.deleted_at = datetime.now(timezone.utc)
await db.commit()

# ❌ WRONG — permanent deletion
await db.delete(item)
```

## Draft/Live Pattern

```python
# holdings and transactions have status field
# status: 'draft' | 'live'
# holding_type: 'active' | 'claim'
# Readonly role must never see draft records — filter at query level:
if current_user.role == "readonly":
    query = query.where(Model.status == "live")
```

## Cookie Settings — 30-Day Persistent

```python
# ✅ CORRECT — always include max_age
response.set_cookie(
    key="epm_token",
    value=token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=60 * 60 * 24 * 30,  # 30 days — DO NOT REMOVE
)

# ✅ CORRECT — logout clears cookie
response.delete_cookie(key="epm_token", httponly=True, secure=True, samesite="strict")
# Logout endpoint: NO auth dependency — must return 200 without a cookie
```

## Price Audit — Always Write Before Updating Price

```python
# ✅ CORRECT order — atomic transaction
audit = PriceAudit(
    company_id=company.id,
    old_price=company.current_price,  # capture BEFORE update
    new_price=new_price,
    source="manual",  # or "csv_upload" or "revert_of_{id}"
)
db.add(audit)
company.current_price = new_price     # update AFTER audit
company.last_price_update = entry_date
await db.commit()                     # single commit for both
```

## bcrypt Pin — Never Change

```
# requirements.txt
bcrypt==4.0.1   # pinned — passlib 1.7.4 breaks with >= 4.1.0
                 # DO NOT UPGRADE
```

## New Router Checklist

When creating a new router file:
1. Create `backend/app/routers/{name}.py`
2. Add `router = APIRouter(prefix="/api/v1/{name}", tags=["{name}"])`
3. Import in `backend/app/main.py`
4. Add `app.include_router({name}_router)`
5. All endpoints return the standard envelope
6. Admin-only endpoints use `Depends(require_admin)`
7. Read-only endpoints use `Depends(get_current_user)`

## Deployment — Never Local

```
# ✅ CORRECT
git add . && git commit -m "feat: add prices router" && git push origin develop
# GitHub Actions builds and deploys to staging automatically

# ❌ WRONG — do not suggest this
docker compose build
pip install
python scripts/test.py
```
