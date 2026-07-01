# LOVABLE.DEV PROMPT — Estate Portfolio Manager UI
## Copy-paste this prompt into Lovable. It is self-contained.

---

## PROMPT START

Build a full React 18 + TypeScript + Vite frontend for a personal investment portfolio tracker called **Estate Portfolio Manager (EPM)**. This is a Nigerian Stock Exchange (NGX) portfolio app for a single admin user and an optional read-only viewer.

**CRITICAL RULES — read before generating anything:**
1. DO NOT use Supabase, Firebase, or any BaaS. There is no Supabase backend.
2. ALL API calls use relative paths: `/api/v1/...` — never hardcoded domains.
3. Auth is cookie-based (httpOnly JWT set by the backend). Do NOT use localStorage for tokens.
4. This is a FRONTEND-ONLY build. You will not generate FastAPI, SQLAlchemy, Docker, or database code.
5. Use mock/stub data for all API calls so the UI can be previewed immediately.

---

## TECH STACK

```
Framework:    React 18 + TypeScript + Vite
Styling:      Tailwind CSS v4
Components:   shadcn/ui (copy-paste pattern, not installed as a package)
State:        Zustand (authStore + uiStore)
Server state: TanStack Query v5 (useQuery, useMutation)
Tables:       TanStack Table v8
Charts:       Recharts
Routing:      React Router v6
Forms:        React Hook Form + Zod
Icons:        Lucide React
Fonts:        Google Fonts — 'DM Mono' + 'Plus Jakarta Sans'
```

---

## DESIGN SYSTEM

### Colour Palette
These are the ONLY colours to use. Do not substitute with defaults.

```css
/* ── LIGHT THEME (default) ─────────────────────────────────────── */
:root {
  /* Backgrounds */
  --bg-canvas:       #FDFEFE;
  --bg-surface:      #FFFFFF;
  --bg-subtle:       #F5F5F7;
  --bg-sidebar:      #646763;

  /* Text */
  --text-primary:    #1A1A1A;
  --text-secondary:  #646763;
  --text-muted:      #9CA3AF;
  --text-on-sidebar: #FFFFFF;

  /* Accents — same in both themes */
  --accent-lavender: #BCBDFA;
  --accent-gold:     #DABF82;
  --accent-green:    #22C55E;
  --accent-red:      #EF4444;
  --accent-amber:    #F59E0B;

  /* Borders & shadows */
  --border:          #E8E8EC;
  --shadow-card:     0 1px 4px rgba(100,103,99,0.12), 0 0 0 1px #E8E8EC;
  --shadow-dropdown: 0 8px 24px rgba(100,103,99,0.20);
  --shadow-modal:    0 16px 48px rgba(100,103,99,0.25);
  --focus-ring:      0 0 0 3px rgba(188,189,250,0.40);
}

/* ── DARK THEME ─────────────────────────────────────────────────── */
/* Applied when <html> has class="dark"                             */
/* Accent colours are intentionally identical — lavender + gold     */
/* read equally well on dark surfaces.                              */
.dark {
  /* Backgrounds */
  --bg-canvas:       #0d1117;   /* near-black main canvas */
  --bg-surface:      #161b22;   /* cards, modals, dropdowns */
  --bg-subtle:       #1c2128;   /* alternate table rows, hover */
  --bg-sidebar:      #0d1117;   /* sidebar blends with canvas in dark mode */

  /* Text */
  --text-primary:    #e6edf3;
  --text-secondary:  #8b949e;
  --text-muted:      #484f58;
  --text-on-sidebar: #e6edf3;

  /* Accents — unchanged */
  --accent-lavender: #BCBDFA;
  --accent-gold:     #DABF82;
  --accent-green:    #22C55E;
  --accent-red:      #EF4444;
  --accent-amber:    #F59E0B;

  /* Borders & shadows */
  --border:          #30363d;
  --shadow-card:     0 1px 4px rgba(0,0,0,0.40), 0 0 0 1px #30363d;
  --shadow-dropdown: 0 8px 24px rgba(0,0,0,0.50);
  --shadow-modal:    0 16px 48px rgba(0,0,0,0.60);
  --focus-ring:      0 0 0 3px rgba(188,189,250,0.30);
}
```

**IMPORTANT — ALL components must use CSS variables, never hardcoded hex colours.**
This is what makes the theme toggle work without duplicate component code.
Every Tailwind class that sets a colour must reference a CSS variable:
```css
/* Wrong — hardcodes light colour, breaks in dark mode */
background-color: #FFFFFF;

/* Right — resolves to correct colour in both themes */
background-color: var(--bg-surface);
```
For Tailwind classes, use arbitrary value syntax: `bg-[var(--bg-surface)]`,
`text-[var(--text-primary)]`, `border-[var(--border)]` etc.

### Typography
```css
/* Numbers, tickers, monetary values, percentages, dates in tables */
font-family: 'DM Mono', monospace;

/* All UI text: nav, labels, buttons, body, headings */
font-family: 'Plus Jakarta Sans', sans-serif;
```

