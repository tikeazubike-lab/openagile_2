# F-016 User Management — Retroactive Spec + Acceptance Verification Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Create the missing feature spec for F-016 (already implemented) and verify it passes all acceptance criteria across DB/API/UI layers.

**Architecture:** The feature is already built — backend router at `/api/v1/admin/users` with full CRUD, frontend at `/settings/users` with modals for create/edit/reset-password/delete. This plan creates the spec document retroactively, submits it for architect review, then runs the 3-layer acceptance checklist.

**Tech Stack:** FastAPI + SQLAlchemy async + React 18 + TanStack Router/Query + Zustand + PostgreSQL (shared openagile_postgres)

---

## **Prerequisites Check** ⚠️ **MUST CONFIRM BEFORE EXECUTION**

| Prerequisite | Status | Verification Needed |
|--------------|--------|---------------------|
| VPS accessible (185.216.177.250) | ✅ Assumed | SSH to VPS works |
| Docker Compose v3 running | ✅ Assumed | `docker compose -f docker-compose.v3.yml ps` shows epm_v3 healthy |
| Database `estate_portfolio` exists | ✅ Assumed | Tables include `users` with role/is_active/deleted_at |
| Admin user exists | ❓ Unknown | Need to verify seed_admin.py ran |
| Frontend built & copied to backend/static | ❓ Unknown | Check `/backend/app/static/assets/` has recent build |

**If any prerequisite fails — STOP and resolve before proceeding.**

---

## **Phase 1: Retroactive Feature Spec Creation**

### Task 1.1: Create F-016 Spec Document
**Objective:** Write the missing feature spec matching the implemented code exactly.

**Files:**
- Create: `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/.context/feature-specs/F-016-user-management.md`

**Step 1: Extract actual implementation details from code**
- Read `backend/app/routers/admin_users.py` — endpoints, schemas, auth guards
- Read `estate-portfolio-manager/src/routes/_app.settings.users.tsx` — UI components, hooks, modals
- Read `backend/app/models.py` — User model fields

