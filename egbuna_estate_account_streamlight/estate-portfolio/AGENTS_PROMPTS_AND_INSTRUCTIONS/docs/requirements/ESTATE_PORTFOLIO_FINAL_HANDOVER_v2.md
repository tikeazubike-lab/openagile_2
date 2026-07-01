# Estate Portfolio — Phase 2 Final Handover Brief (v2)
## Claude (The Brain) → Antigravity (Implementer)

**From**: Claude (The Brain — Architecture + Design)
**To**: Antigravity (Implementer)
**Verified By**: Grok (Zone 2 Spotter — 2026-04-18, second verification pass)
**Date**: 2026-04-18
**Protocol**: MASTER_CONTEXT.md v3.0 — Handover Protocol
**Status**: ALL DECISIONS LOCKED. Lovable.dev role revised per Grok's 2026-04-18 capability audit.

---

## CHANGELOG FROM v1 (2026-04-17)

The following changes are incorporated from Grok's second verification pass:

| # | Change | Source |
|---|--------|--------|
| 1 | **Lovable.dev role narrowed** — frontend-only, no backend generation | Grok capability audit |
| 2 | **Antigravity scope expanded** — owns all FastAPI backend independently | Grok capability audit |
| 3 | **Agent chain formalised** — 5-agent sequence locked | Grok GEMINI.md chain |
| 4 | **Design system updated** — light theme replacing dark theme | User (colour palette + Dialin inspiration image) |
| 5 | **Typography updated** — new font pairing to match light theme | User image analysis |
| 6 | **GitHub as handoff point** — Lovable → GitHub → Antigravity review | Grok confirmation |
| 7 | Dark theme references removed from all wireframe sections | User colour palette override |
| 8 | **Theme toggle added** — system-default + manual dark override, Moon/Sun icon in navbar | User (v2 correction) |

Everything else from v1 is unchanged and locked.

---

## Part A: Revised Role Bifurcation Architecture

### The Fundamental Split (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOVABLE.DEV BOUNDARY (REVISED)               │
│  Owns: React UI ONLY — components, pages, routing, visual design│
│  Does NOT generate: FastAPI code, DB connections, Dockerfiles   │
│  Delivers: /frontend/src/ → synced to GitHub repo               │
│  Limitation: defaults to Supabase; backend prompts need override│
└─────────────────────────────────────────────────────────────────┘
                              │
                    GitHub repo (handoff point)
                    Antigravity reviews Lovable PR/diff
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    ANTIGRAVITY BOUNDARY (EXPANDED)              │
│  Owns: ALL backend — FastAPI, SQLAlchemy, Alembic, Docker,      │
│  Traefik labels, CI/CD, shared Postgres wiring, APScheduler     │
│  Also owns: Wiring Lovable's React output into container        │
│  Also owns: Fixing any Supabase refs Lovable accidentally adds  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    asyncpg / SQLAlchemy 2.0 (async)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (EXISTING — UNTOUCHED)              │
│  openagile_postgres — estate_portfolio DB                       │
│  Access: via openagile_openagile_network inside Docker          │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5-Agent Chain (Locked per GEMINI.md)

```
1. ANTIGRAVITY   — Diagnose existing system, write backend (FastAPI + Alembic + Docker)
        ↓
2. CLAUDE        — Architecture + design + this handover spec
        ↓
3. GROK          — Verify current tool capabilities, flag risks, confirm stack
        ↓
4. LOVABLE       — Generate React UI code from prompt spec → push to GitHub
        ↓
5. ANTIGRAVITY   — Review Lovable PR, fix Supabase → FastAPI mismatches,
                   add Traefik labels, update docker-compose.yml, push to main → deploy
```

---

### What Lovable.dev Actually Does (Post-Grok Correction)

**Lovable generates (~80-85% production-ready):**
- React 18 + TypeScript component code
- TanStack Table, Recharts, shadcn/ui, Zustand, React Router pages
- TanStack Query hooks wired to `/api/v1/...` endpoints (from our prompt)
- Full auth context (login page, route guards, role-conditional rendering)
- All visual design matching colour palette and Dialin-style layout

**Lovable does NOT reliably generate:**
- FastAPI backend code (Antigravity owns this entirely)
- SQLAlchemy ORM models or Alembic migrations
- Dockerfile for single-container build (FastAPI serves React static)
- Docker Compose with Traefik labels + openagile_network
- APScheduler NAV snapshot jobs
- Any reference to shared openagile_postgres (it will try to add Supabase client — Antigravity strips this)

**Antigravity's review checklist for every Lovable PR:**
- [ ] No Supabase client imports anywhere in `/frontend/src/`
- [ ] No `.env` references to `SUPABASE_URL` or `SUPABASE_ANON_KEY`
- [ ] All API calls go to `/api/v1/...` (relative URL, not hardcoded domain)
- [ ] No localStorage for JWT — cookie-only auth
- [ ] Vite build config outputs to `dist/` (Antigravity copies to `/backend/app/static/`)

---

### Layer-by-Layer Responsibility Map (Updated)

#### Layer 1: Database (PostgreSQL) — Antigravity only
```
- Table schema (existing + new additive Alembic migrations)
- Indexes, constraints, foreign keys
- Soft delete pattern (deleted_at column everywhere)
- No Supabase RLS, no Supabase Edge Functions, no Supabase anything
```