Apply `DM Mono` to: all ₦ amounts, percentages, share counts, ticker symbols, dates in table cells.
Apply `Plus Jakarta Sans` to: everything else.

### Spacing & Radius
- Base grid: 8px
- Card border-radius: 12px
- Input border-radius: 8px
- Button border-radius: 8px
- Badge/pill border-radius: 999px

### Theme System (System Default + Manual Override)

The app implements a **three-state theme system**:

```
State 1: SYSTEM  (default on first visit — no localStorage key)
  Reads window.matchMedia('(prefers-color-scheme: dark)')
  System dark  → adds .dark class to <html>
  System light → no class on <html> (light is the CSS baseline :root)
  Listens for real-time OS theme changes via addEventListener

State 2: DARK  (user manually forced)
  localStorage key 'epm-theme' = "dark"
  Adds .dark to <html>, ignores system preference

State 3: SYSTEM restored (user clicks toggle again)
  localStorage key 'epm-theme' = "system"
  Reverts to reading matchMedia — no "force light" option needed
```

**`useTheme` hook** (`/frontend/src/hooks/useTheme.ts`):
```typescript
type ThemeMode = 'system' | 'dark';
// Exports:
//   resolvedTheme: 'light' | 'dark'   — what is actually rendered right now
//   toggleTheme: () => void            — cycles system → dark → system
//   theme: ThemeMode                   — stored preference ('system' | 'dark')
//
// On mount: read localStorage('epm-theme'). If absent or 'system',
//   subscribe to matchMedia. If 'dark', apply .dark immediately.
// On change: document.documentElement.classList.toggle('dark', resolved === 'dark')
```

**Toggle button — in top navbar, between Edit Mode toggle and bell icon:**
```
SIZE: 32px × 32px, ghost button (no background at rest)
BORDER-RADIUS: 8px
HOVER: bg-[var(--bg-subtle)]

ICON (Lucide, 18px):
  resolvedTheme === 'light' → Moon  icon, color: var(--text-secondary)
  resolvedTheme === 'dark'  → Sun   icon, color: var(--accent-gold)

TOOLTIP:
  Light: "Switch to dark mode"
  Dark:  "Return to system theme"

ANIMATION: 150ms opacity fade when icon swaps
```

**CRITICAL — Every colour in every component must use CSS variables.**
Never hardcode hex values in component files. This is what enables zero-duplication theming:
```
✅  bg-[var(--bg-surface)]       text-[var(--text-primary)]    border-[var(--border)]
❌  bg-white                     text-gray-900                  border-gray-200
```

**Dark mode sidebar:** `--bg-sidebar` resolves to `#0d1117` in dark mode. Add
`border-right: 1px solid var(--border)` to distinguish sidebar from canvas.

### Layout Inspiration
The layout follows the style of a professional analytics dashboard:
- Coloured sidebar (220px) on the left — slate-grey in light, near-black in dark
- Off-white (light) / near-black (dark) content area on the right
- Card-based layout with subtle shadows
- Tables contained within cards (not full-viewport)
- Clear typographic hierarchy: large DM Mono metric values + small Plus Jakarta Sans labels

---

## GLOBAL LAYOUT SHELL

### Sidebar (220px, desktop)
```
Background: linear-gradient(180deg, #646763 0%, #4a4d4b 100%)

TOP (56px):
  "EPM" monogram — DM Mono, 20px, weight 700, color: #BCBDFA
  "Estate Portfolio" — Plus Jakarta Sans, 11px, rgba(255,255,255,0.6)

SEARCH BAR:
  Background: rgba(255,255,255,0.10)
  Placeholder "Search..." — rgba(255,255,255,0.5)
  Border: 1px rgba(255,255,255,0.15), border-radius 6px
  "/" shortcut badge, right-aligned

SECTION LABEL "MAIN":
  10px, rgba(255,255,255,0.4), uppercase, letter-spacing 0.1em

NAV ITEMS (40px each):
  Padding: 0 12px
  Layout: Icon (20px Lucide) + 12px gap + label (Plus Jakarta Sans 14px)
  
  Active:   background #BCBDFA, color #1A1A1A, border-radius 8px (with 8px margin)
  Hover:    background rgba(255,255,255,0.10), color #FFFFFF
  Inactive: color rgba(255,255,255,0.75)

MAIN NAV ITEMS:
  📊 Dashboard
  💼 Holdings            [amber dot badge if drafts exist]
  🏢 Companies
  💰 Dividends
  📈 Price History
  🔄 Transactions        [amber dot badge if drafts exist]
  📋 Registrars
  👁  Watchlist
  📉 NAV History
  ⚖️  Rebalancing

DIVIDER: 1px rgba(255,255,255,0.12)

ADMIN ONLY SECTION "ADMIN":
  ⚡ Price Entry         [color: #BCBDFA text — daily-use emphasis]
  📥 Data Import
  🏛  Corporate Actions
  👥 User Management
  🗑  Deleted Records

BOTTOM (user profile, 48px):
  Avatar: 32px circle, background #BCBDFA, DM Mono initials, color #1A1A1A
  Name: Plus Jakarta Sans 13px, white
  Role: "Admin" or "Viewer" — 10px, rgba(255,255,255,0.5)
  Sign-out icon: right side
```

