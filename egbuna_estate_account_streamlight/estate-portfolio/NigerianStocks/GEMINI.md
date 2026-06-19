# Nigerian Stock Portfolio Manager (Obsidian + Python)

This project is a hybrid **Obsidian Vault** and **Python Automation System** designed to track a portfolio of Nigerian stocks. It combines personal knowledge management (notes on companies, claims, registrars) with automated price tracking.

## 📂 Project Structure

### Core Vault (Obsidian)
- **`Companies/`**: The source of truth. Each file represents a stock/company.
  - **Metadata**: stored in YAML frontmatter (ticker, shares, status, etc.).
  - **Content**: Notes, analysis, and administrative actions.
- **`Prices/`**: Automated data storage.
  - Contains subfolders for each ticker (e.g., `Prices/ACCESSCORP/`).
  - Stores daily price logs as individual markdown files for Dataview querying.
- **`Registrars/`**: Reference data for stock registrars (contact info for claims).
- **`Dashboard/`**: Portfolio summaries using Dataview queries.

### Automation (Python)
- **`Scripts/`**: Python scripts to fetch market data and update the vault.
  - **`update_prices.py`**: Main script. Fetches prices from **Yahoo Finance** and updates company files + creates price logs.
  - **`ngx_scraper.py`**: Fallback script. Scrapes the **NGX Group website** directly.

## 🚀 Usage & Automation

### 1. Environment Setup
The scripts require Python 3 and a few dependencies. A virtual environment is recommended.

```bash
cd Scripts
# Create virtual environment (if not exists)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (requests, beautifulsoup4)
pip install requests beautifulsoup4
```

### 2. Updating Stock Prices
Run the update script daily to fetch latest closes.

**Primary Method (Yahoo Finance):**
```bash
python3 Scripts/update_prices.py
```
*   **Target:** Only updates companies with `status: listed`.
*   **Action:** Updates `latest_price` in company frontmatter and creates a new log file in `Prices/<TICKER>/<DATE>.md`.

**Alternative Method (NGX Scraper):**
```bash
python3 Scripts/ngx_scraper.py
```
*   Use this if Yahoo Finance data is delayed or missing.

### 3. Obsidian Configuration
- **Required Plugin:** **Dataview**.
- **Configuration:** Enable "Enable JavaScript Queries" in Dataview settings to render the dashboards and price history charts.

## 📝 Data Model & Conventions

### Company Notes (`Companies/*.md`)
The automation relies heavily on specific YAML frontmatter fields. **Do not remove these keys.**

```yaml
---
type: company
name: "Access Bank PLC"
ticker: "ACCESSCORP"      # Crucial for matching with API/Scraper
status: "listed"          # Determines if price update runs (listed, defunct, etc.)
shares_held: 2338         # User input: Quantity owned
avg_buy_price: 0.00       # User input: Cost basis
latest_price: 25.00       # Automated: Do not edit manually
latest_price_date: "..."  # Automated
registrar: "[[United-Securities-Limited]]"
---
```

### Price Logs (`Prices/<TICKER>/<DATE>.md`)
Generated automatically. Do not edit manually. Used by Dataview to plot history.

```yaml
---
type: price-log
ticker: "ACCESSCORP"
date: 2025-10-03
close: 25.00
prev_close: 24.50
change_pct: 2.04
---
```

## 🛠 Maintenance

- **Adding a Company:** Create a new note in `Companies/` using the standard template/frontmatter.
- **Changing Status:** If a company delists, change `status: listed` to `status: delisted` or `status: defunct` to stop automation errors.
- **Registrar Updates:** Update links in the `registrar` field if a company changes its registrar.

## 🔍 Troubleshooting
- **Missing Ticker:** If `update_prices.py` skips a company, ensure the `ticker` field in frontmatter is correct and matches Yahoo Finance (usually with `.LG` suffix, handled by script).
- **Logs:** Check `price_update.log` in the root or `Scripts/` folder for execution errors.
