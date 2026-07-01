# EPM Phase 2B — Architecture & Design Document
## Obsidian Vault → PostgreSQL Migration + CI Reinstatement

**From**: Claude (The Brain)
**To**: Antigravity (Implementer), Codex (Tester), Grok (Spotter)
**Date**: 2026-04-25
**Protocol**: MASTER_CONTEXT.md v3.0 — Zone 2 Design
**Status**: ALL DECISIONS LOCKED. Ready for implementation.

---

## Part A: Decisions Absorbed

| Question | Answer | Implication |
|----------|--------|-------------|
| Sync model | Vault + web app coexist; import runs on-demand | `import_obsidian.py` inserts **new records only** on re-run; web app edits are never overwritten |
| Conflict resolution | Web app wins after first import | First run = full seed. Re-runs = INSERT new companies/dividends only, skip existing tickers |
| Holding scope | ALL 85 stocks get a record | Listed+merged → `Holdings` table (active). Delisted/defunct → same `Holdings` table but `holding_type = 'claim'`, `cost_basis = 0` |
| UI layout | Two separate tables on Holdings page | Table 1: Active Holdings (listed + merged). Table 2: Claims Portfolio (delisted + defunct). Grand total row sums both |
| Claims detail | Separate `ClaimRecord` table | Linked to `Holding` via FK. Stores AMCON/CAC reference numbers, claim status, compensation received |
| CI reinstatement | Tests back in repo, isolated test schema on shared Postgres | `estate_portfolio_test` schema, transaction rollback isolation, no new container |
| epm-tests/ | Reinstated into repo with new CI strategy | `.gitignore` entry for `epm-tests/` removed; tests travel with code |

---

## Part B: Database Schema — Phase 2B Additions

All changes are **additive only**. Existing tables are never modified destructively.

### B.1 — Changes to Existing `holdings` Table

```sql
-- Add holding_type to distinguish active positions from claim positions
ALTER TABLE holdings
  ADD COLUMN IF NOT EXISTS holding_type VARCHAR(20)
    NOT NULL DEFAULT 'active'
    CHECK (holding_type IN ('active', 'claim'));

-- Add cost_basis_override for claims (always 0 for defunct stocks)
-- The business rule: claim holdings have cost_basis = 0 regardless of
-- original purchase price. This keeps portfolio return% calculations clean
-- while preserving the claim record for administrative purposes.
ALTER TABLE holdings
  ADD COLUMN IF NOT EXISTS cost_basis_override NUMERIC(15,2) DEFAULT NULL;
-- When cost_basis_override IS NOT NULL, use it instead of (shares * avg_price)
-- Claims always set cost_basis_override = 0.00

-- Add obsidian_source flag so we know which records came from the vault
ALTER TABLE holdings
  ADD COLUMN IF NOT EXISTS obsidian_imported BOOLEAN DEFAULT FALSE;
  ADD COLUMN IF NOT EXISTS obsidian_last_synced TIMESTAMPTZ DEFAULT NULL;
```

### B.2 — Changes to Existing `companies` Table

```sql
-- Extend status to include all Obsidian status values
-- Current: active / inactive
-- Extended: listed, delisted, defunct, merged, uncertain
ALTER TABLE companies
  DROP CONSTRAINT IF EXISTS companies_status_check;

ALTER TABLE companies
  ADD CONSTRAINT companies_status_check
    CHECK (status IN ('listed', 'delisted', 'defunct', 'merged', 'uncertain', 'active', 'inactive'));

-- obsidian_slug: the Obsidian filename slug (e.g. "Access-Bank-PLC")
-- Used by import script to detect existing records on re-run
ALTER TABLE companies
  ADD COLUMN IF NOT EXISTS obsidian_slug VARCHAR(255) UNIQUE DEFAULT NULL;

ALTER TABLE companies
  ADD COLUMN IF NOT EXISTS obsidian_imported BOOLEAN DEFAULT FALSE;
```

### B.3 — NEW: `claim_records` Table

