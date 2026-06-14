---
type: HO
id: HO-009
title: Claude → Antigravity: Dashboard, Holdings, Registrars, Price History Implementation
date: 2026-05-08
from: Claude (The Brain)
to: Antigravity (Builder)
protocol: MASTER_CONTEXT.md v4.0
---

# [HO] HO-009 — Claude → Antigravity: UI Implementation
> **Type**: Handover · **Date**: 2026-05-08

---

## Execution Order

Build these four pages simultaneously (they share data — price history
feeds holdings, holdings feeds dashboard). Complete in this sprint order:

```
1. Backend: registrar_contact_fields table + extended API
2. Backend: registrar 405 fix verification
3. Frontend: Price History page (SC-UI-041 to SC-UI-046)
4. Frontend: Holdings inline editing (SC-UI-020 to SC-UI-031)
5. Frontend: Dashboard fixes (SC-UI-001 to SC-UI-019)
6. Frontend: Registrar extended fields + delete (SC-UI-032 to SC-UI-040)
7. AT-003 acceptance test — fill in results
8. Handover HO-010 to Claude
```

Uncle Bob rule applies to each item:
write failing test → confirm RED → write production code → GREEN

---

## 1. Backend — Registrar Extended Contact Fields

### New table (Alembic migration)

```sql
CREATE TABLE registrar_contact_fields (
    id           SERIAL PRIMARY KEY,
    registrar_id INTEGER NOT NULL REFERENCES registrars(id) ON DELETE CASCADE,
    field_type   VARCHAR(20) NOT NULL
                 CHECK (field_type IN ('phone','email','address','website','other')),
    field_value  TEXT NOT NULL,
    label        VARCHAR(100) DEFAULT NULL,
    -- optional label e.g. "WhatsApp" or "Head Office"
    sort_order   SMALLINT NOT NULL DEFAULT 0,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ DEFAULT NULL
);
CREATE INDEX idx_registrar_contact_fields_registrar
  ON registrar_contact_fields(registrar_id) WHERE deleted_at IS NULL;
```

### Updated Registrar response shape

```python
# GET /api/v1/registrars now includes contact_fields array
{
  "id": 13,
  "name": "First Registrars Nigeria Ltd",
  "email": "info@firstregistrars.com.ng",
  "phone": "0800-555-0100",           # kept for backward compat
  "contact_address": "...",
  "response_rating": 4,
  "contact_fields": [                  # NEW
    {"id": 1, "field_type": "phone",   "field_value": "0802-555-0199", "label": null},
    {"id": 2, "field_type": "website", "field_value": "https://firstregistrars.com.ng", "label": null}
  ],
  "linked_companies": [...],
  "requirement_count": 5,
  "pending_document_count": 2
}
```

### Updated PUT /api/v1/registrars/{id}

```python
# Accepts contact_fields array — replaces all existing non-deleted fields
# Pattern: delete existing (soft), insert new ones
class RegistrarUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    contact_address: Optional[str]
    response_rating: Optional[int]
    notes: Optional[str]
    contact_fields: Optional[list[ContactFieldIn]]  # NEW

class ContactFieldIn(BaseModel):
    field_type: Literal['phone','email','address','website','other']
    field_value: str
    label: Optional[str] = None
    sort_order: int = 0
```

---

## 2. Backend — Verify Registrar 405 Fix (HO-008)

HO-008 states this was fixed. Verify with:
```bash
curl -X POST https://demo.estate.zubbystudio.shop/api/v1/registrars/13/companies/115 \
  -H "Cookie: epm_token=<valid_token>"
# Expected: 200 OK (not 405)
```

If 405 still occurs: the router prefix is the culprit. The router must be
mounted at `/api/v1` with the route defined as `/registrars/{id}/companies/{company_id}`.

---

## 3. Frontend — Price History Page

**File**: `src/routes/_app.price-history.tsx`

```
Layout:
  Header: "Price History" h1
  Company selector: searchable dropdown (useCompanies())
  Date range pills: [7D] [30D] [90D] [1Y] [All] — default 30D
  Chart: Recharts LineChart
    - stroke: #BCBDFA (accent-lavender)
    - area fill: rgba(188,189,250,0.15)
    - X-axis: dates, DM Mono
    - Y-axis: ₦ values, DM Mono
    - tooltip: date + price + source
  Table below chart:
    | Date | Price (₦) | Source |
    source badges: manual=grey, ngx_pdf_upload=lavender, csv_upload=blue

Empty state (no company selected):
  "Select a company above to view its price history"

Empty state (company has no history):
  "No price history for {ticker} yet.
   Upload an NGX PDF or use Quick Price Entry to add prices."
```

