# Nigerian Stock Portfolio - Obsidian Vault

This vault tracks your 85 Nigerian shareholdings across different status categories.

## 📂 Vault Structure

- **Companies/** - Individual company files (85 total)
- **Registrars/** - Registrar contact information
- **Prices/** - Historical price data (auto-generated)
- **Dashboard/** - Portfolio overview dashboards
- **Templates/** - Templates for new entries
- **Scripts/** - Automation scripts

## 🚀 Quick Start

### 1. Install Required Plugin
- Install **Dataview** plugin in Obsidian
- Enable JavaScript queries in Dataview settings

### 2. Update Your Holdings
Edit company files in `Companies/` folder to add:
- `shares_held`: Number of shares you own
- `avg_buy_price`: Your average purchase price

### 3. View Dashboard
Open `Dashboard/Portfolio-Summary.md` to see your portfolio overview.

### 4. Setup Price Automation (Listed Companies Only)
```bash
cd Scripts/
python3 update_prices.py
```

## 📊 Portfolio Breakdown

- **Listed & Trading:** ~40 companies - Can be tracked with automated prices
- **Merged/Acquired:** ~15 companies - Requires registrar contact
- **Delisted/Defunct:** ~25 companies - Requires claims process
- **Uncertain:** 4 companies - Status verification needed
- **Special Entities:** 3 entries - Not standard stocks

## 🎯 Priority Actions

1. **High Priority:** Update share quantities for all listed companies
2. **High Priority:** Contact Unity Bank registrar for merged bank shares (#10, #26, #39)
3. **Medium Priority:** Initiate AMCON claims for defunct banks
4. **Medium Priority:** Verify uncertain status companies with NGX
5. **Low Priority:** Research delisted companies for possible claims

## 📞 Key Contacts

### AMCON (Defunct Banks)
- Phone: +234 1 279 4878
- Email: info@amcon.com.ng
- Website: www.amcon.com.ng

### NDIC (Bank Resolutions)
- Phone: +234 1 453 1424
- Email: contactcentre@ndic.gov.ng

### NGX (Status Verification)
- Phone: +234 1 271 2580
- Website: www.ngxgroup.com

### CAC (Delisted Companies)
- Phone: +234 1 469 7800
- Website: www.cac.gov.ng

## 📝 Notes

- Price automation only works for currently listed companies
- Merged companies may have transferred to successor shares
- Defunct bank shares may have compensation schemes via AMCON
- Keep all original share certificates and documentation

## 🔧 Maintenance

- Run `update_prices.py` daily for listed companies
- Review dashboard weekly
- Update claim status in company notes
- Archive resolved entries to a separate folder

---

Generated automatically by Obsidian Vault Setup Script
Date: $(date +%Y-%m-%d)
