# EPM Test Case Builder — Implementation Plan

> **For Hermes:** Use subagent-driven-development to implement this plan task-by-task.
> **Goal:** Build a FastAPI + Jinja2 + vanilla JS web app for QA testers to author, execute, and report on taxonomy-compliant test cases, generating scaffold pytest stubs in the real EPM tests/ directory.
> **Architecture:** Single Docker container (no separate DB container — SQLite file in a volume). Exposed via Traefik at `testbuild.zubbystudio.shop`. Writes scaffold files to the repo's `tests/` directory via a bind mount.
> **Tech Stack:** FastAPI + Jinja2 + vanilla JS + SQLAlchemy (async) + aiosqlite + Docker + Traefik

---

## Current Context / Assumptions

- **Repo root:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/`
- **Docker compose:** New `docker-compose.test-builder.yml` alongside existing `docker-compose.v3.yml` and `docker-compose.yml`
- **Domain:** `testbuild.zubbystudio.shop` — DNS already points to Netcup VPS IP
- **DB:** SQLite via `aiosqlite` — no Postgres dependency. DB file lives in a Docker volume at `/data/test_builder.db` inside the container
- **Stack:** FastAPI + Jinja2 templates + vanilla JS (no React/build step) — intentional simplicity
- **Mount target:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/tests/` — bind-mounted into the container at `/repo/tests`. This directory may not exist yet; the app should create it on first scaffold write.
- **Everything Dockerized** — no packages installed on the host. Single `test-builder` container.
- **Traefik:** Existing on the host. Uses `letsencrypt` certresolver and `openagile_network` network (per EPM conventions — confirmed by inspecting existing compose files).
- **Auth:** Shared password via `TEST_BUILDER_PASSWORD` env var. Session-based with 12h expiry.
- **Secrets:** `TEST_BUILDER_PASSWORD` and `TEST_BUILDER_SESSION_SECRET` stored in `.env.test-builder` file (gitignored).
- **The `.feature` files** will stay flat in `test_builder/` (not moved to a `features/` subdir) to keep directory simple.

### Key Adaptation from Spec: SQLite instead of Postgres

The BUILD_INSTRUCTIONS.md was written for Postgres. Adapting to SQLite means:
- `SERIAL` → `Integer, primary_key=True, autoincrement=True` (SQLAlchemy handles this)
- `TIMESTAMPTZ` → `DateTime(timezone=True)`
- `UNIQUE` constraints → work as-is in SQLite
- `CHECK` constraints → work as-is in SQLite
- Connection string: `sqlite+aiosqlite:///data/test_builder.db`
- WAL mode enabled on startup for concurrent access

---

## Proposed Approach

All code goes under `test_builder/` in the repo root, keeping it cleanly separated from the main EPM app:

```
estate-portfolio/
├── test_builder/
│   ├── BUILD_INSTRUCTIONS.md     ← exists (keep as spec reference)
│   ├── admin_and_auth.feature     ← exists
│   ├── reporting.feature          ← exists
│   ├── scaffold_generation.feature ← exists
│   ├── test_case_management.mdx   ← exists
│   ├── test_execution.feature     ← exists
│   ├── Dockerfile                 ← NEW
│   ├── requirements.txt           ← NEW
│   ├── app/
│   │   ├── __init__.py            ← NEW
│   │   ├── main.py                ← NEW (FastAPI app, lifespan, Jinja2, static mount)
│   │   ├── database.py            ← NEW (SQLAlchemy async engine + models)
│   │   ├── models.py              ← NEW (SQLAlchemy ORM models for SQLite)
│   │   ├── deps.py                ← NEW (auth dependency, session handling)
│   │   ├── routers/
│   │   │   ├── __init__.py        ← NEW
│   │   │   ├── auth.py            ← NEW (/login routes)
│   │   │   ├── test_cases.py      ← NEW (draft/submit/validate)
│   │   │   ├── test_runs.py       ← NEW (execute + versioned runs)
│   │   │   ├── reports.py         ← NEW (generate/download reports + bug reports)
│   │   │   ├── domain_codes.py    ← NEW (admin CRUD for domain codes)
│   │   │   └── scaffold.py        ← NEW (generate folders + pytest stubs)
│   │   └── templates/
│   │       ├── base.html          ← NEW (Jinja2 base layout)
│   │       ├── login.html         ← NEW
│   │       ├── test_cases.html    ← NEW (Add Test Cases page)
│   │       ├── execute.html       │   NEW (Execute Tests page)
│   │       ├── reports.html       │   NEW (View/Download reports)
│   │       └── admin_domain_codes.html  ← NEW
│   └── static/
│       └── app.js                 ← NEW (localStorage handling + form logic)
├── docker-compose.test-builder.yml  ← NEW
└── .env.test-builder                ← NEW (gitignored)
```

---

## Step-by-Step Plan

### Phase 0: Prerequisite Check (do this first, before any code)

**Task to do:** Verify DNS, inspect Traefik, pick a password.

1. **Verify DNS:** `nslookup testbuild.zubbystudio.shop` — should return the VPS IP. If not, ask user to add the A record.
2. **Inspect Traefik network + resolver:** `docker inspect traefik` on the host (via SSH) to confirm the network is `openagile_network` and certresolver is `letsencrypt`. Update compose template if different.
3. **Generate session secret:** `openssl rand -hex 32` for `TEST_BUILDER_SESSION_SECRET`.
4. **Choose shared password:** User provides `TEST_BUILDER_PASSWORD`.
5. **Create `.env.test-builder`** with both secrets (gitignored).

> ⚠️ **NOTE:** I (the planner) cannot SSH into the VPS or run `docker inspect` from this session. This step will need to be done by the implementer (during execution) or confirmed by the user now.

### Task 1: Create project scaffold — Dockerfile + requirements.txt + compose file

**Objective:** Set up the Python environment and Docker build chain so the rest of the code has a home.

