# AT-004 — Acceptance Test: Admin Section Restructure

**Test ID:** AT-004  
**Linked Handover:** HO-024 (Admin Section Restructure — editMode toggle removal)  
**Status:** DRAFT — awaiting Owl Alpha + Nex N2 → HO-026 confirmation  
**Priority:** P0 — must pass before F-016 admin routes are integrated  
**Created:** 2026-06-30  
**Author:** Claude (Architect)  
**Executed by:** Codex (tester agent)

---

## Prerequisites

Before running AT-004, confirm ALL of the following:

- [ ] HO-026 received from Owl Alpha and Nex N2 (implementation report for HO-024)
- [ ] Docker containers are running: `docker compose ps` shows backend + frontend healthy
- [ ] Test user accounts seeded (see §3 below)
- [ ] No pending database migrations — `alembic current` shows `head`
- [ ] Frontend built and served (not dev server) — or dev server with production API

---

## 1. Scope

AT-004 verifies that the admin section restructure delivered in HO-024 is:

1. **Functionally complete** — all admin operations accessible through the new admin section
2. **Regression-free** — editMode toggle is removed and no inline editing exists anywhere in the app
3. **Route-correct** — admin URLs follow the `/admin/*` pattern
4. **Permission-enforced** — non-admin users cannot access admin routes
5. **State-clean** — no residual editMode state, toggle buttons, or conditional edit fields in user-facing views

---

## 2. Test Environment

```yaml
Target: Development environment (openagile_2)
API Base URL: http://localhost:8000   # [VERIFY THIS — confirm dev port]
Frontend URL: http://localhost:3000   # [VERIFY THIS — confirm frontend dev port]
Database: PostgreSQL (shared, local dev instance)
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
  2. Directly navigate to /admin
  3. Directly navigate to /admin/users
  4. Directly navigate to /admin/portfolios
  5. Call GET /api/v1/admin/users (via curl or browser DevTools)

Expected:
  - /admin redirects to / or shows 403 page
  - /admin/users same behaviour
  - API returns HTTP 403 { "detail": "Insufficient permissions" }
  - No admin navigation links visible in sidebar/header

Pass criteria: All 5 steps produce forbidden/redirect outcome
```

#### AT-004-A02 · Admin routes accessible for ADMIN

```
Actor: Authenticated ADMIN (admin@test.epm)
Steps:
  1. Login as admin@test.epm
  2. Navigate to /admin
  3. Verify admin dashboard renders
  4. Navigate to /admin/users
  5. Verify user list renders with ≥1 row (seeded superadmin row)

Expected:
  - /admin renders admin dashboard
  - /admin/users renders paginated user list
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

These tests confirm the locked architectural decision: **editMode toggle is deleted, no inline editing exists**.

#### AT-004-B01 · No editMode toggle on Portfolio List page

```
Actor: Any authenticated user
Steps:
  1. Login and navigate to /portfolios
  2. Inspect page for: "Edit" toggle, pencil icon buttons, inline input fields
  3. Check React DevTools for any component with "editMode" in state name

Expected:
  - No edit toggle button present on portfolio list
  - No inline input fields in table rows
  - No editMode state in React component tree

Pass criteria: Zero editMode indicators found
```

#### AT-004-B02 · No editMode toggle on Portfolio Detail page

```
Actor: Any authenticated user
Steps:
  1. Navigate to /portfolios/{id} for any portfolio
  2. Inspect page for edit toggle, inline inputs, conditional edit sections
  3. Check DOM for aria-label="edit" or data-testid="edit-toggle"

Expected:
  - Page shows read-only portfolio summary
  - Edit operations only accessible via admin section (for admin) or dedicated modal (for owner — confirm with HO-024 scope)

Pass criteria: No inline editing UI present
```

#### AT-004-B03 · No editMode toggle on Holdings page

```
Actor: Any authenticated user
Steps:
  1. Navigate to /portfolios/{id}/holdings
  2. Inspect for edit toggle, inline editable cells, save/cancel inline buttons

Expected: Holdings displayed as read-only table; edit actions via modals only

Pass criteria: No inline edit UI present
```

#### AT-004-B04 · No residual editMode in codebase (Builder verification)

```
Actor: Builder agent / Codex
Steps:
  1. Run: grep -rn "editMode" frontend/src/ --include="*.tsx" --include="*.ts"
  2. Run: grep -rn "setEditMode\|editMode\|isEditing" frontend/src/ --include="*.tsx"