**Step 2: Write spec using feature-spec-template.md format**
```markdown
---
id: F-016
title: User Management
status: IMPLEMENTED_NEEDS_VERIFICATION
owner-backend: Owl Alpha
owner-frontend: Nex N2
architect: DeepSeek
sprint: Phase 3B
test-domain: ADMN
---

# F-016 — User Management

## Goal
Admin interface to manage system users (create, read, update, delete, reset password) with role-based access control (admin/readonly).

## Dependencies
- F-001 Authentication (complete) — provides JWT auth + require_admin guard

## Backend
Router: `backend/app/routers/admin_users.py`
Endpoints:
  GET    /api/v1/admin/users              — list users (admin only)
  POST   /api/v1/admin/users              — create user (admin only)
  PATCH  /api/v1/admin/users/{user_id}    — update user (admin only)
  PUT    /api/v1/admin/users/{user_id}/reset-password — reset password (admin only)
  DELETE /api/v1/admin/users/{user_id}    — soft delete user (admin only, blocks self-delete)

Model: `User` in `backend/app/models.py`
Migration: Already applied (users table exists)

## Frontend
Route: `src/routes/_app.settings.users.tsx`
Components: Inline in route file (UserModal, ResetPasswordModal, DeleteConfirmDialog, RoleBadge, StatusBadge)
Hooks: `useAdminUsers`, `useAdminCreateUser`, `useAdminUpdateUser`, `useAdminResetPassword`, `useAdminDeleteUser` in `src/api/queries.ts`

## API Response Shape
GET /api/v1/admin/users:
```json
{
  "data": [
    {
      "id": 1,
      "username": "admin",
      "name": "Administrator",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-06-15T10:00:00Z",
      "updated_at": "2026-06-15T10:00:00Z"
    }
  ],
  "meta": { "total": 1 },
  "error": null
}
```

POST /api/v1/admin/users request:
```json
{
  "username": "jsmith",
  "name": "John Smith",
  "password": "securepass123",
  "role": "readonly"
}
```

## Layout
Header: "User Management" + "Add User" button (admin only)
Filters: "Show inactive users" checkbox
Table columns: Username, Name, Role (badge), Status (badge), Actions (Edit, Reset Password, Delete)
Modals: Create/Edit User, Reset Password, Delete Confirmation

Empty state: "No users found."
Loading state: "Loading users..."

## Read-Only vs Admin View
All authenticated users see: Page accessible at /settings/users
Admin additionally sees: All action buttons (create, edit, reset password, delete)
Read-only users: Redirected to /dashboard (enforced in component)

Hidden from read-only nav: Page not in sidebar for read-only role

## Acceptance Checklist

### [DB] Database
- [ ] users table exists with columns: id, username, name, hashed_password, role, is_active, created_at, updated_at, deleted_at
- [ ] Soft delete sets deleted_at + is_active=false, does not hard delete
- [ ] UNIQUE constraint on username
- [ ] role CHECK constraint ('admin' | 'readonly')
- [ ] After create: row visible with correct fields, deleted_at=NULL
- [ ] After delete: row has deleted_at timestamp, is_active=false

### [API] Contract
- [ ] GET /api/v1/admin/users → 200, data is array
- [ ] GET without auth → 401
- [ ] GET with read-only user → 403 (require_admin)
- [ ] POST valid payload → 201, returns created user
- [ ] POST duplicate username → 409 "Username already exists"
- [ ] POST without admin → 403
- [ ] POST invalid payload (short password, bad role) → 422
- [ ] PATCH → 200, record updated
- [ ] PUT /reset-password → 200, password hash changed
- [ ] DELETE → 200, soft delete applied
- [ ] DELETE self → 400 "Cannot delete your own account"
- [ ] Monetary fields: N/A (no monetary fields)

### [UI] Interface
- [ ] Page loads without crash or console errors
- [ ] Data renders from API (not mock/hardcoded)
- [ ] Empty state shows message + icon
- [ ] Loading state visible while fetching
- [ ] Admin sees "Add User" button, read-only does not
- [ ] Role badge: admin=purple, readonly=slate
- [ ] Status badge: active=green dot, inactive=red dot
- [ ] Create modal: username/name/password/role fields, password required on create only
- [ ] Edit modal: username disabled, name/role editable, no password field
- [ ] Reset password modal: new password field, submits to PUT /reset-password
- [ ] Delete dialog: confirms username, warns irreversible, blocks self-delete
- [ ] After mutation: user list refreshes (TanStack Query invalidation)
- [ ] Dark theme compatible (CSS variables only)
- [ ] Read-only user redirected to dashboard

## Test IDs (from Taxonomy)
Backend unit:        ADMN-USER-BE-UT-001 through 005
Backend integration: ADMN-USER-BE-INT-001 through 005
Backend contract:    ADMN-USER-BE-API-001 through 005
Frontend E2E:        ADMN-USER-FE-E2E-001 through 005

Requirement ref:     REQ-ADMN-001 (User CRUD), REQ-ADMN-002 (Role guards)

## Sign-Off
- [ ] All [DB] checklist items passing
- [ ] All [API] checklist items passing
- [ ] All [UI] checklist items passing
- [ ] .context/progress-tracker.md updated to COMPLETE
- [ ] HO-XXX.md filed in docs/handovers/
- [ ] AT-XXX.md filed in docs/testing/acceptance/
- [ ] Commit: feat(admin): implement F-016 user management
```

---

## **Phase 2: Architect Review (DeepSeek)**

### Task 2.1: Submit Spec to DeepSeek for Review
**Objective:** Get architect approval on the retroactive spec.

**Action:**
```bash
# Use delegate_task with DeepSeek model
delegate_task(
  role="leaf",
  toolsets=["web"],
  context="Review F-016 User Management spec. Backend and frontend already implemented. Spec must match EXISTING code exactly — no aspirational features. Check: endpoints match admin_users.py, UI matches _app.settings.users.tsx, API shapes match actual responses, acceptance criteria are verifiable against deployed testdrive.epm.zubbystudio.shop.",
  goal="Review F-016 spec for accuracy against implementation. Return APPROVED or list of required corrections."
)
```

