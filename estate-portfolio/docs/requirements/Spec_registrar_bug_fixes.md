---
type: BR
id: EPM-REGISTRAR-BUG-FIXES-SPEC
title: Registrar Page Bug Fixes Spec
status: ARCHIVAL_REFERENCE
version: 1.0
updated: 2026-05-23
source_date: 2026-05-05
---

# Registrar Page — Bug Fixes Spec (AT-002 Follow-up)
**From**: Claude (The Brain)
**To**: Antigravity / Cursor (Builder)
**Date**: 2026-05-05
**Protocol**: MASTER_CONTEXT.md v4.0
**Source**: AT-002 Registrars Acceptance Test results
**Priority**: P1 — fix after governance structure is in place

---

## Issues Identified and Resolutions

### Issue 1 — Detail panel missing office address; phone not on left card

**AT result**: "Details incomplete, office address is missing. Phone number
should be visible in the card of the left panel."

**Fix — Left panel registrar card**:
```typescript
// Add phone number below company count badge
<div className="text-sm font-mono text-[var(--text-secondary)]">
  {registrar.phone ?? "No phone on record"}
</div>
```

**Fix — Detail panel**: Ensure `contact_address` field is displayed.
Check the API response includes it — if the field is in the DB model
but missing from the serialiser, add it to the GET /api/v1/registrars
response object.

---

### Issue 2 — Add / Edit registrar not saving (backend error, UI passed)

**AT result**: "Add registrar is not working, Edit registrar is not working
— Error in backend, UI passed."

**Diagnosis**: UI renders correctly but POST/PUT requests are failing.
Check server logs for the exact error:
```bash
docker compose logs epm_v2 --tail=50 | grep -i "registrar\|422\|500"
```

Common causes:
- Missing required field in Pydantic model (422 validation error)
- Missing `deleted_at` default in model (IntegrityError)
- `response_rating` field not nullable causing constraint failure on add

**Fix**: Add null handling for all optional fields in the registrar
Pydantic schema and SQLAlchemy model. Every field except `name` should
be optional on create.

---

### Issue 3 — Client-side file size validation missing

**AT result**: "200MB file took a long time before registering size error.
User could click back during that time."

**Fix — Frontend validation before upload**:
```typescript
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

const handleFileSelect = (file: File) => {
  if (file.size > MAX_FILE_SIZE) {
    // Show error immediately — no API call made
    setUploadError(`File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB. Maximum is 20MB.`);
    return;
  }
  // Only proceed to upload if size is valid
  uploadMutation.mutate(file);
};
```

Add this check in the file drop handler AND the file picker `onChange`.
The backend size check remains as the server-side guard — this is the
client-side guard that gives instant feedback.

Also add a progress bar for files between 5MB and 20MB:
```typescript
// Use XMLHttpRequest instead of fetch for upload progress tracking
const xhr = new XMLHttpRequest();
xhr.upload.addEventListener('progress', (e) => {
  if (e.lengthComputable) {
    setUploadProgress(Math.round((e.loaded / e.total) * 100));
  }
});
```

---

### Issue 4 — Cannot remove failed upload from initial phase

**AT result**: "After uploading an invalid file type, I cannot remove the
initial phase before uploading the invalid file type — unused document in
initial phase."

**Fix**: When a file is rejected (wrong type or too large), the UI must
reset the drop zone to its initial empty state. Do not leave the filename
displayed. Add a clear button or auto-reset after error:

```typescript
const handleFileReject = (reason: string) => {
  setUploadError(reason);
  setSelectedFile(null);        // clear the file reference
  setUploadProgress(null);      // clear any progress state
  // Drop zone returns to initial state automatically
};
```

---

### Issue 5 — "Download with auth" — clarification

**AT question**: "What do you mean by 'with auth'?"

**Answer**: The download endpoint requires the user to be logged in.
The `epm_token` httpOnly cookie is sent automatically with every request
that uses `credentials: 'include'`. This means:
- Logged-in users: download works transparently
- Logged-out users: get a 401 response