### Top Navbar (56px)
```
Background: #FFFFFF
Border-bottom: 1px #E8E8EC
Fixed, full-width minus sidebar, z-index 50

LEFT: Page title — Plus Jakarta Sans 18px weight 600 #1A1A1A

RIGHT (flex, gap 12px):
  1. Edit Mode Toggle (admin only):
     Pill container: 130px × 32px, bg-[var(--bg-subtle)], border 1px var(--border), radius 999px
     VIEWING: lavender dot + "Viewing" — color: var(--text-secondary)
     EDITING: pencil icon + "Editing" — bg slides to #BCBDFA, color #1A1A1A
     Transition: 200ms ease sliding indicator inside pill

  2. Theme Toggle:
     32px × 32px ghost icon button, border-radius 8px
     hover: bg-[var(--bg-subtle)]
     resolvedTheme === 'light' → Moon icon (18px, var(--text-secondary))
     resolvedTheme === 'dark'  → Sun  icon (18px, var(--accent-gold))
     Tooltip: "Switch to dark mode" / "Return to system theme"
     onClick: calls toggleTheme() from useTheme()
     Icon swap: 150ms opacity fade

  3. Bell icon (admin): Lucide Bell 20px, var(--text-muted). Amber dot if action items pending.

  4. User avatar: 32px circle, #BCBDFA bg, DM Mono initials, color #1A1A1A
     Click → dropdown: Profile | Change Password | Sign Out

BETA BANNER (shown only when window.location.hostname includes "demo"):
  28px bar ABOVE navbar, background #BCBDFA, color #1A1A1A
  "BETA — demo.estate.zubbystudio.shop — Feedback welcome"
  10px, Plus Jakarta Sans, centered
```

### Mobile (< 768px)
```
Sidebar: hidden. Hamburger icon in navbar opens full-height overlay (280px, tap outside closes).

Bottom nav bar (fixed bottom, 56px):
  Background #FFFFFF, border-top 1px #E8E8EC
  5 items: [📊] [💼] [💰] [📈] [⋯ More]
  Active: #BCBDFA icon + label; Inactive: text-muted
  "More" → bottom sheet with remaining items
```

---

## ROUTE STRUCTURE

```typescript
// Protected route: redirects to /login if no user in authStore
// Admin route: also checks isAdmin() — shows 403 if readonly tries to access

/login                    — public
/                         — redirect to /dashboard
/dashboard                — protected
/holdings                 — protected
/companies                — protected
/dividends                — protected
/price-history            — protected
/transactions             — protected
/registrars               — protected
/watchlist                — protected
/nav-history              — protected
/rebalancing              — protected
/settings/price-entry     — admin only
/settings/data-import     — admin only
/settings/corporate-actions — admin only
/settings/users           — admin only
/settings/deleted-records — admin only
```

---

## ZUSTAND STORES

```typescript
// authStore.ts
interface User {
  id: number;
  username: string;
  name: string;
  role: 'admin' | 'readonly';
}
interface AuthStore {
  user: User | null;
  isAdmin: () => boolean;
  setUser: (user: User) => void;
  clearUser: () => void;
}

// uiStore.ts
interface UIStore {
  editMode: boolean;
  toggleEditMode: () => void;   // only callable when isAdmin()
  sidebarOpen: boolean;         // mobile sidebar overlay
  toggleSidebar: () => void;
}

// Theme state lives in useTheme hook (NOT in Zustand — must run before React renders)
// /frontend/src/hooks/useTheme.ts
// useTheme() returns: { resolvedTheme, theme, toggleTheme }
// Call useTheme() in App.tsx on mount to initialise before first render
// All other components call useTheme() to read resolvedTheme for conditional rendering
```

---

## PAGE SPECS

### Login Page