```sql
-- Tracks AMCON/CAC claim administration for defunct/delisted holdings
-- One holding can have multiple claim records (e.g. initial filing + appeal)
CREATE TABLE IF NOT EXISTS claim_records (
    id                  SERIAL PRIMARY KEY,
    holding_id          INTEGER NOT NULL REFERENCES holdings(id) ON DELETE CASCADE,

    -- Claim identity
    claim_reference     VARCHAR(100),          -- AMCON/CAC reference number
    claim_authority     VARCHAR(100),          -- e.g. 'AMCON', 'CAC', 'SEC', 'Court'
    claim_type          VARCHAR(50)            -- e.g. 'liquidation', 'merger_compensation',
                                               --      'court_order', 'regulatory_claim'
                        NOT NULL DEFAULT 'liquidation',

    -- Filing details
    date_filed          DATE,
    date_acknowledged   DATE,
    deadline_date       DATE,

    -- Financial outcome
    claim_status        VARCHAR(30)            -- 'pending', 'approved', 'rejected',
                        NOT NULL DEFAULT 'pending'  -- 'partially_paid', 'paid', 'lapsed'
                        CHECK (claim_status IN (
                            'pending', 'approved', 'rejected',
                            'partially_paid', 'paid', 'lapsed'
                        )),
    expected_payout     NUMERIC(15,2) DEFAULT NULL,   -- ₦ amount expected
    actual_payout       NUMERIC(15,2) DEFAULT NULL,   -- ₦ amount received
    payout_date         DATE DEFAULT NULL,

    -- Notes
    notes               TEXT,                  -- Free-form reference notes
    documents_reference TEXT,                  -- File paths or reference strings

    -- Audit
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ DEFAULT NULL       -- soft delete
);

CREATE INDEX IF NOT EXISTS idx_claim_records_holding_id ON claim_records(holding_id);
CREATE INDEX IF NOT EXISTS idx_claim_records_status ON claim_records(claim_status);
```

### B.4 — NEW: `obsidian_sync_log` Table

```sql
-- Audit trail for every import_obsidian.py run
-- Allows the user to see what was imported, when, and what was skipped
CREATE TABLE IF NOT EXISTS obsidian_sync_log (
    id              SERIAL PRIMARY KEY,
    run_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    run_by          INTEGER REFERENCES users(id),      -- NULL = script run
    vault_path      TEXT NOT NULL,                     -- path passed to script
    companies_new   INTEGER DEFAULT 0,                 -- new Company rows inserted
    companies_skip  INTEGER DEFAULT 0,                 -- existing tickers skipped
    holdings_new    INTEGER DEFAULT 0,
    holdings_skip   INTEGER DEFAULT 0,
    dividends_new   INTEGER DEFAULT 0,
    dividends_skip  INTEGER DEFAULT 0,
    errors          INTEGER DEFAULT 0,
    error_details   JSONB DEFAULT '[]',                -- [{ticker, error_message}]
    run_mode        VARCHAR(20) DEFAULT 'manual'       -- 'manual' | 'api_triggered'
);
```

---

## Part C: Business Logic — Holdings Dual-Table Architecture

### C.1 — The Two Tables

The Holdings page renders **two separate TanStack Table instances**:

```
┌─────────────────────────────────────────────────────────┐
│  ACTIVE PORTFOLIO                                        │
│  Companies with status IN ('listed', 'merged')          │
│  holding_type = 'active'                                 │
│  cost_basis = shares × avg_purchase_price                │
│                                          Subtotal ₦X    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CLAIMS PORTFOLIO                                        │
│  Companies with status IN ('delisted','defunct',         │
│                            'uncertain')                  │
│  holding_type = 'claim'                                  │
│  cost_basis = 0 (overridden)                             │
│  Shows: expected_payout from ClaimRecord if exists       │
│                                          Subtotal ₦Y    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  TOTAL ASSETS: ₦X + ₦Y  (active value + claims payout)  │
│  Note: Claims subtotal uses actual_payout if paid,       │
│        expected_payout if pending, 0 if no claim record  │
└─────────────────────────────────────────────────────────┘
```

### C.2 — Total Assets Computation

