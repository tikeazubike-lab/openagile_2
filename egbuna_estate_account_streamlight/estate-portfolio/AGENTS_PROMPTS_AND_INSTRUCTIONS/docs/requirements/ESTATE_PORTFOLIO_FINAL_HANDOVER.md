# Estate Portfolio — Phase 2 Final Handover Brief
## Claude (The Brain) → Deepseek:flash (Implementer)

**From**: Claude (The Brain — Architecture + Design)
**To**: Deepseek:flash (Implementer)
**Verified By**: Grok (Zone 2 Spotter — 2026-04-17)
**Date**: 2026-04-17
**Protocol**: MASTER_CONTEXT.md v3.0 — Handover Protocol
**Status**: ALL DECISIONS LOCKED. No open questions remain. Ready for implementation.

---

## Part A: Role Bifurcation Architecture

This section defines who owns what across every layer of the system. This is the primary architectural contract for the rebuild.

---

### The Fundamental Split

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOVABLE.DEV BOUNDARY                         │
│  Owns: React components, pages, routing, UI state, API calls    │
│  Delivers: /frontend/src/ directory, complete and deployable    │
└─────────────────────────────────────────────────────────────────┘\n                              │\n                    HTTP/JSON over REST API\n                    /api/v1/... endpoints\n                              │\n┌─────────────────────────────────────────────────────────────────┐\n│                    DEEPSEEK:FLASH BOUNDARY                         │\n│  Owns: FastAPI, SQLAlchemy, Alembic, business logic, Docker     │\n│  Delivers: /backend/ directory, database migrations, CI/CD      │\n└─────────────────────────────────────────────────────────────────┘
                              │
                    asyncpg / SQLAlchemy 2.0
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (EXISTING)                          │
│  openagile_postgres — estate_portfolio DB                       │
│  Owned by: Infrastructure (Netcup VPS)                         │
└─────────────────────────────────────────────────────────────────┘
```

---

### Layer-by-Layer Responsibility Map

#### Layer 1: Database (PostgreSQL)
**Owner**: Infrastructure / Deepseek:flash (via Alembic migrations)
**Lovable touches**: Never. Zero database access from frontend code.

```
Responsible for:
- Table schema (existing + new additive migrations)
- Indexes, constraints, foreign keys
- Soft delete pattern (deleted_at column)
- Computed columns (gain_loss in nav_history)
- No business logic in SQL — only structure and constraints
```

#### Layer 2: Backend Services (FastAPI)
**Owner**: Deepseek:flash
**Lovable touches**: Never. Lovable only calls the API, never writes backend code.

```
Responsible for:
- All database reads/writes via SQLAlchemy async ORM
- All business logic computations (return %, NAV, XIRR, rebalancing gap)
- JWT issuance and verification
- Role enforcement (require_admin dependency)
- CSV/Excel parsing and validation
- APScheduler (NAV snapshots)
- Soft delete logic
- Price audit logging
- Corporate action → transaction auto-generation
- Obsidian import processing
```

#### Layer 3: API Contract (REST Endpoints)
**Owner**: Jointly defined here — Deepseek:flash implements, Lovable consumes
**This document is the contract. Neither side deviates from it.**

```
Rules:
- All endpoints under /api/v1/
- All responses: JSON with consistent envelope:
  {
    "data": <payload>,
    "meta": { "total": N, "page": N },   // for lists
    "error": null                          // or error object
  }
- All timestamps: ISO 8601 UTC strings
- All monetary values: strings with 2 decimal places ("12345.50") — 
  NOT floats, to avoid JS float precision issues
- Soft-deleted records: never returned unless ?include_deleted=true (admin only)
- Draft records: never returned to 'readonly' role users
- HTTP status codes: 200 OK, 201 Created, 400 Validation Error,
  401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable
```

#### Layer 4: React Application
**Owner**: Lovable.dev (frontend) + Deepseek:flash (integration wiring)

```
Lovable owns:
- All React components and pages
- TypeScript interfaces matching API response shapes
- TanStack Query hooks (useHoldings, useDashboard, etc.)
- Zustand store (auth state, edit mode toggle)
- React Router routes and navigation
- All visual design (dark theme, typography, charts, tables)
- Form validation with React Hook Form + Zod
- Role-conditional rendering (admin vs readonly)
- Responsive layout (desktop sidebar ↔ mobile bottom nav)

Deepseek:flash owns (after Lovable delivers):
- Wiring Vite build output into /backend/app/static/
- Updating GitHub Actions to npm ci && npm run build before Docker build
- Verifying CORS config in FastAPI matches production domain
- Confirming httpOnly cookie flows correctly through Traefik
```

---

### User Role Bifurcation (Application Level)

Two roles. Every UI element is conditionally rendered based on `user.role`.

#### Admin Role (`role: "admin"`)
```
Full access:
✅ All pages visible
✅ Edit Mode toggle visible in top navbar
✅ In Edit Mode: inline editing, Add New forms, Soft Delete buttons
✅ Holdings: can create draft, publish, restore deleted
✅ Transactions: can create, edit, publish, soft-delete
✅ Price Entry page (quick + bulk CSV)
✅ Corporate Actions page
✅ Settings → User Management
✅ Settings → Deleted Records (restore)
✅ Settings → Sector Targets (for rebalancing)
✅ Price audit log with revert buttons
✅ NAV History manual snapshot trigger
```

#### Readonly Role (`role: "readonly"`)
```
Read access only:
✅ Dashboard
✅ Holdings (live records only, no draft rows visible)
✅ Companies
✅ Dividends
✅ Transactions (live records only)
✅ Price History
✅ NAV History (chart, no manual snapshot)
✅ Watchlist (view only)
✅ Rebalancing (view only — no target editing)
✅ Registrars

