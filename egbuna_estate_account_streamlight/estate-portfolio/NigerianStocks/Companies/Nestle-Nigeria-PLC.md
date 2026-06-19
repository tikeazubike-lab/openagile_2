---
type: company
name: Nestle Nigeria PLC
ticker: NESTLE
registrar: "[[GTL-Registrars-Limited]]"
sector: Consumer Goods
status: listed
isin: ""
latest_price: 1870
latest_price_date: "2025-10-02"
currency: NGN
shares_held: 9045
avg_buy_price: 0
reference_number: "70"
notes: Actively trading on NGX - Blue chip stock
tags:
  - stock
  - nigerian-stock
  - listed
dividend_frequency: "annual"  # annual, semi-annual, quarterly, irregular
last_dividend_date: ""
last_dividend_per_share: 0.00
next_expected_dividend: ""
total_dividends_received: 0.00
---

# Nestle Nigeria PLC

## Overview
**Ticker:** NESTLE  
**Sector:** Consumer Goods  
**Status:** listed  
**Registrar:** [[GTL-Registrars-Limited]]  
**Reference #:** 70

## Current Status
Actively trading on NGX - Blue chip stock

## Holdings
- **Shares Held:** 0
- **Average Buy Price:** ₦0.00
- **Current Price:** ₦0.00
- **Market Value:** ₦0.00

## Recent Price History
```dataview
TABLE WITHOUT ID
  date as "Date",
  close as "Close",
  high as "High",
  low as "Low",
  volume as "Volume"
FROM "Prices/NESTLE"
WHERE type = "price-log"
SORT date DESC
LIMIT 10
```

## Notes
<!-- Add your investment thesis, claims process, or observations here -->

## Administrative Actions Required
<!-- Track any correspondence or actions needed with the registrar -->

```dataview
TABLE 
  shares_held as "Shares",
  "₦" + avg_buy_price as "Avg Buy",
  "₦" + latest_price as "Current Price",
  "₦" + round(shares_held * latest_price, 2) as "Market Value"
FROM "Companies"
WHERE shares_held > 0
SORT shares_held * latest_price DESC
```