#### Layer 2: FastAPI Backend — Antigravity only
```
- Async SQLAlchemy 2.0 + asyncpg driver
- All business logic: return %, NAV, XIRR, rebalancing gap
- JWT issuance (python-jose) + httpOnly cookie setting
- Role enforcement via FastAPI dependencies (require_admin)
- CSV/Excel parsing (pandas + openpyxl) 
- APScheduler: NAV snapshot at 18:00 WAT weekdays
- Soft delete logic, price audit logging
- Corporate action → transaction auto-generation
- Serves React static files (FastAPI StaticFiles mount)
```

#### Layer 3: API Contract — Antigravity implements, Lovable consumes
```
Contract rules (unchanged from v1):
- All endpoints: /api/v1/
- Envelope: { "data": payload, "meta": {}, "error": null }
- Monetary values: strings ("12345.50"), not floats
- Timestamps: ISO 8601 UTC
- Soft-deleted: excluded unless ?include_deleted=true
- Draft records: excluded for readonly role (API enforces)
- HTTP codes: 200, 201, 400, 401, 403, 404, 422
```

#### Layer 4: React Application — Lovable generates, Antigravity integrates
```
Lovable owns code generation for:
- All React components and pages (see Part C wireframes)
- TypeScript interfaces matching API response shapes
- TanStack Query hooks per domain
- Zustand: authStore + uiStore (editMode)
- React Router v6 routes + protected route wrapper
- Role-conditional rendering (isAdmin checks)
- Visual design: light theme, colour palette, typography
- Responsive layout (sidebar → mobile bottom nav)
- Form validation: React Hook Form + Zod

Antigravity owns after Lovable delivers:
- Copy frontend/dist/ → backend/app/static/ in GitHub Actions
- Verify CORS origins in FastAPI config match domains
- Confirm httpOnly cookie passes through Traefik (no stripping)
- Remove any Supabase remnants
- Fix any absolute URL references → relative /api/v1/
```

---

### User Role Bifurcation (Application Level — Unchanged)

Two roles. Role is returned by `/api/v1/auth/me` and stored in Zustand `authStore`.

#### Admin Role (`role: "admin"`)
```
✅ All pages in sidebar
✅ Edit Mode toggle in top navbar
✅ In Edit Mode: inline editing, Add New forms, Soft Delete, Publish
✅ Holdings + Transactions: create draft → publish workflow
✅ Price Entry page (quick entry + bulk CSV)
✅ Corporate Actions page
✅ Settings → User Management, Deleted Records, Sector Targets
✅ Price audit log with Revert buttons
✅ NAV History manual snapshot trigger
```

#### Readonly Role (`role: "readonly"`)
```
✅ Dashboard, Holdings (live only), Companies, Dividends
✅ Transactions (live only), Price History, NAV History (chart)
✅ Watchlist (view only), Rebalancing (view only), Registrars

❌ Edit Mode toggle — not rendered (Zustand isAdmin() check)
❌ Price Entry — not in sidebar navigation
❌ Settings — entire section hidden
❌ Corporate Actions — not in sidebar
❌ Any edit, delete, publish, add buttons
❌ Draft rows — hidden (API enforces + frontend double-checks)
```

#### Role Communication Pattern
```typescript
// authStore.ts (Zustand)
interface AuthStore {
  user: { id: number; name: string; role: 'admin' | 'readonly' } | null;
  isAdmin: () => boolean;
  setUser: (user: User) => void;
  clearUser: () => void;
}

// Usage:
const { isAdmin } = useAuthStore();
{isAdmin() && <EditModeToggle />}
```

#### Edit Mode (Admin-Only Zustand Boolean)
```
uiStore.editMode = false (default — both roles see this view)

VIEWING (editMode=false):
  TanStack Table: read-only display
  No action buttons, no forms
  Draft rows: invisible

EDITING (editMode=true, admin only):
  TanStack Table: editable cells (configured columns only)
  Add New + Soft Delete + Publish buttons appear
  Draft rows: visible with amber left border + DRAFT badge
```

---

## Part B: Complete API Contract (Unchanged from v1)

Antigravity implements. Lovable consumes via TanStack Query hooks.
All endpoints unchanged — see v1 for full list. Summary below for reference.

```
/api/v1/auth/       login, logout, me, change-password
/api/v1/dashboard   single endpoint returns all KPIs + charts data
/api/v1/companies   CRUD + soft delete
/api/v1/holdings    CRUD + publish + restore + soft delete
/api/v1/prices      quick entry, bulk CSV (2-stage), history, audit, revert
/api/v1/dividends   CRUD + bulk CSV + annual summary
/api/v1/transactions CRUD + publish + bulk CSV + auto-generation
/api/v1/registrars  CRUD with expandable companies
/api/v1/watchlist   CRUD
/api/v1/nav-history list + manual snapshot trigger
/api/v1/rebalancing current allocation vs targets
/api/v1/sector-targets GET + PUT
/api/v1/corporate-actions CRUD + auto-transaction generation
```

---

## Part C: Wireframe Specification for Lovable.dev (Updated — Light/Dark Theme)

> **NOTE TO LOVABLE**: Light theme is the default. Dark theme is available via a toggle
> and via system preference. All colours must use CSS variables — never hardcoded hex.
> Do not use Supabase. All API calls go to `/api/v1/` (relative paths only).

---

### Theme System — System Default + Dark Override

