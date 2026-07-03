# F-016 — User Management

**Feature ID:** F-016  
**Feature Name:** User Management  
**Status:** DRAFT  
**Priority:** P0 — Foundational (must be complete before any Phase 3C feature)  
**Created:** 2026-06-30  
**Author:** Claude (Architect)  
**Stack:** FastAPI · PostgreSQL 15 · React 18 · TypeScript · JWT (httpOnly cookies)

---

## 1. Purpose

Every Phase 3C feature — audit trails, multi-portfolio ownership, admin approvals, price upload permissions — depends on knowing **who** a user is and **what they are allowed to do**. F-016 defines the role model, permission matrix, and user lifecycle operations that all downstream features will reference by FK and policy check.

This spec does **not** introduce a second identity system. EPM v2 already has JWT-authenticated sessions stored in httpOnly cookies (30-day persistence, locked architecture decision). F-016 **extends** that foundation with:

- A formal **role taxonomy** (3 tiers)
- A **permissions matrix** (per-resource, per-operation)
- **Admin CRUD** for user accounts (replaces any residual inline editing)
- **Self-service profile** operations users may perform on themselves
- Soft delete semantics consistent with the locked decision (timezone-aware timestamps)

---

## 2. Scope

### In Scope

| Area | What is covered |
|------|----------------|
| Role taxonomy | SUPERADMIN · ADMIN · USER — definitions, inheritance, mutability rules |
| Permission matrix | Per-resource (portfolios, holdings, prices, users, reports) × per-operation (create/read/update/delete/approve) |
| Admin user CRUD | List · View · Create · Edit roles · Deactivate · Restore |
| Self-service profile | Change display name · Change password · View own role · View own sessions |
| Audit log hook | Every privileged action emits an audit event (consumed by F-019 or successor) |
| API contract | REST endpoints with exact request/response shapes |
| Frontend surfaces | Admin → Users section (consistent with HO-024 admin restructure) |

### Out of Scope

| Area | Reason |
|------|--------|
| OAuth / SSO | Not planned for Phase 3C |
| MFA / TOTP | Separate feature post-3C |
| Fine-grained portfolio ACLs (user-to-portfolio sharing) | F-017 scope |
| Email verification flow | Requires email service not yet provisioned |
| Role-based UI element hiding beyond menu-level | Component-level guard is implementation detail |

---

## 3. Role Taxonomy

### 3.1 Roles

| Role | Numeric Level | Description |
|------|--------------|-------------|
| `SUPERADMIN` | 30 | Full system access. Can create/deactivate ADMIN accounts. Cannot be deactivated by ADMIN. Exactly one SUPERADMIN must exist at all times (the bootstrap user). |
| `ADMIN` | 20 | Can manage USER accounts and perform all operational tasks (price uploads, portfolio approvals). Cannot promote to SUPERADMIN or demote/delete another ADMIN. |
| `USER` | 10 | Standard authenticated user. Manages own portfolios and holdings only. No access to admin section. |

### 3.2 Role Assignment Rules

- A user is assigned exactly **one role** at creation time.
- Only `SUPERADMIN` may change a user's role to or from `ADMIN`.
- `ADMIN` may change `USER` roles **only** between `USER` values (i.e., no promotion).
- Role stored as `ENUM` in PostgreSQL; API returns lowercase string.
- Bootstrap `SUPERADMIN` account: role field is immutable — no API endpoint may alter it.

### 3.3 Role Inheritance

Permissions are **additive upward**: `SUPERADMIN` inherits all `ADMIN` permissions, `ADMIN` inherits all `USER` permissions.

---

## 4. Permission Matrix

`✅` = allowed · `🚫` = forbidden · `⚠️` = conditional (see notes)

### 4.1 User Resource

| Operation | USER | ADMIN | SUPERADMIN |
|-----------|------|-------|------------|
| Read own profile | ✅ | ✅ | ✅ |
| Update own display name / password | ✅ | ✅ | ✅ |
| Read any user profile | 🚫 | ✅ | ✅ |
| Create user account | 🚫 | ✅ | ✅ |
| Edit user role (USER → USER) | 🚫 | ✅ | ✅ |
| Edit user role (USER → ADMIN) | 🚫 | 🚫 | ✅ |
| Edit user role (ADMIN → *) | 🚫 | 🚫 | ✅ |
| Deactivate USER account | 🚫 | ✅ | ✅ |
| Deactivate ADMIN account | 🚫 | 🚫 | ✅ |
| Deactivate SUPERADMIN account | 🚫 | 🚫 | 🚫 (protected) |
| Restore (un-deactivate) account | 🚫 | ✅ ⚠️ | ✅ |
| Hard delete | 🚫 | 🚫 | 🚫 (soft delete only) |