**Expected Output:** `APPROVED` or list of corrections.

**If corrections needed:** Patch the spec file, re-submit.

---

## **Phase 3: Acceptance Testing (3-Layer Verification)**

### Task 3.1: [DB] Database Verification
**Objective:** Verify user table schema and soft-delete behavior.

**Files:** None (read-only SQL)

**Commands to run on VPS:**
```bash
# Connect to shared postgres
docker exec -it openagile_postgres psql -U openagile -d estate_portfolio

# 1. Verify table structure
\d users

# 2. Check constraints
SELECT conname, contype, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'users'::regclass;

# 3. Verify current data
SELECT id, username, name, role, is_active, deleted_at, created_at 
FROM users 
ORDER BY id;

# 4. Test soft delete (if test user exists)
-- UPDATE users SET deleted_at = NOW(), is_active = false WHERE username = 'testuser';
-- SELECT * FROM users WHERE username = 'testuser';
```

**Expected:**
- Columns: id, username, name, hashed_password, role, is_active, created_at, updated_at, deleted_at
- UNIQUE(username), CHECK(role IN ('admin','readonly'))
- Admin user exists (seeded)
- Soft delete sets deleted_at + is_active=false

---

### Task 3.2: [API] Contract Verification
**Objective:** Verify all endpoints return correct shapes, status codes, auth guards.

**Prerequisite:** Admin JWT cookie (`epm_token`) from login.

**Commands (run from VPS or local with tunnel):**
```bash
# Get admin token first
TOKEN=$(curl -s -c cookies.txt -X POST https://testdrive.epm.zubbystudio.shop/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<ADMIN_PASSWORD>"}' | jq -r .data.access_token)

# Or use cookie directly
COOKIE=$(cat cookies.txt | grep epm_token | awk '{print $7}')

# 1. GET list (admin)
curl -s -b "epm_token=$COOKIE" https://testdrive.epm.zubbystudio.shop/api/v1/admin/users | jq .

# 2. GET without auth → expect 401
curl -s https://testdrive.epm.zubbystudio.shop/api/v1/admin/users | jq .

# 3. POST create user
curl -s -b "epm_token=$COOKIE" -X POST https://testdrive.epm.zubbystudio.shop/api/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","name":"Test User","password":"testpass123","role":"readonly"}' | jq .

# 4. POST duplicate → expect 409
curl -s -b "epm_token=$COOKIE" -X POST https://testdrive.epm.zubbystudio.shop/api/v1/admin/users \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser1","name":"Test User","password":"testpass123","role":"readonly"}' | jq .

# 5. PATCH update
curl -s -b "epm_token=$COOKIE" -X PATCH https://testdrive.epm.zubbystudio.shop/api/v1/admin/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name","role":"admin"}' | jq .

# 6. PUT reset-password
curl -s -b "epm_token=$COOKIE" -X PUT https://testdrive.epm.zubbystudio.shop/api/v1/admin/users/2/reset-password \
  -H "Content-Type: application/json" \
  -d '{"new_password":"newpass123"}' | jq .

# 7. DELETE (soft)
curl -s -b "epm_token=$COOKIE" -X DELETE https://testdrive.epm.zubbystudio.shop/api/v1/admin/users/2 | jq .

# 8. Verify soft delete in DB
docker exec -it openagile_postgres psql -U openagile -d estate_portfolio -c "SELECT username, deleted_at, is_active FROM users WHERE username='testuser1';"

# 9. Test self-delete block (use admin's own ID)
curl -s -b "epm_token=$COOKIE" -X DELETE https://testdrive.epm.zubbystudio.shop/api/v1/admin/users/1 | jq .
```

**Expected:** All status codes and response shapes match spec.

---

### Task 3.3: [UI] Browser Verification
**Objective:** Verify frontend renders correctly, interactions work, role guards enforce.