**New TanStack Query hook** (add to queries.ts):
```typescript
export function usePriceHistory(companyId: number | null, days: number) {
  return useQuery({
    queryKey: ['price-history', companyId, days],
    queryFn: () =>
      fetch(`/api/v1/prices/history/${companyId}?days=${days}`,
        { credentials: 'include' })
        .then(r => r.json()).then(r => r.data),
    enabled: companyId !== null,
  });
}
```

---

## 4. Frontend — Holdings Inline Editing

**State model** (add to Holdings page component):
```typescript
// null = no row editing; 'new' = add row; number = editing existing row id
const [editingRowId, setEditingRowId] = useState<number | 'new' | null>(null);
```

**Inline form row** (appears at TOP of table when editingRowId === 'new'):
```
| [Company dropdown] | [Shares input] | [Avg Cost input] | [Status toggle] | [Save] [Cancel] |
```

**Inline edit row** (replaces read-only cells when editingRowId === holdingId):
```
| DANGCEM | Dangote Cement | Banking | [Shares input] | [Avg Cost input] | ... | [Save] [Cancel] |
```

**Validation before API call**:
- Shares: must be integer > 0
- Avg Cost: must be Decimal > 0
- Company (add only): must not already exist in holdings (check useHoldings() cache)

**On Save**:
- Add: POST /api/v1/holdings → invalidate ['holdings', 'dashboard']
- Edit: PATCH /api/v1/holdings/{id} → invalidate ['holdings', 'dashboard']
- Set editingRowId back to null

**On Cancel**:
- Set editingRowId to null
- No API call

**Edit Mode guard**:
- [+ Add Holding] button only renders when `editMode && isAdmin()`
- Edit/Delete icons in Actions column only render when `editMode && isAdmin()`
- editingRowId resets to null when editMode is toggled off

---

## 5. Frontend — Dashboard Fixes

### 5A — Hide edit mode toggle on Dashboard

In `Navbar.tsx`, read the current route:
```typescript
const location = useLocation();
const isDashboard = location.pathname === '/dashboard';

// Render edit toggle only when NOT on dashboard
{isAdmin() && !isDashboard && <EditModeToggle />}
```

### 5B — Theme toggle functional

Verify `useTheme()` hook is wired to the Moon/Sun button in Navbar.
The button must call `toggleTheme()` on click. If it is rendering but
not functional, the onClick handler is missing or the hook is not imported.

```typescript
const { resolvedTheme, toggleTheme } = useTheme();

<button
  data-testid="theme-toggle"
  onClick={toggleTheme}
  aria-label={resolvedTheme === 'light' ? 'Switch to dark mode' : 'Return to system theme'}
>
  {resolvedTheme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
</button>
```

### 5C — Notification bell dropdown

```typescript
// New component: NotificationDropdown.tsx
// Reads from useActionItems() hook (derive from existing queries):

export function useActionItems() {
  const { data: holdings } = useHoldings();
  const { data: dashboard } = useDashboard();

  return useMemo(() => {
    const items = [];

    const draftCount = holdings?.filter(h => h.status === 'draft').length ?? 0;
    if (draftCount > 0)
      items.push({ message: `${draftCount} holdings pending publish`,
                   href: '/holdings', severity: 'amber' });

    const lastUpdated = dashboard?.last_updated;
    if (lastUpdated) {
      const daysSince = daysBetween(new Date(lastUpdated), new Date());
      if (daysSince > 7)
        items.push({ message: `Prices not updated in ${daysSince} days`,
                     href: '/settings/price-entry', severity: 'red' });
    }

    // Add claim-approved alert from dashboard.claims_summary
    const approvedClaims = dashboard?.claims_summary?.approved ?? 0;
    if (approvedClaims > 0)
      items.push({ message: `${approvedClaims} claim approved — collect payout`,
                   href: '/registrars', severity: 'green' });

    return items;
  }, [holdings, dashboard]);
}
```

