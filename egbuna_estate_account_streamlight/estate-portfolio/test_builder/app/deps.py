import os
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

SESSION_SECRET = os.environ.get("TEST_BUILDER_SESSION_SECRET", "dev-secret-change-me")
SHARED_PASSWORD = os.environ.get("TEST_BUILDER_PASSWORD", "password")
SESSION_DURATION_HOURS = 12

serializer = URLSafeTimedSerializer(SESSION_SECRET, salt="session")


def create_session() -> str:
    """Create a signed session token valid for 12 hours."""
    payload = {"created_at": datetime.now(timezone.utc).isoformat()}
    return serializer.dumps(payload)


def validate_session(request: Request) -> bool:
    """Check if the session cookie is valid and not expired."""
    token = request.cookies.get("session")
    if not token:
        return False
    try:
        serializer.loads(token, max_age=timedelta(hours=SESSION_DURATION_HOURS).total_seconds())
        return True
    except (BadSignature, SignatureExpired):
        return False


async def require_auth(request: Request):
    """FastAPI dependency: redirect to login if not authenticated."""
    if not validate_session(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return True
