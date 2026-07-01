# Claude Handover Report — Estate Portfolio Phase 2 Design
**From**: Claude (The Brain — Architectural Review + Feature Design)
**To**: Deepseek:flash (Implementer)
**Date**: 2026-04-14
**Protocol**: MASTER_CONTEXT.md v3.0 — Zone 2 Design Output
**Input Received From**: Antigravity (Investigator Brief) + Grok (Spotter — Dashboard/Page Refinements)
**Scope**: Design decisions only. Zero implementation code. All decisions ready for Antigravity to execute.

---

## Executive Summary

The core problem is a broken data pipeline (EODHD → 402) combined with a public-facing app containing private financial data. Three feature areas fix this: **Manual Data Entry** (replaces EODHD), **Authentication** (privacy gate), and **Edit/Draft-Live Toggle** (safe editing UX). 

Additionally, given Grok's Phase 2 rewrite decision (FastAPI + React, beta subdomain), this document also addresses whether the Streamlit rewrite is the right call or if Phase 2 should be done differently. See Section 8.

---

## Section 1: Free Price Data — Recommendation

### Assessment of All Options

| Option | NGX Coverage | Reliability | Effort | Verdict |
|--------|-------------|-------------|--------|---------|
| A: NGX Daily CSV (manual upload) | ✅ Official | ✅ High | Low build, high daily use | **Primary** |
| B: Stooq.com | ❓ Unverified for XNSA | Medium | Medium | **Fallback (test first)** |
| C: investing.com scraping | ✅ Has NGX | ❌ Fragile | High (Playwright) | Reject |
| D: Manual price entry per stock | ✅ Always works | ✅ 100% | Low build, medium daily use | **Supplement to A** |
| E: Google Sheets export | ✅ If maintained | Medium | Medium | Reject (adds external dependency) |
| F: Hybrid (manual entry + CSV) | ✅ | ✅ | Low | **Selected Architecture** |

### Decision: Hybrid Manual Entry + CSV Import (Option F)

**Primary workflow** (daily, 5 minutes):
- Quick Price Update widget for top 10–15 active holdings
- Enter price, date defaults to today, one click saves

**Secondary workflow** (weekly, when NGX price sheet is available):
- Download NGX Group price sheet (Excel/CSV from ngxgroup.com)
- Upload via Bulk CSV Import with column mapping UI
- App validates, previews, then commits

**On the NGX price sheet format** [VERIFY THIS — based on known NGX Group website patterns]:
- NGX typically publishes as Excel (.xlsx) or PDF
- The Excel version has columns: Company, Ticker, Open, High, Low, Close, Volume, Date
- The app's CSV importer should accept flexible column mapping (user maps "Close" → price) rather than assuming a fixed format
- If it's PDF-only on a given day, the manual entry widget is the fallback

**Stooq.com verdict**: Worth testing with 3–5 NGX tickers before Phase 2 launch. If stooq.com returns data for `DANGCEM.XNSA` or similar, add it as an optional auto-fetch button (not a background cron — user-triggered only to avoid breaking on stooq changes). Do not build the UI around it until confirmed working.

---

## Section 2: Authentication Design Decision

### Recommendation: streamlit-authenticator (Approach 2), not Traefik BasicAuth

**Reasoning against Traefik BasicAuth:**
- The browser's native HTTP auth dialog is visually jarring and has no "remember me"
- It can't be styled or extended (no role-based access later)
- Credentials stored as bcrypt hash in docker-compose labels — that's fine for security, but it means a full container redeploy to change a password
- No audit trail, no session concept

**Reasoning for streamlit-authenticator:**
- Proper login form rendered in Streamlit itself — consistent UX
- Session-aware: once logged in, stays logged in until browser close (or configurable cookie TTL)
- Credentials in a YAML config file mounted as a Docker volume — password change = file edit + app restart (no full rebuild)
- Supports multiple users with roles (future-proof for read-only family member access)
- Library is actively maintained: `streamlit-authenticator==0.3.3` as of early 2026 [VERIFY THIS — check PyPI before pinning]

### Multi-User Design

Design for **two roles from day one**, even if only one user exists initially:

```yaml
# /configs/estate_auth.yaml (mounted as Docker volume)
credentials:
  usernames:
    zubbyik:
      name: Zubby
      password: <bcrypt_hash>  # generated with stauth.Hasher
      role: admin              # sees Edit Mode toggle
    viewer:
      name: Viewer
      password: <bcrypt_hash>
      role: readonly           # no Edit Mode toggle visible
cookie:
  name: estate_portfolio_session
  key: <random_32_char_secret>  # from .env, not hardcoded
  expiry_days: 7
```

**Role enforcement in app.py:**
- After `authenticator.login()` succeeds, check `st.session_state["role"]`
- `admin` → full app including Edit Mode toggle
- `readonly` → all pages visible but edit controls hidden

### Forgot Password

Self-hosted context, single primary user: **no automated forgot-password flow needed.** Instead:
- Document the password reset procedure in a README: edit `estate_auth.yaml`, regenerate hash with `python3 -c "import bcrypt; print(bcrypt.hashpw(b'newpass', bcrypt.gensalt()).decode())"`, restart container
- This is a 30-second operation, not worth building a reset flow

### Secrets Management

```
.env file:
  ESTATE_AUTH_COOKIE_KEY=<random_string>   # not in code
  ESTATE_AUTH_CONFIG=/app/configs/estate_auth.yaml

docker-compose.yml:
  volumes:
    - ./configs/estate_auth.yaml:/app/configs/estate_auth.yaml:ro
  environment:
    - ESTATE_AUTH_COOKIE_KEY=${ESTATE_AUTH_COOKIE_KEY}
```

The YAML file is bind-mounted read-only. To rotate passwords: edit file on server, `docker compose restart streamlit`.

---

## Section 3: Edit/Draft-Live Toggle Design Decision

### Selected Interpretation: Interpretation 1 (Edit Mode Toggle) with schema-level Draft status

**Not Interpretation 2** (full draft/publish workflow): overkill for a personal app. Adding a `status` column to every table and hiding `draft` records from the dashboard creates complexity that doesn't match the actual workflow — you're not staging corporate announcements, you're correcting a share count.

**Not Interpretation 3** (session-based preview): Streamlit's rerun model makes this extremely fragile. Holding uncommitted changes in `st.session_state` across pages is risky — a browser refresh or navigation error loses all staged changes.

### The Selected Design

**A sidebar toggle, visible only to `admin` role:**

```
[ 👁 View Mode ] ←→ [ ✏️ Edit Mode ]   (toggle in sidebar)
```

Stored in `st.session_state["edit_mode"] = True/False`.

**In View Mode (default):**
- All tables use `st.dataframe()` — read-only, clean
- No save/delete buttons visible
- Price data shown as formatted display

**In Edit Mode:**
- Tables switch to `st.data_editor()` with only specific columns editable (not IDs, not `created_at`)
- Below each table: a **[Save Changes]** button that writes only changed rows to DB
- A **[+ Add New]** expander with a form for inserting records
- A **[🗑 Soft Delete]** button per row (sets `deleted_at = NOW()`)
- A **[Restore Deleted]** sub-page in Settings showing soft-deleted records with restore option

**Draft status on Holdings only** (compromise):
- Holdings table gets a `status` column: `'draft' | 'live'`
- New holdings created in Edit Mode default to `draft`
- Dashboard and View Mode only count `live` holdings toward portfolio value
- In Edit Mode, draft holdings shown with a visual indicator (e.g., greyed out, italic)
- User explicitly clicks **[Publish]** to flip to `live`

This gives the user the ability to add a new purchase (e.g., bought GTCO yesterday) as a draft, verify the numbers, then publish — without affecting the live portfolio value display until ready.

**Why only Holdings gets draft status:**
- Price updates: always immediate (no draft needed — wrong price is obvious in the UI)
- Companies: rarely added, no staging needed
- Dividends: add as draft if unconfirmed payment, publish when received

### Interaction with Authentication

- `st.session_state["edit_mode"]` only ever becomes `True` if `st.session_state["role"] == "admin"`
- The toggle widget itself is not rendered for `readonly` role users
- Even if a readonly user somehow sets session state manually, all DB write functions check role before executing

### Streamlit `st.data_editor` Assessment

`st.data_editor` is **sufficient** for this use case with these caveats:
- Disable editing on primary key columns explicitly (`disabled=["id", "company_id", "created_at"]`)
- Use `column_config` to add validation: `st.column_config.NumberColumn(min_value=0)` for prices/shares
- For foreign keys (e.g., registrar dropdown on Companies), use `st.column_config.SelectboxColumn` with options fetched from DB
- Do **not** use `st.data_editor` for Holdings "Add New" — a proper `st.form()` with dropdowns is better for that case