Expected: Zero matches

Pass criteria: grep returns no output
```

---

### Group C — Admin Section Completeness

#### AT-004-C01 · Admin dashboard renders key metrics

```
Actor: ADMIN or SUPERADMIN
Steps:
  1. Navigate to /admin
  2. Verify presence of: total users count · active portfolios count · last price upload date

Expected: Dashboard shows 3+ summary cards with non-null values

Pass criteria: All cards render with values (not "—" or empty)
```

#### AT-004-C02 · Admin navigation structure

```
Actor: ADMIN
Steps:
  1. Login and navigate to /admin
  2. Verify sidebar/navigation shows: Users · Portfolios · Price Data · (Reports if implemented)
  3. Each nav item links to correct /admin/* route

Expected: Navigation items present and functional

Pass criteria: All nav items navigate without 404
```

#### AT-004-C03 · Portfolio operations in admin section

```
Actor: ADMIN
Steps:
  1. Navigate to /admin/portfolios
  2. Verify portfolio list renders
  3. Click on a portfolio → verify detail view (read-only or admin-edit, per HO-024 spec)
  4. Verify no inline editing in admin portfolio view either

Expected:
  - Portfolio list renders
  - Detail view accessible
  - All edits are modal-based (not inline)

Pass criteria: List and detail render; no inline inputs present
```

---

### Group D — API Regression

#### AT-004-D01 · Existing non-admin endpoints unchanged

```
Steps (curl or Postman):
  1. GET /api/v1/portfolios          → 200 (authenticated user)
  2. GET /api/v1/portfolios/{id}     → 200
  3. GET /api/v1/holdings            → 200
  4. POST /api/v1/portfolios         → 201 with valid body
  5. GET /api/v1/prices              → 200

Expected: All return same status codes as pre-HO-024 baseline

Pass criteria: No regression in status codes for listed endpoints
```

#### AT-004-D02 · New admin endpoints return correct permissions

```
Steps:
  1. As USER:      GET /api/v1/admin/users → 403
  2. As ADMIN:     GET /api/v1/admin/users → 200
  3. As SUPERADMIN: GET /api/v1/admin/users → 200

Pass criteria: Permissions enforced on admin namespace
```

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
| AT-004-A01 | USER blocked from /admin/* | ⬜ | |
| AT-004-A02 | ADMIN accesses /admin/* | ⬜ | |
| AT-004-A03 | SUPERADMIN accesses /admin/* | ⬜ | |
| AT-004-B01 | No editMode on Portfolio List | ⬜ | |
| AT-004-B02 | No editMode on Portfolio Detail | ⬜ | |
| AT-004-B03 | No editMode on Holdings | ⬜ | |
| AT-004-B04 | grep returns zero editMode hits | ⬜ | |
| AT-004-C01 | Admin dashboard metrics | ⬜ | |
| AT-004-C02 | Admin navigation structure | ⬜ | |
| AT-004-C03 | Portfolio ops in admin | ⬜ | |
| AT-004-D01 | Non-admin endpoints unchanged | ⬜ | |
| AT-004-D02 | Admin endpoints respect roles | ⬜ | |
| AT-004-E01 | JWT cookie set on login | ⬜ | |
| AT-004-E02 | 30-day session persistence | ⬜ | |

**AT-004 OVERALL:** ⬜ PASS / ⬜ FAIL

> AT-004 passes when ALL 14 test cases are ✅. Any single FAIL blocks F-016 admin route integration.

---

## 6. Failure Triage Guide

| Symptom | Likely Cause | Fix Direction |
|---------|-------------|---------------|
| /admin/* returns 404 | Frontend router missing /admin route | Check App.tsx route definitions |
| /admin/* returns 200 for USER | Permission guard not applied | Check `require_role` dependency on admin router |
| editMode grep returns hits | Incomplete HO-024 implementation | Return to HO-024 — flag to Owl Alpha / Nex N2 |
| Admin nav items missing | Navigation component not updated | Check admin layout component |
| Cookie not httpOnly | Auth change introduced body token | Revert auth endpoint changes |
| 30-day cookie wrong | Token expiry config changed | Check `ACCESS_TOKEN_EXPIRE_MINUTES` env var |

---

## 7. Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester (Codex) | | | |
| Product Owner | Zubbyik | | |
| Architect (Claude) | | | |

> Once signed off, update HO-025 status log and proceed to F-016 implementation.
