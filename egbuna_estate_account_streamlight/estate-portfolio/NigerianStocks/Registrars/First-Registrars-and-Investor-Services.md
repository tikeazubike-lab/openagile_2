---
type: registrar
name: "First-Registrars-and-Investor-Services"
category: "commercial"
contact_email: ""
contact_phone: ""
website: ""
address: ""
tags:
  - registrar
  - commercial
---

# First-Registrars-and-Investor-Services

## Contact Information
- **Email:** 
- **Phone:** 
- **Website:** 
- **Address:** 
- **Category:** commercial

## Companies Under This Registrar
```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  status as "Status",
  sector as "Sector",
  reference_number as "Ref #",
  latest_price as "Latest Price (₦)"
FROM "Companies"
WHERE type = "company" AND meta(registrar).path = this.file.path
SORT status ASC, name ASC
```

## Total Holdings (Listed Companies Only)
```dataview
TABLE WITHOUT ID
  sum(shares_held * latest_price) as "Total Market Value (₦)"
FROM "Companies"
WHERE type = "company" AND meta(registrar).path = this.file.path AND status = "listed"
```

## Action Items
<!-- Track communications, document requests, or claims with this registrar -->

## Notes

```dataview 
LIST file.name
FROM "Companies"
LIMIT 5
```