```python
# backend/app/services/portfolio.py (additive function)

def calculate_total_assets(active_holdings: list, claim_records: list) -> dict:
    """
    Active portfolio value: sum of (shares × current_price) for live, active holdings
    Claims value: sum of actual_payout (if paid) or expected_payout (if pending/approved)
                  for claim holdings that have a ClaimRecord

    Total assets = active_value + claims_value
    """
    active_value = sum(
        h.current_value for h in active_holdings
        if h.status == 'live' and h.holding_type == 'active'
    )

    claims_value = Decimal("0.00")
    for cr in claim_records:
        if cr.claim_status == 'paid' and cr.actual_payout:
            claims_value += cr.actual_payout
        elif cr.claim_status in ('approved', 'partially_paid', 'pending') and cr.expected_payout:
            claims_value += cr.expected_payout

    return {
        "active_portfolio_value": str(active_value),
        "claims_portfolio_value": str(claims_value),
        "total_assets": str(active_value + claims_value),
    }
```

### C.3 — return[%] for Claims Holdings

Claims holdings must NOT show a return% calculation (cost basis = 0, division undefined). The API returns `return_pct: null` for `holding_type = 'claim'`. The frontend renders `"—"` in that cell, not `0.00%` or an error.

---

## Part D: `import_obsidian.py` — Complete Specification

### D.1 — Location and Invocation

```
File:    backend/scripts/import_obsidian.py
Run:     python backend/scripts/import_obsidian.py --vault-path ~/ObsidianVault/NigerianStocks
         python backend/scripts/import_obsidian.py --vault-path ~/ObsidianVault/NigerianStocks --dry-run
Re-run:  Safe to re-run. Skips existing tickers (INSERT new only, never UPDATE).
```

### D.2 — Dependencies

```
python-frontmatter   — parses YAML frontmatter from .md files
PyYAML               — fallback parser
sqlalchemy           — ORM (same as backend)
asyncpg              — async driver (or psycopg2 for sync script)
python-dotenv        — reads .env for DB credentials
```

Add to `backend/requirements.txt`:
```
python-frontmatter==1.1.0
```

### D.3 — Algorithm (Pseudocode → Antigravity implements)

