---
type: BR
id: BR-005
title: Registrar Document Management
status: ACTIVE
version: 1.0
created: 2026-05-01
updated: 2026-05-05
owner: Claude (The Brain)
related: []
---

# [BR] BR-005 — Registrar Document Management
> **Type**: Business Requirement · **Status**: 🟢 ACTIVE · **Version**: 1.0

# Final Implementation Spec — Registrars Page + Document Management
**From**: Claude (The Brain)
**To**: Antigravity / Cursor (Builder)
**Date**: 2026-05-05
**Protocol**: MASTER_CONTEXT.md v4.0
**Input**: Grok Phase 3B brainstorm + user confirmation (per-registrar documents)
**Branch**: test

---

## Tree-of-Thoughts Summary (Decisions Locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| File storage path | Structured volume: `/app/uploads/registrar_documents/{registrar_id}/{requirement_id}/{timestamp}_{filename}` | Collision-free, filesystem-browsable, maps to DB hierarchy |
| File versioning | Multiple rows per requirement, latest shown by default | Preserves history, zero extra schema complexity |
| Document scope | Per-registrar requirements; optional company_id on uploaded files | Requirements are registrar-wide; specific uploads can reference a holding |
| Cloud storage | Rejected | Violates self-hosted preference, adds external dependency |
| Draft/Live on documents | Not applied | Documents are factual records, not staged content |
| Access control | Admin uploads/deletes; readonly can view/download | Consistent with app-wide role model |

---

## Part A: Database Schema (Additive Alembic Migrations)

### A.1 — Existing `registrars` table additions

```sql
-- Add missing fields to registrars table if not already present
ALTER TABLE registrars
  ADD COLUMN IF NOT EXISTS response_rating  SMALLINT DEFAULT NULL
    CHECK (response_rating BETWEEN 1 AND 5),
  ADD COLUMN IF NOT EXISTS notes            TEXT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS deleted_at       TIMESTAMPTZ DEFAULT NULL;
```

### A.2 — New `registrar_requirements` table

```sql
-- Requirement templates per registrar
-- e.g. "Registrar X requires: Proof of Identity, Share Certificate, CSCS number"
CREATE TABLE registrar_requirements (
    id              SERIAL PRIMARY KEY,
    registrar_id    INTEGER NOT NULL REFERENCES registrars(id) ON DELETE CASCADE,

    task_name       VARCHAR(200) NOT NULL,
    -- e.g. "Unclaimed Dividend Claim", "Dematerialisation", "KYC Update",
    --      "Account Reactivation", "Share Certificate Digitisation",
    --      "Delisted Company Claim"

    document_title  VARCHAR(200) NOT NULL,
    -- e.g. "Proof of Identity (NIN/Slip)", "Share Certificate",
    --      "Recent Passport Photograph", "CSCS Number"

    description     TEXT DEFAULT NULL,
    -- Optional longer explanation of what is required

    is_required     BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order      SMALLINT NOT NULL DEFAULT 0,
    -- Controls display order within a task group

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_registrar_requirements_registrar
  ON registrar_requirements(registrar_id)
  WHERE deleted_at IS NULL;
```

### A.3 — New `registrar_documents` table

```sql
-- Actual uploaded files against each requirement
-- Multiple rows per requirement = versioning (latest by uploaded_at)
CREATE TABLE registrar_documents (
    id                          SERIAL PRIMARY KEY,
    registrar_requirement_id    INTEGER NOT NULL
                                  REFERENCES registrar_requirements(id)
                                  ON DELETE CASCADE,

    company_id                  INTEGER DEFAULT NULL
                                  REFERENCES companies(id),
    -- Optional: attach file to a specific holding
    -- e.g. share certificate specifically for ZENITHBANK

    -- File metadata (file content stored on volume, not in DB)
    file_name       VARCHAR(255) NOT NULL,
    -- Original filename as uploaded by user

    file_path       VARCHAR(512) NOT NULL,
    -- Relative path inside uploads volume:
    -- registrar_documents/{registrar_id}/{requirement_id}/{timestamp}_{filename}

    file_size       BIGINT NOT NULL DEFAULT 0,
    -- Bytes

    mime_type       VARCHAR(100) NOT NULL DEFAULT 'application/octet-stream',

    status          VARCHAR(30) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'submitted', 'completed', 'rejected')),
    -- pending:   document uploaded, not yet submitted to registrar
    -- submitted: physically/digitally sent to registrar
    -- completed: registrar confirmed receipt / task resolved
    -- rejected:  registrar rejected this document, re-upload needed

    notes           TEXT DEFAULT NULL,
    -- Free-form notes: "Submitted via email on 2026-05-01"

    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by     INTEGER REFERENCES users(id),
    deleted_at      TIMESTAMPTZ DEFAULT NULL
);

CREATE INDEX idx_registrar_documents_requirement
  ON registrar_documents(registrar_requirement_id)
  WHERE deleted_at IS NULL;

CREATE INDEX idx_registrar_documents_company
  ON registrar_documents(company_id)
  WHERE deleted_at IS NULL;
```

