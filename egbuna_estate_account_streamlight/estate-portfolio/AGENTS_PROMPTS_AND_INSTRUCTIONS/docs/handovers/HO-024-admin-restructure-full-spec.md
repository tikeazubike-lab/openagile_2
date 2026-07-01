---
type: HO
id: HO-024
title: Claude → Deepseek:flash + nemotron-3-ultra-550b-55b:free: Admin Restructure — Full Implementation Spec
date: 2026-06-24
from: Claude (The Brain)
to: Deepseek:flash (Backend) + nemotron-3-ultra-550b-55b:free (Frontend)
protocol: EPM Hybrid Framework v1.0
feature: F-017
parent-ho: HO-023
---

# HO-024 — Admin Restructure Full Spec

## HO-023 Assessment

All 5 bugs confirmed fixed. HO-023 is well-structured and the
implementation plan is directionally correct. Four open questions
are now answered below. No blockers remain.

---

## Answers to HO-023 Open Questions

| Q | Decision | Rationale |
|---|----------|-----------|
| Q1: InlineEditRow.tsx | **DELETE entirely** | Admin uses drawer/modal pattern — inline row editing is the pattern we are removing |
| Q2: TanStack route pattern | **Use `_app.admin.holdings.tsx`** | Consistent with existing routing convention |
| Q3: Read-only preview of admin | **No** | Admin section is invisible to read-only users — no preview mode |
| Q4: Audit logging | **Yes — new `admin_audit` DB table** | Every CRUD action logged: who, what, when, old value, new value |

---

## Part A: Backend — Deepseek:flash

### A1 — New Table: admin_audit

Add Alembic migration for this table first, before any frontend work.

```sql
CREATE TABLE admin_audit (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    action          VARCHAR(20) NOT NULL
                    CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'PUBLISH', 'RESTORE')),
    entity_type     VARCHAR(50) NOT NULL,
    -- e.g. 'holding', 'registrar', 'company', 'dividend', 'claim'
    entity_id       INTEGER NOT NULL,
    old_value       JSONB DEFAULT NULL,
    -- snapshot of record BEFORE change (null for CREATE)
    new_value       JSONB DEFAULT NULL,
    -- snapshot of record AFTER change (null for DELETE)
    performed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address      VARCHAR(45) DEFAULT NULL
    -- optional: track where admin actions came from
);

CREATE INDEX idx_admin_audit_user     ON admin_audit(user_id);
CREATE INDEX idx_admin_audit_entity   ON admin_audit(entity_type, entity_id);
CREATE INDEX idx_admin_audit_performed ON admin_audit(performed_at DESC);
```

### A2 — Audit Helper Service

```python
# backend/app/services/audit.py

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AdminAudit

async def log_admin_action(
    db: AsyncSession,
    user_id: int,
    action: str,          # 'CREATE' | 'UPDATE' | 'DELETE' | 'PUBLISH' | 'RESTORE'
    entity_type: str,     # 'holding' | 'registrar' | etc.
    entity_id: int,
    old_value: dict | None = None,
    new_value: dict | None = None,
):
    """
    Call this BEFORE committing any admin CRUD operation.
    Both the audit record and the entity change commit together.
    """
    audit = AdminAudit(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        performed_at=datetime.now(timezone.utc),
    )
    db.add(audit)
    # Do NOT commit here — caller commits both audit + entity together
```

### A3 — Updated Holdings Router (Admin Endpoints)

The existing `/api/v1/holdings` endpoints are for READ operations.
Add admin-only endpoints under the same router but with `require_admin`:

```python
# backend/app/routers/holdings.py — ADD these endpoints

# GET /api/v1/admin/holdings — admin list (includes drafts + deleted option)
@router.get("/admin/holdings")
async def admin_list_holdings(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    query = select(Holding)
    if not include_deleted:
        query = query.where(Holding.deleted_at.is_(None))
    # admin sees ALL statuses including draft
    ...

# POST /api/v1/admin/holdings — create holding
@router.post("/admin/holdings", status_code=201)
async def admin_create_holding(
    payload: HoldingCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # ... create holding
    await log_admin_action(db, current_user.id, 'CREATE',
        'holding', holding.id,
        old_value=None,
        new_value=holding_to_dict(holding))
    await db.commit()
    ...

# PATCH /api/v1/admin/holdings/{id} — update holding
@router.patch("/admin/holdings/{holding_id}")
async def admin_update_holding(
    holding_id: int,
    payload: HoldingUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    old = holding_to_dict(holding)   # snapshot BEFORE
    # ... apply changes
    await log_admin_action(db, current_user.id, 'UPDATE',
        'holding', holding_id,
        old_value=old,
        new_value=holding_to_dict(holding))
    await db.commit()
    ...

# PUT /api/v1/admin/holdings/{id}/publish
@router.put("/admin/holdings/{holding_id}/publish")
async def admin_publish_holding(...):
    await log_admin_action(db, current_user.id, 'PUBLISH',
        'holding', holding_id, ...)
    ...

# DELETE /api/v1/admin/holdings/{id} — soft delete
@router.delete("/admin/holdings/{holding_id}")
async def admin_delete_holding(...):
    old = holding_to_dict(holding)
    holding.deleted_at = datetime.now(timezone.utc)
    await log_admin_action(db, current_user.id, 'DELETE',
        'holding', holding_id, old_value=old, new_value=None)
    await db.commit()
    ...
```

### A4 — Admin Audit Endpoint

```python
# backend/app/routers/admin.py (NEW FILE)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/audit")
async def get_admin_audit(
    entity_type: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Recent admin actions — shown in /admin audit log."""
    query = (select(AdminAudit, User.username)
             .join(User, AdminAudit.user_id == User.id)
             .order_by(AdminAudit.performed_at.desc())
             .limit(limit))
    if entity_type:
        query = query.where(AdminAudit.entity_type == entity_type)
    ...
    return {
        "data": [
            {
                "id": row.AdminAudit.id,
                "action": row.AdminAudit.action,
                "entity_type": row.AdminAudit.entity_type,
                "entity_id": row.AdminAudit.entity_id,
                "performed_by": row.username,
                "performed_at": row.AdminAudit.performed_at.isoformat(),
                "old_value": row.AdminAudit.old_value,
                "new_value": row.AdminAudit.new_value,
            }
            for row in rows
        ],
        "meta": {"total": len(rows)},
        "error": None,
    }
```

Wire in `main.py`:
```python
from app.routers.admin import router as admin_router
app.include_router(admin_router)
```

### A5 — Deepseek:flash Execution Order

```
[ ] 1. Alembic migration: CREATE TABLE admin_audit
[ ] 2. Add AdminAudit model to models.py
[ ] 3. Create backend/app/services/audit.py
[ ] 4. Add admin endpoints to holdings.py (POST, PATCH, PUT, DELETE)
[ ] 5. Create backend/app/routers/admin.py with GET /admin/audit
[ ] 6. Wire admin router in main.py
[ ] 7. Test: POST /api/v1/admin/holdings creates holding AND audit record
[ ] 8. Test: PATCH creates audit record with old_value + new_value
[ ] 9. Test: GET /api/v1/admin/audit returns recent actions
[ ] 10. Push backend — signal nemotron-3-ultra-550b-55b:free to start frontend
```

---

## Part B: Frontend — nemotron-3-ultra-550b-55b:free

**Do not start until Deepseek:flash confirms backend is pushed and tested.**

### B1 — Delete These Files

```
src/components/holdings/InlineEditRow.tsx    ← DELETE
```

Confirm deletion:
```bash
grep -r "InlineEditRow" src/
# Must return zero results after deletion + cleanup
```

### B2 — Remove editMode from uiStore

```typescript
// src/store/uiStore.ts
// REMOVE: editMode boolean
// REMOVE: toggleEditMode function
// REMOVE: setEditMode function (if exists)
// KEEP: everything else (theme, sidebar state, etc.)
```

Find all usages before deleting:
```bash
grep -r "editMode\|toggleEditMode\|setEditMode" src/
```

Fix every file that referenced editMode — replace all:
```typescript
// BEFORE (any file that had this):
{editMode && <button>Edit</button>}
{isAdmin() && editMode && <SomeComponent />}

// AFTER — admin controls are always visible to admin, never to others:
{isAdmin() && <button>Edit</button>}
// No editMode needed — role is the guard
```

### B3 — Clean Holdings Page

```typescript
// src/routes/_app.holdings.tsx
// REMOVE:
//   - Edit mode toggle button in header
//   - Per-row Edit icon
//   - Per-row Delete icon
//   - Per-row Publish button
//   - [+ Add Holding] button
//   - Any import of InlineEditRow, AddHoldingDrawer
//   - editingRowId state
//   - Any editMode conditional rendering

// KEEP:
//   - Both tables (Active + Claims) — read-only display
//   - All computed columns (Curr Value, Cost Basis, return[%])
//   - Sorting and filtering
//   - Grand total row
//   - All useHoldings() query hooks for display
```