**Files:**
- Create: `test_builder/Dockerfile`
- Create: `test_builder/requirements.txt`
- Create: `docker-compose.test-builder.yml`
- Create: `.gitignore` entry for `.env.test-builder`

**Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
aiosqlite==0.20.0
jinja2==3.1.4
python-multipart==0.0.12
itsdangerous==2.2.0
aiofiles==24.1.0
```

**Step 2: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data && mkdir -p /repo/tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 3: Create docker-compose.test-builder.yml**

```yaml
services:
  test-builder:
    build:
      context: ./test_builder
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file:
      - .env.test-builder
    environment:
      DATABASE_URL: sqlite+aiosqlite:///data/test_builder.db
      REPO_TESTS_PATH: /repo/tests
    volumes:
      - test_builder_data:/data
      - /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/tests:/repo/tests
    networks:
      - openagile_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.test-builder.rule=Host(`testbuild.zubbystudio.shop`)"
      - "traefik.http.routers.test-builder.entrypoints=websecure"
      - "traefik.http.routers.test-builder.tls=true"
      - "traefik.http.routers.test-builder.tls.certresolver=letsencrypt"
      - "traefik.http.services.test-builder.loadbalancer.server.port=8000"
      - "traefik.docker.network=openagile_network"

volumes:
  test_builder_data:

networks:
  openagile_network:
    external: true
```

**Step 4: Add to .gitignore**

```
.env.test-builder
```

**Step 5: Verify**
Run: `cd /path/to/repo && ls test_builder/Dockerfile test_builder/requirements.txt docker-compose.test-builder.yml`
Expected: all 3 files exist.

**Step 6: Commit**
```bash
git add docker-compose.test-builder.yml test_builder/Dockerfile test_builder/requirements.txt .gitignore
git commit -m "feat(test-builder): scaffold Dockerfile, compose file, and dependencies"
```

---

### Task 2: Database models and engine setup

**Objective:** SQLAlchemy ORM models for the four tables (domain_codes, test_cases, test_runs, reports, bug_reports), adapted for SQLite.

**Files:**
- Create: `test_builder/app/__init__.py` (empty)
- Create: `test_builder/app/database.py` (engine + session factory)
- Create: `test_builder/app/models.py` (ORM models)

**Step 1: Create app/\_\_init\_\_.py** — empty file

**Step 2: Create app/database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///data/test_builder.db"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSchemaSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def init_db():
    """Create tables on startup and enable WAL mode for SQLite."""
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrent read/write
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with SessionLocal() as session:
        yield session
```

> **Note:** Use `AsyncAttrs` from `sqlalchemy.ext.asyncio` for async relationship loading. Import via `from sqlalchemy.ext.asyncio import AsyncAttrs`.

**Step 3: Create app/models.py**

```python
import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from app.database import Base


class DomainCode(Base):
    __tablename__ = "domain_codes"

    code = Column(String(4), primary_key=True)
    label = Column(Text, nullable=False)
    folder_slug = Column(String(20), nullable=False)  # required field for folder mapping
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_cases = relationship("TestCase", back_populates="domain")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(40), primary_key=True)          # e.g. 'HOLD-CREATE-BE-INT-001'
    domain_code = Column(String(4), ForeignKey("domain_codes.code"), nullable=False)
    workflow = Column(String(20), nullable=False)
    layer = Column(String(4), nullable=False)           # BE | FE | SEC | INF
    test_type = Column(String(4), nullable=False)       # UT | INT | API | E2E | SEC | SMK
    sequence_no = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    requirement_ref = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("domain_code", "workflow", "layer", "test_type", "sequence_no"),
    )

    domain = relationship("DomainCode", back_populates="test_cases")
    runs = relationship("TestRun", back_populates="test_case", order_by="TestRun.run_number")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(String(40), ForeignKey("test_cases.id"), nullable=False)
    run_number = Column(Integer, nullable=False)
    execution_path = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    status = Column(String(10), nullable=False)  # Passed | Failed
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("test_case_id", "run_number"),
        CheckConstraint("status IN ('Passed','Failed')", name="ck_run_status"),
    )

    test_case = relationship("TestCase", back_populates="runs")
    bug_report = relationship("BugReport", uselist=False, back_populates="test_run")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", back_populates="bug_report")
```

**Step 4: Verify**
Run: `python -c "from app.models import TestCase, TestRun, DomainCode, Report, BugReport; print('OK')"`
Expected: No import errors.

**Step 5: Commit**
```bash
git add test_builder/app/__init__.py test_builder/app/database.py test_builder/app/models.py
git commit -m "feat(test-builder): add SQLAlchemy models and engine setup for SQLite"
```

---

### Task 3: FastAPI app bootstrap — main.py + lifespan + Jinja2 + static

**Objective:** Stand up the FastAPI application with lifespan (for DB init), Jinja2 template engine, and static file serving. Empty routers mounted.

**Files:**
- Create: `test_builder/app/main.py`
- Create: `test_builder/app/routers/__init__.py` (empty)
- Create: `test_builder/app/routers/auth.py` (stub)
- Create: `test_builder/app/routers/test_cases.py` (stub)
- Create: `test_builder/app/routers/test_runs.py` (stub)
- Create: `test_builder/app/routers/reports.py` (stub)
- Create: `test_builder/app/routers/domain_codes.py` (stub)
- Create: `test_builder/app/routers/scaffold.py` (stub)

