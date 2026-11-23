---
type: HO
id: HO-148
title: Claude Web → OpenCode: URGENT — Alembic dual-root incident opened; diagnostic-only, no fixes yet; PR #10 remains held
date: 2026-08-28
from: Claude Web (The Brain / Architect)
to: Hermes deepseek-flash (builder, OpenCode CLI)
protocol: OpenAgile Hybrid Framework v1.0
priority: URGENT
---

## Status change

This is no longer part of F-026b's closure thread. The dual-head finding
(`000` and `e1f2a3b4c5d6` both reporting as heads) and `main`'s apparent
lack of `000_baseline_production_schema.py` in its tracked tree predate
F-026b entirely and affect every environment, not just this feature. I'm
opening it as its own incident. **PR #10 remains held** — do not let it
merge while the chain's actual integrity is unconfirmed, since merging adds
another migration on top of a graph we don't yet understand.

**This phase is diagnostic only. Do not modify any migration file,
down_revision, or the alembic_version table in any environment as part of
this handover.**

## Requirement A — Empirical test, not symbolic inference

Provision a genuinely empty test database (new name, not `epm_test` — don't
touch the existing one) and run:
```
createdb epm_diag_empty
DATABASE_URL=postgresql://.../epm_diag_empty alembic upgrade head
```
Report the raw output verbatim — success with final table count, or the
actual error text if it fails (e.g. "Multiple head revisions..."). I need
to know what actually happens today, not what the heads list implies.

## Requirement B — Was `000` ever actually merged to `main`?

```
git log main -- backend/alembic/versions/000_baseline_production_schema.py
git ls-tree main -- backend/alembic/versions/000_baseline_production_schema.py
```
If both come back empty, confirm explicitly: the HO-083/084/086
disaster-recovery fix exists only on `test`/feature branches and has never
reached `main`. If it does exist on `main`, reconcile why the per-branch
audit table in HO-147 listed it as untracked there.

## Requirement C — When did `001` (or whichever file is `000`'s intended
successor) lose its connection to `000`?

```
git log --all -p -- backend/alembic/versions/<the 001-equivalent file>
```
filtered to changes touching the `down_revision` line. I want to see
whether it was ever set to `"000"` and later reverted, or whether it has
always been `None` and the HO-084 "12/12 validated from empty" claim was
made against a different state (e.g. a manually-stamped database, not a
true `upgrade head` run) that was never actually re-verified since.

## Requirement D — Freeze on new migrations

Until this resolves: no new `alembic revision` files land on any branch
without being immediately committed **and** verified with `alembic heads`
showing a single head, no exceptions, including for unrelated feature work.

## Separately — noted, not yet actioned

`9f0e8d7c6b5a` missing from `main` while present and applied in production
is the same "declared complete, never merged" pattern already found with
F-026's dashboard routes (HO-143). This is being read as a symptom of the
same systemic cause — the workstation-offline exception's direct-VPS-execution
path has now been active for roughly seven weeks, well past what "temporary"
implied when it was granted, and every recent discovery this session
(F-026 dashboard, five migrations, this dual-head question) traces back to
work that shipped via that path without a corresponding PR ever landing.
This is going in front of Zubbyik directly, not something to resolve
inside this handover thread.

## Status

Report back via **HO-149** with Requirements A–C's raw output. Do not
propose a fix in that response — diagnosis first, ruling on remediation
comes after.
