---
type: registrar
name: "Acquirer-Buyout-Scheme-Administrators"
category: "special"
contact_email: ""
contact_phone: ""
website: ""
address: ""
tags:
  - registrar
  - special
---

# Acquirer-Buyout-Scheme-Administrators

## Contact Information
- **Email:** 
- **Phone:** 
- **Website:** 
- **Address:** 
- **Category:** special

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
