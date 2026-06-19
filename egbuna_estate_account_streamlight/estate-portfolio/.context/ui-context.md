# ui-context.md — EPM UI Context

---

## Design Aesthetic

Dark, technical, precise. Feels like a professional finance tool —
not a startup dashboard, not a corporate portal. Measured, trustworthy,
data-forward. Numbers dominate. Colour is used sparingly and deliberately.

---

## Colour Tokens (oklch — Tailwind v4)

NEVER use hardcoded hex values. Always use CSS variable tokens.

Primary action:   var(--accent-lavender)    #BCBDFA  (buttons, active states)
Danger / delete:  var(--accent-red)         #F87171
Success / live:   var(--accent-green)       #4ADE80
Warning / draft:  var(--accent-amber)       #FCD34D
Wealth / gold:    var(--accent-gold)        #DABF82  (total assets row)
Background:       var(--bg-surface)
Subtle bg:        var(--bg-subtle)
Border:           var(--border)
Text primary:     var(--text-primary)
Text secondary:   var(--text-secondary)
Text muted:       var(--text-muted)

---

## Typography

Numbers, tickers, monetary values, dates in tables:   font-mono  (DM Mono)
UI text, labels, headings, body:                      Plus Jakarta Sans
Code snippets:                                        JetBrains Mono

DM Mono is used for ANYTHING that needs to be read precisely:
  Share counts, prices, percentages, return%, cost basis, date strings
  Ticker symbols (always uppercase)

---

## Button Patterns

Primary (main action):
  bg-[var(--accent-lavender)] text-[#1A1A1A] font-medium
  hover:opacity-90 transition-opacity rounded-lg px-4 py-2

Secondary (cancel, back):
  border border-[var(--border)] text-[var(--text-secondary)]
  hover:bg-[var(--bg-subtle)] transition-colors rounded-lg px-4 py-2

Danger (delete, remove):
  text-[var(--accent-red)] border border-[var(--accent-red)]
  hover:bg-[var(--accent-red)] hover:text-white transition-colors rounded-lg px-3 py-1.5

---

## Status Badge Colours

pending:    bg-amber-100  text-amber-700  (amber pill)
live:       bg-green-100  text-green-700  (green pill)
draft:      bg-gray-100   text-gray-600   (grey pill)
claim:      bg-orange-100 text-orange-700 (orange pill)
submitted:  bg-blue-100   text-blue-700   (blue pill)
completed:  bg-green-100  text-green-700  (green pill)
rejected:   bg-red-100    text-red-700    (red pill)

Price audit source badges:
  manual:          grey pill
  ngx_pdf_upload:  lavender pill
  csv_upload:      blue pill
  revert_of_N:     amber pill

---

## Input Pattern

h-9 px-3 rounded-lg border border-[var(--border)]
bg-[var(--bg-surface)] text-[var(--text-primary)] text-sm
focus:outline-none focus:ring-2 focus:ring-[var(--accent-lavender)]

---

## Recharts Pattern (Critical — Charts Were Blank Without This)

Always wrap charts in a sized div + ResponsiveContainer:

  <div style={{ width: '100%', height: 300 }}>
    <ResponsiveContainer>
      <PieChart>...</PieChart>
    </ResponsiveContainer>
  </div>

Recharts requires NUMBERS for data values (not strings).
Parse at the component boundary before passing to chart:

  const chartData = (apiData ?? []).map(d => ({
    name: d.name,               // string — Recharts label (must be "name" field)
    value: parseFloat(d.value), // NUMBER — Recharts sizing (parse here only)
    display: fmtNaira(d.value), // string — tooltip display
  })).filter(d => d.value > 0);

---

## Layout Rules

Edit mode toggle:
  Hidden on /dashboard (always read-only page)
  Visible on all other pages for admin role only

Holdings table:
  Two separate tables — Active Portfolio + Claims Portfolio
  Grand total row below both tables
  Actions column only visible in edit mode

Inline editing:
  InlineEditRow is a CHILD COMPONENT with its own local state
  Parent table does NOT hold edit form state
  (Parent state = cursor jump bug — this was confirmed and fixed)

Add Holding form:
  Slide-out drawer from right (420px width)
  Holdings table stays visible behind drawer
  NOT a modal, NOT an inline table row

Notification bell:
  Count badge (amber) when action items exist
  Dropdown panel shows last 5 items on click
  Clicking outside closes dropdown

Tooltips:
  On ALL interactive icons and buttons
  Use Tooltip wrapper component from src/components/ui/Tooltip.tsx

---

## Chart Colours (Sector Allocation Donut)

CHART_COLORS array (cycle through for segments):
  ['#BCBDFA', '#4ADE80', '#FCD34D', '#F87171', '#DABF82',
   '#818CF8', '#34D399', '#FB923C', '#60A5FA', '#A78BFA']

---

## Empty States (Every Data View Must Have One)

No data yet:
  Icon (Lucide) + heading + helper text
  Never a blank page or a broken table with zero rows

Example:
  <div className="flex flex-col items-center gap-3 py-16 text-[var(--text-muted)]">
    <BarChart3 size={40} className="opacity-40" />
    <p className="text-sm">No price history for {ticker} yet.</p>
    <p className="text-xs">Upload an NGX PDF to add prices.</p>
  </div>

