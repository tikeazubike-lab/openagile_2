# HO-023: Admin Restructure — Remove Inline Editing + Build Admin CRUD

**From:** Claude (The Brain / Architect)
**To:** Owl Alpha (Backend) + Nex N2 (Frontend)
**Date:** 2026-06-23
**Feature:** F-017 — Remove Inline Editing + Build Admin CRUD Section

---

## What Was Done

### Context
The original UX had inline editing toggles on Holdings and Registrars pages. Admin users could edit, add, and delete records directly from the table rows. This created UX issues:
- Cursor jump bug (BUG-002) from inline edit state in parent component
- No clear separation between read-only and admin users
- Edit controls visible to all users (even read-only)
- No centralized admin interface

### Decision
Remove ALL inline editing from user-facing pages. Move ALL CRUD operations to dedicated `/admin/*` routes. Read-only users should never see any edit controls.

---

## What Is Verified

| Item | Status |
|------|--------|
| BUG-001 Dashboard charts blank | ✅ Fixed |
| BUG-002 Holdings inline edit cursor jumps | ✅ Fixed (InlineEditRow created) |
| BUG-003 POST /api/v1/holdings 500 error | ✅ Fixed (total_cost, status keyword) |
| BUG-004 Theme toggle icon static | ✅ Already fixed in existing code |
| BUG-005 Notification bell not showing | ✅ Fixed (isLoading guard) |
| Admin password seeded from .env | ✅ Verified (login working) |
| v3 Docker compose deployed | ✅ Running at testdrive.epm.zubbystudio.shop |

---

## What Is Broken / Uncertain

| Item | Details |
|------|---------|
| Holdings inline edit still present | editMode toggle, InlineEditRow, AddHoldingDrawer still in `_app.holdings.tsx` |
| Registrars inline edit still present | Same pattern as Holdings |
| No `/admin/holdings` route | Needs to be created |
| No `/admin/registrars` route | Needs to be created |
| No role guards on admin routes | Admin routes don't exist yet, but when created need `require_admin` |
| `uiStore.editMode` still exists | Needs to be removed from Zustand store |

---

## Next Actions (Implementation Plan)

### Task 1: Remove editMode from uiStore
- **File:** `estate-portfolio-manager/src/store/uiStore.ts`
- **What:** Remove `editMode` boolean and `toggleEditMode` function
- **Note:** Check all files that import from uiStore — they will need updates

### Task 2: Remove edit controls from Holdings page
- **File:** `estate-portfolio-manager/src/routes/_app.holdings.tsx`
- **What:** Remove edit mode toggle button, per-row Edit/Delete icons, Add Holding button, inline edit cell rendering
- **Keep:** `InlineEditRow.tsx` (will be reused in admin section), `AddHoldingDrawer.tsx` (move to admin)

### Task 3: Remove inline edit from other pages
- **Files:** Check all routes for `editMode` references
- **What:** Remove all edit mode toggles, inline edit buttons, inline add buttons
- **Verification:** `grep -r "editMode" estate-portfolio-manager/src/` returns zero

### Task 4: Create `/admin/holdings` route
- **File:** `estate-portfolio-manager/src/routes/_app.admin.holdings.tsx` (CREATE)
- **What:** Full CRUD — list, create, edit, publish/draft toggle, soft delete
- **Auth:** `require_admin` dependency
- **Reuse:** `AddHoldingDrawer`, existing queries

### Task 5: Create `/admin/registrars` route
- **File:** `estate-portfolio-manager/src/routes/_app.admin.registrars.tsx` (CREATE)
- **What:** Full CRUD for registrars + document/requirements management
- **Auth:** `require_admin` dependency

### Task 6: Add role guards to admin route group
- **File:** `estate-portfolio-manager/src/routes/_app.tsx` or root layout
- **What:** Admin-only route group with role check

### Task 7: Update navigation
- **File:** Sidebar/Navbar component
- **What:** Remove "Edit Mode" nav item, add "Admin" section

### Task 8: Clean up unused imports
- **What:** Remove unused lucide imports, delete orphaned components

---

## Files Likely to Change

| File | Action |
|------|--------|
| `src/store/uiStore.ts` | Remove editMode/toggleEditMode |
| `src/routes/_app.holdings.tsx` | Remove all inline edit UI |
| `src/routes/_app.registrars.tsx` | Remove all inline edit UI |
| `src/routes/_app.admin.holdings.tsx` | CREATE |
| `src/routes/_app.admin.registrars.tsx` | CREATE |
| `src/components/layout/Sidebar.tsx` | Update nav items |
| `src/routes/_app.tsx` | Add admin route group + role guard |
| `backend/app/routers/holdings.py` | May need new admin-only endpoints |

---

## Blockers

None. All prerequisite bugs are fixed. The admin section can be built independently.

---

## Open Questions for Implementer

1. Should `InlineEditRow.tsx` be reused in admin section or deleted?
2. Should the admin section use TanStack file-based routes (`_app.admin.holdings.tsx`) or a different pattern?
3. Should there be a "preview" mode for read-only users to see what the admin section looks like?
4. Do we need audit logging for admin CRUD actions?

---

## Acceptance Criteria

- [ ] `grep -r "editMode" src/` returns zero results
- [ ] Read-only users see NO edit/add/delete buttons on any page
- [ ] Admin users can perform all CRUD via `/admin/holdings` and `/admin/registrars`
- [ ] Admin routes return 403 for non-admin users
- [ ] No console errors
- [ ] Existing functionality (viewing, filtering) still works for all users