```
BEHAVIOUR:
  On first visit (no localStorage): read OS preference via matchMedia
    OS = light → light theme (baseline CSS :root)
    OS = dark  → dark theme (.dark class on <html>)
  
  Toggle click (Moon/Sun icon, top navbar):
    Currently light → force dark → save 'dark' to localStorage('epm-theme')
    Currently dark  → return to system → save 'system', re-read matchMedia

IMPLEMENTATION:
  useTheme hook (/frontend/src/hooks/useTheme.ts)
  Manages: document.documentElement.classList.toggle('dark', ...)
  Called once in App.tsx before first render
  All components call useTheme() to get resolvedTheme: 'light' | 'dark'

TOGGLE BUTTON (navbar, between Edit Mode toggle and bell):
  32×32px ghost icon button
  Light mode: Moon icon (Lucide, 18px, --text-secondary)
  Dark mode:  Sun  icon (Lucide, 18px, --accent-gold)
  Hover: bg-[var(--bg-subtle)]
  Tooltip: "Switch to dark" / "Return to system theme"
  Visible to ALL users (both admin and readonly)
```

---

### Design System — CSS Variables (Apply Globally)

All components use CSS variables. Never hardcode hex. This enables zero-duplication theming.

```css
/* ── LIGHT (default :root) ──────────────── */
:root {
  --bg-canvas:       #FDFEFE;
  --bg-surface:      #FFFFFF;
  --bg-subtle:       #F5F5F7;
  --bg-sidebar:      #646763;
  --text-primary:    #1A1A1A;
  --text-secondary:  #646763;
  --text-muted:      #9CA3AF;
  --text-on-sidebar: #FFFFFF;
  --border:          #E8E8EC;
  --shadow-card:     0 1px 4px rgba(100,103,99,0.12), 0 0 0 1px #E8E8EC;
  --shadow-dropdown: 0 8px 24px rgba(100,103,99,0.20);
  --focus-ring:      0 0 0 3px rgba(188,189,250,0.40);

  /* Accents — identical in both themes */
  --accent-lavender: #BCBDFA;
  --accent-gold:     #DABF82;
  --accent-green:    #22C55E;
  --accent-red:      #EF4444;
  --accent-amber:    #F59E0B;
}

/* ── DARK (.dark on <html>) ─────────────── */
.dark {
  --bg-canvas:       #0d1117;
  --bg-surface:      #161b22;
  --bg-subtle:       #1c2128;
  --bg-sidebar:      #0d1117;   /* sidebar blends with canvas; add right border */
  --text-primary:    #e6edf3;
  --text-secondary:  #8b949e;
  --text-muted:      #484f58;
  --text-on-sidebar: #e6edf3;
  --border:          #30363d;
  --shadow-card:     0 1px 4px rgba(0,0,0,0.40), 0 0 0 1px #30363d;
  --shadow-dropdown: 0 8px 24px rgba(0,0,0,0.50);
  --focus-ring:      0 0 0 3px rgba(188,189,250,0.30);
  /* Accents unchanged */
}
```

**Tailwind usage:** `bg-[var(--bg-surface)]`, `text-[var(--text-primary)]`, `border-[var(--border)]`

**Dark sidebar note:** In dark mode `--bg-sidebar` = `#0d1117` (same as canvas).
Add `border-right: 1px solid var(--border)` to sidebar to maintain visual separation.

```
TYPOGRAPHY:
  Numbers/Tickers/₦:  'DM Mono', monospace
  All UI text:        'Plus Jakarta Sans', sans-serif
  Page h1:            24px, weight 700, var(--text-primary)
  Section heading:    16px, weight 600, var(--text-primary)
  Table header:       12px, weight 600, var(--text-secondary), uppercase, tracking-wide
  KPI value:          28–32px, DM Mono, weight 600, var(--text-primary)
  Label/caption:      12px, var(--text-secondary)

SPACING: 8px grid. Card radius: 12px. Input radius: 8px. Pills: 999px.
```
  Inputs:     8px
  Badges:     999px (pills)
  Buttons:    8px

SHADOWS:
  Card:       0 1px 4px rgba(100,103,99,0.12), 0 0 0 1px #E8E8EC
  Dropdown:   0 8px 24px rgba(100,103,99,0.20)
  Modal:      0 16px 48px rgba(100,103,99,0.25)