### A.4 — Docker volume mount (add to docker-compose.yml)

```yaml
services:
  backend:
    volumes:
      - ./uploads:/app/uploads        # ← add this line
      - ~/ObsidianVaultMirror:/vault:ro
```

```bash
# Create directory on VPS (one-time)
mkdir -p uploads/registrar_documents
```

---

## Part B: API Endpoints

### B.1 — Registrar CRUD (`backend/app/routers/registrars.py` — NEW FILE)

```
GET    /api/v1/registrars
  Returns: all non-deleted registrars with:
    - linked_company_count (int)
    - linked_companies: [{ id, ticker, name }]
    - requirement_count (int)
    - pending_document_count (int)  ← how many requirements have no uploaded file

POST   /api/v1/registrars                    [admin]
PUT    /api/v1/registrars/{id}               [admin]
DELETE /api/v1/registrars/{id}               [admin, soft delete]
```

### B.2 — Requirements CRUD

```
GET    /api/v1/registrars/{id}/requirements
  Returns: requirements grouped by task_name, each with latest document if any

POST   /api/v1/registrars/{id}/requirements  [admin]
  Body: { task_name, document_title, description?, is_required, sort_order? }

PUT    /api/v1/registrar-requirements/{id}   [admin]
DELETE /api/v1/registrar-requirements/{id}   [admin, soft delete]
```

### B.3 — Document Upload / Download / Management

```
POST   /api/v1/registrar-requirements/{req_id}/documents  [admin]
  Body: multipart/form-data
    file:       the PDF/JPG/PNG file
    company_id: optional int
    notes:      optional string
  Action:
    1. Validate file type (PDF, JPG, JPEG, PNG only) and size (max 20MB)
    2. Build path: uploads/registrar_documents/{registrar_id}/{req_id}/{timestamp}_{filename}
    3. Save file to volume
    4. Insert registrar_documents row
  Returns: document metadata (id, file_name, file_size, uploaded_at, status)

GET    /api/v1/registrar-documents/{id}/download   [admin + readonly]
  Action:
    1. Verify document exists and deleted_at IS NULL
    2. Verify current_user has access (any authenticated user)
    3. Return FileResponse from volume path
  Security: Never return the raw file_path to the frontend

PUT    /api/v1/registrar-documents/{id}/status     [admin]
  Body: { status: "pending" | "submitted" | "completed" | "rejected", notes? }

DELETE /api/v1/registrar-documents/{id}            [admin, soft delete]
  Action: Sets deleted_at — does NOT delete file from volume
  Reason: File may be needed for audit trail

GET    /api/v1/registrar-documents/{req_id}/history  [admin + readonly]
  Returns: all versions (including soft-deleted) ordered by uploaded_at DESC
  Use: "Show history" expander in UI
```

### B.4 — Key implementation details for upload endpoint

```python
# backend/app/routers/registrars.py

import os, shutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

UPLOAD_BASE = "/app/uploads/registrar_documents"
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

@router.post("/{req_id}/documents")
async def upload_document(
    req_id: int,
    file: UploadFile = File(...),
    company_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # Validate requirement exists
    req = await db.get(RegistrarRequirement, req_id)
    if not req or req.deleted_at:
        raise HTTPException(404, "Requirement not found")

    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(422, f"File type not allowed. Accepted: PDF, JPG, PNG")

    # Read and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(422, "File exceeds 20MB limit")

    # Build safe file path
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(
        c if c.isalnum() or c in ".-_" else "_"
        for c in file.filename
    )
    rel_path = f"{req.registrar_id}/{req_id}/{timestamp}_{safe_name}"
    abs_path = os.path.join(UPLOAD_BASE, rel_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    with open(abs_path, "wb") as f:
        f.write(content)

    doc = RegistrarDocument(
        registrar_requirement_id=req_id,
        company_id=company_id,
        file_name=file.filename,
        file_path=rel_path,          # relative — never expose abs path
        file_size=len(content),
        mime_type=file.content_type,
        notes=notes,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return {"data": {
        "id": doc.id,
        "file_name": doc.file_name,
        "file_size": doc.file_size,
        "mime_type": doc.mime_type,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at.isoformat(),
    }, "error": None}


@router.get("/documents/{doc_id}/download")
async def download_document(
    doc_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),  # all roles can download
):
    doc = await db.get(RegistrarDocument, doc_id)
    if not doc or doc.deleted_at:
        raise HTTPException(404, "Document not found")

    abs_path = os.path.join(UPLOAD_BASE, doc.file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(404, "File not found on server")

    return FileResponse(
        path=abs_path,
        filename=doc.file_name,
        media_type=doc.mime_type,
    )
```

