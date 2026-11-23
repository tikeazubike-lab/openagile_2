---
type: HO
id: HO-157
title: Claude Web → OpenCode: Fix 000 baseline drift (JSON→JSONB, phantom dividends.holding_id), then finalize PR #10
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

## Housekeeping — HO numbering buffer extended

The HO-122–155 general-purpose buffer is exhausted as of HO-155. HO-156 is
reserved (Phase 3E checkpoint, do not use early) and is skipped. **New
block: HO-157–HO-200**, general-purpose, consumed in sequence. This
handover is HO-157. Note for the v4.11 MASTER_CONTEXT update: reflect this
extension in the Pre-assigned HO numbers table.

## Ruling on the two drift items — fix both, pre-merge

`000` has never reached `main`; this PR is its first real merge. There's no
existing history to reconcile against, so getting it accurate now is
correct rather than deferred.

**First, rule out deliberate intent** for each:
```
git log -p --all -- backend/alembic/versions/000_baseline_production_schema.py \
  | grep -B5 -A5 'dividends\|holding_id'
```
and the equivalent check for the 7 JSON columns. If nothing indicates
either was deliberate, proceed:

1. Convert the 7 flagged columns (`audit_logs.old_values`/`new_values`,
   `chatbot_conversations.extracted_entities`,
   `checklist_runs.results_json`, `communication_logs.tags`/`attachments`,
   `obsidian_sync_log.error_details`) from `sa.JSON()` to `sa.JSONB()`.
2. Remove `dividends.holding_id` from `000` — not present in production.
3. One commit, clearly labeled: `fix: correct 000 baseline drift —
   JSON→JSONB fidelity, remove phantom dividends.holding_id`.
4. Re-run the empty-DB test (`alembic upgrade head`, raw output) and the
   full `information_schema.columns` diff against production once more.
   Expected result this time: **zero diff**.
5. Sync `test` with this same fix.
6. Finalize PR #10's description to name all four things it now carries:
   F-026 dashboard/seed reconciliation, F-026b reminders, the
   disaster-recovery chain completion (HO-150–154), and this baseline
   fidelity correction.

## Status

PR #10 remains held until the re-run in step 4 shows a clean diff. Report
back via **HO-158**.
