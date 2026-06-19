---
type: BR
id: BR-001
title: Personal Nigerian Investment Portfolio Management System
status: ACTIVE
version: 1.0
created: 2026-05-06
updated: 2026-05-06
owner: Claude (The Brain)
related:
  - BR-002 (Price Entry)
  - BR-003 (Obsidian Migration)
  - BR-004 (Claims Tracking)
  - BR-005 (Registrar Document Management)
  - ADR-001 (Single Container)
  - ADR-002 (Shared Postgres)
---

# [BR] BR-001 — Personal Nigerian Investment Portfolio Management System
> **Type**: Business Requirement · **Status**: 🟢 ACTIVE · **Version**: 1.0

---

## 1. Purpose

The Estate Portfolio Manager (EPM) exists to solve a problem that no
existing tool — not Excel, not a broker app, not Obsidian alone — solves
completely for a Nigerian retail investor:

**The complete absence of a single, authoritative source of truth for
what you own, what it is worth today, what administrative work is
outstanding, and what money you are owed but have not yet collected.**

Nigerian stock investing carries a unique administrative burden that
investors in other markets do not face:

- Shares may be held in physical certificates requiring digitisation
- Dividends accumulate unclaimed across multiple registrars
- Companies delist, merge, or go defunct — leaving shareholders with
  claims that must be actively pursued through AMCON, CAC, or court
- Each registrar has its own documentation requirements for every action
- Price data is not available via free APIs — it must be manually sourced
  from the NGX Daily Official List

EPM is the tool that takes ownership of all of this — tracking, valuing,
administering, and documenting every Nigerian investment asset in one place.

---

## 2. The Problem Statement

### 2.1 What Was Happening Before EPM

The user managed a portfolio of 85+ NGX stocks across multiple states:

| Problem | Impact |
|---------|--------|
| No single view of total portfolio value | Could not answer "what am I worth today?" |
| Unclaimed dividends scattered across registrars | Money left uncollected |
| Delisted stocks with no tracking | Potential compensation claims missed |
| Physical share certificates not digitised | Risk of permanent loss |
| Registrar document requirements not tracked | Submissions missed, actions stalled |
| Price data manually maintained in Obsidian | Error-prone, not connected to valuations |
| No NAV history | No way to measure if portfolio was growing |

### 2.2 The Three Core Gaps

**Gap 1 — Visibility**: "What do I own and what is it worth right now?"
No tool gave a live, unified view of all holdings including active stocks,
merged successors, and claims-in-progress.

**Gap 2 — Performance**: "Is my portfolio growing? How have my investments
performed over time?"
No historical NAV tracking meant performance could only be guessed, not measured.

**Gap 3 — Administration**: "What paperwork is outstanding? What do I owe
each registrar? What dividends have I not collected?"
The administrative layer of Nigerian investing — the registrars, the documents,
the claims — was entirely untracked.

---

## 3. Vision

EPM is a **complete personal Nigerian investment management system** that:

1. Tells the user exactly what they own, at current market value, every day
2. Shows performance over time through NAV history and return calculations
3. Manages the full administrative lifecycle of every investment — from
   active holding to dividend collection to delisting claim to final resolution
4. Grows with the user — from single-user today to multi-portfolio tomorrow,
   from NGX stocks today to any Nigerian investment asset in the future

---

## 4. Users

### 4.1 Current Users

| Role | Description | Access |
|------|-------------|--------|
| Admin | Portfolio owner (Zubby) | Full read + write + administration |
| Viewer | Trusted observer (e.g. family member) | Read-only, all pages |

### 4.2 Future Users (Phase 4+)

| Role | Description |
|------|-------------|
| Portfolio Owner (multi-user) | Family members with separate, independent portfolios |
| Shared Viewer | Shared read access across portfolios |