### B4 — Clean Registrars Page

```typescript
// src/routes/_app.registrars.tsx
// REMOVE:
//   - [Edit Registrar] button
//   - [Delete] button
//   - [+ Add Registrar] button
//   - [+ Add Requirement] button
//   - Upload document controls (move to admin)
//   - Status dropdown on documents (move to admin)
//   - RegistrarModal import (move to admin)

// KEEP:
//   - Left panel registrar list (read-only)
//   - Detail panel: contact info, linked companies (read-only)
//   - Requirements accordion (read-only — shows checklist)
//   - Document download links (all authenticated users can download)
```

### B5 — Create /admin/holdings Route

```typescript
// src/routes/_app.admin.holdings.tsx (CREATE)

// This is the full CRUD page — admin only
// Layout:

// Header:
//   "Holdings Administration"
//   [+ Add Holding] button → opens AddHoldingDrawer (moved here from main page)

// Tabs (optional — or just one unified table):
//   [Live] [Draft] [All]

// Table (all holdings including drafts):
//   Same columns as /holdings but with Actions column:
//   | ... | Status | Actions |
//   Each row: [Edit] [Publish/Unpublish] [Delete]

// Edit action → opens EditHoldingDrawer (420px right drawer)
//   Fields: Company (locked after creation), Shares, Avg Cost,
//           Purchase Date, Notes, Status
//   Save → PATCH /api/v1/admin/holdings/{id} + audit log

// Delete action → confirmation dialog
//   "Remove [TICKER] from holdings?"
//   Confirm → DELETE /api/v1/admin/holdings/{id} + audit log

// Audit log section (bottom of page):
//   "Recent Admin Actions" — last 20 entries from GET /api/v1/admin/audit
//   Columns: When | Who | Action | Entity | Change
//   Source badges: CREATE=green, UPDATE=blue, DELETE=red, PUBLISH=lavender

// Auth guard: if (!isAdmin()) redirect to /dashboard
```

### B6 — Create /admin/registrars Route

```typescript
// src/routes/_app.admin.registrars.tsx (CREATE)

// Same two-panel layout as /registrars but with all edit controls:
//   Left panel: registrar list + [+ Add Registrar] button
//   Right panel detail: [Edit Registrar] [Delete] buttons
//                       [+ Add Requirement] per accordion section
//                       Upload/delete document controls
//                       Status dropdown on documents

// Reuse RegistrarModal.tsx (already exists)
// Reuse document upload/download logic (already exists)
// The /registrars page becomes read-only; this page has all write ops
```

### B7 — Add Admin Role Guard to Route Group

```typescript
// src/routes/_app.tsx (or _app.admin.tsx if using nested layout)

// Admin route group — wrap all /admin/* routes:
export const Route = createFileRoute('/_app/admin')({
  beforeLoad: async ({ location }) => {
    const user = useAuthStore.getState().user
    if (!user) throw redirect({ to: '/login' })
    if (user.role !== 'admin') throw redirect({ to: '/dashboard' })
    // Non-admin hitting /admin/* → silently redirected to dashboard
  },
})
```

### B8 — Update Sidebar Navigation

```typescript
// src/components/layout/Sidebar.tsx

// REMOVE: "Edit Mode" toggle button (if present)

// Admin section in sidebar (visible to admin only):
{isAdmin() && (
  <NavSection label="Admin">
    <NavItem to="/admin/holdings"    icon={<Database />}  label="Holdings" />
    <NavItem to="/admin/registrars"  icon={<Building2 />} label="Registrars" />
    <NavItem to="/admin/price-entry" icon={<TrendingUp />} label="Price Entry" />
    <NavItem to="/admin/users"       icon={<Users />}      label="Users" />
    <NavItem to="/admin/data-import" icon={<Upload />}     label="Data Import" />
    <NavItem to="/admin/deleted-records" icon={<Trash2 />} label="Deleted Records" />
  </NavSection>
)}
```

### B9 — New TanStack Query Hooks