> ⚠️ ADMIN may restore only USER-level accounts. SUPERADMIN restores any.

### 4.2 Portfolio Resource

| Operation | USER | ADMIN | SUPERADMIN |
|-----------|------|-------|------------|
| Create own portfolio | ✅ | ✅ | ✅ |
| Read own portfolio | ✅ | ✅ | ✅ |
| Update own portfolio | ✅ | ✅ | ✅ |
| Delete own portfolio (soft) | ✅ | ✅ | ✅ |
| Read any portfolio | 🚫 | ✅ | ✅ |
| Modify any portfolio | 🚫 | 🚫 | ✅ |

### 4.3 Price Data Resource

| Operation | USER | ADMIN | SUPERADMIN |
|-----------|------|-------|------------|
| View prices | ✅ | ✅ | ✅ |
| Upload NGX Daily PDF | 🚫 | ✅ | ✅ |
| Approve uploaded prices | 🚫 | ✅ | ✅ |
| Delete price record | 🚫 | 🚫 | ✅ |

### 4.4 Report Resource

| Operation | USER | ADMIN | SUPERADMIN |
|-----------|------|-------|------------|
| Generate own portfolio report | ✅ | ✅ | ✅ |
| View system-wide reports | 🚫 | ✅ | ✅ |

---

## 5. Data Model

### 5.1 Users Table (extended)

```sql
-- Extends existing users table from Phase 2 auth foundation
-- Additive migration only — no columns removed

ALTER TABLE users
  ADD COLUMN IF NOT EXISTS role        VARCHAR(12)  NOT NULL DEFAULT 'user'
                                       CHECK (role IN ('superadmin','admin','user')),
  ADD COLUMN IF NOT EXISTS is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMPTZ,          -- soft delete timestamp (tz-aware)
  ADD COLUMN IF NOT EXISTS deactivated_by UUID REFERENCES users(id),
  ADD COLUMN IF NOT EXISTS display_name VARCHAR(100),
  ADD COLUMN IF NOT EXISTS created_by  UUID REFERENCES users(id);
```

> **Locked decision honoured:** soft delete uses timezone-aware timestamp (`deactivated_at`), not a boolean flag.

### 5.2 Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_users_role      ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
```

### 5.3 Constraints

- At least one row with `role = 'superadmin'` must exist at all times. Enforce at application layer (not DB-level trigger) to avoid complexity.
- `deactivated_at IS NOT NULL ↔ is_active = FALSE` — enforced at write time by service layer.

---

## 6. API Contract

Base path: `/api/v1/admin/users` (admin operations)  
Self-service path: `/api/v1/me` (own-profile operations, existing endpoint extended)

### 6.1 List Users

```
GET /api/v1/admin/users
Authorization: httpOnly JWT cookie
Required role: ADMIN or SUPERADMIN

Query params:
  role        string   Filter by role (user|admin|superadmin)
  is_active   boolean  Filter by active status (default: true)
  page        int      Page number (default: 1)
  page_size   int      Items per page (default: 20, max: 100)
  search      string   Partial match on email or display_name

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "email": "string",
      "display_name": "string | null",
      "role": "user | admin | superadmin",
      "is_active": true,
      "created_at": "ISO8601",
      "deactivated_at": "ISO8601 | null"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

### 6.2 Get Single User

```
GET /api/v1/admin/users/{user_id}
Required role: ADMIN or SUPERADMIN

Response 200: same shape as single item above
Response 404: { "detail": "User not found" }
```

### 6.3 Create User

```
POST /api/v1/admin/users
Required role: ADMIN (creates USER only) | SUPERADMIN (creates any)

Request body:
{
  "email": "string",            // required, unique
  "password": "string",         // required, min 8 chars
  "display_name": "string",     // optional
  "role": "user | admin"        // default: "user"
}

Response 201:
{
  "id": "uuid",
  "email": "string",
  "display_name": "string | null",
  "role": "string",
  "is_active": true,
  "created_at": "ISO8601"
}

Response 409: { "detail": "Email already registered" }
Response 403: { "detail": "Insufficient permissions to assign this role" }
```

