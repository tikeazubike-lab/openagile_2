---
type: registrar
name: "CardinalStone-Registrars-Limited"
category: "commercial"
contact_email: ""
contact_phone: ""
website: ""
address: ""
tags:
  - registrar
  - commercial
---

# CardinalStone-Registrars-Limited

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
  "₦" + round(sum(shares_held * latest_price), 2) as "Total Market Value"
FROM "Companies"
WHERE type = "company" AND meta(registrar).path = this.file.path AND status = "listed"
```

## Action Items
<!-- Track communications, document requests, or claims with this registrar -->

## Notes
