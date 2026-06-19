---
type: registrar
name: "African-Prudential-Registrars"
category: "commercial"
contact_email: ""
contact_phone: ""
website: ""
address: ""
tags:
  - registrar
  - commercial
---

# African-Prudential-Registrars

## Contact Information
- **Email:** 
- **Phone:** 
- **Website:** 
- **Address:** 
- **Category:** commercial

## Companies Under This Registrar
```dataview
TABLE WITHOUT ID file.link as "Company", ticker as "Ticker", status as "Status", sector as "Sector", reference_number as "Ref #", latest_price as "Latest Price (₦)" FROM "Companies" WHERE type = "company" AND meta(registrar).path = this.file.path SORT status ASC, name ASC
```

## Total Holdings (Listed Companies Only)
```dataview
TABLE WITHOUT ID
  file.link as "Company",
  "₦" + round(shares_held * latest_price, 2) as "Market Value"
FROM "Companies"
WHERE type = "company" AND meta(registrar).path = this.file.path AND status = "listed"
SORT shares_held * latest_price DESC
```





## Action Items
<!-- Track communications, document requests, or claims with this registrar -->

## Notes









