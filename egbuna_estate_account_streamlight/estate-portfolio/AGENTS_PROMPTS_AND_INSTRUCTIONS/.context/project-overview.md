# project-overview.md — EPM Project Overview

## What It Is

A self-hosted Nigerian stock portfolio tracker for personal investment
management. Tracks NGX equities (active holdings + delisted claims),
dividends, registrar relationships, and administrative documents.
All data stays on a self-hosted Netcup VPS. No third-party cloud services.

---

## Three Morning Goals (North Star)

Every Dashboard feature must serve one of these three questions:

  1. NET WORTH:       "What do I own and what is it worth today?"
  2. ADMINISTRATION: "What paperwork is outstanding? What dividends uncollected?"
  3. PERFORMANCE:    "Is my portfolio growing over time?"

If a Dashboard feature does not serve one of these three, it does not
belong on the Dashboard.

---

## Users

Current:
  Admin (owner)  — full read + write + administration
  Viewer         — read-only access (not yet implemented)

Future (Phase 4):
  Multi-portfolio — separate independent portfolios per user

---

## Asset Scope

Current (Phase 2–3):
  NGX listed equities       (holding_type = 'active')
  NGX delisted/defunct      (holding_type = 'claim', cost_basis = 0)
  NGX merged equities       (holding_type = 'active', may have successor)

Future (Phase 4):
  Nigerian Eurobonds        (multi-currency support needed)
  Real estate / property    (Property asset type)
  Treasury bills            (maturity date tracking)
  Fixed deposits            (yield tracking)
  Mutual funds              (NAV-based valuation)

Note: The current Company model is NGX-specific. A future Asset
abstraction will be needed for non-equity instruments. Do not
prematurely generalise the Company model now.

---

## The 16 Features

| ID   | Feature            | Status     |
|------|--------------------|------------|
| F-001| Authentication     | Complete   |
| F-002| Dashboard          | Bugs open  |
| F-003| Holdings           | Bugs open  |
| F-004| Price Entry        | Complete   |
| F-005| Price History      | Complete   |
| F-006| Registrars         | Complete   |
| F-007| NAV History        | Planned    |
| F-008| Dividends          | Planned    |
| F-009| Transactions       | Planned    |
| F-010| Claims             | Planned    |
| F-011| Rebalancing        | Planned    |
| F-012| Watchlist          | Planned    |
| F-013| Companies CRUD     | Planned    |
| F-014| Corporate Actions  | Planned    |
| F-015| Obsidian Import    | Planned    |
| F-016| Settings           | Planned    |

---

## Out of Scope (Never Build)

  Real-time market data feeds   — NGX has no free API
  Automated broker integration  — no standard Nigerian broker API
  Tax filing automation         — manual export + accountant workflow
  Social / sharing features     — personal finance tool, privacy first
  Mobile native app             — responsive web is sufficient
  Automated AMCON/CAC filing    — too legally complex

---

## Success Criteria

The system is complete when ALL of these are true:
  [ ] User sees total net worth in one number on Dashboard
  [ ] User sees all pending administrative actions at a glance
  [ ] User tracks portfolio performance over any time period
  [ ] Every NGX holding (active + claim) is represented correctly
  [ ] All registrar document requirements are tracked with file uploads
  [ ] Dividend history is complete and usable for tax purposes
  [ ] Price updates take < 5 minutes using NGX PDF upload workflow
  [ ] Works reliably on desktop and mobile browsers
