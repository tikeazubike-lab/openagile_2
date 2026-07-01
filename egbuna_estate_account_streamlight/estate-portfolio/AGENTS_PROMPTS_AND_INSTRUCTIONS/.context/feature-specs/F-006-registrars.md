---
id: F-006
title: Registrars
status: COMPLETE
owner-backend: Antigravity
owner-frontend: Deepseek v4
sprint: Phase 3B (complete)
---

# F-006 — Registrars

## Goal
Manage registrar relationships including contact details (multiple phones,
emails, etc.), document requirements per task type, uploaded document files,
and linked companies. All document uploads are auth-gated and version-tracked.

## What Is Built

Backend (backend/app/routers/registrars.py — 579 lines):
  GET    /api/v1/registrars                              — list with counts
  POST   /api/v1/registrars                              — create
  PUT    /api/v1/registrars/{id}                         — update + contact_fields
  DELETE /api/v1/registrars/{id}                         — soft delete
  POST   /api/v1/registrars/{id}/companies/{company_id}  — link company
  DELETE /api/v1/registrars/{id}/companies/{company_id}  — unlink company
  GET    /api/v1/registrars/{id}/requirements            — list grouped by task
  POST   /api/v1/registrars/{id}/requirements            — create requirement
  PUT    /api/v1/registrar-requirements/{id}             — update requirement
  DELETE /api/v1/registrar-requirements/{id}             — soft delete requirement
  POST   /api/v1/registrar-requirements/{req_id}/documents  — upload file
  GET    /api/v1/registrar-documents/{id}/download       — auth-gated download
  PUT    /api/v1/registrar-documents/{id}/status         — update doc status
  DELETE /api/v1/registrar-documents/{id}                — soft delete doc
  GET    /api/v1/registrar-documents/{req_id}/history    — version history

Database tables:
  registrars, registrar_contact_fields, registrar_requirements, registrar_documents

Frontend:
  src/routes/_app.registrars.tsx
  src/components/registrars/RegistrarModal.tsx  (Edit + Add — same component)
  src/components/registrars/RegistrarDetails.tsx

## Extended Contact Fields

registrar_contact_fields table:
  id, registrar_id, field_type, field_value, label, sort_order, deleted_at

field_type enum: phone | email | address | website | other

Add/Edit modal shows predefined type selector when [+ Add Field] clicked.
Grid layout for fields: 80px (type badge) | 1fr (input) | 32px (× button)
NOT flex-wrap — this caused the "horrible layout" complaint in AT-002.

## Document Storage

Volume mount: ./uploads:/app/uploads
Path pattern: uploads/registrar_documents/{registrar_id}/{req_id}/{timestamp}_{filename}
Allowed types: PDF, JPG, PNG (magic-byte validation + MIME type)
Max size: 20MB (client-side guard FIRST, then server-side)
Download: always via authenticated endpoint — never direct path

## Document Status Lifecycle

pending → submitted → completed
            ↓
          rejected → (re-upload → pending)

Status only editable in edit mode (admin).
Status change reflected in pending_document_count on left panel.

## Document Versioning

Multiple uploads per requirement = multiple registrar_documents rows.
Latest shown by default (ordered by uploaded_at DESC).
[Show history ▼] expander shows all versions with dates.
Soft delete hides from view but keeps file on volume (audit trail).

## Page Layout

Two-panel layout:

LEFT PANEL (280px):
  "Registrars" heading + [+ Add Registrar] button (edit mode, admin)
  Per registrar card (clickable):
    Registrar name (bold)
    Phone number (visible on card — not just in detail)
    "N companies · N pending docs" (amber badge if pending > 0)
    Response rating stars

RIGHT PANEL:
  When none selected: "Select a registrar to view details"
  When selected:
    Header: [Registrar Name] [Edit Registrar] [Delete] (edit mode, admin)
    Contact details card: email, phone, address, rating, extended fields
    Linked Companies card: lavender pills (clickable when Companies page exists)
    Requirements & Documents accordion grouped by task_name

## Requirements Accordion

Grouped by task_name (e.g. "Unclaimed Dividend Claim", "Dematerialisation"):
  Each group is an accordion section
  Inside: table of required documents with upload/status per row

Common task_name presets (dropdown in Add Requirement form):
  Unclaimed Dividend Claim | Dematerialisation (CSCS) |
  Share Certificate Digitisation | KYC Update |
  Account Reactivation | Delisted Company Claim | Other

## Document Row Actions

No file uploaded:
  [↑ Upload] button → file picker (PDF/JPG/PNG, 20MB)

File uploaded:
  filename.pdf (2.4MB) [↓ Download] [✕ Remove]
  Status dropdown (edit mode): pending | submitted | completed | rejected
  [Show history ▼] if multiple versions

Download implementation (authenticated):
  handleDownload = async (docId, fileName) => {
    const res = await fetch(`/api/v1/registrar-documents/${docId}/download`,
      { credentials: 'include' })
    const blob = await res.blob()
    // create object URL + click anchor
  }
  NEVER use plain <a href> — cookie not sent without credentials:'include'

## Acceptance Checklist

### [DB]
- [ ] registrar_contact_fields table exists with correct columns
- [ ] registrar_requirements table exists
- [ ] registrar_documents table exists
- [ ] All tables have deleted_at (soft delete)

### [API]
- [ ] GET /api/v1/registrars includes contact_fields array per registrar
- [ ] POST /api/v1/registrars/{id}/companies/{id} → 200 (not 405)
- [ ] DELETE link endpoint → 200, company removed
- [ ] File upload (PDF) → 200, file saved to volume
- [ ] File download → file returned with correct Content-Type
- [ ] Unauthenticated download → 401
- [ ] File > 20MB → 422
- [ ] Wrong file type → 422

### [UI]
- [ ] Left panel shows registrar list with phone + pending count
- [ ] Selecting registrar loads detail panel
- [ ] Edit modal is centered on screen (fixed inset-0 flex items-center)
- [ ] [+ Add Field] shows type selector: phone, email, address, website, other
- [ ] Extra fields render in 3-column grid (not flex-wrap)
- [ ] [Delete] button visible next to [Edit Registrar] in edit mode
- [ ] Delete confirmation mentions linked company count if applicable
- [ ] Link company → 200 → appears in Linked Companies card
- [ ] Upload PDF → appears in document row with status badge
- [ ] Download → file opens/downloads in browser
- [ ] [Show history ▼] shows all document versions
- [ ] Status dropdown changes badge colour
- [ ] Soft delete document → disappears from row
- [ ] Readonly user: can view and download, no upload/edit controls

## Sign-Off
- [x] All checklist items verified (AT-002 + AT-003-1)
- [x] No open bugs
