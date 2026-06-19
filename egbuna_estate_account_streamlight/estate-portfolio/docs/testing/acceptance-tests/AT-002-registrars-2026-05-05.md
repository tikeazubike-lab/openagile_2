---
type: AT
id: AT-002
title: Registrars Acceptance Test
status: COMPLETE
date: 2026-05-05
tester: Antigravity
environment: testdrive.epm.zubbystudio.shop
branch: test
feature: [BR-005]
---

# [AT] AT-002 — Registrars Acceptance Test Results
> **Type**: Acceptance Test · **Date**: 2026-05-05 · **Branch**: test

## Registrars Page — Acceptance Test

### CRUD
- [x] Registrar list renders with company count + pending doc badges
- [fail] Selecting a registrar loads detail panel -> Details incomplete, office address is missing. The phone number should be visible in the card of the left panel
- [x] Add registrar (admin, editMode) → appears in left list -> Error : add registrar is not working, UI -> passed
- [x] Edit registrar details → changes persist -> Error : edit registrar is not working, UI -> passed
- [skip] Linked companies render as clickable lavender pills -> Error : linked companies are not rendered yet(Because companies page doesn't exist yet), UI 

### Requirements
- [x] Requirements grouped by task_name (accordion)
- [x] Add Requirement → appears in correct task group
- [x] Required vs optional distinction visible
- [pending] Status badges render with correct colours -> todo: what does submitted mean? and how can the colour of the badge be changed? -> not fully tested, but the icon is working (will need to add some automation to it, so that if any workflow within the requirement is changed, it will reflect on the status badge)

### Document Upload
- [pending] Upload PDF → appears in requirement row -> Would want to be able to change the requirement once a document has been uploaded[passed], the requirement description should be editable[passed]. Has not been comprehensively tested but so far is working, I think.
- [x] Upload JPG → accepted
- [x] Upload .exe or unsupported type → rejected with error (but now i cannot remove the initial phase before uploading the invalid file type, so I have unused document on the initial phase)
- [x] File > 20MB → rejected with size error -> Error: file > 20MB, size error  but sizes from 200mb took longer time trying to upload, should there not be a something from the client side to truncate the upload or something with error of "file size is too large" or a progress bar before it even gets to the server, because it took a long time for the 200mb file to even register as an error, the user could have clicked the back button or something during that time. -> This has been fixed and is working properly now.
- [pending] Download link retrieves correct file (with auth) -> what do you mean by "with auth"?
- [skipped] Unauthenticated download attempt → 401 -> not possible to get to the /registrars page without being logged in, so this check is not possible.
- [x] Upload second version → history shows both, latest shown by default -> Cannot edit requirement description and also upload a new file for the same requirement, it would mean i have to create another requirement, and a duplicate document would be created which would clutter the page with unused documents. -> fixed
- [pending] Show history → all versions listed with dates -> Error: Not possible same reason as above
- [x] Soft delete document → disappears from row (file kept on volume) -> but cant delete the main category

### Status Updates
- [x] Change status to "submitted" → badge updates -> Cannot do it because after submission of the requirement, i cannot edit it anymore. It turns to view/read-only mode. -> fixed
- [x] Change status to "completed" → badge updates green -> Cannot do it because after submission of the requirement, i cannot edit it anymore. It turns to view/read-only mode.
- [x] Status change reflected in pending doc count on left panel

### Access Control
- [skipped] Readonly user: can view requirements and download files -> Have not created readonly user yet. Will get to that when we are able to work on the /settings/users features
- [skipped] Readonly user: no Upload, Add Requirement, or Edit buttons visible -> Have not created readonly user yet. Will get to that when we are able to work on the /settings/users features
