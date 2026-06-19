# Dividend Tracking Extension

Add comprehensive dividend tracking to your Nigerian stock portfolio.

---

## 📋 Overview

This extension allows you to:
- Track dividend payments received
- Monitor dividend history per company
- Calculate total dividend income
- Project future dividend income
- Track dividend tax (10% WHT in Nigeria)

---

## 🏗️ Setup

### Step 1: Create Dividends Folder

```bash
mkdir ~/ObsidianVault/NigerianStocks/Dividends
```

### Step 2: Add Dividend Fields to Company Template

Update your company files to include dividend tracking in the frontmatter:

```yaml
---
type: company
name: "Nestle Nigeria PLC"
ticker: "NESTLE"
# ... existing fields ...
dividend_frequency: "annual"  # annual, semi-annual, quarterly, irregular
last_dividend_date: ""
last_dividend_per_share: 0.00
next_expected_dividend: ""
total_dividends_received: 0.00
---
```

---

## 📝 Dividend Log Template

Create: `Dividends/Dividend-Log-Template.md`

```markdown
---
type: dividend-payment
company: "[[Company-Name]]"
ticker: "TICKER"
payment_date: YYYY-MM-DD
record_date: YYYY-MM-DD
announcement_date: YYYY-MM-DD
dividend_type: "final"  # interim, final, special
dividend_per_share: 0.00
shares_held: 0
gross_amount: 0.00
withholding_tax: 0.00
net_amount: 0.00
payment_status: "received"  # announced, pending, received
payment_method: "bank_transfer"  # bank_transfer, cheque
tags:
  - dividend
  - income
---

# Dividend Payment: {{COMPANY}} - {{DATE}}

## Payment Details

**Company:** [[{{COMPANY}}]]  
**Dividend Type:** {{TYPE}}  
**Payment Date:** {{PAYMENT_DATE}}  
**Amount per Share:** ₦{{DPS}}

## Calculation

- **Shares Held:** {{SHARES}}
- **Dividend per Share:** ₦{{DPS}}
- **Gross Amount:** ₦{{GROSS}} ({{SHARES}} × ₦{{DPS}})
- **WHT (10%):** ₦{{TAX}}
- **Net Received:** ₦{{NET}}

## Payment Confirmation

- **Status:** {{STATUS}}
- **Payment Method:** {{METHOD}}
- **Account Credited:** {{ACCOUNT}}
- **Reference Number:** {{REF}}

## Notes

<!-- Add any notes about this dividend payment -->
```

---

## 📊 Example Dividend Entry

Create: `Dividends/Nestle-2024-Final-Dividend.md`

```markdown
---
type: dividend-payment
company: "[[Nestle-Nigeria-PLC]]"
ticker: "NESTLE"
payment_date: 2024-06-15
record_date: 2024-05-20
announcement_date: 2024-04-10
dividend_type: "final"
dividend_per_share: 18.50
shares_held: 150
gross_amount: 2775.00
withholding_tax: 277.50
net_amount: 2497.50
payment_status: "received"
payment_method: "bank_transfer"
tags:
  - dividend
  - income
  - 2024
---

# Dividend Payment: Nestle Nigeria - June 2024

## Payment Details

**Company:** [[Nestle-Nigeria-PLC]]  
**Dividend Type:** Final  
**Payment Date:** 2024-06-15  
**Amount per Share:** ₦18.50

## Calculation

- **Shares Held:** 150
- **Dividend per Share:** ₦18.50
- **Gross Amount:** ₦2,775.00 (150 × ₦18.50)
- **WHT (10%):** ₦277.50
- **Net Received:** ₦2,497.50

## Payment Confirmation

- **Status:** Received
- **Payment Method:** Bank Transfer
- **Account Credited:** GTBank ****1234
- **Reference Number:** DIV/NES/2024/001234
- **Date Received:** 2024-06-17

## Notes

Payment received 2 days after payment date. Good dividend from blue-chip stock.
```

---

## 📈 Dividend Dashboard

Create: `Dashboard/Dividend-Summary.md`

```markdown
---
type: dashboard
title: "Dividend Income Dashboard"
---

# 💰 Dividend Income Dashboard

*Last Updated: `= date(now)`*

---

## 📊 Total Dividend Income

```dataview
TABLE WITHOUT ID
  "Total Dividends (All Time)" as "Metric",
  "₦" + round(sum(rows.net_amount), 2) as "Amount"
FROM "Dividends"
WHERE type = "dividend-payment" AND payment_status = "received"
```

### By Year

```dataview
TABLE WITHOUT ID
  dateformat(date(payment_date), "yyyy") as "Year",
  "₦" + round(sum(rows.gross_amount), 2) as "Gross Income",
  "₦" + round(sum(rows.withholding_tax), 2) as "Tax Paid",
  "₦" + round(sum(rows.net_amount), 2) as "Net Income"