**Design implication**: The data model must support multiple independent
portfolios from the beginning. Every `holdings`, `dividends`, and `claims`
record must be associated with a `user_id`, not assumed to belong to a
single global portfolio. This is already partially implemented via the
`users` table — it must be enforced consistently across all future tables.

---

## 5. Asset Scope

### 5.1 In Scope — Now (Phase 2–3)

| Asset Class | Examples | Status |
|-------------|----------|--------|
| NGX Listed Equities | DANGCEM, GTCO, ZENITHBANK | ✅ Implemented |
| NGX Delisted / Defunct Equities | Companies with AMCON/CAC claims | ✅ Implemented |
| NGX Merged Equities | Diamond Bank → Access Bank successors | ✅ Implemented |

### 5.2 In Scope — Future (Phase 4+)

| Asset Class | Examples | Notes |
|-------------|----------|-------|
| Nigerian Eurobonds | FGN USD bonds | Requires multi-currency support |
| Real Estate / Property | Investment properties | Requires Property asset type |
| Fixed Deposits | Bank FDs | Simple yield tracking |
| Treasury Bills | FGN T-bills | Maturity date tracking |
| Other Nigerian instruments | Money market funds, mutual funds | TBD |

**Design implication**: The `Company` model is NGX-specific. A future
`Asset` abstraction will be needed to support non-equity instruments.
Phase 2–3 builds on the current model. Phase 4 introduces the abstraction.
Do not prematurely abstract now — note it here as a future constraint.

---

## 6. Functional Requirements

### FR-1: Portfolio Valuation (Daily)
The system shall display the current market value of every active holding,
computed as `shares × current_price`, updated whenever the user uploads
the NGX Daily Official List PDF or enters a price manually.

### FR-2: Total Net Worth
The system shall compute and display a single **Total Assets** figure:
`active_portfolio_value + claims_portfolio_value`
where `claims_portfolio_value` is the sum of expected or actual payouts
from delisted/defunct stock claims.

### FR-3: Performance Tracking
The system shall record a daily NAV snapshot (portfolio value + cost basis)
and display a NAV history chart, enabling the user to track portfolio
performance over any time period.

### FR-4: Return Calculation
The system shall calculate and display per-holding return metrics:
- Simple return: `(current_value − cost_basis) / cost_basis × 100`
- Dividend yield: `annual_dividend_per_share / current_price × 100`
- XIRR (future): annualised return accounting for multiple purchase dates

### FR-5: Holdings Classification
The system shall maintain two distinct holding categories displayed
as separate tables:
- **Active Portfolio**: listed and merged stocks (holding_type = 'active')
- **Claims Portfolio**: delisted, defunct, uncertain stocks (holding_type = 'claim')
  with cost_basis = 0 and claim tracking via ClaimRecord table

### FR-6: Dividend Tracking
The system shall record all dividend payments per holding, including:
gross amount, net amount, withholding tax (default 10%, configurable),
payment date, type (final/interim), and DRIP (scrip dividend) flag.
Annual dividend summaries shall be available for tax filing purposes.

### FR-7: Registrar Administration
The system shall maintain a per-registrar document management system
tracking required documents for each administrative task
(unclaimed dividends, dematerialisation, KYC updates, claims),
with file upload, status tracking, and version history per document.

### FR-8: Claims Management
The system shall track AMCON/CAC/court claims for delisted/defunct stocks
including reference numbers, filing dates, expected payouts, actual payouts,
and claim status lifecycle (pending → approved → partially_paid → paid).

### FR-9: Price Data Entry
The system shall support two price update methods:
- Manual quick entry (single stock, immediate)
- NGX Daily Official List PDF upload (bulk, automated parsing)
All price updates shall be logged to an audit trail with revert capability.

### FR-10: Rebalancing Analysis
The system shall compare current sector allocation against user-defined
target percentages and display the gap per sector with recommended action
(increase / reduce / hold).

### FR-11: Watchlist
The system shall maintain a watchlist of companies the user is researching
but has not yet purchased, with target price and gap-to-target tracking.