---

## Section 4: Feature Backlog — Ranked by Value/Effort

Claude additions are marked with ⭐.

### P0 — Non-Negotiable (App is broken without these)

| Rank | Feature | Rationale |
|------|---------|-----------|
| 1 | **Login / Authentication** | Personal financial data is public. This is a security issue, not a feature. |
| 2 | **Quick Single-Stock Price Entry Widget** | EODHD is dead. Every dashboard metric shows ₦0 without prices. |
| 3 | **Bulk CSV Price Import** | 72 companies — manual entry one-by-one is untenable. CSV import + column mapping makes weekly updates feasible. |

### P1 — Core Usability (Needed Within 2 Weeks)

| Rank | Feature | Rationale |
|------|---------|-----------|
| 4 | **Edit Mode Toggle** | Currently impossible to fix data errors without DB access. |
| 5 | **UNIQUE constraint + dedup on holdings** | Must be fixed BEFORE edit/delete UI ships, or delete logic becomes ambiguous. |
| 6 | **Soft-Delete UI (restore deleted records)** | Schema already supports this. Completing the pattern is low effort. |
| 7 | **NGX/RapidAPI scraper button removal** | Dead code misleads the user. Remove or clearly mark "Unavailable". |
| ⭐ | **Price entry date validation** | Prevent future-dated prices; warn if date is >7 days old. Simple guard with high data quality impact. |

### P2 — High Value Investment Analytics

| Rank | Feature | Rationale |
|------|---------|-----------|
| 8 | **Dividend Yield column in Holdings** | `(annual_dividend / current_price) × 100` — a primary metric for NGX income investors. |
| 9 | **Portfolio NAV History Chart** | Store daily portfolio value snapshot; plot as line chart. Reveals performance trajectory. |
| 10 | **Bonus Issue / Rights Issue Handling** | NGX-specific. Bonus issues change share count without a purchase transaction. Without this, return % calculations are wrong after corporate actions. |
| ⭐ | **Dividend Reinvestment Tracking (DRIP)** | Some NGX companies offer scrip dividends. Track whether dividends were received as cash or shares — affects cost basis. |
| ⭐ | **Annualised Return (XIRR) per Holding** | More accurate than simple return % for holdings with multiple purchase dates. Python's `scipy.optimize` can compute XIRR from transaction history. |
| 11 | **Target Allocation / Rebalancing Tool** | Input target % per sector; app shows deviation from target. Classic portfolio management feature. |
| 12 | **Watchlist** | Track companies you're researching but haven't bought. Separate table, shown in Holdings as greyed-out "watching" rows or a dedicated page. |

### P3 — Reporting & UX Polish

| Rank | Feature | Rationale |
|------|---------|-----------|
| 13 | **Export to Excel (holdings + dividends)** | Tax calculations, auditing. `openpyxl` already common in Python stacks. |
| ⭐ | **Annual Dividend Summary (tax year view)** | Aggregate dividends by calendar year + WHT withheld. Direct input for tax filing. |
| 14 | **Stooq.com auto-fetch (user-triggered)** | Conditional on Stooq test confirming NGX coverage. If confirmed, add as "Fetch from Stooq" button per company — not a background cron. |
| 15 | **Company Research Notes** | Per-company markdown notes field. Investment thesis, AGM notes, analyst views. |
| 16 | **Mobile-Responsive CSS Tweaks** | Streamlit's mobile support is limited. At minimum, ensure the sidebar collapses properly and tables scroll horizontally. |

### P4 — Future Expansion

| Rank | Feature | Rationale |
|------|---------|-----------|
| 17 | **NGX Index Benchmark** | Compare portfolio return vs NGX All-Share Index. Needs NGX index historical data — manual CSV for now. |
| 18 | **Multi-Currency (₦ + USD)** | For Eurobonds, ADRs, or future non-NGX positions. |
| 19 | **Portfolio Comparison Across Time Periods** | "My portfolio 1Y ago vs today" — requires NAV history (P2 first). |

---

## Section 5: Answers to Antigravity's Open Questions

### Feature A (Manual Data Entry)

**Q1: Where should Quick Price Update live?**

**Decision: Dedicated "Price Entry" sub-page under a top-level "Data Entry" section in the sidebar.**

