# AT-004 — Acceptance Test: Admin Section Restructure

**Test ID:** AT-004  
**Linked Handover:** HO-024 (Admin Section Restructure — editMode toggle removal)  
**Status:** DRAFT — awaiting AT-004 re-run after HO-039 fixes  
**Priority:** P0 — must pass before F-016 admin routes are integrated  
**Created:** 2026-06-30  
**Author:** Claude (Architect)  
**Executed by:** Codex / Owl Alpha (primary) | Hermes deepseek-flash (fallback)

---

## Prerequisites

Before running AT-004, confirm ALL of the following:

- [x] HO-026 received from Owl Alpha and Nex N2 (implementation report for HO-024) — **CLOSED, superseded by HO-037/HO-039**
- [x] Docker containers are running: `docker compose ps` shows backend + frontend healthy
- [x] Test user accounts seeded (see §3 below)
- [x] No pending database migrations — `alembic current` shows `head`
- [x] Frontend built and served (not dev server) — or dev server with production API

**Route update (HO-038):** Admin functions live at `/settings/*`, not `/admin/*`. All test steps referencing `/admin/*` have been updated to `/settings/*`. See HO-038 §2 for the ruling.

---

## 1. Scope

AT-004 verifies that the admin section restructure delivered in HO-024 is:

1. **Functionally complete** — all admin operations accessible through the new admin section at `/settings/*`
2. **Regression-free** — editMode toggle is removed and no `editMode` variable exists anywhere in the codebase
3. **Route-correct** — admin URLs follow the `/settings/*` pattern
4. **Permission-enforced** — non-admin users cannot access admin routes; ADMIN and SUPERADMIN can
5. **State-clean** — no residual editMode state, toggle buttons, or conditional edit fields in user-facing views

---

## 2. Test Environment

```yaml
Target: testdrive.epm.zubbystudio.shop (production container)
API Base URL: https://testdrive.epm.zubbystudio.shop/api/v1
Frontend URL: https://testdrive.epm.zubbystudio.shop
Database: PostgreSQL (shared, container estate_portfolio_v3)
```

---

## 3. Test Data Setup

Run before executing test cases. Use the seeding script or manual SQL:

```sql
-- Seed three test accounts (if not already present)
-- Passwords use bcrypt==4.0.1 hash of "TestPass123!"

INSERT INTO users (id, email, password_hash, role, is_active, created_at)
VALUES
  (gen_random_uuid(), 'superadmin@test.epm', '<hash>', 'superadmin', TRUE, NOW()),
  (gen_random_uuid(), 'admin@test.epm',      '<hash>', 'admin',      TRUE, NOW()),
  (gen_random_uuid(), 'user@test.epm',       '<hash>', 'user',       TRUE, NOW())
ON CONFLICT (email) DO NOTHING;
```

> Generate hashes: `python3 -c "import bcrypt; print(bcrypt.hashpw(b'TestPass123!', bcrypt.gensalt()).decode())"`

---

## 4. Test Cases

### Group A — Route Access Control

#### AT-004-A01 · Admin routes blocked for USER

```
Actor: Authenticated USER (user@test.epm)
Steps:
  1. Login as user@test.epm
  2. Directly navigate to /settings
  3. Directly navigate to /settings/users
  4. Directly navigate to /settings/price-entry
  5. Call GET /api/v1/settings/users (via curl or browser DevTools)

Expected:
  - /settings redirects to / or shows 403 page
  - /settings/users same behaviour
  - API returns HTTP 403 { "detail": "Insufficient permissions" }
  - No admin navigation links visible in sidebar/header

Pass criteria: All 5 steps produce forbidden/redirect outcome
```

#### AT-004-A02 · Admin routes accessible for ADMIN

```
Actor: Authenticated ADMIN (admin@test.epm)
Steps:
  1. Login as admin@test.epm
  2. Navigate to /settings/price-entry
  3. Verify admin page renders
  4. Navigate to /settings/users
  5. Verify user list renders with ≥1 row (seeded superadmin row)

Expected:
  - /settings/price-entry renders admin page
  - /settings/users renders paginated user list
  - Admin navigation links visible

Pass criteria: Both pages render without error
```

#### AT-004-A03 · Admin routes accessible for SUPERADMIN