### FR-12: Multi-Portfolio (Future)
The system shall support multiple independent portfolios — each owned by
a different user — with no data leakage between portfolios.
**This is a Phase 4 requirement. Current implementation is single-portfolio.**

---

## 7. Non-Functional Requirements

### NFR-1: Data Sovereignty
All data is stored on a self-hosted server (Netcup VPS, Nigeria-adjacent).
No data is sent to third-party cloud services. This is non-negotiable.

### NFR-2: Availability
The system shall be accessible via browser on desktop and mobile.
Acceptable downtime: < 1 hour per month (infrastructure permitting).

### NFR-3: Price Data Latency
Portfolio valuations are point-in-time, not real-time. The system does
not require live market data feeds. Daily updates via NGX PDF are sufficient.

### NFR-4: Security
- All pages require authentication (JWT httpOnly cookie, 30-day session)
- Financial data is never exposed to unauthenticated requests
- Document downloads require authentication
- Admin operations require admin role

### NFR-5: Performance
- Dashboard load time: < 2 seconds on a standard broadband connection
- PDF parsing: < 30 seconds for the NGX Daily Official List
- API response time P95: < 500ms for GET endpoints

### NFR-6: Extensibility
The data model shall support future asset classes beyond NGX equities
without requiring destructive schema changes. New asset types are added
as new tables, not modifications to existing ones.

---

## 8. The Three Morning Dashboards

The user identified three things they need to see immediately on opening
the app. These define the Dashboard page information architecture:

### Dashboard 1 — Net Worth (top of page)
```
Total Assets: ₦XX,XXX,XXX
  Active Portfolio:  ₦XX,XXX,XXX  (+X.X% today)
  Claims Portfolio:  ₦XXX,XXX     (X claims pending)
```

### Dashboard 2 — Administrative Actions (action items card)
```
Pending Actions:
  • 3 dividends unclaimed (total ₦XX,XXX)
  • 2 registrar documents awaiting submission
  • 1 claim approved — collect payout
  • Prices last updated: 2 days ago
```

### Dashboard 3 — Performance (charts)
```
NAV History:     [area chart — portfolio value over time]
Sector Breakdown: [donut chart — current allocation]
Top Holdings:    [bar chart — by current value]
```

These three views are the north star for every Dashboard iteration.
If a Dashboard change does not serve one of these three purposes,
it should not be on the Dashboard.

---

## 9. Out of Scope (Explicitly)

| Item | Reason |
|------|--------|
| Real-time market data feeds | NGX does not provide free real-time API |
| Automated broker integration | No standard API from Nigerian brokers |
| Tax filing automation | Manual export + accountant workflow sufficient |
| Social / sharing features | Personal finance tool — privacy first |
| Mobile native app | Responsive web is sufficient for now |
| Automated AMCON/CAC filing | Too legally complex for automation |

---

## 10. Success Criteria

BR-001 is satisfied when the following are all true:

- [ ] User can open the app and see total net worth in one number
- [ ] User can see exactly which administrative actions are pending
- [ ] User can track portfolio performance over any time period
- [ ] Every NGX holding (active + claim) is represented with correct status
- [ ] All registrar document requirements are tracked with file uploads
- [ ] Dividend history is complete and exportable for tax purposes
- [ ] Price updates take < 5 minutes using the NGX PDF upload workflow
- [ ] The system works reliably on both desktop and mobile browsers

---

## 11. Open Questions

| Question | Owner | Due |
|----------|-------|-----|
| Multi-currency support (₦ + USD for Eurobonds) — exact schema design | Claude | Phase 4 planning |
| XIRR calculation — which transaction history to use as input | Claude | Phase 3 |
| Multi-portfolio isolation — row-level security strategy | Claude | Phase 4 planning |

---

## 12. Revision History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-05-06 | Claude (The Brain) | Initial complete draft — replaces stub |