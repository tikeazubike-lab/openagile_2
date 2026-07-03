# F-007 — NAV History

**Feature ID:** F-007  
**Feature Name:** Portfolio NAV (Net Asset Value) History  
**Status:** DRAFT  
**Priority:** P1 — Phase 3C (second priority after F-016)  
**Created:** 2026-06-30  
**Author:** Claude (Architect)  
**Gherkin Scenarios:** SC-025 – SC-031 (already written, referenced below)  
**Stack:** FastAPI · PostgreSQL 15 · React 18 · TypeScript · Recharts

---

## 1. Purpose

A portfolio's current value is a snapshot. NAV History turns that snapshot into a **time series** — enabling users to track how their total portfolio value has evolved over time, identify growth trends, and understand the impact of price changes and new purchases on their overall wealth position.

This feature is the foundation for future performance analytics (IRR, CAGR, benchmark comparison). Phase 3C scope: capture, store, and display the daily NAV series. Performance ratios are out of scope here.

---

## 2. Scope

### In Scope

| Area | Detail |
|------|--------|
| NAV snapshot capture | Daily job writes one NAV row per active portfolio |
| Manual NAV recalculation | Admin can trigger recalculation for a date range |
| NAV history API | Time-series endpoint with date range filter |
| NAV chart | Line chart on Portfolio Detail page |
| NAV summary row | Current NAV · 7-day change · 30-day change · YTD change |
| Historical data seeding | Backfill from existing holdings + price history |

### Out of Scope

| Area | Reason |
|------|--------|
| IRR / CAGR / benchmark | Post-3C analytics feature |
| Per-holding value history | Holdings-level time series (separate feature) |
| Cross-portfolio aggregate NAV | Multi-portfolio dashboard (separate feature) |
| Intraday NAV updates | NGX is daily-only; no intraday price source |

---

## 3. Domain Definitions

**NAV (Net Asset Value):** The total market value of all holdings in a portfolio on a given date.

```
NAV(portfolio, date) = Σ [ quantity(holding) × closing_price(ticker, date) ]
```

Where:
- `quantity` is the net quantity held as of `date` (accounts for all buys/sells up to and including that date)
- `closing_price` is sourced from the NGX Daily Official List for `date`
- If no price exists for a ticker on `date`, use the **most recent prior price** (carry-forward)
- Holdings with zero quantity on `date` are excluded from the sum

**NAV Change:** `(NAV_today - NAV_reference) / NAV_reference × 100` expressed as a percentage.

---

## 4. Data Model

### 4.1 New Table: `portfolio_nav_history`

```sql
CREATE TABLE portfolio_nav_history (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id    UUID        NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    nav_date        DATE        NOT NULL,
    nav_value       NUMERIC(18, 4) NOT NULL,   -- total value in NGN
    price_source    VARCHAR(50) NOT NULL DEFAULT 'ngx_daily',
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes           TEXT,                       -- e.g., "backfill", "manual recalc"

    CONSTRAINT uq_portfolio_nav_date UNIQUE (portfolio_id, nav_date)
);

CREATE INDEX idx_nav_history_portfolio_date
    ON portfolio_nav_history (portfolio_id, nav_date DESC);
```

**Notes:**
- `UNIQUE (portfolio_id, nav_date)` — one row per portfolio per day; upsert on recalculation
- `NUMERIC(18,4)` — consistent with existing monetary precision; returned as **string** in API responses (locked decision)
- No soft delete on this table — NAV history rows are immutable facts; recalculation replaces via upsert

### 4.2 No Changes to Existing Tables

F-007 is purely additive. No existing columns modified.

---

## 5. NAV Calculation Service

### 5.1 Algorithm

```python
async def calculate_nav(portfolio_id: UUID, target_date: date, db: AsyncSession) -> Decimal:
    """
    1. Fetch all holdings for portfolio as of target_date
       (transactions with transaction_date <= target_date, net quantity > 0)
    2. For each holding, fetch closing price on target_date
       (if missing, use MAX(price_date) WHERE price_date <= target_date)
    3. NAV = SUM(quantity * price)
    4. Return Decimal; caller converts to string for API
    """
```

### 5.2 Price Carry-Forward Logic

```sql
-- Most recent price for a ticker on or before target_date
SELECT price
FROM equity_prices                  -- [VERIFY THIS: confirm actual price table name]
WHERE ticker = :ticker
  AND price_date <= :target_date
ORDER BY price_date DESC
LIMIT 1;
```

If **no price exists at all** for a ticker (new listing, no historical data), log a warning and exclude that holding from NAV for that date. Do not raise an error — partial NAV is better than no NAV.

### 5.3 Daily Job

Triggered by the existing task scheduler (confirm whether n8n or a Python APScheduler is in use — [VERIFY THIS]).

```
Schedule: Daily at 18:00 WAT (17:00 UTC)
           (after NGX closes at 14:30 WAT and price upload window closes)
Target: All portfolios where is_active = TRUE
Action: calculate_nav(portfolio_id, today) → upsert into portfolio_nav_history
```

---

## 6. API Contract

### 6.1 Get NAV History

```
GET /api/v1/portfolios/{portfolio_id}/nav-history
Authorization: httpOnly JWT cookie
Required role: USER (own portfolio) | ADMIN/SUPERADMIN (any portfolio)

Query params:
  from_date   date    ISO 8601 date (default: 1 year ago)
  to_date     date    ISO 8601 date (default: today)
  interval    string  "daily" | "weekly" | "monthly" (default: "daily")
              weekly = last trading day of each week
              monthly = last trading day of each month

Response 200:
{
  "portfolio_id": "uuid",
  "from_date": "2025-07-01",
  "to_date": "2026-06-30",
  "interval": "daily",
  "data_points": [
    {
      "date": "2025-07-01",
      "nav": "1250000.0000"    // string — locked decision
    }
    // ...
  ],
  "summary": {
    "current_nav":    "1500000.0000",
    "change_7d":      "2.34",           // percentage string
    "change_30d":     "-1.12",
    "change_ytd":     "12.45",
    "first_nav_date": "2025-07-01"
  }
}

Response 403: { "detail": "Not authorised to view this portfolio" }
Response 404: { "detail": "Portfolio not found" }
Response 200 (empty): { "data_points": [], "summary": null }
  // returned when no NAV history exists yet for portfolio
```