❌ Edit Mode toggle — not rendered
❌ Price Entry page — not in navigation
❌ Settings (entire section hidden)
❌ Corporate Actions — not in navigation
❌ Any form, edit button, delete button, publish button
❌ Draft records — API enforces, frontend also hides
```

#### How Role is Communicated to React
```typescript
// On login, API returns:
{
  "data": {
    "access_token": "...",    // set as httpOnly cookie by FastAPI
    "user": {
      "id": 1,
      "username": "zubbyik",
      "name": "Zubby",
      "role": "admin"         // "admin" | "readonly"
    }
  }
}

// React stores user in Zustand:
// src/store/authStore.ts
interface AuthStore {
  user: { id: number; name: string; role: 'admin' | 'readonly' } | null;
  isAdmin: () => boolean;
  setUser: (user) => void;
  clearUser: () => void;
}

// Usage in any component:
const { user, isAdmin } = useAuthStore();
{isAdmin() && <EditModeToggle />}
{isAdmin() && <button>Delete</button>}
```

---

### Edit Mode Bifurcation (Admin-Only UI State)

Edit Mode is a Zustand boolean, only settable by admin role.

```
VIEWING MODE (default for both roles):
- st.dataframe equivalent → TanStack Table, read-only
- No add/edit/delete buttons visible
- Draft holdings: completely hidden
- Clean, dense data display

EDITING MODE (admin only, toggle in top navbar):
- TanStack Table switches to editable mode
- "Add New" expandable form appears below each table
- Soft Delete (🗑) button appears per row
- Draft holdings appear with amber left border + "DRAFT" badge
- "Publish" button appears on draft rows
- Price Entry prominently available in sidebar
```

---

## Part B: Complete API Contract (Lovable's Integration Reference)

This is the definitive endpoint list Lovable uses to build API hooks. Deepseek:flash implements these exactly.

### Auth Endpoints
```
POST   /api/v1/auth/login
  Body:    { "username": string, "password": string }
  Returns: { data: { user: UserOut }, error: null }
  Side effect: Sets httpOnly JWT cookie

POST   /api/v1/auth/logout
  Returns: 200 OK, clears cookie

GET    /api/v1/auth/me
  Returns: { data: UserOut }
  Use: On app load to restore session

PUT    /api/v1/auth/change-password     [admin only]
  Body: { "current_password": string, "new_password": string }
```

### Dashboard
```
GET    /api/v1/dashboard
  Returns: {
    data: {
      total_portfolio_value: string,    // "₦12,345,678.00"
      total_invested: string,
      unrealised_gain_loss: string,
      unrealised_gain_pct: string,      // "+12.34"
      total_holdings: number,
      sector_allocation: [              // for donut chart
        { sector: string, value: string, pct: string }
      ],
      top_holdings: [                   // for bar chart (top 10)
        { ticker: string, company: string, value: string, return_pct: string }
      ],
      recent_transactions: [            // live only, last 5
        { date: string, ticker: string, type: string, shares: number, amount: string }
      ],
      last_updated: string              // ISO timestamp of last price update
    }
  }
```

### Companies
```
GET    /api/v1/companies
  Query: ?search=string, ?sector=string, ?status=active|inactive
  Returns: { data: CompanyOut[], meta: { total: N } }

POST   /api/v1/companies              [admin only]
  Body: CompanyIn

PUT    /api/v1/companies/{id}         [admin only]
  Body: CompanyIn (partial)

DELETE /api/v1/companies/{id}         [admin only]
  Action: Sets deleted_at (soft delete)
```

### Holdings
```
GET    /api/v1/holdings
  Returns: {
    data: [{
      id, company_id, ticker, company_name, sector,
      num_shares: number,
      avg_purchase_price: string,
      current_price: string,
      current_value: string,
      cost_basis: string,
      return_pct: string,             // "return[%]" column header in UI
      dividend_yield: string,
      status: "draft" | "live",
      last_price_update: string
    }]
  }
  Note: readonly role never sees status=draft rows (API enforces)

POST   /api/v1/holdings              [admin only]
  Body: { company_id, num_shares, avg_purchase_price, notes? }
  Defaults: status = "draft"
  Side effect: auto-creates a "buy" transaction record

PUT    /api/v1/holdings/{id}         [admin only]

PUT    /api/v1/holdings/{id}/publish [admin only]
  Action: Sets status = "live"

DELETE /api/v1/holdings/{id}         [admin only]
  Action: Soft delete