---

## Part C: React Page Layout

### C.1 — Page structure

```
/registrars — Two-panel layout (desktop), stacked (mobile)

LEFT PANEL (280px, scrollable):
  "Registrars" heading + [+ Add Registrar] button (admin, editMode)

  Per registrar — clickable card:
  ┌─────────────────────────────────────┐
  │ First Registrars Nigeria Ltd        │
  │ 12 companies · 3 pending docs       │
  │ ★★★★☆  (response rating)           │
  └─────────────────────────────────────┘
  Active card: lavender left border
  Pending docs badge: amber number if > 0

RIGHT PANEL (remaining width):
  When no registrar selected:
    Empty state: "Select a registrar to view details"

  When registrar selected:
    ┌─ Registrar Details Card ──────────────────────────────────┐
    │ [Name]   [Email]   [Phone]   [Address]   [Rating ★]       │
    │ [Edit] button (admin, editMode)                            │
    └────────────────────────────────────────────────────────────┘

    ┌─ Linked Companies ────────────────────────────────────────┐
    │ [TICKER] Company Name  [TICKER] Company Name  ...         │
    │ Each: lavender pill, clickable → /companies               │
    └────────────────────────────────────────────────────────────┘

    ┌─ Requirements & Documents ────────────────────────────────┐
    │ [+ Add Requirement] button (admin, editMode)              │
    │                                                           │
    │ Grouped by task_name (accordion):                         │
    │                                                           │
    │ ▼ UNCLAIMED DIVIDEND CLAIM                                │
    │ ┌─────────────────────────────────────────────────────┐   │
    │ │ Document          │ Status    │ File        │ Action │   │
    │ │ Proof of Identity │ ●Pending  │ nin-slip.pdf│ ↓ ✕   │   │
    │ │ Share Certificate │ ●Complete │ cert.pdf    │ ↓ ✕   │   │
    │ │ Bank Statement    │ ○Pending  │ —           │Upload  │   │
    │ └─────────────────────────────────────────────────────┘   │
    │                                                           │
    │ ▼ DEMATERIALISATION                                       │
    │ ┌─────────────────────────────────────────────────────┐   │
    │ │ CSCS Account No.  │ ●Submitted│ cscs-form.pdf│ ↓ ✕ │   │
    │ └─────────────────────────────────────────────────────┘   │
    └────────────────────────────────────────────────────────────┘
```

### C.2 — Status badge colours

```
pending:    amber pill  (#FEF3C7 bg, #D97706 text)  ○
submitted:  blue pill   (#DBEAFE bg, #2563EB text)  ●
completed:  green pill  (#DCFCE7 bg, #16A34A text)  ●
rejected:   red pill    (#FEE2E2 bg, #DC2626 text)  ●
```

### C.3 — Upload interaction (per requirement row)

```
No file yet:
  [↑ Upload] button → opens file picker (PDF/JPG/PNG, max 20MB)
  Optional: drag file onto the row directly

File uploaded (latest shown):
  filename.pdf (2.4MB)  [↓ Download] [✕ Remove]
  "Show history ▼" link if multiple versions exist

History expanded:
  | Version | Date         | Size  | Status    | [↓] |
  | v3      | 2026-05-01   | 2.4MB | submitted |  ↓  |
  | v2      | 2026-04-15   | 1.8MB | pending   |  ↓  |
  | v1      | 2026-03-10   | 2.1MB | rejected  |  ↓  |

Company tag (optional):
  If document has company_id:
  Show [TICKER] badge next to filename
  e.g. "cert-zenith.pdf [ZENITHBANK]"
```

