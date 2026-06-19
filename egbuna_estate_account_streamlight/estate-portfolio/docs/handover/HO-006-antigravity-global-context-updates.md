---
type: HO
id: HO-006
title: Antigravity → Claude: Global Governance & Wiki Alternative
date: 2026-05-06
from: Antigravity (Builder)
to: Claude (The Brain)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-006 — Antigravity → Claude: Global Governance & AT-002 Fixes
> **Type**: Handover · **Date**: 2026-05-08

## 1. What Was Done
- **Global Constraints Updated**: Modified `MASTER_CONTEXT.md`, `AGENTS.md`, and `GEMINI.md` at the root of `openagile` to embed the new EPM Governance SDLC/STLC rules. This ensures any agent reading these files is strictly constrained to use the `docs/` structure, `BR`/`ADR` prefixes, YAML frontmatter, and conventional commits.
- **Wiki Alternative Implemented**: Created `egbuna_estate_account_streamlight/estate-portfolio/docs/README.md` to serve as a markdown-native alternative to the GitHub Wiki.
- **AT-002 Bug Fixes Implemented**: Addressed all bugs and UI issues documented in `Spec_registrar_bug_fixes.md`:
  - UI Details: Added phone, email, and contact address to the left panel registrar list cards.
  - Backend Validation: Fixed the Add/Edit Registrar failure by explicitly setting `nullable=True` in the SQLAlchemy models and allowing `str | None` in the Pydantic schema.
  - Upload Logic: Added 20MB client-side validation, integrated XMLHttpRequest for upload progress tracking, and added state reset on file rejection.
  - Auth Downloads: Replaced standard `<a href>` downloads with authenticated `fetch` blob downloads.
  - State & Requirements: Replaced the Update Status modal with an inline status `<select>` dropdown (in Edit Mode) and added a Trash icon for bulk deleting a task group's requirements.
  - **Testing**: Generated the updated test record at `docs/testing/acceptance-tests/AT-002-registrars-v2-2026-05-08.md`.

## 2. What Is Verified Working
- All central context and agent files now reflect the new governance rules.
- The `docs/README.md` file correctly references all the generated placeholder and migrated specification documents.
- Registrar Document Management: Full CRUD on Registrars, Requirement groups, and Document Statuses correctly handles null values, permissions, and file edge-cases.

## 3. Decisions Taken
- **GitHub Wiki Limitation**: Realizing that GitHub disables the Wiki and Branch Protection features for private repositories on free personal accounts, I decided to abandon the GitHub Wiki UI approach.
- Instead, I implemented a native `docs/README.md` file. GitHub automatically renders the `README.md` when visiting the `docs/` folder in the web UI, effectively providing the exact same navigational experience as a Wiki without needing a paid account or public repo.
- **Task Group Deletion**: Rather than adding complex DB cascades for "task groups", clicking the trash icon iterates over the grouped requirements in the frontend and calls the standard `deleteRequirement.mutate()` endpoint.

## 4. Blockers
- **Branch Protection**: We cannot programmatically or manually enforce branch protection rules (like requiring PRs before merging to `main`) because of the free account limitations. We must rely entirely on agent discipline to follow the rule: "Never commit directly to main."

## 5. Next Agent's Action List
1. Acknowledge the updated global context, SDLC rules, and AT-002 bug fix implementations.
2. Proceed with the next phase of development (e.g., Holdings, Claims tracking) by creating the relevant `BR` and `TC` documents in the `docs/` folder first.
