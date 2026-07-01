---
id: F-XXX
title: [Feature Name]
status: PLANNED
owner-backend: [Agent]
owner-frontend: [Agent]
sprint: [Phase X]
test-domain: [DOMAIN code from taxonomy]
---

# F-XXX — [Feature Name]

## Goal
[One sentence: what does this produce when complete?]

## Dependencies
- [F-YYY must be complete first — reason]
- [Package: scipy==1.13.1 must be in requirements.txt — reason]

## Backend

Router: backend/app/routers/[name].py
Endpoints:
  GET    /api/v1/[resource]              — [description] — all authenticated
  POST   /api/v1/[resource]              — [description] — admin only
  PATCH  /api/v1/[resource]/{id}         — [description] — admin only
  DELETE /api/v1/[resource]/{id}         — [description] — admin only, soft delete

Model: [ModelName] in backend/app/models.py
Migration: yes | no

## Frontend

Route: src/routes/_app.[name].tsx
Admin route (if applicable): src/routes/_app.admin.[name].tsx
Components:
  - src/components/[domain]/[ComponentName].tsx
Hooks: use[Name](), useCreate[Name]() in src/api/queries.ts

## API Response Shape

GET /api/v1/[resource]:
```json
{
  "data": [
    {
      "id": 1,
      "field_name": "value",
      "monetary_field": "12345.00",
      "created_at": "2026-05-18T18:00:00Z"
    }
  ],
  "meta": { "total": 1 },
  "error": null
}
```

POST /api/v1/[resource] request:
```json
{
  "field_name": "value",
  "monetary_field": "12345.00"
}
```

## Layout

[Describe the page top to bottom, left to right.
Be specific enough that two agents produce the same UI.]

Header: "[Page Title]" + [action button if admin]

Main content:
  [Table / Chart / Form description]

Empty state (no data):
  [Exact message and icon]

## Read-Only vs Admin View

All authenticated users see: [list what everyone sees]
Admin additionally sees: [list admin-only controls]
Read-only users cannot see: [list hidden elements]
Hidden from read-only entirely: [yes/no — does the page appear in their nav?]

## Acceptance Checklist

### [DB] Database
- [ ] [DB] Table exists with correct columns after migration
- [ ] [DB] Soft delete sets deleted_at, does not hard delete
- [ ] [DB] Monetary columns are Decimal type (not float)
- [ ] [DB] After create: row visible with correct field values
- [ ] [DB] After delete: row has deleted_at timestamp, not removed

### [API] Contract
- [ ] [API] GET /api/v1/[resource] → 200, data is array
- [ ] [API] GET without auth → 401
- [ ] [API] POST with valid payload → 201
- [ ] [API] POST without admin → 403
- [ ] [API] POST with invalid payload → 422
- [ ] [API] PATCH → 200, record updated
- [ ] [API] DELETE → 200, soft delete only
- [ ] [API] Monetary fields are JSON strings (not floats)
- [ ] [API] Null fields return null (not missing from response)

### [UI] Interface
- [ ] [UI] Page loads without crash or console errors
- [ ] [UI] Data renders from API (not mock/hardcoded)
- [ ] [UI] Empty state shows message + icon (not blank page)
- [ ] [UI] Loading state visible while data fetches
- [ ] [UI] Admin controls visible to admin, hidden to read-only
- [ ] [UI] Monetary values display in DM Mono font
- [ ] [UI] After mutation: related queries invalidated (dashboard refreshes)
- [ ] [UI] Read-only user: page accessible | not accessible [choose one]

## Test IDs (from Taxonomy)

Backend unit:        [DOMAIN]-[WORKFLOW]-BE-UT-001
Backend integration: [DOMAIN]-[WORKFLOW]-BE-INT-001
Backend contract:    [DOMAIN]-[WORKFLOW]-BE-API-001
Frontend E2E:        [DOMAIN]-[WORKFLOW]-FE-E2E-001

Requirement ref:     REQ-[DOMAIN]-001

## Sign-Off

- [ ] All [DB] checklist items passing
- [ ] All [API] checklist items passing
- [ ] All [UI] checklist items passing
- [ ] .context/progress-tracker.md updated to COMPLETE
- [ ] HO-XXX.md filed in docs/handovers/
- [ ] AT-XXX.md filed in docs/testing/acceptance/
- [ ] Commit: feat([domain]): implement F-XXX [feature-name]