GET    /api/v1/holdings/deleted      [admin only]
  Returns: soft-deleted holdings list

PUT    /api/v1/holdings/{id}/restore [admin only]
```

### Prices
```
GET    /api/v1/prices
  Returns: current price for all companies

POST   /api/v1/prices/quick          [admin only]
  Body: { "company_id": N, "price": "123.45", "date": "2026-04-17" }
  Side effect: writes to price_audit table

POST   /api/v1/prices/bulk-csv       [admin only]
  Body: multipart/form-data, file upload
  Stage 1: POST → returns { preview: rows[], errors: rows[], column_mapping_needed: bool }
  Stage 2: POST with confirmed mapping → commits valid rows
  Returns: { updated: N, skipped: N, skipped_reasons: [...] }

GET    /api/v1/prices/history/{company_id}
  Query: ?from=date&to=date
  Returns: [{ date, price, source }]

GET    /api/v1/prices/audit          [admin only]
  Returns: last 50 price changes with old/new values

POST   /api/v1/prices/audit/{id}/revert  [admin only]
```

### Dividends
```
GET    /api/v1/dividends
  Query: ?year=N, ?company_id=N
  Returns: DividendOut[] with wht_amount computed

POST   /api/v1/dividends             [admin only]
PUT    /api/v1/dividends/{id}        [admin only]
DELETE /api/v1/dividends/{id}        [admin only]

POST   /api/v1/dividends/bulk-csv    [admin only]
  Same two-stage flow as price CSV import

GET    /api/v1/dividends/summary
  Returns: [{ year: N, gross_total: string, wht_total: string, net_total: string }]
```

### Transactions
```
GET    /api/v1/transactions
  Query: ?company_id=N, ?type=buy|sell|bonus_receipt|rights_subscription,
         ?from=date, ?to=date, ?status=draft|live
  Returns: TransactionOut[] (readonly role: live only)

POST   /api/v1/transactions          [admin only]
  Body: {
    transaction_date, ticker, transaction_type, num_shares,
    price_per_share, net_amount, broker_fee?, notes?,
    status: "draft" | "live",
    reference_id?, linked_holding_id?
  }

PUT    /api/v1/transactions/{id}     [admin only]
PUT    /api/v1/transactions/{id}/publish  [admin only]
DELETE /api/v1/transactions/{id}     [admin only]

POST   /api/v1/transactions/bulk-csv [admin only]
  Expects: transaction_type column in CSV
```

### Registrars
```
GET    /api/v1/registrars
  Returns: registrar list, each with companies: CompanyOut[] (expandable)

POST   /api/v1/registrars            [admin only]
PUT    /api/v1/registrars/{id}       [admin only]
DELETE /api/v1/registrars/{id}       [admin only]
```

### Watchlist
```
GET    /api/v1/watchlist
POST   /api/v1/watchlist             [admin only]
PUT    /api/v1/watchlist/{id}        [admin only]
DELETE /api/v1/watchlist/{id}        [admin only]
```

### NAV History
```
GET    /api/v1/nav-history
  Query: ?from=date&to=date
  Returns: [{ snapshot_date, total_value, total_cost, gain_loss }]

POST   /api/v1/nav-history/snapshot  [admin only]
  Triggers manual snapshot computation
```

### Rebalancing
```
GET    /api/v1/rebalancing
  Returns: [{
    sector, current_value, current_pct,
    target_pct, gap_pct,      // positive = overweight
    gap_direction: "over" | "under" | "on-target"
  }]

GET    /api/v1/sector-targets
PUT    /api/v1/sector-targets         [admin only]
  Body: [{ sector_name, target_pct }]
```

### Corporate Actions
```
GET    /api/v1/corporate-actions
  Query: ?company_id=N
POST   /api/v1/corporate-actions      [admin only]
  Body: { company_id, action_type, action_date, ratio_numerator, ratio_denominator, notes? }
  Side effect: auto-generates linked transaction record
PUT    /api/v1/corporate-actions/{id} [admin only]
```

---

## Part C: Wireframe Specification for Lovable.dev

This is a complete written wireframe description for every page and component. Lovable should implement these pixel-by-pixel as the design brief.

---

### Design System (Apply Globally)

```
COLOR PALETTE:
  Background:       #0d1117   (near-black — main canvas)
  Surface:          #161b22   (cards, sidebar, modals)
  Surface-elevated: #1c2128   (hover states, selected rows)
  Border:           #30363d   (dividers, table borders)
  Text-primary:     #e6edf3   (headings, important values)
  Text-secondary:   #8b949e   (labels, metadata)
  Text-muted:       #484f58   (placeholder, disabled)

  Accent-green:     #10b981   (gains, positive %, live badges)
  Accent-red:       #ef4444   (losses, negative %, error states)
  Accent-amber:     #f59e0b   (draft status, warnings)
  Accent-blue:      #58a6ff   (links, active nav, primary buttons)
  Accent-purple:    #a78bfa   (watchlist, secondary highlights)

TYPOGRAPHY:
  Numbers/Tickers:  'DM Mono', monospace — all monetary values, share counts, %
  UI Text:          'Geist', sans-serif — labels, nav, buttons, body
  Headings:         'Geist', weight 600-700