### 6.4 Update User Role

```
PATCH /api/v1/admin/users/{user_id}/role
Required role: SUPERADMIN (any change) | ADMIN (USER→USER only, i.e., no-op guard)

Request body:
{
  "role": "user | admin | superadmin"
}

Response 200: { "id": "uuid", "role": "string" }
Response 403: { "detail": "Cannot promote to this role" }
Response 422: { "detail": "Cannot modify SUPERADMIN role" }  // on bootstrap account
```

### 6.5 Deactivate User

```
DELETE /api/v1/admin/users/{user_id}
Required role: ADMIN (USER targets only) | SUPERADMIN (ADMIN targets)

This is a SOFT DELETE — sets is_active=false, deactivated_at=now(), deactivated_by=caller.

Response 200:
{
  "id": "uuid",
  "is_active": false,
  "deactivated_at": "ISO8601"
}

Response 403: { "detail": "Insufficient permissions to deactivate this account" }
Response 409: { "detail": "Cannot deactivate the only SUPERADMIN" }
```

### 6.6 Restore User

```
POST /api/v1/admin/users/{user_id}/restore
Required role: ADMIN (USER accounts) | SUPERADMIN (any)

Response 200:
{
  "id": "uuid",
  "is_active": true,
  "deactivated_at": null
}
```

### 6.7 Self-service: Update Own Profile

```
PATCH /api/v1/me/profile
Required role: Any authenticated user

Request body (all optional):
{
  "display_name": "string"
}

Response 200: { "id": "uuid", "display_name": "string" }
```

### 6.8 Self-service: Change Own Password

```
POST /api/v1/me/change-password
Required role: Any authenticated user

Request body:
{
  "current_password": "string",
  "new_password": "string"    // min 8 chars
}

Response 200: { "message": "Password updated" }
Response 401: { "detail": "Current password incorrect" }
```

---

## 7. Frontend Requirements

All admin user management lives inside the **Admin section** established by HO-024. No inline editing anywhere — consistent with locked decision.

### 7.1 Admin → Users List Page (`/admin/users`)

| Element | Behaviour |
|---------|-----------|
| Table | Columns: Email · Display Name · Role (badge) · Status (Active/Inactive) · Joined · Actions |
| Role badge | Colour-coded: SUPERADMIN = purple · ADMIN = amber · USER = grey |
| Status badge | Active = green · Inactive = red |
| Filter bar | By role dropdown · Active/Inactive toggle · Search (email/name) |
| Pagination | Server-side, 20 per page |
| "New User" button | Opens Create User modal |
| Row actions | View · Edit Role · Deactivate / Restore |

### 7.2 Create User Modal

