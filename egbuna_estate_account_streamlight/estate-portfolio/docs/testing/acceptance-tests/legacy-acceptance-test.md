# EPM manual acceptance tests

## Price Entry Page (/settings/price-entry)

### Quick Price Update

- [ ] Page loads without crash for admin user
- [ ] Page is blocked (redirect) for readonly user
- [ ] Company dropdown populates with tickers + current prices
- [ ] Selecting a company shows its current price in the dropdown label
- [ ] Valid price entry → success toast shows old price, new price, delta%
- [ ] Updated price immediately reflected on /dashboard (no manual refresh)
- [ ] Updated price immediately reflected on /holdings (no manual refresh)
- [ ] Price audit log updates after successful entry
- [ ] Future date rejected with validation message (no API call)
- [ ] Negative price rejected with validation message
- [ ] Price > ₦100,000 rejected with sanity cap message
- [ ] First-ever price (old = null) → toast shows "first price set"

### Price Audit Log

- [ ] Last 20 price changes render in table
- [ ] Source badges: manual (grey), csv_upload (blue), revert_of_N (amber)
- [ ] Revert button on valid record → confirmation dialog appears
- [ ] Confirmation → price reverts → audit log updates → dashboard refreshes
- [ ] Revert button disabled on first-ever record (old_price = null)
- [ ] Empty state renders when no history exists

### Bulk CSV Import

- [ ] NGX info box visible with correct library URL
- [ ] [Download CSV Template] generates file with real tickers from DB
- [ ] .csv file accepted; .xlsx and .pdf rejected at upload
- [ ] Empty file returns 422 error message
- [ ] Valid 3-row CSV → preview shows 3 valid rows → commit → 3 prices updated
- [ ] Mixed CSV (47 valid + 3 invalid) → preview shows both → commit applies 47 only
- [ ] All-invalid CSV → commit button disabled in preview
- [ ] Error rows show row number, ticker, and specific error reason
- [ ] "Show details" expander works for skipped rows after commit
- [ ] [Import Another File] resets panel to Step 1
- [ ] Dashboard + Holdings refresh after successful CSV commit