```python
"""
backend/scripts/import_obsidian.py
"""

HOLDING_TYPE_MAP = {
    "listed":    ("active", False),   # (holding_type, is_claim)
    "merged":    ("active", False),   # merged may have successor — still active tracking
    "delisted":  ("claim",  True),
    "defunct":   ("claim",  True),
    "uncertain": ("claim",  True),
}

def run_import(vault_path: str, dry_run: bool = False):
    log = SyncLog()

    # ── PASS 1: Companies ──────────────────────────────────────────────
    for md_file in glob(f"{vault_path}/Companies/*.md"):
        fm = frontmatter.load(md_file)
        ticker = fm.get("ticker")
        if not ticker:
            log.error(md_file, "Missing ticker field")
            continue

        slug = Path(md_file).stem   # e.g. "Access-Bank-PLC"
        obsidian_status = fm.get("status", "uncertain").lower()

        existing = db.query(Company).filter_by(ticker=ticker).first()
        if existing:
            log.companies_skip += 1
            continue  # Web app wins — never overwrite existing company

        company = Company(
            ticker=ticker,
            name=fm.get("name", ticker),
            sector=fm.get("sector"),
            registrar=fm.get("registrar"),
            status=obsidian_status,
            obsidian_slug=slug,
            obsidian_imported=True,
        )
        if not dry_run:
            db.add(company)
        log.companies_new += 1

    if not dry_run:
        db.flush()   # get company IDs before Holdings pass

    # ── PASS 2: Holdings ───────────────────────────────────────────────
    admin_user = db.query(User).filter_by(role="admin").first()

    for md_file in glob(f"{vault_path}/Companies/*.md"):
        fm = frontmatter.load(md_file)
        ticker = fm.get("ticker")
        company = db.query(Company).filter_by(ticker=ticker).first()
        if not company:
            continue

        obsidian_status = fm.get("status", "uncertain").lower()
        holding_type, is_claim = HOLDING_TYPE_MAP.get(obsidian_status, ("claim", True))
        shares = fm.get("shares_held", 0)
        avg_price = fm.get("avg_buy_price", 0)

        # All 85 stocks get a Holding record
        # Claims get cost_basis_override = 0
        existing_holding = db.query(Holding).filter_by(company_id=company.id).first()
        if existing_holding:
            log.holdings_skip += 1
            continue

        holding = Holding(
            company_id=company.id,
            user_id=admin_user.id,
            num_shares=shares if not is_claim else shares,  # preserve original share count for reference
            avg_purchase_price=str(avg_price) if not is_claim else "0.00",
            holding_type=holding_type,
            cost_basis_override=Decimal("0.00") if is_claim else None,
            status="live",
            obsidian_imported=True,
            obsidian_last_synced=datetime.now(timezone.utc),
        )
        if not dry_run:
            db.add(holding)
        log.holdings_new += 1

    if not dry_run:
        db.flush()

    # ── PASS 3: Dividends ──────────────────────────────────────────────
    for md_file in glob(f"{vault_path}/Dividends/*.md"):
        fm = frontmatter.load(md_file)
        company_ref = fm.get("company")  # Obsidian [[link]] or plain string
        ticker = extract_ticker_from_link(company_ref)  # strips [[ ]] if present
        company = db.query(Company).filter_by(ticker=ticker).first()
        if not company:
            log.error(md_file, f"Company not found: {ticker}")
            continue

        holding = db.query(Holding).filter_by(company_id=company.id).first()
        if not holding:
            log.dividends_skip += 1
            continue

        # Check for duplicate (same holding + payment_date)
        payment_date = fm.get("payment_date")
        existing_div = db.query(Dividend).filter_by(
            holding_id=holding.id,
            payment_date=payment_date,
        ).first()
        if existing_div:
            log.dividends_skip += 1
            continue

        dividend = Dividend(
            holding_id=holding.id,
            payment_date=payment_date,
            dividend_type=fm.get("dividend_type", "final"),
            gross_amount=str(fm.get("gross_amount", "0.00")),
            net_amount=str(fm.get("net_amount", "0.00")),
            withholding_tax=str(fm.get("withholding_tax", "0.00")),
            payment_status=fm.get("payment_status", "paid"),
            source="obsidian_import",
            obsidian_imported=True,
        )
        if not dry_run:
            db.add(dividend)
        log.dividends_new += 1

    # ── COMMIT & LOG ───────────────────────────────────────────────────
    if not dry_run:
        db.commit()
        db.add(SyncLogRecord(
            vault_path=vault_path,
            companies_new=log.companies_new,
            companies_skip=log.companies_skip,
            holdings_new=log.holdings_new,
            holdings_skip=log.holdings_skip,
            dividends_new=log.dividends_new,
            dividends_skip=log.dividends_skip,
            errors=len(log.errors),
            error_details=log.errors,
        ))
        db.commit()

    print_summary(log, dry_run)
```

### D.4 — Dry Run Output Format

```
EPM Obsidian Import — DRY RUN (no changes written)
====================================================
Vault path:   ~/ObsidianVault/NigerianStocks
Companies:    45 new  |  40 skip (already in DB)
Holdings:     45 new  |  40 skip
  → Active:   45 (listed/merged)
  → Claims:   40 (delisted/defunct/uncertain)
Dividends:   120 new  |   0 skip
Errors:        2
  → COURTVILLE.md: Missing ticker field
  → UNKNOWN_DIV.md: Company 'XYZ' not found in DB

Run without --dry-run to apply these changes.
```

### D.5 — Conflict Rules (Locked)

| Scenario | Action |
|----------|--------|
| Ticker already in `companies` | SKIP — web app record preserved |
| `(company_id)` already in `holdings` | SKIP — web app record preserved |
| Same `(holding_id, payment_date)` in dividends | SKIP — no duplicate |
| Company in Obsidian but missing ticker field | LOG error, skip file |
| Dividend references unknown company/ticker | LOG error, skip file |
| Status not in known HOLDING_TYPE_MAP | Default to `("claim", True)` |

---

## Part E: New API Endpoints for Phase 2B

### E.1 — Obsidian Import Trigger (Admin only)