```typescript
// src/api/queries.ts — ADD these admin hooks

export function useAdminHoldings(includeDeleted = false) {
  return useQuery({
    queryKey: ['admin-holdings', includeDeleted],
    queryFn: () =>
      fetch(`/api/v1/admin/holdings?include_deleted=${includeDeleted}`,
        { credentials: 'include' })
        .then(r => r.json()).then(r => r.data),
  })
}

export function useAdminCreateHolding() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload) =>
      fetch('/api/v1/admin/holdings', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then(r => r.json()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-holdings'] })
      qc.invalidateQueries({ queryKey: ['holdings'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      qc.invalidateQueries({ queryKey: ['admin-audit'] })
    },
  })
}

export function useAdminUpdateHolding() { /* PATCH */ }
export function useAdminDeleteHolding() { /* DELETE */ }
export function useAdminPublishHolding() { /* PUT /publish */ }

export function useAdminAudit(entityType?: string) {
  return useQuery({
    queryKey: ['admin-audit', entityType],
    queryFn: () =>
      fetch(`/api/v1/admin/audit${entityType ? `?entity_type=${entityType}` : ''}`,
        { credentials: 'include' })
        .then(r => r.json()).then(r => r.data),
  })
}
```

### B10 — nemotron-3-ultra-550b-55b:free Execution Order

```
WAIT for Deepseek:flash to confirm backend is pushed and tested first.

Then:
[ ] 1. Delete InlineEditRow.tsx
[ ] 2. Remove editMode from uiStore.ts
[ ] 3. Fix all files that referenced editMode (grep first)
[ ] 4. Clean _app.holdings.tsx (remove all edit controls)
[ ] 5. Clean _app.registrars.tsx (remove all edit controls)
[ ] 6. Create _app.admin.holdings.tsx with full CRUD + audit log
[ ] 7. Create _app.admin.registrars.tsx with full CRUD
[ ] 8. Add admin role guard to _app.tsx admin route group
[ ] 9. Update Sidebar.tsx navigation
[ ] 10. Add admin query hooks to queries.ts
[ ] 11. Run: grep -r "editMode" src/ → confirm zero results
[ ] 12. Test /holdings as admin → no edit controls visible
[ ] 13. Test /admin/holdings as admin → full CRUD works
[ ] 14. Test /admin/holdings as readonly → redirected to /dashboard
[ ] 15. Rebuild frontend, restart container, verify on testdrive
```

---

## Part C: Acceptance Criteria (AT-004)

File AT-004 in docs/testing/acceptance/ after implementation.

### [DB]
- [ ] admin_audit table exists with correct columns
- [ ] After creating a holding via admin: admin_audit row exists with
      action='CREATE', entity_type='holding', old_value=null
- [ ] After updating a holding: admin_audit row has old_value ≠ new_value
- [ ] After deleting a holding: holdings row has deleted_at set (not hard deleted)
      AND admin_audit row has action='DELETE', new_value=null

### [API]
- [ ] GET /api/v1/admin/holdings → 200 for admin, 403 for readonly
- [ ] POST /api/v1/admin/holdings (valid) → 201
- [ ] PATCH /api/v1/admin/holdings/{id} → 200, audit record created
- [ ] DELETE /api/v1/admin/holdings/{id} → 200, soft delete only
- [ ] GET /api/v1/admin/audit → 200, recent actions listed
- [ ] All monetary values in admin responses are strings

### [UI]
- [ ] grep -r "editMode" src/ → zero results
- [ ] /holdings page: zero edit/delete/add buttons visible (admin or readonly)
- [ ] /registrars page: zero edit/delete/add buttons visible
- [ ] /admin/holdings: [+ Add Holding] button works → drawer opens
- [ ] /admin/holdings: Edit icon → drawer opens with prefilled values → save works
- [ ] /admin/holdings: Delete → confirmation → row disappears → audit log updated
- [ ] /admin/holdings: Publish → status changes live/draft → dashboard updates
- [ ] /admin/registrars: All CRUD operations work
- [ ] Sidebar shows Admin section to admin, nothing to readonly
- [ ] Non-admin visiting /admin/* → redirected to /dashboard silently
- [ ] Audit log at bottom of admin pages shows recent actions with badges
- [ ] No console errors on any page

---

## Part D: Progress Tracker Update

After AT-004 passes, update .context/progress-tracker.md:

```
F-017  Remove editMode toggle    → COMPLETE
F-003b Holdings Admin Edit View  → COMPLETE
F-006b Registrars Admin Edit View → COMPLETE
```

---

**End of HO-024**
**Deepseek:flash**: execute Part A first, signal when done
**nemotron-3-ultra-550b-55b:free**: wait for Deepseek:flash signal, then execute Part B
**AT-004**: file after both parts complete
**Next HO to Claude**: HO-025 with AT-004 results