**Implementation**: Do not use a plain `<a href>` anchor for downloads —
it won't send the cookie. Use a fetch call or an anchor with a click
handler that fires the authenticated request:

```typescript
const handleDownload = async (docId: number, fileName: string) => {
  const response = await fetch(`/api/v1/registrar-documents/${docId}/download`, {
    credentials: 'include',
  });
  if (!response.ok) {
    toast.error('Download failed — please log in again');
    return;
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
};
```

---

### Issue 6 — Status badge: what does "submitted" mean + how to change it

**AT question**: "What does submitted mean? How can the colour of the badge
be changed?"

**Answer — Status meanings**:
| Status | Meaning | Colour |
|--------|---------|--------|
| `pending` | Document uploaded, not yet sent to registrar | 🟡 Amber |
| `submitted` | You have physically/digitally sent it to the registrar | 🔵 Blue |
| `completed` | Registrar confirmed receipt / task resolved | 🟢 Green |
| `rejected` | Registrar rejected the document, re-upload needed | 🔴 Red |

**Answer — How to change it**:
In Edit Mode, each document row should have a status dropdown:
```typescript
// In the document row (editMode only):
<select
  value={doc.status}
  onChange={(e) => updateStatusMutation.mutate({
    docId: doc.id,
    status: e.target.value
  })}
>
  <option value="pending">Pending</option>
  <option value="submitted">Submitted to registrar</option>
  <option value="completed">Completed</option>
  <option value="rejected">Rejected — re-upload needed</option>
</select>
```

The status dropdown should only be visible in Edit Mode (admin).
In View Mode, show the badge only (not editable).

**Automation note from AT**: "If any workflow within the requirement is
changed, it should reflect on the status badge."

Good observation. The status should automatically update to `submitted`
when the user marks a requirement as submitted — but this is Phase 3C
scope. For now, manual status change via dropdown is sufficient.

---

### Issue 7 — Cannot delete main category (task group)

**AT result**: "Can't delete the main category."

**Fix**: The task group header (task_name accordion) needs a delete
button in Edit Mode. This deletes the `registrar_requirement` row
(soft delete — sets `deleted_at`). All associated documents are also
soft-deleted via CASCADE.

Add to the accordion header (Edit Mode only):
```typescript
{isAdmin() && editMode && (
  <button
    onClick={() => deleteRequirementMutation.mutate(requirement.id)}
    className="text-[var(--accent-red)] hover:opacity-80"
    title="Delete this requirement"
  >
    <Trash2 size={14} />
  </button>
)}
```

Show a confirmation dialog before deleting — requirements with uploaded
documents should warn: "This will also remove N uploaded documents.
Are you sure?"

---

### Issue 8 — Linked companies not rendered (expected — Companies page pending)

**AT result**: "Linked companies are not rendered yet because Companies
page doesn't exist yet."

**Status**: Expected and acceptable. The company pill links are correct
in the spec — they will work once the Companies page is built.
No fix needed now. Mark as deferred to Companies page sprint.

---

## Acceptance Test Update (AT-002)

After implementing fixes 1–7 above, update `AT-002` with results.
Use the new document naming convention: `AT-002-registrars-v2-YYYY-MM-DD.md`
The original AT-002 is kept as a historical record — do not overwrite it.

---

## Commit Message

```
fix(registrars): address AT-002 issues — address display, upload UX,
status dropdown, delete requirement

- Add phone to left panel card
- Fix contact_address in detail panel
- Add client-side 20MB file size guard
- Add upload progress bar for large files
- Reset drop zone state after file rejection
- Add status dropdown (editMode) for document status changes
- Add delete button for requirement groups (editMode)
- Fix authenticated download via fetch + createObjectURL
```

Push to `test` branch after all fixes.
Write HO-006 handover to Claude with AT-002 v2 results.