```
Actor: Authenticated SUPERADMIN (superadmin@test.epm)
Steps: Same as AT-004-A02
Expected: Same as AT-004-A02 plus superadmin-only actions visible
Pass criteria: All pages render, promote-to-admin button visible
```

---

### Group B — editMode Removal

These tests confirm the locked architectural decision: **`editMode` toggle is deleted, no `editMode` variable exists**.

#### AT-004-B01 · No editMode toggle on Portfolio List page

```
Actor: Any authenticated user
Steps:
  1. Login and navigate to /dashboard
  2. Inspect page for: "Edit" toggle, pencil icon buttons, inline input fields
  3. Check React DevTools for any component with "editMode" in state name

Expected:
  - No edit toggle button present on dashboard
  - No inline input fields in table rows
  - No editMode state in React component tree

Pass criteria: Zero editMode indicators found
```

#### AT-004-B02 · No editMode toggle on Portfolio Detail page

```
Actor: Any authenticated user
Steps:
  1. Navigate to /holdings for any portfolio
  2. Inspect page for edit toggle, inline inputs, conditional edit sections
  3. Check DOM for aria-label="edit" or data-testid="edit-toggle"

Expected:
  - Page shows read-only portfolio summary
  - No inline editing UI present

Pass criteria: No inline editing UI present
```

#### AT-004-B03 · No editMode toggle on Holdings page

```
Actor: Any authenticated user
Steps:
  1. Navigate to /holdings
  2. Inspect for edit toggle, inline editable cells, save/cancel inline buttons

Expected: Holdings displayed as read-only table; no editMode toggle

Pass criteria: No editMode toggle or state present
```

#### AT-004-B04a · `editMode` variable — zero hits (Builder verification)

```
Actor: Builder agent / Codex
Steps:
  1. Run: grep -rn "editMode" frontend/src/ --include="*.tsx" --include="*.ts"
  2. Confirm: editMode toggle variable has 0 occurrences

Expected: Zero matches for `editMode` variable

Pass criteria: grep returns no output for `editMode`
```

**Status: ✅ PASS (confirmed in HO-037)**

#### AT-004-B04b · `isEditing` / `editingRowId` — modal context report

```
Actor: Builder agent / Hermes
Steps:
  1. Run: grep -rn "isEditing\|editingRowId" frontend/src/ --include="*.tsx" --include="*.ts"
  2. For each hit, report the surrounding 5 lines of context
  3. Claude rules whether each hit is acceptable (modal) or a violation (inline data-write)

Expected:
  - Modal-context isEditing: ACCEPTABLE (e.g., settings.users.tsx modal edit state)
  - Inline data-write isEditing: VIOLATION (e.g., holdings.tsx inline row editing)

Pass criteria: Zero inline data-write isEditing hits remain after remediation
```

**Status: ⏳ PENDING — Claude ruling required (see HO-039 isEditing context report)**

---

### Group C — Admin Section Completeness

#### AT-004-C01 · Admin dashboard renders key metrics

```
Actor: ADMIN or SUPERADMIN
Steps:
  1. Navigate to /dashboard as admin
  2. Verify presence of: total portfolio value · invested amount · realized P&L · holdings count

Expected: Dashboard shows 4+ summary cards with non-null values

Pass criteria: All cards render with values (not "—" or empty)
```

#### AT-004-C02 · Admin navigation structure

```
Actor: ADMIN
Steps:
  1. Login and navigate to any /settings/* page
  2. Verify sidebar shows ADMIN section with: User Management · Price Entry · Data Upload
  3. Each nav item links to correct /settings/* route

Expected: Navigation items present and functional

Pass criteria: All nav items navigate without 404
```

#### AT-004-C03 · Portfolio operations in admin section

```
Actor: ADMIN
Steps:
  1. Navigate to /settings/data-upload
  2. Verify data upload page renders
  3. Click Companies tab → verify company list renders
  4. Click Cost Basis tab → verify upload options
  5. Click Claims tab → verify upload guide renders

Expected:
  - Data Upload page renders
  - Each tab section accessible

Pass criteria: Upload page and tabs render; no 404 or errors
```

---

### Group D — API Regression

#### AT-004-D01 · Existing non-admin endpoints unchanged

