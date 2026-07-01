---
type: AT
id: AT-005
title: F-016 User Management — Acceptance Tests
date: 2026-06-24
feature: F-016
status: PASS
---

# AT-005 — User Management Acceptance Criteria

## [DB]
- [x] No schema changes needed (users table already exists with correct columns)
- [x] users table has role column defaulting to 'readonly'
- [x] users table has is_active, deleted_at columns for soft-delete support

## [API]
- [x] GET /api/v1/admin/users → 200 for admin, 403 for readonly
- [x] POST /api/v1/admin/users (valid) → 201
- [x] POST /api/v1/admin/users (duplicate username) → 409
- [x] PATCH /api/v1/admin/users/{id} → 200, audit fields updated
- [x] PATCH /api/v1/admin/users/{id} (not found) → 404
- [x] PUT /api/v1/admin/users/{id}/reset-password → 200
- [x] DELETE /api/v1/admin/users/{id} → 200, soft delete only (deleted_at set, is_active=false)
- [x] DELETE /api/v1/admin/users/{self} → 400
- [x] Password validation: minimum 8 characters enforced
- [x] Role validation: only 'admin' or 'readonly' accepted

## [UI]
- [x] /admin/users page shows table of all users (Username, Name, Role, Status, Actions)
- [x] Add User button works → Create User modal opens
- [x] Edit button → modal opens with prefilled values → save works
- [x] Reset Password button → modal opens → submit works
- [x] Delete button → confirmation dialog → row disappears on confirm
- [x] Role badges: admin = purple, readonly = slate
- [x] Status indicators: Active = green dot, Inactive = red dot
- [x] Non-admin users redirected to /dashboard
- [x] Sidebar Admin section includes User Management link
- [x] No console errors

## Test Results
- Backend: 15/15 tests passing
- Frontend: Build succeeds, TypeScript check clean
- Spec compliance: PASS (backend + frontend)
- Code quality: APPROVED (backend + frontend)

## Files Changed
| File | Action |
|------|--------|
| `backend/app/routers/admin_users.py` | CREATE |
| `backend/app/main.py` | MODIFY (wire router) |
| `backend/tests/unit/test_admin_users.py` | CREATE |
| `estate-portfolio-manager/src/api/queries.ts` | MODIFY (add admin user hooks) |
| `estate-portfolio-manager/src/routes/_app.settings.users.tsx` | MODIFY (replace stub) |
| `estate-portfolio-manager/src/components/layout/Sidebar.tsx` | MODIFY (update nav links) |
| `claude_handovers/progresstracker.md` | MODIFY (F-016 → COMPLETE) |

---
**Result: PASS — All acceptance criteria met.**
