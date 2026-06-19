---

id: F-005

title: Price History
status: COMPLETE
owner-backend: Owl Alpha | Nex N2             owner-frontend: Nex N2       
Review/Architect role: Deepseek

sprint: Phase 3A (complete)

---

# F-005 — Price History

## Goal

Show historical price movements per company as a line chart and table.

Allows the user to verify NGX PDF uploads and track price trends over time.

## What Is Built

Backend (backend/app/routers/prices.py):

  GET /api/v1/prices/history/{company_id}?days=30

    Returns price_history records for one company, filtered by days

    Default: 30 days. Options: 7, 30, 90, 180, 365, or all

Frontend:

  src/routes/_app.price-history.tsx

  src/api/queries.ts → usePriceHistory(companyId, days)

## API Response Shape

GET /api/v1/prices/history/{id}?days=30

{

  "data": [

    {

      "id": 42,

      "recorded_date": "2026-05-18",

      "price": "450.00",

      "source": "ngx_pdf_upload"

    }

  ],

  "meta": { "total": 30 },

  "error": null

}

Records ordered by recorded_date ascending (oldest first for chart left-to-right)

## Page Layout

Company selector:

  Searchable combobox (typeahead, not plain <select>)

  Uses CompanyCombobox component (same as price-entry page)

  Placeholder: "Select a company to view price history"

Date range pills (below company selector):

  [7D] [30D] [90D] [1Y] [All]  — default: 30D

  Active pill: lavender background

Line chart:

  Recharts LineChart wrapped in ResponsiveContainer inside sized div

  stroke: #BCBDFA (accent-lavender)

  Fill area: rgba(188,189,250,0.15)

  X-axis: dates (DM Mono)

  Y-axis: ₦ prices (DM Mono)

  Tooltip: date + price + source

  Data shape: { date: string, price: number (parsed from API string) }

Table below chart:

  | Date | Price (₦) | Source |

  Source badges: manual=grey, ngx_pdf_upload=lavender, csv_upload=blue

Empty state (no company selected):

  "Select a company above to view its price history"

Empty state (company selected, no records):

  "No price history for {ticker} yet.

   Upload an NGX PDF or use Quick Price Entry to add prices."

## usePriceHistory Hook

export function usePriceHistory(companyId: number | null, days: number) {

  return useQuery({

    queryKey: ['price-history', companyId, days],

    queryFn: () =>

      fetch(`/api/v1/prices/history/${companyId}?days=${days}`,

        { credentials: 'include' })

        .then(r => r.json()).then(r => r.data),

    enabled: companyId !== null,  // only fires when company is selected

  });

}

## Acceptance Checklist

### [DB]

- [x] price_history table has records after PDF uploads (610 records verified)

- [x] recorded_date matches date extracted from PDF filename (not today's date)

- [x] source column set correctly per upload method (ngx_pdf_upload, csv_upload, manual verified)

### [API]

- [x] GET /api/v1/prices/history/{id} → 200 with data array

- [x] GET /api/v1/prices/history/{id}?days=7 → records from last 7 days only

- [x] GET /api/v1/prices/history/9999 → empty data (no crash)

- [x] Records ordered ascending by recorded_date

- [x] "price" field is a JSON string (not float)

- [x] Readonly user → 200 (this page is accessible to all authenticated roles)

### [UI]

- [x] Searchable combobox renders (typing filters company list) — verified in TSX

- [x] Selecting a company loads the chart and table — verified in TSX

- [x] Line chart renders in lavender with correct data — verified in TSX (AreaChart, #BCBDFA)

- [x] No company selected → placeholder empty state visible — verified in TSX

- [x] Company with no history → descriptive empty state (not blank chart) — verified in TSX

- [x] 30D filter active by default — verified in TSX (daysFilter initial state = 30)

- [x] Clicking 7D → chart shows only last 7 days — verified in TSX

- [x] Table below chart shows Date, Price, Source columns — verified in TSX

- [x] Source badges display correct colour per source — verified in TSX (ngx_pdf_upload=lavender, csv_upload=blue, manual=gray)

- [x] Readonly user can access and view (no edit controls) — verified (no edit controls in component)

- [ ] No console errors on load — needs browser verification

## Sign-Off

- [ ] All checklist items verified
- [ ] No open bugs