Rationale: A floating widget sounds good but adds complexity (Streamlit's overlay support is poor). Inline inputs on the Companies page would make that page cluttered and confusing for a 72-company table. A dedicated page is the cleanest pattern and matches how the user will actually use it (open Price Entry → enter prices → go check Dashboard).

The page structure:
```
Data Entry (sidebar section)
  ├── Price Entry         ← quick single + bulk CSV
  ├── Holdings Entry      ← add new purchase
  └── Dividend Entry      ← log dividend receipt
```

**Q2: Bulk CSV column format + preview?**

**Decision: Flexible column mapping with a mandatory preview step.**

Workflow:
1. User uploads CSV/Excel
2. App reads headers, shows a mapping UI: `Your Column → App Field`
   - Mandatory: `ticker`, `price`, `date`
   - Optional: `volume`, `source_note`
3. App shows a preview table (max 10 rows visible) with validation results highlighted in red
4. User clicks **[Commit X rows]** — only rows that pass validation write to DB

Validation rules:
- Price: must be numeric, > 0
- Date: must be a valid date, not in the future, not more than 30 days old (warn, not reject)
- Ticker: must exist in `companies` table (reject unknown tickers with a list of unmatched ones shown)

**Q3: Undo capability?**

**Decision: Yes, via a "Recent Price Changes" audit log on the Price Entry page.**

Not a full undo stack. Instead:
- Every price write logs to a `price_audit` table: `(company_id, old_price, new_price, changed_at, changed_by, source)`
- The Price Entry page shows the last 20 changes with a **[Revert]** button per row
- Revert writes the `old_price` back as a new current price entry (doesn't delete the audit record)

This uses soft-delete philosophy: nothing is deleted, everything is traceable.

**Q4: NGX daily price sheet format?**

As noted in Section 1 — likely Excel (.xlsx) with non-standard column names. Build the column mapping UI generically so it handles any column-name variation without code changes.

### Feature B (Authentication)

All questions answered in Section 2. Summary:
- Use `streamlit-authenticator`
- Two roles: admin + readonly
- YAML config in mounted volume
- No forgot-password automation needed
- Cookie key from `.env`

### Feature C (Edit/Draft-Live Toggle)

All questions answered in Section 3. Summary:
- Interpretation 1 (Edit Mode toggle) + draft status on Holdings table only
- `st.data_editor` is sufficient with proper column config
- Edit Mode only visible to `admin` role
- New Holdings default to `draft`, user publishes explicitly

---

## Section 6: Pre-Implementation Cleanup (Antigravity — Do These First, No Design Needed)

These are unambiguous and should be done in a single commit before Phase 2 features land:

1. **Remove `version: '3.8'`** from `docker-compose.yml` — one line delete
2. **Disable NGX Scraper + RapidAPI Scraper buttons** — wrap in `st.expander("⚠️ Unavailable Scrapers (Deprecated)", expanded=False)` with a note explaining 402 error. Do NOT delete them yet — data shows the scraper code, and removing UI before confirming the new price system works is premature.
3. **Remove `RAPIDAPI_KEY`** from `.env.example` — add comment `# Deprecated: RapidAPI scraper removed in Phase 2`
4. **Add `streamlit-authenticator==0.3.3`** to `requirements.txt` — image will rebuild on next push
5. **Add UNIQUE constraint on `holdings(company_id)`** — migration script:
   ```sql
   -- Run AFTER manually resolving any duplicate company_id rows
   -- First: find duplicates
   SELECT company_id, COUNT(*) FROM holdings WHERE deleted_at IS NULL GROUP BY company_id HAVING COUNT(*) > 1;
   -- Then: after resolving manually, add constraint
   ALTER TABLE holdings ADD CONSTRAINT holdings_company_id_unique UNIQUE (company_id);
   ```
   [VERIFY THIS: confirm no legitimate reason to have two open positions in the same company before adding this constraint]

---

## Section 7: Grok Phase 2 Rewrite Assessment (FastAPI + React)

Grok's recommendation is a full rewrite to FastAPI + React with a beta subdomain. I want to flag a concern before Antigravity acts on it.

**The concern**: The Streamlit app is working, deployed, and the user's primary problem is broken data pipeline + no auth + no edit UI. A full rewrite to FastAPI + React is a significant engineering effort that introduces new failure modes (React build pipeline, FastAPI routing, JWT auth system, separate frontend container).

**My recommendation**: Phase 2 should be **Streamlit-first** — implement Auth, Price Entry, and Edit Mode in the current Streamlit app. This delivers value in days, not weeks.

**FastAPI + React rewrite should be Phase 3**, triggered only if:
- The Streamlit app hits a genuine performance or UX ceiling (e.g., the data_editor lag is unacceptable with 72 stocks)
- The user explicitly requests a mobile-optimised frontend that Streamlit can't provide
- Collaborative features require proper API contracts (multi-user write access, etc.)

**If Grok's rewrite is already in progress**: honour it, but don't block the Auth and Price Entry features on it. Those should be shipped to the current production URL (`estate.zubbystudio.shop`) immediately while the React app develops on `demo.estate.zubbystudio.shop`.

---

## Section 8: Verification Checklist (Pass to Antigravity for Post-Implementation)

```
AUTH:
□ https://estate.zubbystudio.shop shows login form (not dashboard) for unauthenticated requests
□ Wrong credentials → error message, no access
□ Correct admin credentials → full app + Edit Mode toggle visible in sidebar
□ Correct readonly credentials → full app but NO Edit Mode toggle
□ Session persists across page navigations within same browser session
□ Direct URL to any sub-page also redirects to login if not authenticated

PRICE ENTRY:
□ Quick price entry for DANGCEM → dashboard portfolio value updates immediately on refresh
□ CSV upload with 5 rows (valid) → preview shows 5 rows, commit updates all 5
□ CSV upload with 1 invalid row (negative price) → that row highlighted red, rest can still commit
□ Ticker not in companies table → row rejected, error message names the unknown ticker
□ Price audit log shows the change with old and new price
□ Revert button on audit log → price reverts to previous value

EDIT MODE:
□ In View Mode: no edit controls visible anywhere
□ Switch to Edit Mode: data_editor appears on Holdings page, Add New expander appears
□ Edit a share count → Save Changes → DB updated → refresh shows new value
□ Add new holding as Draft → visible in Edit Mode as greyed, NOT counted in dashboard total
□ Publish holding → now counted in dashboard portfolio value
□ Soft delete a holding → disappears from Holdings (deleted_at set), appears in Settings > Restore
□ Restore deleted holding → reappears in Holdings

DATA INTEGRITY:
□ UNIQUE constraint on holdings prevents duplicate company_id INSERT
□ Obsidian re-import uses UPSERT (ON CONFLICT DO UPDATE) not bare INSERT
```

---

## Section 9: Decision Log

| Decision | Rationale | Alternative Rejected |
|----------|-----------|---------------------|
| streamlit-authenticator over Traefik BasicAuth | Session management, role support, proper UX | BasicAuth: no roles, ugly dialog, redeploy to change password |
| Edit Mode toggle (Interpretation 1) over Draft/Publish (Interpretation 2) | Personal app, single user — full staging workflow is overkill | Interpretation 2: schema complexity on every table |
| Draft status on Holdings only | Holdings is the table where staged additions matter most (new purchases) | Full draft on all tables: excessive |
| Hybrid CSV + manual price entry (Option F) | Covers both daily use (quick entry) and weekly bulk update (NGX sheet) | EODHD: 402 error, not free; Stooq: unverified for XNSA |
| Phase 2 = Streamlit first (disagree with Grok's rewrite) | Value delivery in days vs weeks; rewrite risk outweighs benefit now | FastAPI+React rewrite: deferred to Phase 3 |
| Column mapping UI for CSV import | NGX price sheet column names are not standardised | Fixed column format: breaks whenever NGX changes their export format |

---

**END OF CLAUDE HANDOVER REPORT**

**Next Agent**: Deepseek:flash (Implementation)
**Implementation Order**: 
1. Pre-implementation cleanup (Section 6)
2. Authentication (streamlit-authenticator, two roles)
3. Quick Price Entry widget + Price Audit Log
4. Bulk CSV Import with column mapping + preview
5. Edit Mode toggle + Holdings draft status
6. Soft-delete UI in Settings
7. UNIQUE constraint on holdings (after dedup)

**Blockers Before Starting**:
- Confirm whether Grok's FastAPI+React rewrite is proceeding in parallel or replacing this plan
- Manually check `holdings` table for duplicate `company_id` rows before adding UNIQUE constraint
- Test 2–3 NGX tickers on Stooq.com to determine if Option B is viable as an automated fallback
