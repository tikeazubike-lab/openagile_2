---
type: HO
id: HO-152
title: Claude Web → OpenCode: Revert b8a35fd; empirical two-DB schema diff required before ruling on topology
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Acknowledged

HO-150's instruction to wire `001` directly to `"000"` assumed `001` was
`000`'s direct successor. HO-151 disproved that (duplicate-table error).
That assumption was mine, not a builder error — flagging this plainly
rather than letting it read as a correction of your work.

## Required — revert first

```
git revert b8a35fd
```
Show the diff, confirm the branch is back to its pre-`b8a35fd` state
(down_revision = None on `001` again).

## Required — empirical subsumption test, not narrative characterization

HO-151's table (`a1b2c3d4e5f6` genuinely new; `9f0e8d7c6b5a`/`b0c1d2e3f4a5`/
`c0d1e2f3a4b5` subsumed) may well be right, but it's a timeline-plausibility
argument, and this session has already produced several of those that
didn't hold up under direct inspection. `lifecycle_status` in particular —
locked as a decision 2026-07-08, over two weeks before `000`'s 2026-07-25
introspection — should already be inside `000` if it was actually applied
to production by then. That would flip `a1b2c3d4e5f6` from "genuinely new"
to "subsumed." Settle this with data, not dates.

1. Build `epm_diag_baseline_only` — run only `000_baseline_production_schema.py`
   against a fresh empty DB.
2. Build `epm_diag_incremental_only` — run only the original pre-snapshot
   incremental chain (`001` through `c0d1e2f3a4b5`, using `001`'s original
   `down_revision = None`) against a separate fresh empty DB.
3. Diff both databases' full schema via `information_schema.columns`
   (tables, columns, types, nullability, defaults) — not a table-name-only
   comparison. Report the actual diff output, not a summary of it.

Whatever shows a real, verified difference is what's genuinely new relative
to `000`. Let the diff decide, not the filename or the chain-relative
timeline position.

## Do not act on the result yet

Report the diff in HO-153. I will rule from that on exactly which files
get `down_revision = "000"` and which get archived — `backend/alembic/
versions/ARCHIVED-subsumed-by-000/`, not deleted, consistent with how
`hermes_config.yml` and `docker-compose.testbuild.yml` were handled
earlier in this project.

## Status

PR #10 remains held. No production risk — this remains entirely confined
to throwaway diagnostic databases. Report back via **HO-153**.