SPACING: 8px base grid. Padding multiples: 8, 16, 24, 32, 48
BORDER RADIUS: 6px (cards, inputs), 4px (badges, tags), 999px (pills)

SHADOWS:
  Card shadow: 0 1px 3px rgba(0,0,0,0.4)
  Modal shadow: 0 8px 32px rgba(0,0,0,0.6)
```

---

### Component: Top Navigation Bar

```
┌──────────────────────────────────────────────────────────────────────┐
│  [≡ MENU]  Estate Portfolio              [● VIEWING ↔ ✏ EDITING]  [👤]│
└──────────────────────────────────────────────────────────────────────┘

HEIGHT: 56px
BACKGROUND: #161b22 with bottom border 1px #30363d
POSITION: fixed top, full width, z-index 50

LEFT: Hamburger menu icon (mobile only — collapses sidebar)
      "Estate Portfolio" wordmark in Geist 500 weight, text-primary
CENTER: Empty on desktop
RIGHT:
  - Edit Mode Toggle (admin only):
    Pill toggle, 120px wide
    VIEWING state: green dot + "Viewing" text, background #1c2128
    EDITING state: amber pencil + "Editing" text, background #2d2006, border amber
    Smooth 200ms transition between states
  - User avatar circle (initials), 32px, background accent-blue
    Click → dropdown: "Profile", "Change Password", "Sign Out"

BETA BANNER (demo subdomain only):
  Thin 28px bar above navbar, full width
  Background: #1a1a2e, text: "BETA — demo.estate.zubbystudio.shop"
  Amber text, centered, 12px font
```

---

### Component: Sidebar Navigation

```
WIDTH: 240px (desktop), hidden (mobile — slides in from left)
BACKGROUND: #161b22
BORDER-RIGHT: 1px solid #30363d
POSITION: fixed left, below navbar, full height

TOP SECTION — Logo area (48px):
  "EPM" monogram in accent-blue, 24px, DM Mono

NAVIGATION ITEMS (48px each):
  Icon (20px Lucide) + Label + optional badge

  MAIN:
  📊 Dashboard
  💼 Holdings           [DRAFT count badge if any drafts exist — amber pill]
  🏢 Companies
  💰 Dividends
  📈 Price History
  🔄 Transactions       [DRAFT count badge]
  📋 Registrars
  👁 Watchlist
  📉 NAV History
  ⚖️ Rebalancing

  ADMIN ONLY (shown below a divider):
  ⚙️ Settings
    └── Price Entry      [highlighted, accent-blue bg — used daily]
    └── Data Import
    └── Corporate Actions
    └── User Management
    └── Deleted Records

ACTIVE STATE: Left border 3px accent-blue, background #1c2128, text-primary
HOVER STATE: Background #1c2128, text-primary
INACTIVE STATE: text-secondary

MOBILE:
  Bottom navigation bar (5 most important items):
  [Dashboard] [Holdings] [Prices] [Dividends] [More ↑]
  "More" opens a bottom sheet with remaining nav items
```

---

### Page: Login

```
LAYOUT: Centered card on full-screen background
BACKGROUND: #0d1117 with subtle dot-grid pattern (opacity 0.05)

CARD: 400px wide, #161b22, border #30363d, border-radius 12px, padding 40px

CONTENT TOP-TO-BOTTOM:
  - "EPM" monogram, 48px, accent-blue, centered
  - "Estate Portfolio" heading, Geist 700, 24px, text-primary, centered
  - "Personal Investment Tracker" subtitle, 14px, text-secondary, centered
  - 32px gap
  - Username input field:
      Label: "Username", 12px, text-secondary, uppercase tracking-wide
      Input: full width, 44px height, #0d1117 bg, border #30363d,
             border-radius 6px, text-primary, DM Mono font
      Focus: border accent-blue, subtle blue glow
  - 16px gap
  - Password input field: same styling + show/hide toggle icon (eye)
  - 24px gap
  - "Sign In" button:
      Full width, 44px, background accent-blue, text white, Geist 500
      Hover: slightly lighter blue
      Loading state: spinner replaces text
  - Error message: 12px, accent-red, below button, fade-in animation

FOOTER: "Estate Portfolio Manager v2.0" — 12px text-muted, centered
```

---

### Page: Dashboard

```
LAYOUT: Full width minus sidebar. Padding 24px.

SECTION 1 — KPI Cards (top, 4 cards in a row, each 25% wide)
  CARD STRUCTURE: #161b22 bg, 1px border #30363d, 16px padding, 6px radius

  Card 1: Total Portfolio Value
    Label: "TOTAL VALUE" — 11px, text-muted, uppercase, tracking-wide
    Value: "₦12,345,678.00" — DM Mono, 28px, text-primary, COUNTS UP FROM 0 ON LOAD
    Sub: "+₦1,234,567.00 (12.34%)" — green if positive, red if negative, 13px

  Card 2: Total Invested
    Value in DM Mono 28px, text-primary
    Sub: "Cost basis across all holdings"

  Card 3: Unrealised Gain/Loss
    Value: large, green or red based on sign
    Sub: percentage, same color

  Card 4: Total Holdings
    Value: count number, 28px, text-primary
    Sub: "X live · Y draft" (admin only — draft count)

