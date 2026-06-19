---
type: dashboard
title: "Portfolio Status Summary"
---

# 📋 Portfolio Status Summary

Quick reference for understanding your holdings across different administrative categories.

## 🟢 Category A: Listed & Trading (Highest Priority)

These companies are actively trading. **Action: Update share quantities and run price automation.**

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  ticker as "Ticker",
  registrar as "Registrar",
  reference_number as "Ref #"
FROM "Companies"
WHERE type = "company" AND status = "listed"
SORT sector ASC, name ASC
```

---

## 🟡 Category B: Merged/Acquired (Medium Priority)

These shares may have been converted to successor company shares. **Action: Contact registrar to confirm status and conversion.**

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  registrar as "Contact Registrar",
  reference_number as "Ref #",
  notes as "Details"
FROM "Companies"
WHERE type = "company" AND status = "merged"
SORT registrar ASC
```

---

## 🔴 Category C: Delisted/Defunct (Claims Required)

These require administrative action or claims process. **Action: Contact AMCON/NDIC/CAC for resolution.**

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  status as "Sub-Status",
  registrar as "Contact Point",
  reference_number as "Ref #"
FROM "Companies"
WHERE type = "company" AND (status = "delisted" OR status = "defunct")
SORT registrar ASC, name ASC
```

---

## ⚪ Category D: Uncertain Status

Status needs verification. **Action: Check with NGX or original documentation.**

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  reference_number as "Ref #",
  notes as "Notes"
FROM "Companies"
WHERE type = "company" AND status = "uncertain"
```

---

## 📞 Key Contact Points

### For Listed Companies:
Contact the registrar shown in each company file.

### For Merged Companies:
Contact the successor company's registrar (shown in notes).

### For Failed Banks:
- **AMCON:** +234 1 279 4878 | info@amcon.com.ng
- **NDIC:** +234 1 453 1424 | contactcentre@ndic.gov.ng

### For Delisted Companies:
- **CAC Registrar General:** +234 1 469 7800
- **NGX Compliance:** +234 1 271 2580

### For Uncertain Status:
- **NGX Help Desk:** +234 1 271 2580
- **SEC Nigeria:** +234 1 280 9002

---

## 🎯 Recommended Action Sequence

1. ✅ **Week 1:** Update all share quantities for listed companies
2. ✅ **Week 2:** Contact registrars for merged companies (Unity Bank, FCMB, etc.)
3. ✅ **Week 3:** Initiate claims for defunct banks via AMCON/NDIC
4. ✅ **Week 4:** Research and confirm uncertain status companies
5. ✅ **Week 5:** Follow up on delisted company claims with CAC

