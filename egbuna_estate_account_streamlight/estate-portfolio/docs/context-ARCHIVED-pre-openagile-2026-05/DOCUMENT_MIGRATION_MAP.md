---
type: CONTEXT
id: EPM-DOCUMENT-MIGRATION-MAP
title: EPM Documentation Migration Map
status: PARTIALLY_IMPLEMENTED
version: 1.0
created: 2026-05-23
scope: egbuna_estate_account_streamlight/estate-portfolio
---

# EPM Documentation Migration Map

This map records both proposed and implemented documentation cleanup work for
EPM. The first archive-only pass was implemented on 2026-05-23.

## Decisions Already Confirmed

- Root-level workspace files stay where they are.
- EPM docs may reference root files when they are relevant to this project.
- Redundant EPM-local documents and openagile's[parent's] documents  should be archived under `docs/archive/`, not
  deleted, for each of the mentioned folders [EPM-local folder, openagile's parent's folder and other subfolders]
- Each subproject should maintain its own context engine under its own `docs/`.

## Proposed Context Engine

| New file | Purpose |
|---|---|
| `docs/context/MASTER_CONTEXT.md` | EPM-local operating contract. |
| `docs/context/AGENT_STATE.yaml` | Current agent roles, scope, and task state. |
| `docs/context/DELEGATION_REGISTRY.md` | File ownership and collaboration rules. |
| `docs/context/WORKFLOW.md` | EPM-local agentic workflow and verification rules. |
| `docs/context/DOCUMENT_MIGRATION_MAP.md` | This migration proposal. |

## Root Files To Reference In Place

| Root file | Proposed EPM reference | Action |
|---|---|---|
| `/HO-018-claude-to-both-agents.md` | `docs/handover/HO-018-claude-to-both-agents.md` and amendment `docs/handover/HO-018-1-claude-to-deepseek-antigravity-grok.md` | MOVED |
| `/AT-003-1-followup-test.md` | `docs/testing/acceptance-tests/AT-003-1-followup-test.md` | MOVED |
| `/DEEPSEEK_CONTEXT.md` | `docs/archive/2026-05-23-root-cleanup/root-context/DEEPSEEK_CONTEXT.md` | ARCHIVED; current rules extracted into context engine |
| `/HO-016-antigravity-to-claude.md` | `docs/handover/HO-016-antigravity-to-claude.md` | MOVED |
| `/At-003-dashboard-holdings-registrars-pricehist.md` | `docs/testing/acceptance-tests/AT-003-dashboard-holdings-registrars-pricehist-root-copy.md` | MOVED |

## EPM Root Docs Cleanup Status