- Fields: Email (required) · Display Name (optional) · Role selector (constrained by caller's permissions) · Password (required)
- Submit → `POST /api/v1/admin/users`
- On 409: show inline "Email already exists" error

### 7.3 Edit Role Modal

- Single role dropdown, pre-populated with current role
- Options constrained client-side (ADMIN sees only USER options; SUPERADMIN sees all)
- Server enforces the same constraint independently

### 7.4 Deactivate Confirmation Dialog

- Text: "Deactivating [email] will prevent login immediately. This can be reversed."
- Confirm button → `DELETE /api/v1/admin/users/{id}`

### 7.5 User Detail Page (`/admin/users/{id}`)

- Read-only summary card
- Role history log (if audit feature F-019 is live) or placeholder
- Action buttons: Edit Role · Deactivate · Restore

---

## 8. Backend Implementation Notes

### 8.1 Password Hashing

Use `bcrypt==4.0.1` (pinned, passlib incompatibility — locked decision). Hash at service layer, never store plaintext.

### 8.2 Permission Guard Pattern

Implement as FastAPI dependency:

```python
# deps/permissions.py
def require_role(*roles: str):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency

# Usage in router:
@router.get("/admin/users")
async def list_users(caller: User = Depends(require_role("admin", "superadmin"))):
    ...
```

### 8.3 SUPERADMIN Bootstrap Protection

```python
# services/user_service.py
async def deactivate_user(target_id: UUID, caller: User, db: AsyncSession):
    target = await db.get(User, target_id)
    if target.role == "superadmin":
        # Count remaining active superadmins
        count = await db.scalar(
            select(func.count()).where(User.role == "superadmin", User.is_active == True)
        )
        if count <= 1:
            raise HTTPException(409, "Cannot deactivate the only SUPERADMIN")
    ...
```

### 8.4 Monetary Values

Not applicable to this feature — no monetary data handled in user management.

### 8.5 Audit Event Emission

Every state-changing operation must emit an event to the audit log (structure TBD by F-019). Minimum payload:

```python
{
    "action": "user.deactivated | user.role_changed | user.created | user.restored",
    "actor_id": caller.id,
    "target_id": target.id,
    "timestamp": datetime.now(timezone.utc),
    "metadata": { "old_role": ..., "new_role": ... }  # where applicable
}
```

If F-019 is not yet implemented, write to application log at INFO level and store in a `pending_audit_events` table for replay.

---

## 9. Migration Strategy

### 9.1 Existing Users

All existing user rows default to `role = 'user'`, `is_active = TRUE`. This is safe — no existing session is invalidated.

### 9.2 Bootstrap SUPERADMIN

A one-time migration script sets the first user (lowest `created_at`) to `role = 'superadmin'`. This should be reviewed and confirmed manually before running in production.

```sql
-- migration: 0XX_add_roles_and_soft_delete.sql
UPDATE users
SET role = 'superadmin'
WHERE id = (SELECT id FROM users ORDER BY created_at ASC LIMIT 1);
```

### 9.3 Migration File Naming

Follow existing Alembic convention. Create: `0XX_add_user_roles_and_soft_delete.py`

---

## 10. Acceptance Criteria

These map to Gherkin scenarios to be written as AT-F016-001 through AT-F016-010.

| ID | Scenario | Expected Outcome |
|----|----------|-----------------|
| AT-F016-001 | SUPERADMIN lists all users | Returns paginated list including inactive |
| AT-F016-002 | ADMIN lists users | Returns list, excludes other ADMIN/SUPERADMIN edit capability |
| AT-F016-003 | USER accesses /admin/users | HTTP 403 |
| AT-F016-004 | ADMIN creates USER account | Account created, role = user |
| AT-F016-005 | ADMIN attempts to create ADMIN account | HTTP 403 |
| AT-F016-006 | SUPERADMIN promotes USER to ADMIN | Role updated, audit event emitted |
| AT-F016-007 | ADMIN deactivates USER | is_active = false, deactivated_at set |
| AT-F016-008 | ADMIN attempts to deactivate ADMIN | HTTP 403 |
| AT-F016-009 | Deactivate last SUPERADMIN | HTTP 409, no change |
| AT-F016-010 | Deactivated user attempts login | HTTP 401 |
| AT-F016-011 | ADMIN restores deactivated USER | is_active = true, deactivated_at = null |
| AT-F016-012 | User changes own display name | Updated, reflected on next /me call |
| AT-F016-013 | User changes own password with wrong current | HTTP 401 |

---

## 11. Dependencies

| Dependency | Direction | Notes |
|------------|-----------|-------|
| Phase 2 JWT auth (httpOnly cookies) | Required upstream | Already implemented |
| HO-024 Admin section restructure | Required upstream | Admin routes must exist |
| F-017 Portfolio Ownership | Downstream consumer | Uses `user_id` FK established here |
| F-019 Audit Log | Downstream consumer | Receives audit events from this feature |
| AT-004 | Testing dependency | Acceptance test for HO-024 must pass before F-016 routes integrate |

---

## 12. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| OQ-1 | Should deactivated users' portfolios be hidden or read-only? | Product (Zubbyik) | Open |
| OQ-2 | Is there a need for an invitation flow (email-based sign-up) vs admin-only creation? | Product | Open |
| OQ-3 | Should role changes require re-authentication on next request? | Architect | Recommend: no (JWT remains valid; role re-read from DB on each request) |

---

## 13. Handover Note

This spec is the **gate document** for all Phase 3C features. Before any F-017, F-018, F-019 or later implementation begins, confirm:

- [ ] F-016 API endpoints deployed and smoke-tested
- [ ] Migration applied to production DB (roles column + soft delete columns)
- [ ] SUPERADMIN bootstrap confirmed
- [ ] AT-F016-001 through AT-F016-013 passing

**Do not merge any Phase 3C feature branch until F-016 is green.**