SECTION 2 — Charts Row (below KPIs, 2 columns: 40% + 60%)
  LEFT — Sector Allocation Donut (40%):
    Recharts PieChart, 240px diameter
    Centre label: "Sector\nAllocation"
    Legend below chart: color dot + sector name + percentage
    Colors: distinct palette for up to 10 sectors
    Hover: tooltip shows ₦ value + %

  RIGHT — Top 10 Holdings Bar (60%):
    Horizontal bar chart, Recharts
    Y-axis: ticker symbols, DM Mono
    X-axis: value in ₦
    Bars: gradient from accent-blue to accent-purple
    Each bar has return % label at end: "+12.3%" in green/red

SECTION 3 — Bottom Row (2 columns: 60% + 40%)
  LEFT — Recent Transactions (last 5 live only):
    Simple table, no header (just rows):
    [date] [ticker] [type badge] [shares] [amount]
    type badges: "BUY" green pill, "SELL" red pill, "BONUS" purple pill
    "View all →" link to Transactions page

  RIGHT — Action Items Card:
    Title: "Action Items" 14px, text-secondary
    Content: 
      - If any draft holdings: "X holdings pending publish" → amber badge, clickable
      - If any draft transactions: "X transactions pending review" → amber badge
      - If prices > 7 days old: "Prices not updated in 8 days" → red warning
      - If all clear: large green checkmark + "Portfolio up to date"
    "Last Updated: YYYY-MM-DD HH:MM WAT" timestamp, 12px, text-muted, bottom-right

MOBILE DASHBOARD:
  KPI cards: 2x2 grid
  Charts: stacked vertically, full width
  Recent Transactions: below charts
```

---

### Page: Holdings

```
LAYOUT: Full width, padding 24px

HEADER ROW:
  Left: "Holdings" h1 + "(N positions)" subtitle
  Right (admin, Editing mode):
    [+ Add Holding] button — accent-blue
    [↓ Export] dropdown — CSV or Excel

FILTER ROW (below header):
  [Search by ticker/name...] [Sector ▼] [Status: All ▼] [Sort by ▼]
  Status filter: "All" | "Live" | "Draft" (Draft option admin-only)

TABLE (TanStack Table, full width):
  Columns:
  | Ticker  | Company Name     | Sector    | Shares   | Avg Cost | Current Price | Current Value | Cost Basis | return[%]  | Div Yield | Status  | Actions |
  | DM Mono | text-secondary   | pill badge| DM Mono  | DM Mono  | DM Mono       | DM Mono 600   | DM Mono    | +12.3% green| 4.5%     | badge   | icons   |

  RETURN[%] COLUMN:
    Positive: accent-green, prefix "+"
    Negative: accent-red, prefix "-"
    Zero: text-muted

  STATUS COLUMN (admin only in Editing mode):
    "LIVE" — small green pill
    "DRAFT" — small amber pill
    
  DRAFT ROWS VISUAL TREATMENT:
    Left border: 3px solid accent-amber
    Row background: rgba(245, 158, 11, 0.05)
    All values slightly muted (opacity 0.7)
    DRAFT badge in Status column

  ACTIONS COLUMN (Editing mode, admin only):
    Live row: [✏ Edit] [🗑 Delete]
    Draft row: [✏ Edit] [✓ Publish] [🗑 Delete]

  READONLY MODE:
    No Actions column
    No draft rows visible
    Clean, dense table

  PAGINATION: 25 rows per page, bottom-right
  STICKY HEADER: yes
  STICKY FIRST COLUMN (Ticker): yes on mobile

ADD NEW HOLDING (Editing mode, admin):
  Expandable panel below table header, slides down
  Form fields:
    Company: searchable dropdown (typeahead from /api/v1/companies)
    Shares: number input, DM Mono
    Average Purchase Price (₦): number input, DM Mono
    Purchase Date: date picker
    Notes: textarea (optional)
    Status: toggle "Draft" | "Publish immediately"
  [Cancel] [Save as Draft] or [Save & Publish]
  On save: new row animates into table

EDIT HOLDING (inline panel, same design as Add New):
  Pre-filled with existing values
  [Cancel] [Save Changes]
```

---

### Page: Price Entry (Settings → Price Entry)

```
LAYOUT: Two-column, 55% left + 45% right

LEFT COLUMN — Quick Price Update:
  Heading: "Quick Price Update" + subtitle "Update a single stock price"
  
  Form:
    Company/Ticker: searchable dropdown
      Shows: [TICKER] Company Name — current price ₦XX.XX
    New Price (₦): large number input, DM Mono 24px
    Date: date picker, defaults to today
    [Update Price] button — accent-blue, full width
  
  Feedback:
    Success: green checkmark + "DANGCEM updated to ₦123.45"
    Error: red message

  ── PRICE AUDIT LOG ──
  Heading: "Recent Changes" (last 20)
  Table:
  | Date     | Ticker  | Old Price | New Price | Change   | Source | [Revert] |
  | DM Mono  | DM Mono | DM Mono   | DM Mono   | +3.2%    | badge  | link     |
  Source badges: "manual" text-secondary, "csv_upload" blue, "stooq_csv" purple
  Revert: small text link, opens confirmation dialog

