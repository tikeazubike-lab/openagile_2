import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import settings
from app.deps import create_access_token, decode_token, require_admin


def test_create_access_token_contains_expected_claims():
  token = create_access_token(42, "admin")
  payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
  assert payload["sub"] == "42"
  assert payload["role"] == "admin"


def test_decode_token_rejects_invalid_token():
  with pytest.raises(HTTPException) as exc_info:
    decode_token("not-a-token")
  assert exc_info.value.status_code == 401


def test_require_admin_returns_admin_user():
  user = SimpleNamespace(role="admin")
  assert asyncio.run(require_admin(user)) is user


def test_require_admin_rejects_readonly_user():
  user = SimpleNamespace(role="readonly")
  with pytest.raises(HTTPException) as exc_info:
    asyncio.run(require_admin(user))
  assert exc_info.value.status_code == 403