```

---

### Layout Reference: Dialin Dashboard Analysis

The provided Dialin screenshot establishes the layout language. Key patterns to replicate:

```
1. LEFT SIDEBAR: Dark/coloured background (we use #646763 slate), white text,
   search bar at top, grouped navigation items, user profile at bottom.
   WIDTH: 220px desktop, hidden mobile.

2. MAIN CONTENT: White/off-white background, 24px padding, full remaining width.

3. CARD GRID: KPI cards in a row at the top, uniform height (~120px),
   white background, subtle border + shadow.

4. CHART CARDS: White background cards, rounded corners, 16px internal padding,
   title + period selector (Weekly/Daily/Monthly dropdown) in header.

5. DATA DENSITY: Medium density — not cramped, not sparse. Similar to Dialin's
   analytics section. Tables are not full-viewport, they're card-contained.

6. TYPOGRAPHY HIERARCHY: Clear distinction between metric values (large, bold,
   monospaced) and supporting labels (small, grey).

7. GRADIENT ACCENT: Dialin uses a subtle gradient blob in the overview card.
   We use a lavender (#BCBDFA) gradient blob in the KPI summary card.
```

---

### Component: Sidebar

```
WIDTH: 220px (desktop), hidden (mobile — hamburger opens overlay)
BACKGROUND: linear-gradient(180deg, #646763 0%, #4a4d4b 100%)

TOP — App identity (56px):
  "EPM" — DM Mono, 20px, weight 700, #BCBDFA (lavender on dark)
  "Estate Portfolio" — Plus Jakarta Sans, 11px, rgba(255,255,255,0.6)

SEARCH BAR (below logo, 32px height):
  Background: rgba(255,255,255,0.10)
  Placeholder: "Search..." — rgba(255,255,255,0.5), 13px
  Border: 1px rgba(255,255,255,0.15), radius 6px
  Keyboard shortcut hint: "/" key badge, right-aligned

NAVIGATION LABEL (section header):
  "MAIN" — 10px, rgba(255,255,255,0.4), uppercase, tracking-widest, 16px left padding

NAV ITEMS (40px each):
  Layout: 12px left padding | 20px Lucide icon | 12px gap | label text
  Font: Plus Jakarta Sans, 14px

  Active:   Background #BCBDFA, text #1A1A1A, border-radius 8px (full width −16px margin)
  Hover:    Background rgba(255,255,255,0.10), text #FFFFFF
  Inactive: Text rgba(255,255,255,0.75)

  MAIN section:
    📊 Dashboard
    💼 Holdings           [amber dot if draft count > 0]
    🏢 Companies
    💰 Dividends
    📈 Price History
    🔄 Transactions       [amber dot if draft count > 0]
    📋 Registrars
    👁 Watchlist
    📉 NAV History
    ⚖️ Rebalancing

  Divider: 1px rgba(255,255,255,0.12), 8px vertical margin

  ADMIN ONLY section (label: "ADMIN"):
    ⚡ Price Entry       ← lavender text, slightly brighter (daily-use emphasis)
    📥 Data Import
    🏛 Corporate Actions
    👥 User Management
    🗑 Deleted Records

BOTTOM — User profile (48px):
  Avatar circle: 32px, background #BCBDFA, initials in #1A1A1A, DM Mono
  Name: Plus Jakarta Sans 13px, #FFFFFF
  Role badge: "Admin" or "Viewer" — 10px, rgba(255,255,255,0.5)
  Sign out icon: right side, on hover rgba(255,255,255,0.7)
```

---

### Component: Top Navigation Bar

```
HEIGHT: 56px
BACKGROUND: #FFFFFF
BORDER-BOTTOM: 1px solid #E8E8EC
POSITION: fixed, full width minus sidebar, z-index 50

LEFT:
  Page title — Plus Jakarta Sans, 18px, weight 600, #1A1A1A
  Breadcrumb on sub-pages: "Settings / Price Entry" in text-secondary

RIGHT (desktop, flex gap-3):
  1. Edit Mode Toggle (admin only):
     Pill container, 130px wide, 32px height, background #F5F5F7
     border: 1px #E8E8EC, border-radius: 999px
     VIEWING:  left side active — lavender dot + "Viewing", text #646763
     EDITING:  right side active — pencil icon + "Editing", bg #BCBDFA text #1A1A1A
     Smooth sliding animation 200ms ease

  2. Notification bell icon (20px, text-secondary)
     Badge: amber dot if action items exist

  3. User avatar (32px circle, #BCBDFA bg, initials, DM Mono)
     Click → dropdown: Profile | Change Password | Sign Out

BETA BANNER (demo subdomain only, above navbar):
  28px bar, background #BCBDFA, text #1A1A1A
  "BETA — demo.estate.zubbystudio.shop — Feedback welcome"
  10px, Plus Jakarta Sans, centered
```

---

### Page: Login

```
FULL SCREEN LAYOUT:
  Left panel (60%): decorative
    Background: linear-gradient(135deg, #646763 0%, #4a4d4b 50%, #3a3d3b 100%)
    Center content:
      Large "EPM" monogram — DM Mono, 72px, weight 700, #BCBDFA
      "Your Portfolio, Clearly." — Plus Jakarta Sans, 20px, rgba(255,255,255,0.85)
      Subtle lavender gradient blob behind monogram (radial, 400px, 20% opacity)
      Bottom left: "Estate Portfolio Manager v2.0" — 12px, rgba(255,255,255,0.4)

  Right panel (40%): login form
    Background: #FDFEFE
    Vertically centered content, 360px max-width, 40px horizontal margin

    "Welcome back" — Plus Jakarta Sans, 28px, weight 700, #1A1A1A
    "Sign in to your portfolio" — 14px, text-secondary, 8px below heading
    32px gap
    
    Username field:
      Label: "Username" — 12px, weight 600, text-secondary, uppercase, tracking-wide
      Input: 44px height, #FFFFFF bg, 1px border #E8E8EC, 8px radius
      Focus: border #BCBDFA, box-shadow focus ring
    
    Password field (16px below):
      Same styling + eye toggle icon (show/hide)
    
    "Sign In" button (24px below):
      Full width, 44px, background #BCBDFA, text #1A1A1A, weight 600
      Hover: background #a9aaef (slightly darker lavender)
      Loading: spinner centered

    Error message: 13px, #EF4444, fade-in, below button

MOBILE LOGIN: Single column, no left panel, top: EPM monogram, then form
```

---

### Page: Dashboard

```
PAGE PADDING: 24px all sides
SECTION GAP: 24px between all sections

── SECTION 1: KPI Cards (4 cards, equal-width row) ──────────────────────

Each card:
  Background: #FFFFFF, border 1px #E8E8EC, border-radius 12px, padding 20px
  Shadow: 0 1px 4px rgba(100,103,99,0.12)
  
  Top row: metric label (12px, Plus Jakarta Sans, uppercase, tracking-wide,
           text-secondary) + trend icon (right-aligned, 16px Lucide)
  Value row: DM Mono, 30px, weight 600, text-primary
             COUNT-UP ANIMATION on page load (0 → actual value, 800ms ease-out)
  Bottom row: change indicator (13px, DM Mono)
              Positive: "#22C55E +12.34% ↑"
              Negative: "#EF4444 -3.21% ↓"

  Card 1: TOTAL PORTFOLIO VALUE
    Icon: TrendingUp (lavender)
    Value: "₦12,345,678.00"
    Sub: "Unrealised gain +₦1.2M"
    Left border accent: 3px solid #BCBDFA

  Card 2: TOTAL INVESTED
    Icon: DollarSign (gold)
    Value: "₦11,100,000.00"
    Sub: "Cost basis"
    Left border accent: 3px solid #DABF82

  Card 3: UNREALISED GAIN/LOSS
    Icon: BarChart2 (green or red)
    Value: "+₦1,245,678.00"
    Sub: "+11.22% overall"
    Left border accent: 3px solid #22C55E (or red if negative)

  Card 4: TOTAL HOLDINGS
    Icon: Briefcase (lavender)
    Value: "24"
    Sub: (admin only) "22 live · 2 draft"
    Left border accent: 3px solid #BCBDFA

── SECTION 2: Charts Row (two cards, 45% + 55%) ─────────────────────────

LEFT CARD — Sector Allocation:
  Header: "Sector Allocation" (16px, weight 600) + "Monthly" dropdown (right)
  Recharts PieChart, donut style, 200px diameter
  Hole center: portfolio total value (DM Mono, 14px)
  Legend: right of chart, vertical list
    ● Banking 35.2% — color dot + label + pct
    ● Consumer 18.1%
    (etc.)
  Colors: distinct 8-color set — use lavender variants + gold + greens
  Hover tooltip: sector name + ₦value + %

RIGHT CARD — Top Holdings:
  Header: "Top Holdings" (16px, weight 600) + "by Value" label
  Recharts HorizontalBarChart
  Y-axis: ticker symbols, DM Mono, 12px
  X-axis: ₦ values
  Bars: #BCBDFA fill, rounded right ends (radius 4px)
  End label on each bar: return% in green/red, DM Mono, 12px
  Max 10 companies shown

── SECTION 3: Bottom Row (60% + 40%) ────────────────────────────────────

LEFT CARD — Recent Transactions:
  Header: "Recent Transactions" + "View all →" link (right, lavender, 13px)
  Table (5 rows, no pagination):
    | Date        | Ticker  | Type Badge  | Shares    | Amount      |
    | DM Mono 13px| DM Mono | pill        | DM Mono   | DM Mono 13px|
  
  Type badges (pill, 10px, Plus Jakarta Sans, weight 600):
    BUY:    #DCFCE7 background, #16A34A text
    SELL:   #FEE2E2 background, #DC2626 text
    BONUS:  #EDE9FE background, #7C3AED text
    RIGHTS: #DBEAFE background, #2563EB text
  
  Row hover: #F5F5F7 background
  Empty state: muted icon + "No transactions yet"

RIGHT CARD — Action Items:
  Header: "Action Items" (16px, weight 600)
  
  Each item is a row with left icon + text + right badge/count:
  
  🟡 "2 holdings pending publish"  → amber badge "2"  → clickable → Holdings page
  🟡 "3 transactions to review"    → amber badge "3"  → clickable → Transactions
  🔴 "Prices not updated in 8 days" → red badge "!"  → clickable → Price Entry
  
  All clear state:
    Large ✓ icon in #22C55E, 48px
    "Portfolio up to date" — Plus Jakarta Sans, 14px, text-secondary
  
  Footer: "Last updated: Mon Apr 14, 2026 18:02 WAT"
          12px, DM Mono, text-muted, right-aligned

── MOBILE DASHBOARD ─────────────────────────────────────────────────────
  KPI cards: 2×2 grid (full width each)
  Charts: stacked, full width
  Recent Transactions + Action Items: stacked below
```

---

### Page: Holdings

```
HEADER ROW:
  Left: "Holdings" h1 + "(24 positions)" in text-secondary 14px
  Right (admin, Editing mode): [+ Add Holding] lavender button [↓ Export ▼] ghost button

FILTER ROW (card, 12px below header):
  Background: #FFFFFF, border #E8E8EC, 12px radius, padding 12px 16px
  [🔍 Search ticker or company...] [Sector ▼] [Status ▼] [Sort by ▼]
  Status options: All | Live | Draft (Draft admin-only)

MAIN TABLE CARD:
  Background: #FFFFFF, border #E8E8EC, border-radius 12px
  Table header: 12px, Plus Jakarta Sans, weight 600, uppercase, text-secondary,
                tracking-wide, #F5F5F7 background, 40px height
  Table rows: 48px height, alternating #FFFFFF / #F5F5F7 (subtle stripe)
  Row hover: #EEF0FF (very light lavender)

  COLUMNS:
  | Ticker   | Company Name    | Sector    | Shares   | Avg Cost | Curr Price | Curr Value   | Cost Basis | return[%]    | Div Yield | Status | Actions   |
  | DM Mono  | Plus Jakarta 14 | pill badge| DM Mono  | DM Mono  | DM Mono    | DM Mono 600  | DM Mono    | DM Mono color| DM Mono   | badge  | icon btns |

  SECTOR BADGES: small rounded pill, 10px, each sector a distinct soft colour
    Banking: #DBEAFE / #2563EB text
    Consumer: #DCFCE7 / #16A34A text
    Oil & Gas: #FEF3C7 / #D97706 text
    (consistent across all pages)

  RETURN[%] COLUMN ("return[%]" exact header text):
    Positive: #22C55E, DM Mono, "+12.34%"
    Negative: #EF4444, DM Mono, "-3.21%"
    Zero: text-muted, "0.00%"

  STATUS COLUMN (admin only):
    LIVE: #DCFCE7 bg, #16A34A text, pill
    DRAFT: #FEF3C7 bg, #D97706 text, pill

  DRAFT ROW TREATMENT:
    Left border: 3px solid #F59E0B
    Background: rgba(245, 158, 11, 0.04)
    All values: opacity 0.75
    STATUS cell: amber DRAFT pill

  ACTIONS (Editing mode, admin):
    Live rows:  [✏] [🗑] — icon buttons, 32px, ghost style
    Draft rows: [✏] [✓ Publish] [🗑] — Publish is lavender pill button

  READONLY: no Actions column, no draft rows, no filter for Draft status

  PAGINATION: 25 rows/page, bottom right, Plus Jakarta Sans 13px

ADD HOLDING PANEL (Editing mode, slides down from header, card style):
  Form in 2-column grid:
    Company (searchable dropdown)     Status toggle: Draft | Publish now
    Shares (DM Mono number input)     Purchase Date (date picker)
    Avg Purchase Price (₦, DM Mono)  Notes (full width textarea)
  Buttons: [Cancel] ghost  [Save as Draft] secondary  [Save & Publish] lavender primary
  Success: row animates into table (fade + slide down)
```

---

### Page: Price Entry (Settings → Price Entry)

```
PAGE LAYOUT: Two-column on desktop (55% + 45%), stacked on mobile

LEFT — Quick Price Update:
  Card: #FFFFFF, 12px radius, 24px padding
  Heading: "Quick Price Update" (18px, weight 600)
  Subtitle: "Update a single stock's current price" (14px, text-secondary)
  
  Form:
    Company search: typeahead dropdown
      Each option: [TICKER] Company Name — Current: ₦XX.XX
    New Price: large input, DM Mono, 32px font, 56px height
      ₦ prefix inside input, text-secondary
    Date: date picker, defaults to today
    [Update Price] — full width, lavender button, 44px

  Success toast: slides from top-right, green, "DANGCEM updated to ₦123.45"

  ── PRICE AUDIT LOG ──
  Sub-heading: "Recent Changes" (14px, weight 600)
  Table (last 20 entries):
  | Date     | Ticker  | Old     | New     | Δ      | Source    | [Revert] |
  | DM Mono  | DM Mono | DM Mono | DM Mono | +3.2%  | badge     | text link|
  
  Source badges:
    manual:     #F5F5F7 bg, text-secondary
    csv_upload: #DBEAFE bg, #2563EB text
    stooq_csv:  #EDE9FE bg, #7C3AED text
  
  Revert: "Revert" text link in lavender, opens confirmation modal

RIGHT — Bulk CSV Import:
  Card: #FFFFFF, 12px radius, 24px padding
  Heading: "Bulk CSV Import" (18px, weight 600)

  STEP 1 — Drop Zone:
    Dashed border (#BCBDFA 1.5px), border-radius 12px, 180px height, #F8F8FF bg
    ↑ upload icon (40px, lavender)
    "Drop CSV or Excel here" — 15px, text-secondary
    "or click to browse" — 13px, text-muted
    ".csv · .xlsx · .xls accepted"

    ℹ️ NOTE BOX (below drop zone, #F0F0FF bg, lavender left border 3px):
    "💡 Stooq Scraper available — generates CSV automatically.
     See README → Price Data Sources for server command."

  STEP 2 — Column Mapping (replaces drop zone after upload):
    "Map your columns" heading
    Each row: "Required Field" → [Your Column dropdown]
      Ticker  → [Symbol ▼]
      Price   → [Close  ▼]
      Date    → [Date   ▼]
    Optional: Volume → [Skip ▼]
    [Preview →] lavender button

  STEP 3 — Preview (replaces mapping):
    "Preview (first 10 rows)" heading
    Mini-table: valid rows normal, error rows: left border red, tooltip on hover
    Summary pill: "47 valid" (green) · "3 errors" (red) · "2 unknown" (amber)
    [← Back] ghost  [Commit 47 rows →] lavender

  STEP 4 — Result:
    Large animated ✓ (lavender, 64px, scale-in animation)
    "47 prices updated successfully"
    "3 rows skipped" — details collapsed, "Show details ▼" toggle
    [Import Another] secondary button
```

---

### Page: NAV History

```
HEADER:
  "NAV History" h1
  Right (admin): [▶ Take Snapshot] — ghost button with play icon

PERIOD FILTER PILLS (below header, inline):
  [1M] [3M] [6M] [1Y] [All]
  Active: #BCBDFA bg, #1A1A1A text; Inactive: ghost

CHART CARD (full width):
  Recharts AreaChart, 360px height
  Two areas:
    Portfolio Value: fill #BCBDFA opacity 0.25, stroke #BCBDFA 2px
    Total Invested:  fill #DABF82 opacity 0.20, stroke #DABF82 2px dashed
  X-axis: dates, DM Mono, 12px, text-secondary
  Y-axis: ₦ amounts, DM Mono, right-aligned
  Tooltip card: white, 12px radius, shadow, shows date + value + cost + gain%
  Grid lines: #E8E8EC, horizontal only

STATS ROW (3 mini-cards below chart):
  Best Day / Worst Day / Since Inception
  Same card style as dashboard KPIs but smaller (16px value, 20px padding)

DATA TABLE (collapsible, default 30 rows):
  | Date | Portfolio Value | Total Invested | Gain/Loss | Return % |
  "Show all" / "Collapse" toggle link
```

---

### Page: Rebalancing

```
HEADER:
  "Rebalancing" h1
  Sub: "Target vs current sector allocation"
  Right (admin): [✏ Edit Targets] lavender button

ALLOCATION TABLE CARD:
  | Sector | Current Value | Current % | Target % | Gap | Recommendation |
  
  GAP COLUMN:
    Overweight:  #EF4444, "▲ +5.2%"
    Underweight: #F59E0B, "▼ -1.9%"
    On target:   #22C55E, "≈ On Target"

  VISUAL BAR (inline, between columns — 200px wide):
    Blue fill = current %; vertical gold dashed line = target %
    Red extension if over; amber dotted reach if under

  RECOMMENDATION:
    "Reduce" — red light text
    "Increase" — green light text
    "Hold" — text-muted

EDIT TARGETS DRAWER (right side, 380px, slides in):
  Heading: "Set Sector Targets"
  Warning: "Targets must sum to 100%"
  Running total: "Current total: 98.0% ⚠️" in amber, or "100% ✓" in green
  Per row: sector label + number input (DM Mono) + "%" suffix
  [+ Add Sector] text link
  [Save Targets] lavender button (disabled if ≠ 100%)
```

---

### Page: Transactions

```
HEADER + ACTIONS:
  "Transactions" h1
  Right (admin, Editing): [+ Add Transaction] [Import CSV]

FILTER ROW (card):
  [Search...] [Type ▼: All/Buy/Sell/Bonus/Rights] [Date range] [Status ▼]

TABLE (TanStack Table):
  | Date | Ticker | Type | Shares | Price/Share | Net Amount | Broker Fee | Notes | Status | Actions |
  
  TYPE BADGES (pill, soft colours):
    BUY:    green  SELL: red  BONUS: purple  RIGHTS: blue
  
  AUTO-GENERATED ROWS (from corporate actions):
    Grey "AUTO" badge in Notes — ✏ edit button is disabled + tooltip "Auto-generated"
  
  DRAFT rows: amber left border treatment (same as Holdings)
  
EMPTY STATE:
  Empty inbox icon (48px, text-muted)
  "No transactions recorded yet."
  "Add via Holdings or import a CSV."
  [Go to Holdings →] lavender ghost button
```

---

### Pages: Companies / Registrars / Watchlist / Dividends

All follow the same card + TanStack Table pattern established above.

```
COMPANIES:
  Registrar column: lavender text link → /registrars/{id}
  Sector column: same coloured pill badges as Holdings

REGISTRARS:
  "Companies" column: count badge (e.g. "12")
  Click row → TanStack Table row expand accordion
  Expanded: list of companies with ticker + name links

WATCHLIST:
  "Gap to Target" column:
    Current < Target: #22C55E "▼ -15.3% to target"
    Current > Target: #EF4444 "▲ +8.2% above target"
    No target: text-muted "—"
  Actions: [+ Add to Holdings] (one-click pre-fill, admin Editing mode)

DIVIDENDS:
  Tabs: [All Dividends] [Annual Summary] [Import CSV]
  Annual Summary: year-group rows + running lifetime total card
  DRIP column: checkmark icon (is_scrip=true) or "—"
```

---

### Components: Empty States & Loading

```
EMPTY STATES (every table):
  Centered in card, 120px height minimum
  Icon (Lucide, 40px, text-muted)
  Primary message (14px, text-secondary)
  Secondary message (13px, text-muted)
  CTA button if applicable (admin Editing mode only)

LOADING STATES:
  KPI cards: shimmer skeleton (grey animated gradient, matches card dimensions)
  Tables: 5 skeleton rows, column widths proportional to real data
  Charts: pulsing placeholder rectangle
  All skeletons: background #F5F5F7 with shimmer animation in #E8E8EC

TOAST NOTIFICATIONS (top-right, stacked):
  Success: #DCFCE7 bg, #16A34A border-left 3px, green check icon
  Error:   #FEE2E2 bg, #EF4444 border-left 3px, X icon
  Warning: #FEF3C7 bg, #F59E0B border-left 3px, ! icon
  Auto-dismiss: 4 seconds, with progress bar
```

---

### Mobile Responsive Rules

```
BREAKPOINTS:
  Desktop:  ≥ 1024px — sidebar 220px, full tables
  Tablet:   768–1023px — sidebar icon-only 56px, tables scroll
  Mobile:   < 768px — sidebar hidden, bottom nav 5 items

MOBILE BOTTOM NAV:
  Fixed bottom, 56px, white bg, border-top #E8E8EC
  5 items: [📊 Dashboard] [💼 Holdings] [💰 Dividends] [📈 Prices] [⋯ More]
  Active: lavender icon + label; Inactive: text-muted
  "More" → bottom sheet with remaining navigation

MOBILE TABLES:
  Sticky first column (Ticker) with white background shadow
  Horizontal scroll on remaining columns
  Column widths: minimum enforced, no word-wrap on numbers

MOBILE CARDS (Dashboard KPIs): 2×2 grid, full width
MOBILE SIDEBAR: Opens as full-height overlay from left, 280px, tap outside closes
```

---

## Part D: Implementation Order (Updated with Lovable Parallel Track)

### Antigravity Track (Backend First — No Lovable Dependency)

```
Phase 2A: Foundation
1.  Repo structure: backend/ frontend/ scripts/stooq_scraper/
2.  FastAPI app factory, config, async database (SQLAlchemy + asyncpg)
3.  Alembic: migrations for existing tables + 6 new tables
4.  Auth: users table seed + JWT httpOnly cookie + require_admin dependency
5.  Stub /api/v1/ endpoints returning mock JSON (allows Lovable to integrate immediately)
6.  Docker single-container build: React static in /app/static/
7.  GitHub Actions: npm build → static copy → docker build → SSH deploy
8.  Traefik: demo.estate.zubbystudio.shop labels

Phase 2B: Real endpoints (replace stubs)
9.  Dashboard endpoint (all KPIs computed)
10. Holdings CRUD + publish + restore
11. Prices: quick entry + bulk CSV (2-stage) + audit
12. Companies CRUD
13. Dividends + annual summary
14. Transactions CRUD + publish + auto-generation
15. Registrars + expandable companies
16. Watchlist + Rebalancing + NAV History + APScheduler
17. Corporate Actions + auto-transaction trigger
```

### Lovable Track (Frontend — Runs in Parallel with Phase 2B)

```
Prompt sequence (send to Lovable one step at a time):
  Step 1: Design system + layout shell (sidebar, navbar, auth pages)
  Step 2: Dashboard page (4 KPIs, 2 charts, 2 bottom cards)
  Step 3: Holdings page (table + draft/live + edit mode forms)
  Step 4: Price Entry page (quick entry + CSV import flow)
  Step 5: Companies + Registrars pages
  Step 6: Dividends + Transactions pages
  Step 7: NAV History + Rebalancing + Watchlist pages
  Step 8: Settings (User Management + Deleted Records)
  Step 9: Mobile responsive pass
  Step 10: Animations (count-up, skeleton, toast notifications)
```

### Sync Points (Antigravity reviews Lovable GitHub output)

```
After Lovable Step 1: Verify no Supabase, correct routing, cookie auth pattern
After Lovable Step 3: Integration test Holdings against stub API
After Lovable Step 5: Integration test all CRUD pages against stub API
After Lovable Step 8: Full integration test against real backend
Final: Static build wired into container → deploy to demo subdomain
```

---

## Part E: Decisions Log (Final State — v2)

| Area | Decision | Status |
|------|----------|--------|
| Stack | FastAPI + React 18 + TypeScript + Vite | LOCKED |
| Container | Single — FastAPI serves React static | LOCKED |
| Auth | JWT httpOnly cookie, users in DB, 2 roles | LOCKED |
| Theme | Light default + dark override toggle + system auto-detect | LOCKED (updated v2) |
| Theme toggle | Moon/Sun icon in navbar; visible to both roles; cycles system→dark→system | LOCKED (added v2) |
| Typography | DM Mono (numbers) + Plus Jakarta Sans (UI) | LOCKED (updated v2) |
| Edit mode | Top navbar toggle, admin only | LOCKED |
| Draft status | Holdings + Transactions | LOCKED |
| Lovable role | Frontend-only React code generation | LOCKED (updated v2 — Grok correction) |
| Antigravity role | All backend + integration wiring + Lovable PR review | LOCKED (updated v2) |
| GitHub handoff | Lovable pushes to repo → Antigravity reviews PR | LOCKED (updated v2) |
| Price input | Quick entry + CSV with column mapping | LOCKED |
| Stooq scraper | Server-side standalone, README reminder | LOCKED |
| NAV snapshots | APScheduler in-process, 18:00 WAT weekdays | LOCKED |
| Beta subdomain | demo.estate.zubbystudio.shop parallel to old app | LOCKED |
| Transaction columns | Full list incl. broker_fee, reference_id, linked_holding_id | LOCKED |
| Viewer scope | All pages, read-only, no draft records | LOCKED |

---

**END OF HANDOVER BRIEF v2**

**Lovable.dev receives**: Part C (Wireframes) + Part B (API Contract) → see LOVABLE_PROMPT.md
**Antigravity receives**: Parts A, B, D, E (this full document)
**Old Streamlit container**: stays live on estate.zubbystudio.shop until Phase 2E cutover