```
POST /api/v1/obsidian/import
  Body: { "vault_path": "/home/zubbyik/ObsidianVault/NigerianStocks", "dry_run": false }
  Returns: SyncLogRecord (same shape as obsidian_sync_log row)
  Auth: Admin only
  Note: Runs import_obsidian.py as a subprocess or inline function call.
        Long-running — use BackgroundTasks to avoid timeout.

GET  /api/v1/obsidian/sync-log
  Returns: [SyncLogRecord] — history of all import runs, newest first
  Auth: Admin only
```

### E.2 — Claims Endpoints (Admin + Readonly)

```
GET  /api/v1/claims
  Query: ?holding_id=N, ?status=pending|approved|paid, ?authority=AMCON|CAC
  Returns: [ClaimRecord] with holding + company joined
  Auth: Both roles (readonly sees claims too — it's their assets)

POST /api/v1/claims              [admin only]
  Body: ClaimRecordCreate

PUT  /api/v1/claims/{id}         [admin only]
  Body: ClaimRecordUpdate (partial)
  Key update: when claim_status → 'paid', actual_payout must be provided

DELETE /api/v1/claims/{id}       [admin only]
  Action: soft delete (deleted_at = NOW())
```

### E.3 — Holdings Endpoint Update

```
GET /api/v1/holdings
  Existing endpoint updated to accept:
  Query: ?holding_type=active|claim|all   (default: all)

  Response shape updated — each holding now includes:
  {
    ...existing fields...,
    "holding_type": "active" | "claim",
    "cost_basis_override": "0.00" | null,
    "effective_cost_basis": "0.00",   -- computed: override ?? (shares × avg_price)
    "return_pct": "+11.22" | null,    -- null for claim holdings
    "claim_summary": {                -- null for active holdings
      "claim_count": 2,
      "latest_status": "pending",
      "expected_payout": "45000.00",
      "actual_payout": null
    }
  }
```

### E.4 — Dashboard Endpoint Update

```
GET /api/v1/dashboard
  Response updated to include:
  {
    ...existing fields...,
    "active_portfolio_value": "12345678.00",
    "claims_portfolio_value": "450000.00",
    "total_assets": "12795678.00",        -- active + realised claims
    "claims_summary": {
      "total_claims": 40,
      "pending": 28,
      "approved": 5,
      "paid": 7,
      "total_expected": "1200000.00",
      "total_received": "450000.00"
    }
  }
```

---

## Part F: CI Reinstatement — Isolated Test Schema Strategy

### F.1 — The Problem Antigravity Hit

`epm-tests/` was `.gitignored` because the user didn't want test files bloating PRs. But GitHub Actions needs tests in the repo to run them. The resolution is to reinstate tests but with two changes:

1. Tests live **in the repo** (un-gitignore `epm-tests/`)
2. Tests use a **separate schema** (`estate_portfolio_test`) inside the same shared `openagile_postgres` — zero risk to production data, zero new containers

### F.2 — Test Schema Isolation Pattern

```sql
-- Created once by a migration or setup script
-- Never touched by production Alembic migrations
CREATE SCHEMA IF NOT EXISTS estate_portfolio_test;

-- All test tables are identical to public schema tables
-- but live in estate_portfolio_test.*
-- Created by test conftest.py on first run, torn down after suite
```

```python
# backend/tests/integration/conftest.py (updated)

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?options=-csearch_path%3Destate_portfolio_test"  # ← schema isolation
)

# On session start: CREATE SCHEMA IF NOT EXISTS estate_portfolio_test
# Run Alembic against test schema: alembic -x schema=estate_portfolio_test upgrade head
# Each test: BEGIN SAVEPOINT → test runs → ROLLBACK TO SAVEPOINT
# On session end: DROP SCHEMA estate_portfolio_test CASCADE (optional — or leave for debug)
```

### F.3 — GitHub Actions Secret Required

```
New secret: DB_TEST_SCHEMA = "estate_portfolio_test"
Existing secrets reused: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
```

### F.4 — Updated CI Pipeline (Stage 2 only — rest unchanged)