Bell badge: `items.length > 0 ? <span className="badge">{items.length}</span> : null`

Dropdown: renders last 5 items, closes on outside click (use `useClickOutside` hook).

### 5D — Top Holdings chart toggle

```typescript
// uiStore addition
holdingsChartView: 'value' | 'shares'   // default: 'value'
setHoldingsChartView: (v) => void

// In Dashboard TopHoldingsChart component:
const { holdingsChartView, setHoldingsChartView } = useUIStore();
const chartData = holdingsChartView === 'value'
  ? topHoldings.map(h => ({ name: h.ticker, value: parseFloat(h.current_value) }))
  : topHoldings.map(h => ({ name: h.ticker, value: h.num_shares }));
```

### 5E — Recent Transactions columns

Confirm the Recent Transactions component renders these exact columns:
`Date | Ticker | Type (badge) | Shares (num_shares) | Amount (net_amount ₦)`

If Shares or Amount shows placeholder/null, trace back to the
dashboard API endpoint — confirm `recent_transactions` array includes
`num_shares` and `net_amount` fields.

### 5F — Action Items card

The card reads from `useActionItems()` (defined in 5C).
Four possible alerts:
1. Draft holdings → /holdings
2. Stale prices (>7 days) → /settings/price-entry
3. Approved claims → /registrars
4. All-clear state (no alerts) → green checkmark + "Portfolio up to date"

---

## 6. Frontend — Registrar Extended Fields + Delete

### 6A — Extended fields in Edit/Add modal

```typescript
// In RegistrarModal.tsx (used by both Edit and Add)

// State for extra fields
const [extraFields, setExtraFields] = useState<ContactFieldIn[]>([]);

const FIELD_TYPES = ['phone', 'email', 'address', 'website', 'other'] as const;

// Add field button
<button onClick={() => setShowFieldTypeSelector(true)}>+ Add Field</button>

// Field type selector (small popover)
{showFieldTypeSelector && (
  <div className="field-type-selector">
    {FIELD_TYPES.map(type => (
      <button key={type}
        onClick={() => {
          setExtraFields([...extraFields, { field_type: type, field_value: '', sort_order: extraFields.length }]);
          setShowFieldTypeSelector(false);
        }}>
        {type}
      </button>
    ))}
  </div>
)}

// Render extra field inputs
{extraFields.map((field, idx) => (
  <div key={idx} className="extra-field-row">
    <span className="field-type-badge">{field.field_type}</span>
    <input value={field.field_value}
      onChange={e => {
        const updated = [...extraFields];
        updated[idx].field_value = e.target.value;
        setExtraFields(updated);
      }} />
    <button onClick={() => setExtraFields(extraFields.filter((_, i) => i !== idx))}>×</button>
  </div>
))}
```

On Save: include `contact_fields: extraFields` in PUT/POST payload.

### 6B — Delete Registrar button

In the registrar detail panel header (alongside Edit Registrar button):
```typescript
{isAdmin() && editMode && (
  <>
    <button onClick={() => setShowEditModal(true)}>Edit Registrar</button>
    <button
      className="btn-danger"
      onClick={() => setShowDeleteConfirm(true)}
    >
      Delete
    </button>
  </>
)}

// Confirmation dialog
{showDeleteConfirm && (
  <ConfirmDialog
    title={`Delete ${registrar.name}?`}
    message={`This will remove all linked requirements and documents.
              ${linkedCount > 0 ? `${linkedCount} companies will be unlinked.` : ''}`}
    onConfirm={() => deleteRegistrarMutation.mutate(registrar.id)}
    onCancel={() => setShowDeleteConfirm(false)}
    confirmLabel="Delete"
    danger
  />
)}
```

---

## Acceptance Test

After implementation, fill in AT-003 (file: AT-003-dashboard-holdings-registrars-pricehist.md).
File the completed AT in `docs/testing/acceptance-tests/`.

Return HO-010 to Claude with AT-003 results.

---

## Dependencies to Add

```
# No new backend dependencies required for this sprint
# Frontend: no new packages — uses existing Recharts, TanStack, Zustand, Lucide
```

---

## Branch

All work on `test` branch. Push after each logical unit (backend migration,
then price history page, then holdings, then dashboard, then registrars).
Do not batch everything into one commit — smaller commits allow easier rollback.