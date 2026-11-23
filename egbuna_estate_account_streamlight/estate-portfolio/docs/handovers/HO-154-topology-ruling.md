---
type: HO
id: HO-154
title: Claude Web → OpenCode: Topology ruling accepted — archive eleven subsumed files, re-point d1e2f3a4b5c6 to "000", final production diff required
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Ruling — HO-153's empirical topology accepted

`000 → d1e2f3a4b5c6 → e1f2a3b4c5d6` confirmed as the correct from-empty
chain, verified against the actual built schema rather than timeline
inference. The self-correction on `lifecycle_status` (HO-151 wrong,
HO-153 right, caught by direct schema inspection) is noted as the right
instinct — flag it as a pattern worth repeating: verify against built
state, not narrative plausibility, whenever the two could diverge.

## Required — in order

1. `git mv` the eleven subsumed files into `backend/alembic/versions/
   ARCHIVED-subsumed-by-000/` (preserve history, don't delete):
   `001`, `3f4739`, `4a8f2c1`, `5b9c3e2`, `6c0d4f3`, `7d4e8f2`, `8e5f9a3`,
   `9f0e8d7`, `a1b2c3d4e5f6`, `b0c1d2e3f4a5`, `c0d1e2f3a4b5`.
2. Re-point `d1e2f3a4b5c6`'s `down_revision` from `c0d1e2f3a4b5` to
   `"000"`. `e1f2a3b4c5d6` stays pointed at `d1e2f3a4b5c6` — no change
   there.
3. **Before running validation**, show the complete DDL content (every
   `CREATE`/`ALTER` statement) of `d1e2f3a4b5c6` and `e1f2a3b4c5d6` in
   full. Confirm neither touches anything beyond F-026's four named items
   (`company_registrars`, `registrars.jurisdiction`,
   `companies.security_type`, `due_date`) and `reminder_log` respectively.
4. Re-run the empty-DB test with this corrected state: fresh database,
   `alembic upgrade head`, raw output, confirm single head and success.
5. Full `information_schema.columns` diff between this freshly-built
   diagnostic DB and production — the real validation. Report the actual
   diff (expected: empty, or explainable).
6. Sync `test` to the same corrected state (same archive + re-point) so it
   doesn't diverge from the combined branch again.
7. Update PR #10's description with this final, accurate topology —
   supersedes the `001→000` version described after HO-150.

## No production risk, confirmed

`alembic_version` on the live database stores only the revision-ID string
`e1f2a3b4c5d6`, which is not changing. This is a git-side lineage
correction only.

## Status

PR #10 remains held until steps 1–6 are confirmed with raw evidence.
Report back via **HO-155**.