```yaml
# In .github/workflows/ci.yml — replace integration job with:

  integration:
    name: "Stage 2 — Integration, Contract & DB Tests"
    runs-on: ubuntu-latest
    needs: [unit-backend, unit-frontend]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        working-directory: backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx jsonschema asyncpg

      - name: Create test schema on shared Postgres
        run: |
          PGPASSWORD=${{ secrets.DB_PASSWORD }} psql \
            -h ${{ secrets.DB_HOST }} \
            -U ${{ secrets.DB_USER }} \
            -d ${{ secrets.DB_NAME }} \
            -c "CREATE SCHEMA IF NOT EXISTS estate_portfolio_test;"

      - name: Run Alembic migrations against test schema
        working-directory: backend
        run: |
          alembic -x schema=estate_portfolio_test upgrade head
        env:
          DATABASE_URL: postgresql+asyncpg://${{ secrets.DB_USER }}:${{ secrets.DB_PASSWORD }}@${{ secrets.DB_HOST }}/${{ secrets.DB_NAME }}

      - name: Run integration + contract + DB tests
        working-directory: backend
        run: pytest tests/integration/ tests/contract/ tests/db/ -v --tb=short -x
        env:
          PYTHONPATH: .
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_NAME: ${{ secrets.DB_NAME }}
          DB_USER: ${{ secrets.DB_USER }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
          DB_TEST_SCHEMA: estate_portfolio_test
          JWT_SECRET: ${{ secrets.JWT_SECRET }}

      - name: Tear down test schema
        if: always()   # runs even if tests fail
        run: |
          PGPASSWORD=${{ secrets.DB_PASSWORD }} psql \
            -h ${{ secrets.DB_HOST }} \
            -U ${{ secrets.DB_USER }} \
            -d ${{ secrets.DB_NAME }} \
            -c "DROP SCHEMA IF EXISTS estate_portfolio_test CASCADE;"
```

---

## Part G: Implementation Order for Antigravity

```
Phase 2B — Sprint Order

1. [ ] Alembic migration: alter holdings (holding_type, cost_basis_override, obsidian_*)
2. [ ] Alembic migration: alter companies (extended status check, obsidian_slug, obsidian_imported)
3. [ ] Alembic migration: CREATE TABLE claim_records
4. [ ] Alembic migration: CREATE TABLE obsidian_sync_log
5. [ ] Update SQLAlchemy models in app/models.py for all 4 changes above
6. [ ] Build app/services/portfolio.py — business logic including calculate_total_assets()
7. [ ] Build import_obsidian.py per D.3 spec (dry-run mode mandatory)
8. [ ] Test import_obsidian.py locally with --dry-run against actual vault before committing
9. [ ] Add POST /api/v1/obsidian/import + GET /api/v1/obsidian/sync-log endpoints
10.[ ] Add /api/v1/claims CRUD endpoints
11.[ ] Update GET /api/v1/holdings to return holding_type + claim_summary
12.[ ] Update GET /api/v1/dashboard to return total_assets + claims_summary
13.[ ] Remove epm-tests/ from .gitignore (reinstate CI tests)
14.[ ] Update conftest.py with test schema isolation pattern
15.[ ] Run first import: python backend/scripts/import_obsidian.py --vault-path ~/ObsidianVault/NigerianStocks --dry-run
16.[ ] Confirm dry-run output matches expected ~85 companies, 85 holdings, ~N dividends
17.[ ] Run live import (no --dry-run) and verify in PostgreSQL
18.[ ] Deploy to demo.estate.zubbystudio.shop and verify Holdings dual-table renders correctly
```

---

## Part H: Tasks for Codex (Tester)

Once Antigravity completes steps 1–5 (migrations + models):