RIGHT COLUMN — Bulk CSV Import:
  Heading: "Bulk CSV Import"
  Subtitle: "Upload NGX price sheet or Stooq CSV output"

  STEP 1 — Upload Zone:
    Dashed border rectangle, 200px height
    Icon: cloud upload
    "Drag & drop CSV or Excel file here"
    "or click to browse"
    Accepted: .csv, .xlsx, .xls
    Note: "💡 Running the Stooq scraper? See README → Price Data Sources for instructions."
    [Browse File] button

  STEP 2 — Column Mapping (appears after upload):
    Heading: "Map your columns"
    Card per required field:
      "Ticker" → [Symbol ▼] (dropdown of detected headers)
      "Price"  → [Close  ▼]
      "Date"   → [Date   ▼]
    Optional: "Volume" → [Skip ▼]
    [Preview Data →] button

  STEP 3 — Preview Table (appears after mapping):
    Shows first 10 rows
    Valid rows: normal display
    Error rows: red left border + error tooltip
    Unknown ticker rows: amber + "Unknown ticker: TEXACO" note
    Summary: "47 valid · 3 errors · 2 unknown tickers"
    [← Back] [Commit 47 rows] button

  STEP 4 — Result (after commit):
    Large checkmark animation
    "47 prices updated successfully"
    "3 rows skipped — see details below"
    Skipped rows table: ticker + reason
    [Import Another File] button
```

---

### Page: Companies

```
LAYOUT: Full width, padding 24px

HEADER ROW:
  "Companies" h1 + "(72 companies)" count
  Right (admin, Editing): [+ Add Company]

FILTER ROW:
  [Search...] [Sector ▼] [Registrar ▼] [Status: Active ▼]

TABLE:
  | Ticker  | Company Name          | Sector   | ISIN         | Registrar (link) | Status | Actions |
  | DM Mono | text-primary          | pill     | DM Mono sm   | blue link        | badge  |         |

  Registrar cell: clickable → navigates to /registrars/{id}

  EDIT COMPANY (inline sliding panel, Editing mode):
    Ticker (read-only if existing)
    Company Name
    Sector: dropdown
    ISIN
    Registrar: searchable dropdown
    Status: Active / Inactive
    [Save] [Cancel]
```

---

### Page: Dividends

```
LAYOUT: Full width, padding 24px

HEADER + TABS:
  "Dividends" h1
  Tabs: [All Dividends] [Annual Summary] [Import CSV]

TAB 1 — All Dividends:
  Filter: [Year ▼] [Company ▼] [Source ▼]
  Table:
  | Date | Ticker | Gross/Share | Shares | Gross Total | WHT (10%) | Net Received | Source | DRIP? | Actions |
  
  DRIP column: checkmark icon if is_scrip = true, "-" otherwise
  Source badges: "manual", "csv", "api (future)"

TAB 2 — Annual Summary:
  Year-by-year aggregated view:
  | Year | Gross Total | Total WHT | Net Received |
  | 2024 | ₦234,567    | ₦23,456   | ₦211,111     |
  Large running total card at bottom: "Lifetime Dividends Received: ₦X,XXX,XXX"

TAB 3 — Import CSV:
  Same two-stage flow as Price Entry CSV import
  Required columns: ticker, date, gross_per_share, shares
  Optional: source, is_scrip, scrip_shares

ADD DIVIDEND (Editing mode):
  Inline form above table
  Fields: Company (dropdown), Date, Gross per share, Shares held, WHT rate (default 10%, editable), Is DRIP? toggle
```

---

### Page: Transactions

```
LAYOUT: Full width, padding 24px

HEADER:
  "Transactions" h1
  Right (admin, Editing): [+ Add Transaction] [Import CSV]

FILTER ROW:
  [Search ticker...] [Type ▼: Buy/Sell/Bonus/Rights] [Date range] [Status ▼]

TABLE:
  | Date     | Ticker  | Type    | Shares   | Price/Share | Net Amount | Broker Fee | Notes | Status | Ref ID | Actions |
  | DM Mono  | DM Mono | badge   | DM Mono  | DM Mono     | DM Mono 600| DM Mono sm | trunc | badge  | sm     |         |

  TYPE BADGES:
    "BUY" — green pill
    "SELL" — red pill
    "BONUS" — purple pill
    "RIGHTS" — blue pill

  AUTOGENERATED ROWS (from corporate actions or holdings):
    Small "AUTO" grey badge in Notes/Ref column
    Cannot be manually edited (Edit button greyed, tooltip: "Auto-generated from Holdings")

  DRAFT ROWS: same amber treatment as Holdings

EMPTY STATE:
  Large empty-inbox icon
  "No transactions recorded yet."
  "Add via Holdings page or import a CSV."
  [Go to Holdings] button