**Steps:**
1. Open https://testdrive.epm.zubbystudio.shop/settings/users as admin
2. Verify: Page loads, table shows users, "Add User" button visible
3. Click "Add User" → fill form → submit → verify user appears in table
4. Click "Edit" on a user → change role → save → verify badge updates
5. Click "Reset Password" → enter new password → submit → verify success
6. Click "Delete" → confirm → verify user removed from table (soft delete)
7. Verify self-delete blocked: try deleting admin account → error toast
8. Open DevTools Console → **zero errors**
9. Open Network tab → verify API calls match expected endpoints
10. **Test read-only guard:** Login as read-only user (or temporarily demote admin) → navigate to /settings/users → should redirect to /dashboard
11. **Test dark theme:** Toggle theme → verify badges/modals use CSS variables
12. **Test empty state:** Delete all non-admin users → verify "No users found" message

---

## **Phase 4: Documentation & Handover**

### Task 4.1: Update Progress Tracker
**File:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/.context/progress-tracker.md`

**Changes:**
- F-016 status: `PLANNED` → `COMPLETE`
- Last HO: `HO-XXX` (new handover ID)
- Notes: "Retroactive spec created, all 3-layer AT passed"

### Task 4.2: Write Handover Brief
**File:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/docs/handovers/HO-XXX.md`

**Format:** Use handover-template.md — sections 1-5 with exact verification evidence.

### Task 4.3: Write Acceptance Test Record
**File:** `/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio/docs/testing/acceptance/AT-XXX.md`

**Format:** Use 3-layer checklist with PASS/FAIL for each item.

### Task 4.4: Commit
```bash
cd /home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio
git add .context/feature-specs/F-016-user-management.md
git add .context/progress-tracker.md
git add docs/handovers/HO-XXX.md
git add docs/testing/acceptance/AT-XXX.md
git commit -m "feat(admin): F-016 user management retroactive spec + verification"
git push origin develop
```

---

## **Phase 5: Next Feature — F-017 Remove editMode Toggle**

### Task 5.1: Create F-017 Spec (NEW feature — standard workflow)
**Objective:** Write spec BEFORE implementation.

**Files:**
- Create: `.context/feature-specs/F-017-remove-editmode-toggle.md`

**Key Requirements (from progress-tracker.md):**
- Delete `uiStore.editMode` from `src/store/uiStore.ts`
- Replace inline edit toggle with role guards (admin sees edit controls, read-only doesn't)
- Affected pages: Holdings, Registrars (any page using editMode)
- Admin edit views: F-003b `/admin/holdings`, F-006b `/admin/registrars` (separate specs)

**Dependencies:** F-016 COMPLETE (roles defined and working)

---

## **Risks & Open Questions**

| Risk | Impact | Mitigation |
|------|--------|------------|
| Admin password unknown | Can't get JWT for API tests | Check `.env` or `seed_admin.py` for credentials |
| Frontend not rebuilt after backend changes | UI tests stale | Rebuild: `cd estate-portfolio-manager && npm run build && cp -r dist/* ../backend/app/static/` |
| Read-only user doesn't exist | Can't test role guard | Create one via API or seed script |
| Tracker has stale "BUGS-OPEN" for F-002/F-003 | Confusion on priority | Update tracker after F-016 verification |

---

## **Execution Order Summary**

```
1. Create F-016 spec (retroactive)           → .context/feature-specs/F-016-user-management.md
2. DeepSeek review                            → delegate_task (DeepSeek)
3. [DB] Verify users table + soft delete      → psql on VPS
4. [API] Verify all 7 endpoints + guards      → curl with admin cookie
5. [UI] Browser verification checklist        → testdrive.epm.zubbystudio.shop
6. Update progress-tracker.md                 → F-016 = COMPLETE
7. Write HO-XXX.md + AT-XXX.md                → docs/handovers/ + docs/testing/acceptance/
8. Commit & push                              → git add/commit/push
9. Create F-017 spec (next feature)           → .context/feature-specs/F-017-remove-editmode-toggle.md
```

---

**Plan saved to:** `.hermes/plans/2026-06-30_143000-F016-user-management-retroactive-spec-and-verification.md`

**Ready to execute when prerequisites confirmed.**