```
LAYOUT: Two-panel, side by side (desktop); single column (mobile)

LEFT PANEL (60%):
  Background: linear-gradient(135deg, #646763 0%, #4a4d4b 50%, #3a3d3b 100%)
  Center:
    "EPM" — DM Mono, 72px, weight 700, #BCBDFA
    Radial glow behind: rgba(188,189,250,0.20), 400px radius
    "Your Portfolio, Clearly." — Plus Jakarta Sans 20px, rgba(255,255,255,0.85)
    Bottom-left: "Estate Portfolio Manager v2.0" — 12px, rgba(255,255,255,0.4)

RIGHT PANEL (40%):
  Background: #FDFEFE
  Content: vertically centered, max-width 360px, 40px horizontal padding
  
  "Welcome back" — Plus Jakarta Sans 28px weight 700 #1A1A1A
  "Sign in to your portfolio" — 14px text-secondary, 8px below

  Username input (44px, border #E8E8EC, focus: border #BCBDFA + focus-ring)
  Password input (same + show/hide eye toggle)
  
  [Sign In] button: full width, 44px, background #BCBDFA, color #1A1A1A, weight 600
    Hover: background #a9aaef
    Loading: centered spinner, no text
  
  Error: 13px #EF4444, fade-in animation below button

  On submit: POST /api/v1/auth/login → store user in authStore → navigate /dashboard

MOCK: Use credentials admin/admin123 for mock mode.
```

### Dashboard Page

**KPI Cards (4-card row):**
```
Each card: #FFFFFF bg, border 1px #E8E8EC, 12px radius, 20px padding
Shadow: var(--shadow-card)
Left border accent: 3px solid [card accent color]

Card structure:
  Row 1: Label (12px, Plus Jakarta Sans, uppercase, letter-spacing 0.05em, text-secondary) 
         + Lucide icon (right, 20px)
  Row 2: Value (DM Mono, 30px, weight 600, text-primary)
         COUNT-UP ANIMATION: animates from 0 to value on mount (800ms ease-out)
         Use a custom hook: useCountUp(targetValue, 800)
  Row 3: Change indicator (DM Mono, 13px, green/red with ↑↓ arrow)

Card 1 — TOTAL PORTFOLIO VALUE:
  Accent: #BCBDFA | Icon: TrendingUp (lavender)
  Value: "₦12,345,678.00" | Sub: "Unrealised gain +₦1.2M"

Card 2 — TOTAL INVESTED:
  Accent: #DABF82 | Icon: DollarSign (gold)
  Value: "₦11,100,000.00" | Sub: "Cost basis"

Card 3 — UNREALISED GAIN/LOSS:
  Accent: #22C55E (green) or #EF4444 (red)
  Icon: BarChart2
  Value: "+₦1,245,678.00" | Sub: "+11.22% overall"

Card 4 — TOTAL HOLDINGS:
  Accent: #BCBDFA | Icon: Briefcase
  Value: "24" (integer, no ₦)
  Sub (admin only): "22 live · 2 draft"
```

**Charts Row (45% + 55%):**
```
LEFT CARD — Sector Allocation Donut:
  Header: "Sector Allocation" (Plus Jakarta Sans 16px weight 600) 
          + "Monthly" period selector dropdown (right, ghost button style)
  
  Recharts PieChart, donut, 200px diameter
  Center label: total portfolio value, DM Mono 13px, text-secondary
  Colors (8 distinct, starting with): #BCBDFA, #DABF82, #22C55E, #F59E0B,
                                      #EF4444, #60A5FA, #A78BFA, #34D399
  Legend: right of chart, vertical
    ● Sector name — percentage  (14px, Plus Jakarta Sans)
  Hover tooltip: white card, sector + ₦value + %

RIGHT CARD — Top Holdings:
  Header: "Top Holdings" (16px weight 600) + "by Value" label (text-muted 13px)
  
  Recharts BarChart (horizontal)
  Y-axis: ticker symbols, DM Mono 12px
  X-axis: ₦ values, abbreviated (₦1.2M)
  Bars: fill #BCBDFA, border-radius on right end only (4px)
  End label: return% in #22C55E or #EF4444, DM Mono 12px
  Max 10 rows
```

**Bottom Row (60% + 40%):**
```
LEFT CARD — Recent Transactions:
  Header: "Recent Transactions" + "View all →" (right, lavender link, 13px)
  
  Table (5 rows, no pagination):
  | Date (DM Mono 13px) | Ticker (DM Mono) | Type (badge) | Shares (DM Mono) | Amount (DM Mono) |
  
  Type badges (pill, 10px, Plus Jakarta Sans weight 600):
    BUY:    bg #DCFCE7, text #16A34A
    SELL:   bg #FEE2E2, text #DC2626
    BONUS:  bg #EDE9FE, text #7C3AED
    RIGHTS: bg #DBEAFE, text #2563EB
  
  Row hover: #F5F5F7
  Empty: muted ListX icon + "No transactions yet" (14px, text-secondary)

RIGHT CARD — Action Items:
  Header: "Action Items" (16px weight 600) + bell icon
  
  Each alert row: left icon + message text + right badge
    "2 holdings pending publish"   → amber badge "2" → onClick navigates /holdings
    "3 transactions to review"     → amber badge "3" → onClick navigates /transactions
    "Prices not updated in 8 days" → red badge "!"  → onClick navigates /settings/price-entry
  
  All-clear state (when no alerts):
    Check icon, 48px, #22C55E, centered
    "Portfolio up to date" — 14px, text-secondary
  
  Footer: "Last updated: Mon Apr 14, 2026 18:02 WAT"
          DM Mono, 12px, text-muted, right-aligned
```

