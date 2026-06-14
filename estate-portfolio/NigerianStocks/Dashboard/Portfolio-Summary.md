---
type: dashboard
title: "Nigerian Stock Portfolio Dashboard"
last_updated: ""
---

# 📊 Nigerian Stock Portfolio Dashboard

*Last Updated: `= date(now)`*

---

## 🎯 Portfolio Overview by Status

```dataview
TABLE WITHOUT ID
  status as "Status",
  length(rows.file) as "Count",
  "₦" + round(sum(map(rows, (r) => r.shares_held * r.latest_price)), 2) as "Market Value"
FROM "Companies"
WHERE type = "company"
GROUP BY status
SORT status ASC
```

---

## 💼 Active Holdings (Listed Companies Only)

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  sector as "Sector",
  registrar as "Registrar",
  shares_held as "Shares",
  "₦" + avg_buy_price as "Avg Buy",
  "₦" + latest_price as "Current",
  "₦" + round(shares_held * latest_price, 2) as "Market Value",
  round((latest_price - avg_buy_price) / avg_buy_price * 100, 2) + "%" as "Return %"
FROM "Companies"
WHERE type = "company" AND status = "listed" AND shares_held > 0
SORT shares_held * latest_price DESC
```

---

## 🏦 Merged/Acquired Companies Requiring Action

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  registrar as "Contact",
  reference_number as "Ref #",
  notes as "Action Required"
FROM "Companies"
WHERE type = "company" AND status = "merged"
SORT name ASC
```

---

## ⚠️ Delisted/Defunct Companies - Claims Management

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  registrar as "Contact Point",
  reference_number as "Ref #",
  notes as "Status"
FROM "Companies"
WHERE type = "company" AND status = "delisted" OR status = "defunct"
SORT registrar ASC, name ASC
```

---

## ❓ Companies with Uncertain Status

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  reference_number as "Ref #",
  notes as "Action Needed"
FROM "Companies"
WHERE type = "company" AND status = "uncertain"
SORT name ASC
```

---

## 🏢 Holdings by Sector (Listed Only)

```dataview
TABLE WITHOUT ID
  sector as "Sector",
  length(rows) as "Companies",
  "₦" + round(sum(rows.shares_held * rows.latest_price), 2) as "Total Value"
FROM "Companies"
WHERE type = "company" AND status = "listed" AND shares_held > 0
GROUP BY sector
SORT sum(rows.shares_held * rows.latest_price) DESC
```

---

## 📋 Holdings by Registrar

```dataview
TABLE WITHOUT ID
  registrar as "Registrar",
  length(rows) as "Companies",
  status as "Status Mix"
FROM "Companies"
WHERE type = "company"
GROUP BY registrar
SORT length(rows) DESC
```

---

## 🎯 Top Priority Actions

### Immediate Actions Required:
1. **Update Share Quantities:** Edit each company file to add your actual `shares_held` and `avg_buy_price`
2. **Verify Merged Companies:** Contact registrars for companies with "merged" status
3. **Claims for Delisted:** Initiate claims process for defunct/delisted companies
4. **Confirm Uncertain:** Verify status with NGX for companies marked "uncertain"

### Next Steps:
- [ ] Run price update script for listed companies
- [ ] Contact AMCON/NDIC for defunct bank shares
- [ ] Reach out to registrars for merged entities
- [ ] Verify Abacus Unit Trust holdings (See Special Entities note)
- [ ] Update registrar contact information

---

## 📊 Summary Statistics

```dataview
TABLE WITHOUT ID
  "Total Companies Tracked" as "Metric",
  length(list(type, type = "company")) as "Value"
FROM "Companies"
UNION
TABLE WITHOUT ID
  "Listed & Trading" as "Metric",
  length(list(status, status = "listed")) as "Value"
FROM "Companies"
UNION
TABLE WITHOUT ID
  "Merged/Acquired" as "Metric",
  length(list(status, status = "merged")) as "Value"
FROM "Companies"
UNION
TABLE WITHOUT ID
  "Delisted/Defunct" as "Metric",
  length(list(status, status = "delisted" OR status = "defunct")) as "Value"
FROM "Companies"
UNION
TABLE WITHOUT ID
  "Uncertain Status" as "Metric",
  length(list(status, status = "uncertain")) as "Value"
FROM "Companies"
```

---

*For special entities (Abacus Unit Trust, registrar notes), see [[Special-Entities-NOT-STOCKS]]*