**Step 1: Create main.py**

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routers import auth, test_cases, test_runs, reports, domain_codes, scaffold


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="EPM Test Case Builder", lifespan=lifespan)

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(auth.router)
app.include_router(test_cases.router)
app.include_router(test_runs.router)
app.include_router(reports.router)
app.include_router(domain_codes.router)
app.include_router(scaffold.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/test-cases")
```

**Step 2: Create each router stub file**

Each router stub follows this pattern (showing auth.py as example, all others identical except prefix and tag):

```python
from fastapi import APIRouter

router = APIRouter(tags=["auth"])
```

**Step 3: Create routers/__init__.py** — empty

**Step 4: Verify**
Run: `python -c "from app.main import app; print('OK')"`
Expected: No import errors.

**Step 5: Commit**
```bash
git add test_builder/app/main.py test_builder/app/routers/
git commit -m "feat(test-builder): bootstrap FastAPI app with lifespan and router stubs"
```

---

### Task 4: Jinja2 base template + login page + auth routes

**Objective:** Create the base Jinja2 template with consistent layout. Implement the login page and session-based auth with shared password.

**Files:**
- Create: `test_builder/app/templates/base.html`
- Create: `test_builder/app/templates/login.html`
- Create: `test_builder/app/deps.py` (auth dependency)
- Modify: `test_builder/app/routers/auth.py` (full implementation)
- Modify: `test_builder/app/main.py` (add session middleware)

**Step 1: Create base.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EPM Test Builder{% endblock %}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <a href="/test-cases">Add Test Cases</a>
        <a href="/test-cases/execute">Execute Tests</a>
        <a href="/admin/domain-codes">Domain Codes</a>
        <form action="/logout" method="post" style="display:inline">
            <button type="submit">Logout</button>
        </form>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="/static/app.js"></script>
</body>
</html>
```

**Step 2: Create deps.py** — session auth dependency using `itsdangerous` for URL-safe signed cookies.

```python
import os
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return True
```

> **Note:** For actual usage in routes, the auth check is done via a session cookie middleware or per-route dependency. We'll keep it simple — the login routes are unprotected, everything else uses `Depends(require_auth)`.

**Step 3: Implement auth.py router**

```python
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from app.templates import templates  # from main.py
from app.deps import create_session, SHARED_PASSWORD, require_auth

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password != SHARED_PASSWORD:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials",
        }, status_code=401)
    response = RedirectResponse(url="/test-cases", status_code=302)
    response.set_cookie(
        key="session",
        value=create_session(),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 12,  # 12 hours
    )
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session", httponly=True, secure=True, samesite="lax")
    return response
```

> **Implementation note:** The `templates` object needs to be shared. Either import from `app.main` or instantiate it in a shared module. For simplicity, import from `app.main` or create `app/templates.py` as a module-level singleton.

**Step 4: Create login.html**

```html
{% extends "base.html" %}
{% block title %}Login — EPM Test Builder{% endblock %}
{% block content %}
<h1>EPM Test Case Builder</h1>
<form method="post" action="/login">
    <label>Password:
        <input type="password" name="password" required>
    </label>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <button type="submit">Login</button>
</form>
{% endblock %}
```

> **Design note:** The login page should NOT inherit from `base.html` because the nav requires auth. Create a `login_base.html` or use a conditional block. For simplicity, login.html is a standalone page (no nav).

**Step 5: Verify auth flow works**
Run: `uvicorn test_builder.app.main:app` and curl:
```bash
curl -s http://localhost:8000/login | grep -c "Login"
# Expected: 1 (page renders)
```

**Step 6: Commit**
```bash
git add test_builder/app/templates/ test_builder/app/deps.py test_builder/app/routers/auth.py test_builder/app/main.py
git commit -m "feat(test-builder): add session-based auth with shared password"
```

---

### Task 5: Test case management — draft + submit + validate

**Objective:** Implement the "Add Test Cases" page — localStorage draft cache, taxonomy ID generation with sequential numbering, required field validation, and batch submission to SQLite.

**Files:**
- Create: `test_builder/app/templates/test_cases.html`
- Create: `test_builder/app/static/app.js`
- Modify: `test_builder/app/routers/test_cases.py` (full implementation)

**Step 1: Implement test_cases router**

```python
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_session
from app.models import TestCase, DomainCode
from app.deps import require_auth
from app.templates import templates

router = APIRouter(prefix="/test-cases", tags=["test-cases"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def add_test_cases_page(request: Request, session: AsyncSession = Depends(get_session)):
    # Get domain codes for the dropdown
    result = await session.execute(select(DomainCode).order_by(DomainCode.code))
    domains = result.scalars().all()
    return templates.TemplateResponse("test_cases.html", {
        "request": request,
        "domains": [{"code": d.code, "label": d.label} for d in domains],
    })


@router.get("/api/next-sequence")
async def get_next_sequence(
    domain: str, workflow: str, layer: str, test_type: str,
    session: AsyncSession = Depends(get_session),
):
    """Compute next sequence number for a taxonomy tuple."""
    result = await session.execute(
        select(func.coalesce(func.max(TestCase.sequence_no), 0))
        .where(
            TestCase.domain_code == domain.upper(),
            TestCase.workflow == workflow.upper(),
            TestCase.layer == layer.upper(),
            TestCase.test_type == test_type.upper(),
        )
    )
    max_seq = result.scalar()
    return JSONResponse(content={"sequence_no": max_seq + 1})


@router.post("/api/submit")
async def submit_test_cases(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Submit all drafted test cases from localStorage to DB."""
    body = await request.json()
    cases = body.get("cases", [])
    if not cases:
        raise HTTPException(status_code=400, detail="Add at least one test case before submitting")

    created = []
    for case in cases:
        # Validate required fields
        if not case.get("layer"):
            raise HTTPException(status_code=400, detail="Layer is required to generate a Test ID")

        # Get next sequence
        result = await session.execute(
            select(func.coalesce(func.max(TestCase.sequence_no), 0))
            .where(
                TestCase.domain_code == case["domain"].upper(),
                TestCase.workflow == case["workflow"].upper(),
                TestCase.layer == case["layer"].upper(),
                TestCase.test_type == case["test_type"].upper(),
            )
        )
        seq = result.scalar() + 1

        test_id = f"{case['domain'].upper()}-{case['workflow'].upper()}-{case['layer'].upper()}-{case['test_type'].upper()}-{seq:03d}"

        tc = TestCase(
            id=test_id,
            domain_code=case["domain"].upper(),
            workflow=case["workflow"].upper(),
            layer=case["layer"].upper(),
            test_type=case["test_type"].upper(),
            sequence_no=seq,
            title=case.get("title", ""),
            requirement_ref=case.get("requirement_ref"),
        )
        session.add(tc)
        created.append(test_id)

    await session.commit()
    return JSONResponse(content={"submitted": created, "count": len(created)})
```

**Step 2: Create test_cases.html**

The page has:
- A form with dropdowns: domain (from DB), workflow, layer (BE/FE/SEC/INF), test_type (UT/INT/API/E2E/SEC/SMK)
- Title field and requirement_ref field (optional)
- "Save" button — writes to localStorage
- "Submit Test Cases" button — POST all drafts to /api/submit
- Draft list rendered client-side from localStorage

See the Gherkin scenarios in `test_case_management.feature` for expected behavior.

**Step 3: Create app.js**

Core functions needed:
- `getDrafts()` / `addDraft()` / `clearDrafts()` — localStorage CRUD
- `generateTestId(domain, workflow, layer, type)` — generates ID like `AUTH-LOGIN-BE-INT-001`
- `renderDraftList()` — renders the on-page list of drafted cases
- `validateDraft(formData)` — checks required fields
- `submitDrafts()` — POST to /api/submit, redirect on success

**Step 4: Verify**
- Open `/test-cases` in browser
- Fill in domain "AUTH", workflow "LOGIN", layer "BE", type "INT"
- Click "Save" — AUTH-LOGIN-BE-INT-001 appears in list
- Click "Save" again — AUTH-LOGIN-BE-INT-002 appears
- Click "Submit Test Cases" — confirm redirect to /test-cases/execute
- Check SQLite: `sqlite3 /data/test_builder.db "SELECT * FROM test_cases;"` should show the rows

**Step 5: Commit**
```bash
git add test_builder/app/routers/test_cases.py test_builder/app/templates/test_cases.html test_builder/app/static/app.js
git commit -m "feat(test-builder): add test case drafting, localStorage cache, and DB submission"
```

---

### Task 6: Test execution — record versioned runs

**Objective:** Implement the "Execute Tests" page — list submitted test cases, record execution path/expected/actual/status, versioned run history.

**Files:**
- Create: `test_builder/app/templates/execute.html`
- Modify: `test_builder/app/routers/test_runs.py` (full implementation)

**Step 1: Implement test_runs router**

```python
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_session
from app.models import TestCase, TestRun, BugReport
from app.deps import require_auth
from app.templates import templates

router = APIRouter(prefix="/test-cases/execute", tags=["test-runs"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def execute_page(request: Request, session: AsyncSession = Depends(get_session)):
    # Get all test cases with their latest run
    result = await session.execute(select(TestCase).order_by(TestCase.id))
    test_cases = result.scalars().all()

    cases_with_runs = []
    for tc in test_cases:
        latest = await session.execute(
            select(TestRun).where(TestRun.test_case_id == tc.id).order_by(TestRun.run_number.desc()).limit(1)
        )
        latest_run = latest.scalar_one_or_none()
        cases_with_runs.append({
            "test_case": {"id": tc.id, "title": tc.title, "domain_code": tc.domain_code},
            "latest_run": {
                "run_number": latest_run.run_number if latest_run else None,
                "status": latest_run.status if latest_run else None,
                "executed_at": latest_run.executed_at.isoformat() if latest_run and latest_run.executed_at else None,
            } if latest_run else None,
        })

    return templates.TemplateResponse("execute.html", {
        "request": request,
        "test_cases": cases_with_runs,
    })


@router.post("/api/runs")
async def save_run(request: Request, session: AsyncSession = Depends(get_session)):
    body = await request.json()
    test_case_id = body.get("test_case_id")
    execution_path = body.get("execution_path", "")
    expected_result = body.get("expected_result", "")
    actual_result = body.get("actual_result", "")
    status = body.get("status", "")

    # Validation
    if not actual_result:
        raise HTTPException(status_code=400, detail="Actual result is required")
    if status not in ("Passed", "Failed"):
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # Get next run number
    result = await session.execute(
        select(func.coalesce(func.max(TestRun.run_number), 0))
        .where(TestRun.test_case_id == test_case_id)
    )
    run_number = result.scalar() + 1

    run = TestRun(
        test_case_id=test_case_id,
        run_number=run_number,
        execution_path=execution_path,
        expected_result=expected_result,
        actual_result=actual_result,
        status=status,
    )
    session.add(run)
    await session.flush()  # get run.id

    # Auto-generate bug report if Failed
    if status == "Failed":
        bug_markdown = _generate_bug_report(run, test_case_id, session)
        bug_report = BugReport(test_run_id=run.id, markdown=bug_markdown)
        session.add(bug_report)

    await session.commit()
    return JSONResponse(content={"run_id": run.id, "run_number": run_number, "status": status})


def _generate_bug_report(run, test_case_id, session):
    """Generate bug report markdown from EPM template."""
    # Inline implementation — uses run fields to fill template
    lines = [
        f"# Bug Report — {test_case_id}",
        "",
        "## What I Did",
        run.execution_path,
        "",
        "## What I Expected",
        run.expected_result,
        "",
        "## What Actually Happened",
        run.actual_result,
        "",
        "## Feature Affected",
        "(Feature from domain code — fetch in context)",
        "",
        "## Severity",
        "(leave blank)",
        "",
        "## Layer",
        "(leave blank)",
        "",
        "## Evidence",
        "(leave blank)",
    ]
    return "\n".join(lines)
```

**Step 2: Create execute.html**

The page shows each test case with:
- Test case ID and title
- Latest run status (if any)
- Form fields: execution_path, expected_result, actual_result, status radio (Passed/Failed)
- "Save Result" button per test case
- Run history per test case

**Step 3: Verify**
- Open `/test-cases/execute` — see submitted test cases
- Fill in execution details, mark "Passed", save — run created
- Execute same test again — run_number increments
- Mark "Failed" — bug report auto-generated
- Try empty actual_result — error shown

**Step 4: Commit**
```bash
git add test_builder/app/routers/test_runs.py test_builder/app/templates/execute.html
git commit -m "feat(test-builder): add test execution with versioned runs and auto-bug-report"
```

---

### Task 7: Reports + bug reports — generate, view, download

**Objective:** Implement the reporting page — generate markdown reports from latest runs, download as .md, view auto-generated bug reports.

**Files:**
- Create: `test_builder/app/templates/reports.html`
- Modify: `test_builder/app/routers/reports.py` (full implementation)

**Step 1: Implement reports router**

```python
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_session
from app.models import TestCase, TestRun, Report, BugReport
from app.deps import require_auth
from app.templates import templates
import datetime

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def reports_page(request: Request, session: AsyncSession = Depends(get_session)):
    # Show list of generated reports
    result = await session.execute(select(Report).order_by(Report.generated_at.desc()))
    reports = result.scalars().all()
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "reports": [{"id": r.id, "generated_at": r.generated_at.isoformat() if r.generated_at else ""} for r in reports],
    })


@router.post("/api/submit")
async def submit_report(session: AsyncSession = Depends(get_session)):
    # Get latest run for each test case
    # Check all test cases have at least one run
    result = await session.execute(select(func.count(TestCase.id)))
    total_cases = result.scalar()

    result = await session.execute(
        select(func.count(func.distinct(TestRun.test_case_id)))
    )
    cases_with_runs = result.scalar()

    if total_cases != cases_with_runs:
        raise HTTPException(status_code=400, detail="All test cases must have at least one execution result")

    # Build markdown report
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Test Run Report — {now}", "", "| Test ID | Status | Expected | Actual |", "|---|---|---|---|"]

    result = await session.execute(select(TestCase).order_by(TestCase.id))
    test_cases = result.scalars().all()

    for tc in test_cases:
        latest = await session.execute(
            select(TestRun).where(TestRun.test_case_id == tc.id).order_by(TestRun.run_number.desc()).limit(1)
        )
        run = latest.scalar_one_or_none()
        if run:
            lines.append(f"| {tc.id} | {run.status} | {run.expected_result} | {run.actual_result} |")

    markdown = "\n".join(lines)

    report = Report(markdown=markdown)
    session.add(report)
    await session.commit()

    return JSONResponse(content={"report_id": report.id, "markdown": markdown})


@router.get("/api/reports/{report_id}/download")
async def download_report(report_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return PlainTextResponse(content=report.markdown, media_type="text/markdown")


@router.get("/api/bug-reports/{bug_report_id}/download")
async def download_bug_report(bug_report_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(BugReport).where(BugReport.id == bug_report_id))
    bug = result.scalar_one_or_none()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return PlainTextResponse(content=bug.markdown, media_type="text/markdown")
```

**Step 2: Create reports.html**

Page with:
- "Generate Report" button — calls POST /reports/api/submit
- Rendered markdown preview (inline)
- "Download .md" button for each saved report
- List of bug reports for failed runs
- "Download" button for each bug report

**Step 3: Verify**
- Execute at least one test case
- Generate report — should render markdown table
- Download report — content matches inline
- Execute a failing test — bug report should appear
- Generate report before any executions — error "All test cases must have at least one execution result"

**Step 4: Commit**
```bash
git add test_builder/app/routers/reports.py test_builder/app/templates/reports.html
git commit -m "feat(test-builder): add markdown report generation and bug report download"
```

---

### Task 8: Admin — domain code CRUD

**Objective:** Implement the admin page for managing domain codes (list, add, edit). The folder_slug field is required for scaffold generation.

**Files:**
- Create: `test_builder/app/templates/admin_domain_codes.html`
- Modify: `test_builder/app/routers/domain_codes.py` (full implementation)

**Step 1: Implement domain_codes router**

```python
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models import DomainCode
from app.deps import require_auth
from app.templates import templates

router = APIRouter(prefix="/admin/domain-codes", tags=["domain-codes"], dependencies=[Depends(require_auth)])


@router.get("", response_class=HTMLResponse)
async def list_domain_codes(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(DomainCode).order_by(DomainCode.code))
    codes = result.scalars().all()
    return templates.TemplateResponse("admin_domain_codes.html", {
        "request": request,
        "codes": [{"code": c.code, "label": c.label, "folder_slug": c.folder_slug} for c in codes],
    })


@router.post("")
async def add_domain_code(
    request: Request,
    session: AsyncSession = Depends(get_session),
    code: str = Form(...),
    label: str = Form(...),
    folder_slug: str = Form(...),
):
    # Check duplicate
    existing = await session.execute(select(DomainCode).where(DomainCode.code == code.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Domain code {code.upper()} already exists")

    dc = DomainCode(code=code.upper(), label=label, folder_slug=folder_slug)
    session.add(dc)
    await session.commit()
    return RedirectResponse(url="/admin/domain-codes", status_code=302)


@router.post("/{code}/edit")
async def edit_domain_code(
    code: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    label: str = Form(...),
    folder_slug: str = Form(...),
):
    result = await session.execute(select(DomainCode).where(DomainCode.code == code.upper()))
    dc = result.scalar_one_or_none()
    if not dc:
        raise HTTPException(status_code=404, detail="Domain code not found")
    dc.label = label
    dc.folder_slug = folder_slug
    await session.commit()
    return RedirectResponse(url="/admin/domain-codes", status_code=302)
```

**Step 2: Seed default domain codes on startup**

Add seed to `init_db()` in database.py — insert the 17 taxonomy domain codes if the table is empty.

```python
DEFAULT_DOMAIN_CODES = [
    ("AUTH", "Authentication (login, logout, session, cookie)", "auth"),
    ("HOLD", "Holdings (CRUD, valuations, portfolios)", "holdings"),
    ("PRIC", "Prices (market price updates, CSV upload, quick entry)", "prices"),
    ("PRIH", "Price History (historical snapshots, charting data)", "price-history"),
    ("DASH", "Dashboard (overview, KPIs, charts)", "dashboard"),
    ("REGR", "Registrars (company registrars, contact, dividend mandates)", "registrars"),
    ("CLAM", "Claims (next rights issue, dividend claims)", "claims"),
    ("DIVD", "Dividends (declared, paid, reconciled)", "dividends"),
    ("TRAN", "Transactions (buy/sell, corp action bookings)", "transactions"),
    ("NAVH", "NAV History (fund NAV snapshots, performance)", "nav-history"),
    ("WTCH", "Watchlist (user watchlist, alerts)", "watchlist"),
    ("COMP", "Companies (company master, metadata, sector)", "companies"),
    ("ADMN", "Admin (user management, settings, audit log)", "admin"),
    ("USER", "Admin/Users (role management, invite flow)", "admin/users"),
    ("OBSD", "Obsidian Import (vault sync, markdown parsing)", "admin/obsidian"),
    ("CHAT", "Chat (AI ChatBot, intent router, response)", "chat"),
    ("SEC", "Security (authentication bypass, authorization, RBAC)", "../security"),
    ("INF", "Infrastructure (deploy pipeline, DB migration, Docker)", "../infrastructure"),
]
```

**Step 3: Create admin_domain_codes.html**

Page with:
- Table of existing domain codes (code, label, folder_slug)
- "Add Domain Code" form (code, label, folder_slug)
- Inline edit for each row (expandable form)
- Duplicate rejection shown as error

**Step 4: Verify**

Scenario: Add a new domain code
- Open `/admin/domain-codes` — see default codes
- Add "TEST" with label "Test Domain" and folder_slug "test"
- Confirm it appears in the table
- Open `/test-cases` — "TEST" appears in domain dropdown
- Try adding "AUTH" again — error "Domain code AUTH already exists"
- Edit "CHAT" label — dropdown reflects change

**Step 5: Commit**
```bash
git add test_builder/app/routers/domain_codes.py test_builder/app/templates/admin_domain_codes.html test_builder/app/database.py
git commit -m "feat(test-builder): add domain code CRUD with default seed data"
```

---

### Task 9: Scaffold generation — write pytest stubs to mounted volume

**Objective:** Generate folder structures and pytest .py stubs on the real repo's `tests/` directory via the bind mount.

**Files:**
- Create: `test_builder/app/scaffold.py` (helper functions for folder mapping and file generation)
- Modify: `test_builder/app/routers/scaffold.py` (full implementation)

**Step 1: Create scaffold helpers (app/scaffold.py)**

```python
import os
import re

DOMAIN_FOLDERS = {
    "AUTH": "auth", "HOLD": "holdings", "PRIC": "prices", "PRIH": "price-history",
    "DASH": "dashboard", "REGR": "registrars", "CLAM": "claims", "DIVD": "dividends",
    "TRAN": "transactions", "NAVH": "nav-history", "WTCH": "watchlist",
    "COMP": "companies", "ADMN": "admin", "USER": "admin/users",
    "OBSD": "admin/obsidian", "CHAT": "chat", "SEC": "../security", "INF": "../infrastructure",
}


def test_id_to_path(test_id: str, base_path: str) -> str:
    """Convert a test ID like 'HOLD-CREATE-BE-INT-001' to an absolute file path."""
    parts = test_id.split("-")
    domain_code = parts[0]
    workflow = parts[1].lower()
    layer = parts[2].lower()
    test_type = parts[3].lower()

    folder = DOMAIN_FOLDERS.get(domain_code)
    if not folder:
        raise ValueError(f"Unknown domain code: {domain_code}")

    test_dir = os.path.join(base_path, "backend", folder, workflow, test_type)
    test_file = os.path.join(test_dir, f"{test_id}.py")
    return test_file, test_dir


def generate_test_stub(test_id: str, domain_code: str, workflow: str, layer: str,
                       test_type: str, title: str, requirement_ref: str = "") -> str:
    """Generate pytest stub file content."""
    func_name = f"test_{test_id.replace('-', '_')}"

    lines = [
        f'"""',
        f"Test ID:     {test_id}",
        f"Title:       {title}",
        f"Domain:      {domain_code}",
        f"Workflow:    {workflow}",
        f"Layer:       {layer}",
        f"Type:        {test_type}",
        f"Requirement: {requirement_ref}" if requirement_ref else "",
        f'"""',
        "",
        "import pytest",
        "",
        "",
        f"async def test_{func_name}():",
        f"    # TODO: implement test logic",
        f"    # Original execution path:",
        f"    # ...",
        f'    assert False  # TODO: implement',
        "",
    ]
    return "\n".join(lines)
```

**Step 2: Implement scaffold router**

```python
import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models import TestCase, DomainCode
from app.deps import require_auth
from app.scaffold import test_id_to_path, generate_test_stub

REPO_TESTS_PATH = os.environ.get("REPO_TESTS_PATH", "/repo/tests")

router = APIRouter(prefix="/api/test-cases", tags=["scaffold"], dependencies=[Depends(require_auth)])


@router.post("/{test_id}/scaffold")
async def generate_scaffold(test_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    # Verify test case exists
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case {test_id} not found")

    try:
        test_file, test_dir = test_id_to_path(test_id, REPO_TESTS_PATH)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check if file already exists
    if os.path.exists(test_file):
        return JSONResponse(content={
            "warning": "File already exists - overwrite?",
            "path": test_file,
            "exists": True,
        })

    # Create directory and write file
    try:
        os.makedirs(test_dir, exist_ok=True)
        content = generate_test_stub(
            test_id=test_id,
            domain_code=tc.domain_code,
            workflow=tc.workflow,
            layer=tc.layer,
            test_type=tc.test_type,
            title=tc.title,
            requirement_ref=tc.requirement_ref,
        )
        with open(test_file, "w") as f:
            f.write(content)

        return JSONResponse(content={
            "message": "Scaffold generated",
            "path": test_file,
            "exists": False,
        })
    except PermissionError:
        raise HTTPException(status_code=500, detail=f"Cannot write to {REPO_TESTS_PATH} - check volume permissions")
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{test_id}/scaffold/overwrite")
async def overwrite_scaffold(test_id: str, request: Request, session: AsyncSession = Depends(get_session)):
    """Explicit confirmation endpoint for overwriting existing scaffold files."""
    result = await session.execute(select(TestCase).where(TestCase.id == test_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail=f"Test case {test_id} not found")

    try:
        test_file, test_dir = test_id_to_path(test_id, REPO_TESTS_PATH)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        os.makedirs(test_dir, exist_ok=True)
        content = generate_test_stub(...)
        with open(test_file, "w") as f:
            f.write(content)
        return JSONResponse(content={"message": "Scaffold overwritten", "path": test_file})
    except (PermissionError, OSError) as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Step 3: Verify**

Scenario: Generate a scaffold
- Submit a test case "HOLD-CREATE-BE-INT-001"
- POST to `/api/test-cases/HOLD-CREATE-BE-INT-001/scaffold`
- Check that `/repo/tests/backend/holdings/create/integration/HOLD-CREATE-BE-INT-001.py` exists
- File content has docstring with test ID, has `async def test_...` with `assert False`
- POST same endpoint again — receive "File already exists - overwrite?" warning
- POST to `/api/test-cases/HOLD-CREATE-BE-INT-001/scaffold/overwrite` — file is overwritten

**Step 4: Commit**
```bash
git add test_builder/app/scaffold.py test_builder/app/routers/scaffold.py
git commit -m "feat(test-builder): add scaffold generation for pytest stubs on mounted volume"
```

---

### Task 10: CSS styling + polish

**Objective:** Add basic CSS for a clean, usable dark-theme UI consistent with EPM's look. No React — just a single stylesheet.

**Files:**
- Create: `test_builder/app/static/style.css`

**Step 1: Create style.css**

A minimal dark-theme stylesheet with:
- Dark background (`#1a1a2e` or similar)
- Light text, accent colors for buttons
- Form styling (inputs, selects, buttons)
- Table styling for test case lists and reports
- Error message styling
- Responsive nav bar

**Step 2: Commit**
```bash
git add test_builder/app/static/style.css
git commit -m "feat(test-builder): add CSS styling for dark theme"
```

---

### Task 11: Docker build + deploy

**Objective:** Build the Docker image, create the necessary host paths, and deploy to the VPS with Traefik routing.

**Prerequisite:** Ensure `tests/` dir exists at the host path:
```bash
mkdir -p /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/tests
```

**Step 1: Build and verify locally**
```bash
docker compose -f docker-compose.test-builder.yml build
```

**Step 2: Push/deploy on VPS**
```bash
git add . && git commit -m "feat(test-builder): initial implementation complete"
git push origin main
# SSH into VPS, pull, run:
docker compose -f docker-compose.test-builder.yml up -d
```

**Step 3: Verify Traefik routing**
```bash
curl -s https://testbuild.zubbystudio.shop/login | grep -c "Login"
# Expected: 1 (login page renders)
```

**Step 4: Verify mount works**
```bash
# Inside container or via host:
ls /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/tests/
# Expected: initially empty, populated after scaffold generation
```

---

### Task 12: Verify Selenium/smoke tests against .feature files (optional)

**Objective:** Optionally add basic Playwright or Selenium tests that automate each Gherkin scenario. Low priority — can be done after deployment.

**Files:**
- Create: `test_builder/tests/test_smoke.py`

---

## Files That Will Change

### New Files (in creation order):

| # | File | Purpose |
|---|------|---------|
| 1 | `test_builder/Dockerfile` | Python container build |
| 2 | `test_builder/requirements.txt` | Python dependencies (FastAPI, SQLAlchemy, aiosqlite, Jinja2) |
| 3 | `docker-compose.test-builder.yml` | Docker service + Traefik labels + volumes |
| 4 | `.gitignore` entry for `.env.test-builder` | Prevent secrets from being committed |
| 5 | `test_builder/app/__init__.py` | Package init |
| 6 | `test_builder/app/database.py` | SQLAlchemy engine, init_db, session factory |
| 7 | `test_builder/app/models.py` | ORM models (domain_codes, test_cases, test_runs, reports, bug_reports) |
| 8 | `test_builder/app/main.py` | FastAPI app bootstrap |
| 9 | `test_builder/app/routers/__init__.py` | Package init |
| 10 | `test_builder/app/routers/auth.py` | Login/logout routes |
| 11 | `test_builder/app/routers/test_cases.py` | Draft/submit/validate routes |
| 12 | `test_builder/app/routers/test_runs.py` | Execute + versioned runs |
| 13 | `test_builder/app/routers/reports.py` | Generate/download reports + bug reports |
| 14 | `test_builder/app/routers/domain_codes.py` | Admin domain code CRUD |
| 15 | `test_builder/app/routers/scaffold.py` | Scaffold generation endpoint |
| 16 | `test_builder/app/deps.py` | Auth dependency (session validation) |
| 17 | `test_builder/app/scaffold.py` | Scaffold helpers (folder mapping + file generation) |
| 18 | `test_builder/app/templates/base.html` | Base Jinja2 layout |
| 19 | `test_builder/app/templates/login.html` | Login page |
| 20 | `test_builder/app/templates/test_cases.html` | Add Test Cases page |
| 21 | `test_builder/app/templates/execute.html` | Execute Tests page |
| 22 | `test_builder/app/templates/reports.html` | Reports page |
| 23 | `test_builder/app/templates/admin_domain_codes.html` | Admin domain codes page |
| 24 | `test_builder/app/static/app.js` | Vanilla JS (localStorage draft cache + form logic) |
| 25 | `test_builder/app/static/style.css` | Dark-theme CSS |
| 26 | `test_builder/tests/test_smoke.py` | Optional: Playwright smoke tests |

### Modified Files:
- `.gitignore` — add `.env.test-builder` entry
- `test_builder/app/database.py` — add seed data for default domain codes

---

## Tests / Validation

### Per-Task Validation

Every task includes inline verification steps. The key validation points are:

1. **Models import correctly** — `python -c "from app.models import ...; print('OK')"`
2. **App boots** — `uvicorn app.main:app` starts without errors
3. **Login page renders** — curl `/login`
4. **Test case draft + submit** — browser test: localStorage → POST /api/submit → check DB
5. **Execution + runs** — POST /api/runs → check run_number increments
6. **Report generation** — POST /reports/api/submit → check markdown output
7. **Domain code CRUD** — add/edit via forms, duplicate rejection
8. **Scaffold generation** — POST /api/test-cases/{id}/scaffold → check file on disk
9. **Full end-to-end** — add test case → submit → execute → generate report → scaffold
10. **Docker build** — `docker compose build` succeeds
11. **Traefik route** — `curl https://testbuild.zubbystudio.shop/login` returns 200

### Gherkin Scenario Coverage

Each `.feature` scenario maps to a validation check. The complete matrix:

| Feature | Scenario | Validated By |
|---------|----------|-------------|
| test_case_management | Draft in localStorage | Task 5, Verify step |
| test_case_management | Sequential numbering | Task 5, Verify step |
| test_case_management | Reject missing layer | Task 5, API validation |
| test_case_management | Submit all to DB | Task 5, POST /api/submit |
| test_case_management | Block empty submission | Task 5, validation |
| test_execution | Record passing run | Task 6, POST /api/runs Passed |
| test_execution | Record failing run + bug report | Task 6, POST /api/runs Failed |
| test_execution | Re-execution keeps history | Task 6, run_number increment |
| test_execution | Invalid status rejection | Task 6, status validation |
| test_execution | Empty actual result rejection | Task 6, validation |
| reporting | Full report generation | Task 7, POST /reports/api/submit |
| reporting | Downloaded report matches | Task 7, GET download |
| reporting | Block without runs | Task 7, missing runs check |
| reporting | Auto bug report on fail | Task 6, _generate_bug_report |
| reporting | Passed runs no bug report | Task 6, conditional logic |
| admin_and_auth | Add domain code | Task 8, POST /admin/domain-codes |
| admin_and_auth | Duplicate rejection | Task 8, duplicate check |
| admin_and_auth | Edit label | Task 8, POST edit |
| admin_and_auth | Wrong password | Task 4, login endpoint |
| admin_and_auth | Session expiry | Task 4, itsdangerous max_age |
| scaffold_generation | Create folder structure | Task 9, os.makedirs |
| scaffold_generation | Generate pytest stub | Task 9, file content check |
| scaffold_generation | Warn on overwrite | Task 9, exists check |
| scaffold_generation | Fail gracefully | Task 9, PermissionError handling |

---

## Risks, Tradeoffs, and Open Questions

### Risks

| Risk | Mitigation |
|------|-----------|
| **SQLite concurrent access** — Multiple testers editing at once could cause `database is locked` errors | SQLite WAL mode + single-user tool assumption. If it becomes multi-user, migrate to Postgres |
| **Bind mount permissions** — The container may not have write permission to the host `tests/` path | Docker runs as root by default so this should work. If not, add `user: "1000:1000"` to compose |
| **Session secret rotation** — Changing SESSION_SECRET invalidates all active sessions | Document in README. Acceptable for a QA tool |
| **`testbuild.zubbystudio.shop` DNS not pointing to VPS IP** | Verify with `nslookup` before deploy. User confirmed it resolves |
| **SQLite `TIMESTAMPTZ`** — SQLite doesn't have native timezone-aware datetime storage | SQLAlchemy's `DateTime(timezone=True)` stores as ISO text; timezone info is preserved in Python |
| **`python-multipart` required for form data** — FastAPI requires it for `Form(...)` parameters | Already in requirements.txt |

### Tradeoffs

| Decision | Alternative Considered | Why Chosen |
|----------|----------------------|------------|
| SQLite instead of Postgres | Shared openagile_postgres | Zero dependencies, no DB container, simpler deployment |
| Jinja2 + vanilla JS instead of React | React + TanStack Router | No build step, no npm, single container, matches "simple tool" scope |
| Itsdangerous for sessions instead of JWT | JWT with pyjwt | Simpler API, built-in expiry, no secret rotation needed |
| Single-container instead of separate DB+app | Split containers | Only one container to manage, SQLite in volume |
| Flat `.feature` files at `test_builder/` root | `test_builder/features/` subdir | Simpler, matches current layout |

### Resolved Decisions (from user)

| Decision | Answer |
|----------|--------|
| `TEST_BUILDER_PASSWORD` | Same as EPM admin password |
| `TEST_BUILDER_SESSION_SECRET` | Generated: `65ca24772743f6448c0d7b9f2c264b6af9f690463f075eddd11cdb0b5390067d` |
| `tests/` directory | Auto-create in Dockerfile, bind-mount to host path |
| Compose format | v3 (`docker-compose.test-builder.yml`) |
| CSS priority | Match EPM's dark theme (oklch tokens, DM Mono for numbers) |
| Smoke tests | Include — Task 12 is now Playwright smoke tests against all .feature files |

### Secrets file (`.env.test-builder`)

```
TEST_BUILDER_PASSWORD=5WCoBq42CmmS
TEST_BUILDER_SESSION_SECRET=65ca24772743f6448c0d7b9f2c264b6af9f690463f075eddd11cdb0b5390067d
```

---

## Execution Handoff

All open questions resolved. Ready to execute using **subagent-driven-development** — dispatch fresh subagents per task with two-stage review (spec compliance then code quality).

**Shall I proceed with implementation?**