```
Steps (curl or browser):
  1. GET /api/v1/portfolios          → 200 (authenticated user)
  2. GET /api/v1/portfolios/{id}     → 200
  3. GET /api/v1/holdings            → 200
  4. GET /api/v1/prices              → 200

Expected: All return same status codes as pre-HO-024 baseline

Pass criteria: No regression in status codes for listed endpoints
```

#### AT-004-D02 · New admin endpoints return correct permissions

```
Steps:
  1. As USER:      GET /api/v1/admin/users → 403
  2. As ADMIN:     GET /api/v1/admin/users → 200
  3. As SUPERADMIN: GET /api/v1/admin/users → 200

Pass criteria: Permissions enforced on admin namespace for all three roles
```

**Note:** After HO-039 fix (ADMIN_ROLES set constant), SUPERADMIN should return 200.

---

### Group E — Session / Auth Regression

#### AT-004-E01 · JWT cookie still set on login

```
Steps:
  1. POST /api/v1/auth/login with valid credentials
  2. Inspect response headers for Set-Cookie

Expected:
  - Set-Cookie header present
  - Cookie: HttpOnly=true, SameSite=Lax (or Strict), Secure (if HTTPS)
  - No token in response body

Pass criteria: httpOnly cookie set, not body token
```

#### AT-004-E02 · 30-day session persistence

```
Steps:
  1. Login and note the cookie expiry date
  2. Verify cookie Max-Age or Expires ≈ 30 days from now

Pass criteria: Expiry within 29–31 days of test execution
```

---

## 5. Pass / Fail Summary Sheet

| Test ID | Description | Status | Notes |
|---------|-------------|--------|-------|
| AT-004-A01 | USER blocked from /settings/* | ⬜ | |
| AT-004-A02 | ADMIN accesses /settings/* | ⬜ | |
| AT-004-A03 | SUPERADMIN accesses /settings/* | ⬜ | |
| AT-004-B01 | No editMode on Portfolio List | ⬜ | |
| AT-004-B02 | No editMode on Portfolio Detail | ⬜ | |
| AT-004-B03 | No editMode on Holdings | ⬜ | |
| AT-004-B04a | grep `editMode` → zero hits | ✅ | Confirmed HO-037 |
| AT-004-B04b | isEditing context — modal vs inline | ✅ | PASS after HO-041 fix — modal-based edit dialog |
| AT-004-C01 | Admin dashboard metrics | ⬜ | |
| AT-004-C02 | Admin navigation structure | ⬜ | |
| AT-004-C03 | Portfolio ops in admin | ⬜ | |
| AT-004-D01 | Non-admin endpoints unchanged | ⬜ | |
| AT-004-D02 | Admin endpoints respect roles | ⬜ | |
| AT-004-E01 | JWT cookie set on login | ⬜ | |
| AT-004-E02 | 30-day session persistence | ⬜ | |

**AT-004 OVERALL:** ⬜ PASS / ⬜ FAIL

> AT-004 passes when ALL test cases are ✅. Any single FAIL blocks F-016 admin route integration.
>
> B04a (editMode variable) is confirmed PASS from HO-037.
> B04b (isEditing/editingRowId) awaits Claude ruling — see HO-039 isEditing context report.

---

## 6. Failure Triage Guide

| Symptom | Likely Cause | Fix Direction |
|---------|-------------|---------------|
| /settings/* returns 404 | Frontend router missing /settings route | Check App.tsx route definitions |
| /settings/* returns 200 for USER | Permission guard not applied | Check `require_role` dependency on admin router |
| editMode grep returns hits | Incomplete HO-024 implementation | Return to HO-024 — flag to Owl Alpha / Nex N2 |
| Admin nav items missing | Navigation component not updated | Check admin layout component |
| Cookie not httpOnly | Auth change introduced body token | Revert auth endpoint changes |
| 30-day cookie wrong | Token expiry config changed | Check `ACCESS_TOKEN_EXPIRE_MINUTES` env var |

---

## 7. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester (Codex / Hermes fallback) | | | |
| Product Owner | Zubbyik | | |
| Architect (Claude) | | | |

> Once signed off, update progress-tracker and proceed to F-016 implementation.