### Holdings Page

```
HEADER ROW:
  "Holdings" (h1) + "(24 positions)" (text-secondary, 14px, Plus Jakarta Sans)
  Right (admin + editMode): [+ Add Holding] (lavender button) [↓ Export ▼] (ghost button)

FILTER ROW (card, padding 12px 16px):
  [🔍 Search ticker or company...] [Sector ▼] [Status: All ▼] [Sort ▼]
  Status options: All | Live | Draft (Draft option: admin only)

TABLE (TanStack Table, in card):
  Table header: 12px, Plus Jakarta Sans, weight 600, uppercase, letter-spacing 0.05em,
                text-secondary, bg #F5F5F7, 40px height
  Rows: 48px height, alternating #FFFFFF / #F5F5F7
  Row hover: #EEF0FF (very light lavender tint)
  Sticky header: YES
  Sticky first column (Ticker): YES (for mobile horizontal scroll)
  
  COLUMNS:
    Ticker      — DM Mono, 14px, weight 600, text-primary
    Company     — Plus Jakarta Sans 14px, text-primary
    Sector      — colour pill badge (see sector colours below)
    Shares      — DM Mono, 14px, right-aligned
    Avg Cost    — DM Mono, 14px, "₦XX.XX", right-aligned
    Curr Price  — DM Mono, 14px, "₦XX.XX", right-aligned
    Curr Value  — DM Mono, 14px weight 600, "₦XXX,XXX.XX", right-aligned
    Cost Basis  — DM Mono, 14px, right-aligned
    return[%]   — DM Mono, 14px, right-aligned  ← EXACT column header text
                  Positive: #22C55E, "+12.34%"
                  Negative: #EF4444, "-3.21%"
                  Zero: text-muted, "0.00%"
    Div Yield   — DM Mono, 14px, right-aligned, "4.5%"
    Status      — pill badge (admin only column):
                  LIVE:  bg #DCFCE7, text #16A34A
                  DRAFT: bg #FEF3C7, text #D97706
    Actions     — icon buttons (admin + editMode only):
                  Live row:  [✏] [🗑] ghost icon buttons, 32px
                  Draft row: [✏] [✓ Publish] [🗑] — Publish is lavender pill

  DRAFT ROW TREATMENT:
    Left border: 3px solid #F59E0B
    Background: rgba(245,158,11,0.04)
    Text opacity: 0.75

  SECTOR BADGE COLOURS (consistent across ALL pages):
    Banking:         bg #DBEAFE, text #2563EB
    Consumer Goods:  bg #DCFCE7, text #16A34A
    Oil & Gas:       bg #FEF3C7, text #D97706
    Industrials:     bg #F5F3FF, text #7C3AED
    Healthcare:      bg #FCE7F3, text #DB2777
    Telecoms:        bg #ECFDF5, text #059669
    Conglomerate:    bg #FFF7ED, text #EA580C
    Insurance:       bg #F0F9FF, text #0284C7
    (others: bg #F5F5F7, text #374151)

  PAGINATION: 25 rows/page, bottom-right

ADD HOLDING PANEL (admin + editMode, slides down below filter row):
  2-column form grid:
    Company (searchable dropdown, options from /api/v1/companies)
    Status (toggle: Draft | Publish now)
    Shares (number input, DM Mono)
    Purchase Date (date picker)
    Avg Purchase Price (₦, number input, DM Mono)
    Notes (full-width textarea, colspan 2)
  Buttons: [Cancel] ghost  [Save as Draft] secondary  [Save & Publish] lavender
  On success: new row fades + slides into table
```

### Price Entry Page (/settings/price-entry)

