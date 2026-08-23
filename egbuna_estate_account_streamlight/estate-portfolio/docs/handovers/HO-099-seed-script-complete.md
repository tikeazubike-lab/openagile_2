---
type: HO
id: HO-099
title: OpenCode → Claude: Seed Script Complete — Idempotent, Tested, epm_test Dry Run Passed
date: 2026-07-29
from: Hermes deepseek-flash (builder, OpenCode CLI)
to: Claude Web (The Brain / Architect)
protocol: OpenAgile Hybrid Framework v1.0
priority: HIGH
---

# HO-099 — Seed Script Implementation & Validation

## Script: `backend/scripts/seed_registrar_mapping.py`

- **13 registrars** seeded (including Computershare UK with `jurisdiction='international'`)
- **143 companies** seeded (~93 linked to registrars, 50 unmapped Main Board group)
- **93 regular links** + **1 special link** (Seplat → Computershare UK co_registrar)
- **Idempotent** — second run produces zero new rows
- **--preview mode** for read-only dry-run against production

## Tests (4 new)

| Test | Result |
|------|--------|
| Idempotency — run twice, second run creates 0 rows | PASS |
| Seplat co-registration (DataMax primary + Computershare UK co_registrar) | PASS |
| Africa Prudential dual-entity separation | PASS |
| Dynamic company count (relative invariant) | PASS |

## Production preview

```
Registrars: 0 would be created, 13 already exist
Companies: 0 would be created, 143 already exist
Links: 0 would be created, 93 already existing
Special links: 0 would be created, 3 already existing
Unmapped companies: 50
```

## Production cleanup

5 duplicate company rows (wrong tickers: ENAMELWARE, GGBREW, CHELLARAMS, MBANQ, UNIVPRESS) soft-deleted. All zero links, zero holdings — no real data affected.

## Full suite: 166 passed, 4 xfailed, 8 xpassed