```

---

### Page: NAV History

```
LAYOUT: Full width, padding 24px

HEADER:
  "Portfolio NAV History" h1
  Right (admin): [▶ Take Snapshot Now] button

CHART SECTION:
  Full-width area chart (Recharts AreaChart)
  HEIGHT: 360px
  X-axis: dates (auto-scaled)
  Y-axis: ₦ value (DM Mono, formatted)
  Two areas stacked:
    Total Value (accent-blue, 0.3 opacity fill)
    Total Cost/Invested (accent-purple, 0.2 opacity fill)
  Hover tooltip: date + value + cost + gain/loss + gain%

DATE RANGE FILTER (above chart):
  [1M] [3M] [6M] [1Y] [All]  — pill buttons, active = accent-blue

SUMMARY STATS ROW (below chart, 3 cards):
  "Best Day" — date + gain amount
  "Worst Day" — date + loss amount
  "Since Inception" — total return %

DATA TABLE (below cards):
  | Date | Portfolio Value | Total Invested | Daily Gain/Loss | Cumulative Return |
  Collapsible, shows last 30 rows by default, "Show All" toggle
```

---

### Page: Rebalancing

```
LAYOUT: Full width, padding 24px

HEADER:
  "Portfolio Rebalancing" h1
  Subtitle: "Compare current allocation vs targets"
  Right (admin): [Edit Targets] button → opens side drawer

ALLOCATION TABLE + VISUAL (full width):
  | Sector       | Current Value | Current % | Target % | Gap      | Action         |
  | Banking      | ₦4,567,890   | 35.2%     | 30.0%    | +5.2%    | [Reduce]       |
  | Consumer     | ₦2,345,678   | 18.1%     | 20.0%    | -1.9%    | [Increase]     |
  | Oil & Gas    | ₦1,890,123   | 14.6%     | 15.0%    | -0.4%    | ≈ On Target    |

  GAP COLUMN:
    Positive (overweight): accent-red + "▲ +5.2%"
    Negative (underweight): accent-amber + "▼ -1.9%"
    ≈ 0 (±0.5%): accent-green + "≈ On Target"

  VISUAL BAR per row (between Current % and Target %):
    Current % bar: solid accent-blue
    Target % marker: vertical dashed line
    Excess: red extension beyond target
    Deficit: amber dotted extension to target

EDIT TARGETS DRAWER (admin, slides from right, 400px):
  Title: "Sector Target Allocation"
  Subtitle: "Must sum to 100%"
  Running total: "Current total: 98% ⚠️" or "100% ✓"
  
  Per sector row:
    [Sector Name] [XX.X%] ← editable number input
  [Add Sector] link
  [Save Targets] button (disabled if total ≠ 100%)
```

---

### Page: Registrars

```
TABLE:
  | Name | Email | Phone | Address | Rating | Companies | Actions |

  COMPANIES COLUMN:
    Shows count badge: "12 companies"
    Click → expands accordion row below showing company list
    Each company: [TICKER] Name — clickable link to Company detail

  RATING: 1–5 star display (read) or star picker (Editing mode)
```

---

### Page: Watchlist

```
TABLE:
  | Ticker | Company | Sector | Current Price | Target Price | Gap to Target | Notes | Added | Actions |

  GAP TO TARGET:
    If current < target: accent-green "▼ -15.3% to buy"
    If current > target: accent-red "▲ +8.2% above target"
    If no target set: text-muted "—"

  ACTIONS (admin, Editing): [✏ Edit] [+ Add to Holdings] [🗑 Remove]
  
  "Add to Holdings" button: one-click shortcut to Holdings → Add New form, pre-filled with ticker
```

---

### Page: Settings

```
LAYOUT: Two-panel — settings nav (left, 200px) + content (right)

SETTINGS NAV (admin only):
  › Price Entry          ← highlighted (most used)
  › Data Import
  › Corporate Actions
  › User Management
  › Deleted Records

SETTINGS: User Management
  Table: | Username | Name | Role | Last Login | Status | Actions |
  [+ Add User] button
  Actions: [Reset Password] [Deactivate]
  Cannot delete own account

SETTINGS: Deleted Records
  Tabs: [Holdings] [Transactions] [Companies] [Dividends]
  Each tab shows soft-deleted records with:
    | Ticker | Name | Deleted Date | Deleted By | [Restore] |
  Restore: confirmation dialog → sets deleted_at = NULL
```

---

### Component: Mobile Responsive Rules

```
BREAKPOINTS:
  Desktop: ≥ 1024px — sidebar visible, full tables
  Tablet:  768–1023px — sidebar collapses to icon-only (48px wide)
  Mobile:  < 768px — sidebar hidden, bottom nav bar

MOBILE TABLE HANDLING:
  Sticky first column (Ticker/Company)
  Horizontal scroll for remaining columns
  Minimum column widths enforced
  Sortable columns still work via tap

MOBILE BOTTOM NAV (5 items):
  [📊] [💼] [💰] [📈] [⋯]
  Active: accent-blue icon + label, 2px top border
  
MOBILE CARDS (Dashboard KPIs):
  2×2 grid, equal width
  Full-width on very small screens (< 375px)