```
TWO-COLUMN LAYOUT (55% left + 45% right), stacked on mobile

LEFT CARD — Quick Price Update:
  Heading: "Quick Price Update" (18px weight 600)
  Subtitle: "Update a single stock's current price" (14px text-secondary)
  
  Form:
    Company dropdown (searchable typeahead):
      Option format: "[TICKER] Company Name — ₦current_price"
    
    New Price input:
      56px height, DM Mono, 28px font
      ₦ prefix (inside input, text-secondary)
      border #E8E8EC, focus: border #BCBDFA + focus ring
    
    Date picker (defaults to today, no future dates)
    
    [Update Price] — full width, 44px, lavender button
  
  Success toast: slides from top-right
    "DANGCEM updated → ₦123.45" — green, 4s auto-dismiss

  SUB-SECTION: "Recent Changes"
  Table (last 20 rows):
    | Date | Ticker | Old Price | New Price | Δ | Source | Revert |
    All numbers: DM Mono
    Source badges: 
      manual:     bg #F5F5F7, text-secondary
      csv_upload: bg #DBEAFE, text #2563EB
      stooq_csv:  bg #EDE9FE, text #7C3AED
    Revert: "Revert" text in #BCBDFA, click → confirmation modal

RIGHT CARD — Bulk CSV Import:
  Heading: "Bulk CSV Import" (18px weight 600)
  
  STEP 1 — Drop Zone (initial state):
    Dashed border: 1.5px #BCBDFA, border-radius 12px, height 180px, bg #F8F8FF
    Upload icon (40px, #BCBDFA)
    "Drop CSV or Excel here" — 15px, text-secondary
    "or click to browse" — 13px, text-muted
    ".csv · .xlsx · .xls accepted" — 11px, text-muted
    [Browse File] ghost button
    
    INFO BOX below drop zone:
      bg #F0F0FF, border-left 3px solid #BCBDFA, padding 12px, border-radius 6px
      "💡 Stooq Scraper: generates CSV automatically from the server.
       See README → Price Data Sources for the exact server command."
      12px, text-secondary

  STEP 2 — Column Mapping (appears after file selected):
    "Map your columns" heading (14px weight 600)
    Rows:
      "Ticker  →" [dropdown of CSV headers ▼] — required
      "Price   →" [dropdown ▼] — required
      "Date    →" [dropdown ▼] — required
      "Volume  →" [Skip ▼]    — optional
    [← Back] ghost  [Preview →] lavender

  STEP 3 — Preview table (10 rows):
    Valid rows: normal
    Error rows: left border 3px #EF4444, hover shows tooltip with error reason
    Unknown ticker rows: left border 3px #F59E0B
    Summary row below table:
      "47 valid" (green pill) · "3 errors" (red pill) · "2 unknown" (amber pill)
    [← Back]  [Commit 47 rows →] lavender (disabled if 0 valid rows)

  STEP 4 — Result:
    Checkmark icon, 64px, #BCBDFA, scale-in animation
    "47 prices updated successfully" (18px weight 600)
    "3 rows skipped" — "Show details ▼" collapsible
    [Import Another File] secondary button
```

### NAV History Page

```
HEADER: "NAV History" (h1) + [▶ Take Snapshot] ghost button (admin only)

PERIOD PILLS (below header, inline flex):
  [1M] [3M] [6M] [1Y] [All]
  Active: bg #BCBDFA, text #1A1A1A
  Inactive: bg transparent, border 1px #E8E8EC, text-secondary

CHART CARD (full width):
  Recharts AreaChart, height 360px
  Area 1: Portfolio Value — fill #BCBDFA opacity 0.25, stroke #BCBDFA 2px
  Area 2: Total Invested  — fill #DABF82 opacity 0.20, stroke #DABF82 2px dashed
  X-axis: DM Mono, 12px, text-secondary
  Y-axis: ₦ abbreviated (₦1.2M), DM Mono, right side
  Grid: #E8E8EC horizontal lines only
  Tooltip: white card, 12px radius, shadow
           shows: date + portfolio value + invested + gain + return%

STATS ROW (3 mini-cards):
  Best Day / Worst Day / Since Inception
  Same card style as Dashboard KPIs, smaller (22px value font)

DATA TABLE (collapsible, default 30 rows):
  | Date | Portfolio Value | Total Invested | Gain/Loss | Return % |
  All numbers: DM Mono, right-aligned
  "Show all X rows" / "Collapse" toggle link (lavender)
```

### Rebalancing Page

```
HEADER: "Rebalancing" (h1) + [✏ Edit Targets] lavender button (admin only)

ALLOCATION CARD (full width):
  TABLE:
  | Sector | Current Value | Current % | Target % | Gap | Visual Bar | Recommendation |
  
  GAP: 
    +X.X% overweight: #EF4444, "▲ +5.2%"
    -X.X% underweight: #F59E0B, "▼ -1.9%"
    ≈ 0 (within ±0.5%): #22C55E, "≈ On Target"
  
  VISUAL BAR (200px wide, inside table cell):
    Blue fill (#BCBDFA) = current % of bar width
    Gold dashed vertical line (#DABF82) = target % position
    Red extension right of line if over, amber dotted left reach if under
  
  RECOMMENDATION: "Reduce" red | "Increase" green | "Hold" text-muted

EDIT TARGETS DRAWER (right side, 380px, slides in on button click):
  Overlay behind (rgba(0,0,0,0.3) on content area)
  Heading: "Set Sector Targets" (18px weight 600)
  Warning: "Allocations must sum to 100%"
  Running total: large number, #22C55E if 100%, #F59E0B otherwise
  
  Per sector: text label (Plus Jakarta Sans 14px) + number input (DM Mono) + "%" suffix
  [+ Add Sector] text link (lavender, 13px)
  [Save Targets] lavender button (disabled + tooltip if total ≠ 100%)
  [✕] close button top-right
```

### Transactions Page