### 6.2 Trigger Manual Recalculation

```
POST /api/v1/admin/portfolios/{portfolio_id}/nav-history/recalculate
Required role: ADMIN | SUPERADMIN

Request body:
{
  "from_date": "2025-01-01",
  "to_date": "2026-06-30"
}

Response 202:
{
  "job_id": "uuid",
  "status": "queued",
  "portfolio_id": "uuid",
  "from_date": "2025-01-01",
  "to_date": "2026-06-30"
}
```

> 202 Accepted — calculation is async. For Phase 3C, this may be synchronous with a 30s timeout if no task queue is in place; document the actual implementation choice in the handover brief.

### 6.3 Get Latest NAV (convenience endpoint)

```
GET /api/v1/portfolios/{portfolio_id}/nav
Required role: USER (own) | ADMIN/SUPERADMIN (any)

Response 200:
{
  "portfolio_id": "uuid",
  "nav": "1500000.0000",
  "nav_date": "2026-06-30",
  "change_1d": "0.85"
}
```

---

## 7. Frontend Requirements

### 7.1 Portfolio Detail Page — NAV Chart

- **Library:** Recharts (already in React stack)
- **Chart type:** Line chart, single series
- **X-axis:** Date labels, auto-thinned based on range
- **Y-axis:** NAV in NGN, formatted as `₦1,250,000`
- **Tooltip:** Show exact NAV and date on hover
- **Default range:** 12 months
- **Range selector:** Buttons: 1M · 3M · 6M · 1Y · All

### 7.2 NAV Summary Row

Displayed above the chart on Portfolio Detail page:

```
Current NAV       7D Change     30D Change    YTD Change
₦1,500,000       +2.34%        -1.12%        +12.45%
```

- Positive change: green text with ↑
- Negative change: red text with ↓
- Zero / no data: grey `—`

### 7.3 Empty State

When no NAV history exists for a portfolio (e.g., new portfolio, no price data yet):

> "NAV history will appear here once daily prices are available. Prices are uploaded from the NGX Daily Official List each trading day."

---

## 8. Gherkin Scenario Mapping

Scenarios SC-025 through SC-031 (already written) map to these acceptance tests:

| Scenario | AC ID | Description |
|----------|-------|-------------|
| SC-025 | AT-F007-001 | View NAV history chart — data present |
| SC-026 | AT-F007-002 | View NAV history chart — no data (empty state) |
| SC-027 | AT-F007-003 | Change date range — chart updates |
| SC-028 | AT-F007-004 | NAV summary row shows correct changes |
| SC-029 | AT-F007-005 | Daily job populates NAV row |
| SC-030 | AT-F007-006 | Admin triggers manual recalculation |
| SC-031 | AT-F007-007 | USER cannot access another user's NAV history (403) |

---

## 9. Backfill Strategy

On first deployment, existing portfolios will have zero NAV history rows. Backfill process:

1. Determine earliest transaction date across all portfolios
2. For each calendar day from that date to yesterday:
   - Skip non-trading days (weekends; public holidays not yet modelled — skip if no price data for that date)
   - Run `calculate_nav(portfolio_id, date)` for all active portfolios
   - Upsert into `portfolio_nav_history`
3. Estimate: if 2 years of history × 10 portfolios × ~250 trading days = ~5,000 upserts. Acceptable in a single batch run.

Run as a one-shot admin script, not an API endpoint. Log output to file.

---

## 10. Acceptance Criteria Summary

| ID | Criterion |
|----|-----------|
| AT-F007-001 | NAV chart renders with ≥1 data point when history exists |
| AT-F007-002 | Empty state message shown when no NAV history |
| AT-F007-003 | Range selector changes chart data without page reload |
| AT-F007-004 | 7D/30D/YTD change values match manual calculation |
| AT-F007-005 | Daily job creates one NAV row per active portfolio per day |
| AT-F007-006 | Manual recalculation overwrites existing rows via upsert |
| AT-F007-007 | USER A cannot read NAV history for USER B's portfolio |
| AT-F007-008 | NAV value returned as string in all API responses |
| AT-F007-009 | Carry-forward logic used when price missing for a date |
| AT-F007-010 | Holding with zero net quantity excluded from NAV sum |

---

## 11. Dependencies

| Dependency | Direction | Notes |
|------------|-----------|-------|
| F-016 User Management | Required upstream | Permission guards for /admin/ recalculation endpoint |
| NGX price data (existing) | Required upstream | NAV calculation requires price table to be populated |
| Holdings table (existing) | Required upstream | Net quantities derived from transactions |
| F-019 Audit Log | Downstream | Manual recalculation should emit audit event |

---

## 12. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| OQ-1 | Confirm actual equity_prices table name — [VERIFY THIS] | Builder agent | Open |
| OQ-2 | Task scheduler: n8n webhook or Python APScheduler? | Zubbyik | Open |
| OQ-3 | Should non-trading days be stored (carry-forward NAV) or skipped? | Product | Recommend: skip (only store actual trading day NAVs) |
| OQ-4 | NGN or "kobo" precision for NAV storage? | Architect | Recommend: NGN with 4dp (NUMERIC 18,4) |