MOBILE PRICE ENTRY:
  Single column (stack left+right panels)
  Quick entry form first, CSV import second
```

---

### Component: Empty States

Every table/list has a designed empty state (not just a blank area):

```
Holdings (empty):
  Icon: briefcase outline, 64px, text-muted
  "No holdings yet"
  "Add your first holding to start tracking your portfolio"
  [+ Add Holding] button (admin only)

Transactions (empty):
  Icon: list outline
  "No transactions recorded yet."
  "Add via Holdings page or import a CSV."

Watchlist (empty):
  Icon: eye outline
  "Your watchlist is empty"
  "Track companies you're researching before investing"
  [+ Add to Watchlist] button

NAV History (empty):
  Icon: chart-line outline
  "No history yet"
  "Portfolio snapshots are taken daily at 18:00 WAT."
  [Take Snapshot Now] button (admin)
```

---

### Component: Loading States

```
KPI CARDS: Skeleton shimmer (grey animated gradient) while fetching
TABLES: 5 skeleton rows, column widths matching actual data
CHARTS: Pulsing placeholder area matching chart dimensions
PRICES: Inline spinner next to last-updated timestamp
```

---

## Part D: Implementation Order for Deepseek:flash

All decisions locked. Implement in this exact sequence:

### Phase 2A — Foundation
1. Repo restructure: `backend/`, `frontend/`, `scripts/stooq_scraper/`
2. FastAPI skeleton: `main.py`, `config.py`, `database.py` (async SQLAlchemy + asyncpg)
3. Alembic: migrations for all existing tables + 6 new tables from rebuild spec
4. Auth system: `users` table, JWT httpOnly cookie, `require_admin` dependency
5. React skeleton: Vite + TypeScript + Tailwind + shadcn/ui init + React Router
6. Zustand stores: `authStore` (user + role) + `uiStore` (editMode boolean)
7. GitHub Actions: npm build → copy to static → Docker build → SSH deploy
8. Traefik: `demo.estate.zubbystudio.shop` Traefik labels (old Streamlit container unchanged)

### Phase 2B — Core Data
9. `/api/v1/dashboard` endpoint + Dashboard React page (exact layout from wireframe)
10. `/api/v1/holdings` CRUD + Holdings React page (draft/live + edit mode)
11. `/api/v1/prices/quick` + `/api/v1/prices/bulk-csv` + Price Entry React page
12. `/api/v1/companies` CRUD + Companies React page
13. `/api/v1/prices/history` + Price History React page

### Phase 2C — All Remaining Pages
14. Dividends (CRUD + CSV + annual summary tabs)
15. Transactions (CRUD + CSV + auto-generated rows)
16. Registrars (CRUD + expandable company accordion)
17. Watchlist page

### Phase 2D — New Features
18. NAV History (APScheduler job + chart page)
19. Rebalancing (sector targets drawer + gap table)
20. Corporate Actions (CRUD + auto-transaction generation)
21. Settings: User Management, Deleted Records restore UI
22. Price audit log + revert button

### Phase 2E — Polish + Cutover
23. Mobile responsive pass
24. Dashboard count-up animation
25. Stooq scraper script + README price data section
26. Remove old Streamlit container → point `estate.zubbystudio.shop` to new app
27. Update MASTER_CONTEXT.md with new stack entry

---

## Part E: Decisions Log (Final State)

| Area | Decision | Status |
|------|----------|--------|
| Stack | FastAPI + React 18 + TypeScript | LOCKED |
| Container | Single container, FastAPI serves React static | LOCKED |
| Auth | JWT httpOnly cookie, users in DB, 2 roles | LOCKED |
| Edit mode | Top navbar toggle, admin only | LOCKED |
| Draft status | Holdings + Transactions (Grok addition) | LOCKED |
| Price input | Quick entry + CSV with column mapping | LOCKED |
| Stooq | Standalone script on server, README reminder | LOCKED |
| NAV snapshots | APScheduler in-process, 18:00 WAT weekdays | LOCKED |
| Beta subdomain | demo.estate.zubbystudio.shop parallel to old app | LOCKED |
| Transaction triggers | Manual + auto (Holdings create, corporate actions, Obsidian) | LOCKED |
| Transaction columns | Full list incl. broker_fee, reference_id, linked_holding_id | LOCKED |
| DB tables | 6 additive new tables, no destructive changes | LOCKED |
| WHT rate | Configurable per dividend entry (not hardcoded) | LOCKED |
| Transaction types | buy, sell, bonus_receipt, rights_subscription, transfer_in | LOCKED |
| Viewer scope | All pages visible (read-only), no draft records | LOCKED |

---

**END OF HANDOVER BRIEF**

**Lovable.dev receives**: Part C (Wireframes) + API Contract from Part B
**Deepseek:flash receives**: Parts A, B, D, E (full brief)
**Next action**: Deepseek:flash begins Phase 2A. Lovable begins Login + Dashboard + Holdings pages in parallel.
**Sync point**: After Phase 2A Foundation — Deepseek:flash shares base API URL + running auth endpoint with Lovable for integration testing.