| Current file | Destination | Status | Reason |
|---|---|---|---|
| `ESTATE_PORTFOLIO_FINAL_HANDOVER.md` | `docs/archive/2026-05-23-root-cleanup/ESTATE_PORTFOLIO_FINAL_HANDOVER.md` | IMPLEMENTED | Superseded Phase 2 handover; useful history but no longer current. |
| `GEMINI.md` | `docs/archive/2026-05-23-root-cleanup/GEMINI-legacy-streamlit-context.md` | IMPLEMENTED | Legacy Streamlit deployment context; not current EPM v2 workflow. |
| `CI_CD_SETUP.md` | `docs/archive/2026-05-23-root-cleanup/CI_CD_SETUP-legacy.md` | IMPLEMENTED | Historical CI/CD notes; current rules live in context/onboarding. |
| `Urgent_eodhd_fix.md` | `docs/archive/2026-05-23-root-cleanup/Urgent_eodhd_fix.md` | IMPLEMENTED | Issue-specific note retained for traceability. |
| `acceptance_test.md` | `docs/testing/acceptance-tests/legacy-acceptance-test.md` | IMPLEMENTED | Test docs belong under `docs/testing/acceptance-tests/`. |
| `epm_ui_acceptance_tests.feature` | `docs/testing/features/epm_ui_acceptance_tests.feature` | IMPLEMENTED | Gherkin specs belong under testing. |
| `epm_ui_acceptance_tests2.feature` | `docs/testing/features/epm_ui_acceptance_tests2.feature` | IMPLEMENTED | Gherkin specs belong under testing. |
| `features/batch_upload.feature` | `docs/testing/features/batch_upload.feature` | IMPLEMENTED | Feature specs belong under testing. |
| `project_artifact/Estate_Portfolio_Project_Report.md` | `docs/archive/2026-05-23-root-cleanup/Estate_Portfolio_Project_Report.md` | IMPLEMENTED | Project report is historical. |
| Root `docs/BR001_GHERKIN_SPEC.md` | `docs/testing/features/BR001_GHERKIN_SPEC.md` | IMPLEMENTED | EPM-specific Gherkin reference belonged in EPM testing docs. |
| Root `docs/br001_gherkin_pipeline.svg` | `docs/testing/features/br001_gherkin_pipeline.svg` | IMPLEMENTED | Companion EPM testing diagram belonged with the spec. |
| `/Ho-009-dashboard-holdings-registrars-pricelist.md` | `docs/handover/HO-009-dashboard-holdings-registrars-pricelist.md` | IMPLEMENTED | EPM handover belongs under handover docs. |
| `/Ho-011-claude-to-ntigravity.md` | `docs/handover/HO-011-claude-to-antigravity.md` | IMPLEMENTED | EPM handover moved and typo normalized. |
| `/Ho-013-claude-to-antigravity.md` | `docs/handover/HO-013-claude-to-antigravity.md` | IMPLEMENTED | EPM handover belongs under handover docs. |
| `/Ho-014-antigravity-to-claude.md` | `docs/handover/HO-014-antigravity-to-claude.md` | IMPLEMENTED | EPM handover belongs under handover docs. |
| `/HO-015-claude-to-antigravity.md` | `docs/handover/HO-015-claude-to-antigravity.md` | IMPLEMENTED | EPM handover belongs under handover docs. |
| `/HO-017-antigravity-to-claude.md` | `docs/handover/HO-017-antigravity-to-claude.md` | IMPLEMENTED | EPM handover belongs under handover docs. |
| `/Claude_price_entry_final_spec.md` | `docs/requirements/Claude_price_entry_final_spec.md` | IMPLEMENTED | EPM spec belongs under requirements docs. |
| `/Spec_registrar_bug_fixes.md` | `docs/requirements/Spec_registrar_bug_fixes.md` | IMPLEMENTED | EPM spec belongs under requirements docs. |
| `/PROJECT_STATUS.md` | `docs/context/PROJECT_STATUS.md` | IMPLEMENTED | EPM status board belongs under EPM context. |
| `/claude_handover_report.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/claude_handover_report.md` | IMPLEMENTED | Historical EPM root handover archived. |
| `/handover_from_antigravity.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/handover_from_antigravity.md` | IMPLEMENTED | Historical EPM root handover archived. |
| `/handover_from_codex_to_claude_antigravity_and_grok.md` | `docs/archive/2026-05-23-root-cleanup/root-handovers/handover_from_codex_to_claude_antigravity_and_grok.md` | IMPLEMENTED | Historical EPM root handover archived. |
| `/general.mdc` | `docs/archive/2026-05-23-root-cleanup/root-context/general.mdc` | IMPLEMENTED | Legacy EPM Cursor rule archived; current rules live in context engine. |

## EPM Root Non-Doc Files Proposed For Cleanup Review

These are not documentation files, so they need extra caution before any move.

| Current file | Proposed action | Reason |
|---|---|---|
| `temp_daily.txt` | Archive or delete after explicit approval | Temporary parser artifact. |
| `temp_prices1.txt` | Archive or delete after explicit approval | Temporary parser artifact. |
| `temp_prices2.txt` | Archive or delete after explicit approval | Temporary parser artifact. |
| `test_pdf.py` through `test_pdf8.py` | Move to `scripts/dev/` or archive after review | Experimental parser scripts; not structured tests. |
| `test_regex.py` through `test_regex3.py` | Move to `scripts/dev/` or archive after review | Experimental parser scripts. |
| `extract_tickers.py`, `extract_tickers_from_txt.py` | Keep or move to `scripts/dev/` after review | Utility scripts may still be useful. |
| `tickers.txt`, `ngx_companies_list.txt` | Keep until data import flow is clarified | May be seed/source data. |

## Implemented Archive Pass

Archive index:

```text
docs/archive/2026-05-23-root-cleanup/INDEX.md
```

## Proposed Next Step

1. Review non-doc temp/parser files before any archive or delete action.
2. Decide whether `CHANGELOG.md`, `CONTRIBUTING.md`, and `.github/` should
   remain at project root as conventional repository files.
3. Decide whether legacy Streamlit code should remain active or be clearly
   marked as legacy in a future architecture note.
4. Leave root workspace files untouched unless explicitly approved.
