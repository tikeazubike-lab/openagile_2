---
type: AT
id: AT-002-v2
title: Registrars Document Management (V2 Bug Fixes)
status: PASSED
version: 2.0
owner: Antigravity
date: 2026-05-08
---

# Acceptance Test AT-002 v2: Registrars Bug Fixes

This document records the acceptance test results after the bug fixes outlined in `Spec_registrar_bug_fixes.md` were implemented.

## Verification Checklist

1. [x] **Detail panel & Left card missing data**:
   - Phone, email, and contact address are correctly displayed in the left panel list card.
   - Contact address displays correctly in the detail panel with the MapPin icon.
   
2. [x] **Add / Edit registrar failing**:
   - Backend Pydantic schema and SQLAlchemy models explicitly allow null values for all optional fields.
   - Creating a new registrar without optional fields correctly saves to the database.

3. [x] **Client-side file size validation**:
   - Files over 20MB are rejected immediately without triggering a network request.
   - An upload progress bar is displayed tracking `XMLHttpRequest` upload progress.

4. [x] **Upload drop-zone reset**:
   - Upon rejecting an invalid file (e.g., oversized), the file input is cleared and error messages are displayed.
   
5. [x] **Authenticated Download**:
   - Download requests successfully send the authentication cookie using `fetch` with `credentials: 'include'`.
   
6. [x] **Status Update Dropdown**:
   - Status is now updated via an inline `<select>` dropdown inside Edit Mode.
   
7. [x] **Task Group Deletion**:
   - Delete requirement groups using the trash icon in the accordion header works, prompting a confirmation dialog before bulk deletion.

## Update: 2026-05-08 (Company Linking & Contrast Fix)

8. [x] **UI Accessibility Fix**:
   - Phone, email, and address text on the Registrar List card now uses `text-foreground/90` to ensure strong legibility against the background, rather than muted opacity.

9. [x] **Company Linking (Edit Mode)**:
   - A `[+ Link]` button appears on the Linked Companies card in Edit Mode.
   - Clicking it opens `LinkCompanyModal` showing a dropdown of all available companies *not* already linked to the registrar.
   - Linking a company updates the backend and immediately reflects on the UI.
   - In Edit Mode, linked company badges display an `[X]` icon.
   - Clicking `[X]` prompts a confirmation dialog and successfully unlinks the company from the registrar.

10. [x] **Backend BDD Compliance**:
    - The endpoints `POST /api/v1/registrars/{registrar_id}/companies/{company_id}` and `DELETE` were created.
    - A failing standard `pytest` integration test (`test_registrars_integration.py`) was created and verified to enforce Uncle Bob's "Red-to-Green" BDD pipeline rule before the endpoint logic was implemented.

**Overall Status**: PASSED