### C.4 — Add Requirement form (admin, editMode)

```
Slide-down panel below the task group:
  Task Name:       [dropdown of common tasks + "Other (type)"]
  Document Title:  [text input]
  Description:     [textarea, optional]
  Required:        [toggle]
  [Save] [Cancel]

Common task presets (dropdown options):
  Unclaimed Dividend Claim
  Dematerialisation (CSCS)
  Share Certificate Digitisation
  KYC Update
  Account Reactivation
  Delisted Company Claim
  Other (free text)
```

### C.5 — TanStack Query hooks to add

```typescript
// src/api/queries.ts — add these

export function useRegistrars() { ... }
export function useRegistrarRequirements(registrarId: number) { ... }
export function useUploadDocument() { ... }          // useMutation
export function useUpdateDocumentStatus() { ... }    // useMutation
export function useDeleteDocument() { ... }          // useMutation

// Download is a direct link — not a query hook:
// href={`/api/v1/registrar-documents/${doc.id}/download`}
// credentials: 'include' via an anchor click handler
```

---

## Part D: File Security Considerations

1. **Never expose `file_path` to frontend** — the download endpoint is the only access path. Frontend never knows where files live on disk.

2. **Auth on every download** — `GET /api/v1/registrar-documents/{id}/download` calls `get_current_user`. Unauthenticated requests get 401.

3. **File type validation** — both MIME type (from browser) and file content must match. A renamed `.exe` file should be rejected. Add a magic-byte check for PDF (starts with `%PDF`), JPEG (`FFD8FF`), PNG (`89504E47`).

4. **Path traversal prevention** — the `safe_name` sanitisation in the upload endpoint strips all non-alphanumeric characters except `.-_`. Never use raw `file.filename` in a filesystem path.

5. **Volume backup** — the `./uploads` bind mount means files survive container rebuilds. Include it in any backup strategy alongside the database.

---

## Part E: Implementation Order

```
[ ] 1. Alembic migration: registrar_requirements + registrar_documents tables
[ ] 2. Add volume mount to docker-compose.yml + create uploads/ directory
[ ] 3. SQLAlchemy models for both new tables in models.py
[ ] 4. backend/app/routers/registrars.py — full CRUD + upload + download
[ ] 5. Wire registrars router in main.py
[ ] 6. TanStack Query hooks in queries.ts
[ ] 7. /registrars page — two-panel layout + left registrar list
[ ] 8. Registrar detail panel — details card + linked companies
[ ] 9. Requirements accordion + status badges
[ ] 10. Upload interaction per requirement row
[ ] 11. History expander
[ ] 12. Add Requirement form (editMode, admin)
[ ] 13. Commit → push to test → verify on staging
[ ] 14. Write acceptance test handover to Claude
```

---

## Part F: Acceptance Test (Fill After Implementation)

```markdown
## Registrars Page — Acceptance Test

### CRUD
- [ ] Registrar list renders with company count + pending doc badges
- [ ] Selecting a registrar loads detail panel
- [ ] Add registrar (admin, editMode) → appears in left list
- [ ] Edit registrar details → changes persist
- [ ] Linked companies render as clickable lavender pills

### Requirements
- [ ] Requirements grouped by task_name (accordion)
- [ ] Add Requirement → appears in correct task group
- [ ] Required vs optional distinction visible
- [ ] Status badges render with correct colours

### Document Upload
- [ ] Upload PDF → appears in requirement row
- [ ] Upload JPG → accepted
- [ ] Upload .exe or unsupported type → rejected with error
- [ ] File > 20MB → rejected with size error
- [ ] Download link retrieves correct file (with auth)
- [ ] Unauthenticated download attempt → 401
- [ ] Upload second version → history shows both, latest shown by default
- [ ] Show history → all versions listed with dates
- [ ] Soft delete document → disappears from row (file kept on volume)

### Status Updates
- [ ] Change status to "submitted" → badge updates
- [ ] Change status to "completed" → badge updates green
- [ ] Status change reflected in pending doc count on left panel

### Access Control
- [ ] Readonly user: can view requirements and download files
- [ ] Readonly user: no Upload, Add Requirement, or Edit buttons visible
```

---

**END OF SPEC**

**Receiving agent**: Antigravity / Cursor — implement in order A → B → C → D
**After implementation**: send acceptance test results to Claude
**Do not start next page until registrars acceptance test is received**