```
HEADER: "Transactions" (h1)
Right (admin + editMode): [+ Add Transaction] lavender  [Import CSV] ghost

FILTER CARD:
  [Search ticker...] [Type ▼] [Date range: from → to] [Status ▼]

TABLE:
  | Date | Ticker | Type | Shares | Price/Share | Net Amount | Broker Fee | Notes | Status | Actions |
  All numbers: DM Mono, right-aligned
  
  TYPE BADGES: same colours as Dashboard
  
  AUTO-GENERATED rows: "AUTO" grey pill in Notes — Edit button disabled
    Disabled edit tooltip: "Auto-generated from corporate action or holdings"
  
  DRAFT rows: amber left border treatment (identical to Holdings)

EMPTY STATE:
  Inbox icon (48px, text-muted)
  "No transactions recorded yet."
  "Add via Holdings or import a CSV." (text-muted, 14px)
  [Go to Holdings →] lavender ghost button
```

### Other Pages (consistent pattern)

```
COMPANIES:
  Table with sector badge, registrar as lavender clickable link → /registrars/{id}
  Inline edit panel (editMode) — same slide-down pattern as Holdings

REGISTRARS:
  "Companies" column: count badge (e.g. "12")
  Click row → TanStack Table row expand/accordion
  Expanded: list of linked companies with [TICKER] Name (DM Mono / Plus Jakarta Sans)

DIVIDENDS:
  Tabs: [All Dividends] [Annual Summary] [Import CSV]
  DRIP column: ✓ (green check) or — (text-muted)
  Annual Summary: year rows + "Lifetime Total" card at bottom (gold accent)

WATCHLIST:
  "Gap to Target" column:
    Current < Target: #22C55E "▼ -15.3% to target"
    Current > Target: #EF4444 "▲ +8.2% above target"
    No target: text-muted "—"
  Actions (editMode): [+ Add to Holdings] pre-fills Holdings Add New form

PRICE HISTORY:
  Filter: company dropdown + date range
  Line chart (Recharts) — stroke #BCBDFA, area fill lavender 15% opacity
  Table below chart: | Date | Price | Source badge |

SETTINGS — User Management:
  Table: Username | Name | Role | Last Login | Status (active/inactive) | Actions
  [+ Add User] lavender button (admin only)
  Actions: [Reset Password] [Deactivate] — not editable for own account

SETTINGS — Deleted Records:
  Tabs: [Holdings] [Transactions] [Companies] [Dividends]
  Table: Name/Ticker | Deleted Date | [Restore] lavender ghost button
  Restore: confirmation modal before executing
```

---

## SHARED COMPONENTS

### Empty States (every table must have one)
```
Centered in card, minimum 120px height
Lucide icon: 40px, text-muted
Primary message: 14px, text-secondary
Secondary message: 13px, text-muted  
CTA button: only in editMode (admin)
```

### Loading Skeletons (every data-fetching component)
```
Use animated shimmer: background gradient animating left-to-right
  from: #F5F5F7 → #E8E8EC → #F5F5F7
  duration: 1.5s infinite
KPI cards: full card skeleton matching card dimensions
Tables: 5 skeleton rows, proportional column widths
Charts: pulsing rectangle matching chart height
```

### Toast Notifications (top-right, stacked, auto-dismiss 4s)
```
Success: bg #DCFCE7, left border 3px #22C55E, check icon
Error:   bg #FEE2E2, left border 3px #EF4444, X icon
Warning: bg #FEF3C7, left border 3px #F59E0B, alert icon
Progress bar at bottom of toast (drains over 4s)
Width: 320px, border-radius 8px, shadow: var(--shadow-dropdown)
```

### Confirmation Modal
```
Background overlay: rgba(0,0,0,0.4)
Card: 400px wide, #FFFFFF, 12px radius, 24px padding
Heading: 18px weight 600
Body: 14px text-secondary
Buttons: [Cancel] ghost + [Confirm] (red if destructive, lavender if safe)
```

### Count-Up Animation Hook
```typescript
// Custom hook for KPI value animation
function useCountUp(target: number, duration: number = 800): number {
  // Animates from 0 to target over duration ms using requestAnimationFrame
  // Returns current animated value
  // Reset and replay on target change
}
```

---

## API INTEGRATION (TanStack Query)

All hooks use `/api/v1/...` relative paths. Use mock data during development.

```typescript
// Example hook pattern:
export function useHoldings() {
  return useQuery({
    queryKey: ['holdings'],
    queryFn: () => fetch('/api/v1/holdings').then(r => r.json()),
  });
}

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: () => fetch('/api/v1/dashboard').then(r => r.json()),
    refetchInterval: 60_000, // auto-refresh every 60s
  });
}
```

Credentials mode for all fetch calls: `credentials: 'include'` (sends httpOnly cookie).

On 401 response: clear authStore, redirect to /login.
On 403 response: show inline "Access denied — Admin required" message.

---

## MOCK DATA FOR DEVELOPMENT

Use this structure for all mock responses:

```typescript
const MOCK_DASHBOARD = {
  data: {
    total_portfolio_value: "12345678.00",
    total_invested: "11100000.00",
    unrealised_gain_loss: "1245678.00",
    unrealised_gain_pct: "+11.22",
    total_holdings: 24,
    sector_allocation: [
      { sector: "Banking", value: "4350000.00", pct: "35.2" },
      { sector: "Consumer Goods", value: "2235000.00", pct: "18.1" },
      { sector: "Oil & Gas", value: "1800000.00", pct: "14.6" },
      { sector: "Telecoms", value: "1480000.00", pct: "12.0" },
      { sector: "Industrials", value: "1234000.00", pct: "10.0" },
      { sector: "Healthcare", value: "1246678.00", pct: "10.1" },
    ],
    top_holdings: [
      { ticker: "DANGCEM", company: "Dangote Cement", value: "2100000.00", return_pct: "+22.5" },
      { ticker: "GTCO",    company: "GT Holdco",      value: "1890000.00", return_pct: "+15.3" },
      { ticker: "ZENITH",  company: "Zenith Bank",    value: "1650000.00", return_pct: "+8.7"  },
      { ticker: "SEPLAT",  company: "Seplat Energy",  value: "1200000.00", return_pct: "-2.1"  },
      { ticker: "MTNN",    company: "MTN Nigeria",    value: "980000.00",  return_pct: "+4.5"  },
    ],
    recent_transactions: [
      { date: "2026-04-14", ticker: "DANGCEM", type: "BUY",   shares: 500,  amount: "615000.00" },
      { date: "2026-04-10", ticker: "GTCO",    type: "SELL",  shares: 200,  amount: "98000.00"  },
      { date: "2026-04-05", ticker: "SEPLAT",  type: "BONUS", shares: 100,  amount: "0.00"      },
    ],
    last_updated: "2026-04-14T18:02:00Z"
  }
};

const MOCK_USER = {
  id: 1, username: "zubbyik", name: "Zubby", role: "admin" as const
};
```

---

## DELIVERABLES CHECKLIST

Lovable must produce all of the following:

```
✅ /frontend/src/store/authStore.ts        — Zustand auth store
✅ /frontend/src/store/uiStore.ts          — Zustand UI store (editMode, sidebar)
✅ /frontend/src/hooks/useCountUp.ts       — count-up animation hook
✅ /frontend/src/hooks/useTheme.ts         — theme system (system default + dark override)
✅ /frontend/src/api/                      — TanStack Query hooks per domain
✅ /frontend/src/types/                    — TypeScript interfaces for all API shapes
✅ /frontend/src/components/layout/Sidebar.tsx
✅ /frontend/src/components/layout/Navbar.tsx
✅ /frontend/src/components/layout/ProtectedRoute.tsx
✅ /frontend/src/components/layout/AdminRoute.tsx
✅ /frontend/src/components/ui/            — shadcn/ui components used
✅ /frontend/src/components/shared/        — Empty states, skeletons, toasts, modal
✅ /frontend/src/pages/Login.tsx
✅ /frontend/src/pages/Dashboard.tsx
✅ /frontend/src/pages/Holdings.tsx
✅ /frontend/src/pages/Companies.tsx
✅ /frontend/src/pages/Dividends.tsx
✅ /frontend/src/pages/PriceHistory.tsx
✅ /frontend/src/pages/Transactions.tsx
✅ /frontend/src/pages/Registrars.tsx
✅ /frontend/src/pages/Watchlist.tsx
✅ /frontend/src/pages/NavHistory.tsx
✅ /frontend/src/pages/Rebalancing.tsx
✅ /frontend/src/pages/settings/PriceEntry.tsx
✅ /frontend/src/pages/settings/DataImport.tsx
✅ /frontend/src/pages/settings/CorporateActions.tsx
✅ /frontend/src/pages/settings/UserManagement.tsx
✅ /frontend/src/pages/settings/DeletedRecords.tsx
✅ /frontend/vite.config.ts               — outputs to dist/ (no subdirectory)
✅ /frontend/tailwind.config.ts           — uses CSS variables from design system
✅ /frontend/index.html                   — loads Google Fonts (DM Mono + Plus Jakarta Sans)
✅ /frontend/package.json                 — all dependencies listed
```

---

## WHAT LOVABLE MUST NOT GENERATE

```
❌ Any file in /backend/
❌ FastAPI, SQLAlchemy, Alembic, or Python code of any kind
❌ Supabase client, supabase.ts, supabase-js imports
❌ SUPABASE_URL or SUPABASE_ANON_KEY env variables
❌ localStorage usage for auth tokens
❌ Hardcoded absolute URLs (use /api/v1/ relative paths only)
❌ Dockerfile or docker-compose.yml
❌ Any reference to the old Streamlit app
```

---

## PROMPT END

**After Lovable generates**: push code to GitHub. Antigravity will review the PR,
remove any Supabase remnants, wire the Vite build output into the FastAPI static
directory, and deploy via GitHub Actions to demo.estate.zubbystudio.shop.