```
Codex Sprint 2B Tests to write on `test` branch:

Unit tests (backend/tests/unit/):
  test_business_logic.py:
    + test_calculate_total_assets_sums_active_and_claims()
    + test_claims_value_uses_actual_payout_when_paid()
    + test_claims_value_uses_expected_payout_when_pending()
    + test_return_pct_is_null_for_claim_holdings()
    + test_cost_basis_override_zero_for_claim_holdings()

  test_pydantic_schemas.py:
    + test_holding_type_accepts_active_and_claim()
    + test_holding_type_rejects_unknown_values()
    + test_claim_record_requires_holding_id()
    + test_claim_status_enum_validates_correctly()

DB tests (backend/tests/db/):
  test_schema_integrity.py:
    + test_claim_records_table_exists()
    + test_obsidian_sync_log_table_exists()
    + test_holdings_holding_type_column_exists_with_default_active()
    + test_holdings_cost_basis_override_column_exists()
    + test_claim_records_holding_id_fk_references_holdings()
    + test_claim_records_status_check_constraint_enforced()

Integration tests (backend/tests/integration/):
  test_obsidian_integration.py (NEW FILE):
    + test_import_script_dry_run_writes_nothing_to_db()
    + test_import_script_inserts_companies_on_first_run()
    + test_import_script_skips_existing_tickers_on_rerun()
    + test_import_script_creates_claim_holding_for_defunct_stock()
    + test_import_script_creates_active_holding_for_listed_stock()
    + test_import_script_sets_cost_basis_override_zero_for_claim()
    + test_import_script_logs_run_to_obsidian_sync_log()
    + test_claim_cost_basis_never_contributes_to_portfolio_return_pct()
```

---

## Part I: Frontend Changes (for Lovable — next session)

The Holdings page needs two tables. Pass this as an addendum to the Lovable prompt:

```
HOLDINGS PAGE UPDATE (Phase 2B):

Replace single holdings table with TWO separate TanStack Table instances.

TABLE 1 — "Active Portfolio" (holding_type = 'active'):
  Filter: /api/v1/holdings?holding_type=active
  Columns: Ticker | Company | Sector | Shares | Avg Cost | Curr Price |
           Curr Value | Cost Basis | return[%] | Div Yield | Status | Actions
  Subtotal row: sum of current_value for live holdings
  Label: "Active Portfolio" (green dot badge)

TABLE 2 — "Claims Portfolio" (holding_type = 'claim'):
  Filter: /api/v1/holdings?holding_type=claim
  Columns: Ticker | Company | Sector | Shares | Status | Claim Authority |
           Claim Status | Expected Payout | Actual Payout | Actions
  Note: return[%] column is ABSENT from this table (claims have null return%)
  Subtotal row: sum of actual_payout (paid) or expected_payout (pending)
  Label: "Claims Portfolio" (amber dot badge)

TOTAL ASSETS ROW (below both tables):
  Single wide row spanning full width
  "Total Assets: ₦XX,XXX,XXX.XX"
  Breakdown: "Active: ₦X,XXX,XXX + Claims: ₦XXX,XXX"
  Style: gold (#DABF82) accent, DM Mono, 20px, weight 600

CLAIM DETAIL DRAWER (edit mode, admin):
  Clicking a claim row opens a right-side drawer (380px)
  Shows all ClaimRecord fields for that holding
  [+ Add Claim] button creates new ClaimRecord
  Each claim: reference number, authority, status, expected/actual payout, dates
```

---

## Part J: Open Questions Deferred to Phase 2C

These are NOT blocking Phase 2B. Log in OpenProject for future sprint:

1. **Bidirectional sync**: Should successful claim payouts update a field back in Obsidian? (Probably not — but worth deciding)
2. **Merged stocks**: Some merged stocks may have a successor company (e.g. Diamond Bank → Access Bank). Should the system link them? Requires a `successor_company_id` FK on `companies`.
3. **Price history for defunct stocks**: Should delisted stocks have price history entries up to their delisting date, or is that unnecessary complexity?
4. **Claim notifications**: When a claim status changes to 'approved' or 'paid', should the system surface an alert in the Dashboard Action Items card?

---

**END OF PHASE 2B ARCHITECTURE DOCUMENT**

**Receiving agents**:
- **Antigravity**: Execute Part G (implementation order), starting with migrations
- **Codex**: Execute Part H (tests) once migrations are complete, on `test` branch
- **Grok**: Verify `python-frontmatter` library stability and any known Obsidian YAML quirks
- **Lovable**: Execute Part I (frontend) in next UI session
