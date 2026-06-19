---
type: ARCHIVE
id: EPM-ARCHIVE-2026-05-23-ROOT-CLEANUP
title: EPM Root Cleanup Archive Index
status: ACTIVE
version: 1.0
updated: 2026-05-23
---

# EPM Root Cleanup Archive Index

This archive preserves historical EPM project documents that were previously
scattered in the EPM project root. Files were moved here instead of deleted.

## Archived Files

| Original path | Archived path | Reason |
|---|---|---|
| `ESTATE_PORTFOLIO_FINAL_HANDOVER.md` | `docs/archive/2026-05-23-root-cleanup/ESTATE_PORTFOLIO_FINAL_HANDOVER.md` | Superseded Phase 2 handover; useful history. |
| `GEMINI.md` | `docs/archive/2026-05-23-root-cleanup/GEMINI-legacy-streamlit-context.md` | Legacy Streamlit-era context; conflicts with current EPM v2 workflow if treated as current. |
| `CI_CD_SETUP.md` | `docs/archive/2026-05-23-root-cleanup/CI_CD_SETUP-legacy.md` | Historical CI/CD setup notes; current routing lives in context/onboarding. |
| `Urgent_eodhd_fix.md` | `docs/archive/2026-05-23-root-cleanup/Urgent_eodhd_fix.md` | Issue-specific note retained for traceability. |
| `project_artifact/Estate_Portfolio_Project_Report.md` | `docs/archive/2026-05-23-root-cleanup/Estate_Portfolio_Project_Report.md` | Historical project report. |
| Root `DEEPSEEK_CONTEXT.md` | `docs/archive/2026-05-23-root-cleanup/root-context/DEEPSEEK_CONTEXT.md` | Superseded by current context engine. |
| Root `general.mdc` | `docs/archive/2026-05-23-root-cleanup/root-context/general.mdc` | Legacy Cursor rule archived; current rules live in context engine. |
| Root `claude_handover_report.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/claude_handover_report.md` | Historical root handover. |
| Root `handover_from_antigravity.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/handover_from_antigravity.md` | Historical root handover. |
| Root `handover_from_codex_to_claude_antigravity_and_grok.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/handover_from_codex_to_claude_antigravity_and_grok.md` | Historical root handover. |

## Files Moved To Structured Testing Docs

| Original path | New path | Reason |
|---|---|---|
| `acceptance_test.md` | `docs/testing/acceptance-tests/legacy-acceptance-test.md` | Acceptance tests belong under testing docs. |
| `epm_ui_acceptance_tests.feature` | `docs/testing/features/epm_ui_acceptance_tests.feature` | Gherkin specs belong under testing docs. |
| `epm_ui_acceptance_tests2.feature` | `docs/testing/features/epm_ui_acceptance_tests2.feature` | Gherkin specs belong under testing docs. |
| `features/batch_upload.feature` | `docs/testing/features/batch_upload.feature` | Feature specs belong under testing docs. |
| Root `AT-003-1-followup-test.md` | `docs/testing/acceptance-tests/AT-003-1-followup-test.md` | EPM acceptance test belongs under testing docs. |
| Root `At-003-dashboard-holdings-registrars-pricehist.md` | `docs/testing/acceptance-tests/AT-003-dashboard-holdings-registrars-pricehist-root-copy.md` | EPM acceptance test copy moved from root. |
| Root `Ho-009-dashboard-holdings-registrars-pricelist.md` | `docs/handover/HO-009-dashboard-holdings-registrars-pricelist.md` | EPM handover belongs under handover docs. |
| Root `Ho-011-claude-to-ntigravity.md` | `docs/handover/HO-011-claude-to-antigravity.md` | EPM handover moved and typo normalized. |
| Root `Ho-013-claude-to-antigravity.md` | `docs/handover/HO-013-claude-to-antigravity.md` | EPM handover belongs under handover docs. |
| Root `Ho-014-antigravity-to-claude.md` | `docs/handover/HO-014-antigravity-to-claude.md` | EPM handover belongs under handover docs. |
| Root `HO-015-claude-to-antigravity.md` | `docs/handover/HO-015-claude-to-antigravity.md` | EPM handover belongs under handover docs. |
| Root `HO-016-antigravity-to-claude.md` | `docs/handover/HO-016-antigravity-to-claude.md` | EPM handover belongs under handover docs. |
| Root `HO-017-antigravity-to-claude.md` | `docs/handover/HO-017-antigravity-to-claude.md` | EPM handover belongs under handover docs. |
| Root `HO-018-claude-to-both-agents.md` | `docs/handover/HO-018-claude-to-both-agents.md` | EPM handover belongs under handover docs. |
| Root `Claude_price_entry_final_spec.md` | `docs/requirements/Claude_price_entry_final_spec.md` | EPM spec belongs under requirements docs. |
| Root `Spec_registrar_bug_fixes.md` | `docs/requirements/Spec_registrar_bug_fixes.md` | EPM spec belongs under requirements docs. |
| Root `PROJECT_STATUS.md` | `docs/context/PROJECT_STATUS.md` | EPM status board belongs under context docs. |

## Not Touched In This Pass

- Root workspace files such as `/HO-018-claude-to-both-agents.md`.
- EPM non-doc temp files and parser experiments.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`.
- `NigerianStocks/` docs and data files.