FROM "Dividends"
WHERE type = "dividend-payment" AND payment_status = "received"
GROUP BY dateformat(date(payment_date), "yyyy")
SORT dateformat(date(payment_date), "yyyy") DESC
```

---

## 📅 Recent Dividend Payments

```dataview
TABLE WITHOUT ID
  payment_date as "Date",
  company as "Company",
  dividend_type as "Type",
  "₦" + dividend_per_share as "DPS",
  shares_held as "Shares",
  "₦" + net_amount as "Net Received"
FROM "Dividends"
WHERE type = "dividend-payment" AND payment_status = "received"
SORT payment_date DESC
LIMIT 10
```

---

## 📋 Pending Dividend Payments

```dataview
TABLE WITHOUT ID
  payment_date as "Expected Date",
  company as "Company",
  dividend_type as "Type",
  "₦" + dividend_per_share as "DPS",
  shares_held as "Shares",
  "₦" + gross_amount as "Expected Amount"
FROM "Dividends"
WHERE type = "dividend-payment" AND payment_status != "received"
SORT payment_date ASC
```

---

## 🏆 Top Dividend Payers (All Time)

```dataview
TABLE WITHOUT ID
  company as "Company",
  length(rows) as "Payments",
  "₦" + round(sum(rows.net_amount), 2) as "Total Received",
  "₦" + round(avg(rows.dividend_per_share), 2) as "Avg DPS"
FROM "Dividends"
WHERE type = "dividend-payment" AND payment_status = "received"
GROUP BY company
SORT sum(rows.net_amount) DESC
```

---

## 📊 Dividend Income by Company (This Year)

```dataview
TABLE WITHOUT ID
  company as "Company",
  length(rows) as "Payments",
  "₦" + round(sum(rows.net_amount), 2) as "Total Received"
FROM "Dividends"
WHERE type = "dividend-payment" 
  AND payment_status = "received"
  AND dateformat(date(payment_date), "yyyy") = dateformat(date(now), "yyyy")
GROUP BY company
SORT sum(rows.net_amount) DESC
```

---

## 📅 Dividend Calendar (Next 3 Months)

```dataview
TABLE WITHOUT ID
  payment_date as "Date",
  company as "Company",
  dividend_type as "Type",
  "₦" + dividend_per_share as "DPS",
  payment_status as "Status"
FROM "Dividends"
WHERE type = "dividend-payment" 
  AND payment_date >= date(now)
  AND payment_date <= date(now) + dur(90 days)
SORT payment_date ASC
```

---

## 💹 Dividend Yield Analysis

### Current Holdings with Dividend Info

```dataview
TABLE WITHOUT ID
  file.link as "Company",
  shares_held as "Shares",
  "₦" + latest_price as "Price",
  "₦" + last_dividend_per_share as "Last DPS",
  round((last_dividend_per_share / latest_price * 100), 2) + "%" as "Yield %",
  dividend_frequency as "Frequency"
FROM "Companies"
WHERE type = "company" 
  AND status = "listed" 
  AND shares_held > 0
  AND last_dividend_per_share > 0
SORT (last_dividend_per_share / latest_price) DESC
```

---

## 📈 Projected Annual Dividend Income

Based on last dividend paid and current holdings:

```dataview
TABLE WITHOUT ID
  "Projected Annual Income" as "Metric",
  "₦" + round(sum(rows.shares_held * rows.last_dividend_per_share * 0.9), 2) as "Amount (Net of 10% WHT)"
FROM "Companies"
WHERE type = "company" 
  AND status = "listed" 
  AND shares_held > 0
  AND last_dividend_per_share > 0
```

*Note: Projection assumes companies maintain last dividend amount. Actual may vary.*

---

## 🎯 Dividend Growth Tracking

### Companies That Increased Dividends

(Manual tracking - update as announcements are made)

- **Nestle:** ₦15.00 (2023) → ₦18.50 (2024) = +23.3%
- **Dangote Cement:** ₦16.00 (2023) → ₦20.00 (2024) = +25%
- (Add your own as you track)

---

## 📝 Action Items

### Upcoming Record Dates

- [ ] Check AGM announcements for companies you hold
- [ ] Ensure shares registered before record date
- [ ] Verify bank details with registrar

### Payment Follow-ups

- [ ] Track pending payments that are overdue
- [ ] Contact registrar for missing payments
- [ ] Update bank details if needed

---

## 💡 Nigerian Dividend Tax Information

**Withholding Tax Rate:** 10% (standard for Nigerian dividends)

**Tax Treatment:**
- Dividends are subject to 10% WHT at source
- This is a final tax for most individual investors
- No need to declare in annual tax returns (WHT is final)

**Documentation:**
- Keep dividend warrants/notifications
- Bank credit alerts serve as proof
- Annual dividend statements from registrar

**For Tax Planning:**
- Total dividends inform overall income picture
- Capital gains on shares are taxable (10%)
- Keep records for at least 6 years

---

*Dashboard powered by Dataview plugin*
```

---

## 🔄 Workflow for Recording Dividends

### When Dividend is Announced

1. **Check your email/post** for dividend notice from registrar
2. **Note key dates:**
   - Announcement date
   - Qualification/Record date (must hold shares by this date)
   - Payment date
3. **Create pending dividend entry** in Dividends folder
4. **Update company file** with expected dividend info

### On Qualification Date

1. **Verify you hold shares** on the record date
2. **Confirm share register** is updated (call registrar if unsure)
3. **Verify bank details** on file with registrar

### On Payment Date

1. **Monitor your bank account** (usually pays within 2-7 days)
2. **When received:**
   - Update dividend log: status = "received"
   - Add actual amount, reference number, date received
   - Update company file: `total_dividends_received`
3. **If not received within 7 days:**
   - Contact registrar
   - Provide certificate number and shareholder details
   - Get payment trace reference

### End of Year

1. **Generate annual summary** from dashboard
2. **Total dividend income** for the year
3. **Keep for tax records** (though WHT is final)
4. **Review dividend payers** - which companies performed best?

---

## 📊 Company File Updates

For each company that pays dividends, update these fields:

```yaml
# In Nestle-Nigeria-PLC.md
---
dividend_frequency: "annual"
last_dividend_date: "2024-06-15"
last_dividend_per_share: 18.50
next_expected_dividend: "2025-06-15"  # Estimate
total_dividends_received: 5240.75  # Cumulative net amount
---
```

This allows dashboard queries to calculate:
- Dividend yield
- Projected income
- Dividend payment history per company

---

## 🎯 Advanced Features

### Dividend Reinvestment Tracking

If you reinvest dividends:

```markdown
---
type: dividend-reinvestment
date: 2024-06-20
company: "[[Nestle-Nigeria-PLC]]"
dividend_received: 2497.50
shares_purchased: 2
purchase_price: 1248.75
---

# Dividend Reinvestment: Nestle - June 2024

Used dividend of ₦2,497.50 to purchase 2 additional shares at ₦1,248.75 each.

New total: 152 shares
```

### Dividend Announcement Tracker

Create: `Dividends/Expected-Announcements.md`

```markdown
# Expected Dividend Announcements

## Companies That Usually Pay Dividends

| Company | Last Payment | Typical Timing | Next Expected |
|---------|--------------|----------------|---------------|
| Nestle | June 2024 | June annually | June 2025 |
| Dangote Cement | March 2024 | March annually | March 2025 |
| Access Bank | May 2024 | May annually | May 2025 |

## Monitoring

- [ ] Check AGM announcements monthly
- [ ] Review NGX notices for dividend declarations
- [ ] Set calendar reminders for expected dates
```

### Tax Summary Report

Create: `Dividends/Tax-Summary-2024.md`

```markdown
# Dividend Tax Summary - 2024

## Annual Summary

**Total Gross Dividend Income:** ₦XX,XXX.XX  
**Total WHT Deducted (10%):** ₦X,XXX.XX  
**Net Dividend Income:** ₦XX,XXX.XX

## By Company

```dataview
TABLE WITHOUT ID
  company as "Company",
  sum(gross_amount) as "Gross",
  sum(withholding_tax) as "WHT",
  sum(net_amount) as "Net"
FROM "Dividends"
WHERE dateformat(date(payment_date), "yyyy") = "2024"
GROUP BY company
SORT company ASC
```

**Supporting Documents:**
- Dividend warrants (attached)
- Bank credit alerts (attached)
- Annual statements from registrars (attached)

*Keep this file for 6 years for tax purposes*
```

---

## 📱 Quick Actions

### Record a Dividend Payment (Quick)

1. Duplicate last dividend file
2. Update company, date, and amounts
3. Link to company file
4. Dashboard auto-updates

### Check Missing Payments

```dataview
LIST
FROM "Dividends"
WHERE payment_status = "pending" 
  AND payment_date < date(now) - dur(7 days)
```

### Annual Income Summary

```dataview
TABLE WITHOUT ID
  "2024" as "Year",
  "₦" + sum(net_amount) as "Total Dividend Income"
FROM "Dividends"
WHERE dateformat(date(payment_date), "yyyy") = "2024"
```

---

## 💡 Tips

1. **Set up email alerts** - Most registrars email dividend notices
2. **Join AGMs** - Learn about company plans, meet management
3. **Track trends** - Is dividend growing, stable, or declining?
4. **Diversify income** - Don't rely on one company for dividends
5. **Reinvest strategically** - Use dividends to buy more shares
6. **Keep all documentation** - Dividend warrants, bank alerts
7. **Verify payments** - If you don't receive, call immediately
8. **Update bank details** - Inform registrar of any changes

---

## 🔗 Integration with Main System

The dividend tracker integrates seamlessly:

**Company Files** → Track dividend history per company  
**Dashboard** → Shows total dividend income  
**Dividend Folder** → Detailed payment records  
**Tax Records** → Annual summaries

All connected through Dataview queries!

---

## ✅ Setup Checklist

- [ ] Created Dividends folder
- [ ] Added dividend fields to company template
- [ ] Created Dividend-Log-Template.md
- [ ] Created Dividend-Summary.md dashboard
- [ ] Recorded first dividend payment
- [ ] Tested dashboard queries
- [ ] Set up dividend payment workflow
- [ ] Created tax summary template

---

**Now you can track every kobo of dividend income! 💰📈**