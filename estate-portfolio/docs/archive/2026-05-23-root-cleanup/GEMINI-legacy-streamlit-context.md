# Estate Portfolio Manager

## Project Overview

**Estate Portfolio Manager** is a self-hosted application designed to track and manage an investment portfolio, specifically focused on the Nigerian Exchange Group (NGX) market. It visualizes holdings, tracks dividends, and monitors stock prices.

**Tech Stack:**
*   **Frontend/App:** Streamlit (Python)
*   **Database:** PostgreSQL 15
*   **Data Sources:**
    *   **Obsidian Vault:** Imports investment notes/data from Obsidian Markdown files.
    *   **EODHD API:** Primary price source for Nigerian Exchange stocks (`.XNSA` format).
    *   **NGX Scraper:** Legacy scraper (fragile, not recommended).
    *   **RapidAPI Scraper:** Legacy scraper (doesn't support NGX).
*   **Infrastructure:** Docker Compose (integrated with Traefik/OpenAgile).

## Architecture

The project consists of two main services defined in `docker-compose.yml`:

1.  **`postgres` (estate_portfolio_db):**
    *   Stores all portfolio data (companies, holdings, transactions, dividends).
    *   Initialized with `init_db.sql`.
    *   **Note:** Ticker column increased to `VARCHAR(20)` to support longer symbols.

2.  **`streamlit` (estate_portfolio_app):**
    *   Hosts the main user interface (exposed on port 8501).
    *   Connects to the database to fetch and display portfolio metrics.
    *   Integrates into the `openagile_openagile_network` for Traefik routing.

## Key Components

### Application (`app.py`)
*   **Entry Point:** Main Streamlit app.
*   **Features:** Dashboard, Companies master list, Holdings tracking, Transaction history, Dividend tracking, Reports (Valuation, Performance, Tax), **Price Update Button**.
*   **Database Integration:** Uses `psycopg2` with `env_file` for credential management.
*   **Price Updates:** Settings page includes one-click button to run EODHD scraper with real-time progress feedback.

### Scripts (`/scripts`)
*   **`import_obsidian.py`**:
    *   Parses Markdown files from the mounted `NigerianStocks` vault.
    *   Supports YAML frontmatter parsing and "flattens" unquoted wiki links.
    *   Correctly handles zero-cost holdings and missing fields.
*   **`eodhd_scraper.py`**:
    *   **PRIMARY PRICE SCRAPER** using EODHD.com API for NGX stocks.
    *   Uses `.XNSA` exchange suffix for Nigerian Exchange (fixed Dec 2025).
    *   Fetches end-of-day prices for Nigerian Exchange stocks.
    *   Required: `EODHD_API_KEY` in `.env` (get from https://eodhd.com).
    *   Free tier: 20 API calls/day | Paid: $19.99/month for unlimited.
    *   **Status:** Active and working - successfully updates 22+ stocks daily.
*   **`rapidapi_scraper.py`**:
    *   Legacy scraper using the `sparior/yahoo-finance15` RapidAPI provider.
    *   **Status:** Does not support NGX stocks with `.LG` suffix.
*   **`yfinance_scraper.py`**:
    *   Alternative scraper using the `yfinance` library.
    *   **Limitation:** Blocked by Yahoo Finance on datacenter IPs (Netcup server).
*   **`ngx_scraper.py`**:
    *   Legacy scraper targeting the NGX website directly.
    *   **Status:** Too fragile due to anti-bot measures.

## Deployment & Operation

### Prerequisites
*   OpenAgile infrastructure (Traefik on `openagile_openagile_network`).
*   `.env` file with `DB_PASSWORD` and `RAPIDAPI_KEY`.

### Running the Application
```bash
docker compose up -d --build
```

### Data Synchronization
To import data from the Obsidian vault and update prices:

```bash
# 1. Import from Obsidian
docker compose exec streamlit python scripts/import_obsidian.py NigerianStocks

# 2. Update Prices (EODHD - Primary)
docker compose exec streamlit python scripts/eodhd_scraper.py

# Alternative scrapers (if needed):
# - RapidAPI (not working for NGX): docker compose exec streamlit python scripts/rapidapi_scraper.py
# - yfinance (IP blocked): docker compose exec streamlit python scripts/yfinance_scraper.py
```

**Setting up EODHD API:**
1. Register at https://eodhd.com/register
2. Get your API key from the dashboard
3. Add to your `.env` file: `EODHD_API_KEY=your_key_here`
4. Restart containers: `docker compose up -d`
5. Run the scraper: `docker compose exec streamlit python scripts/eodhd_scraper.py`

**Free Tier Limits:**
- 20 API calls per day
- End-of-day data (not real-time)
- Sufficient for ~20 stocks daily or all 72 stocks every 3-4 days

**Paid Plan ($19.99/month):**
- Unlimited API calls
- Update all 72 stocks daily
- Access to historical data

## Troubleshooting & Successes (Dec 2025)

*   **Database Sync:** Resolved `FATAL: password authentication failed` by hard-resetting volumes and using `env_file` in Compose.
*   **Schema Fix:** Increased `ticker` column size to 20 to prevent truncation errors.
*   **Obsidian Parsing:** Implemented recursive flattening for unquoted links in YAML (e.g., `[[Unity]]`).
*   **IP Blocking:** Identified that server IPs (Netcup) are blocked by Yahoo Finance; migrated to EODHD.com for stable price fetching.
*   **EODHD Ticker Format Fix:** Changed from `.LG` (Yahoo format) to `.XNSA` (EODHD format for Nigerian Exchange) - resolved 404 errors.
*   **Price Data Solution:** Successfully implemented EODHD.com scraper as primary price source - 22 stocks updating successfully.
*   **UI Price Updates:** Added one-click price update button in Streamlit app (Settings → Price Scraper tab) with real-time progress feedback.
*   **CI/CD Pipeline:** Implemented GitHub Actions for automatic deployment on code push.

## Development Conventions

*   **Python:** 3.11-slim.
*   **DB Access:** Aggregations must use `COALESCE(..., 0)` to prevent NoneType formatting errors in Streamlit.
*   **Type Safety:** Always use `pd.to_numeric()` when processing SQL counts/sums in Pandas.

## CI/CD Deployment

The project uses **GitHub Actions** for automated deployment to the OpenAgile server.

### Workflow
1. Push code to `main` branch on GitHub
2. GitHub Actions automatically:
   - Connects to server via SSH
   - Pulls latest changes
   - Rebuilds containers if needed
   - Runs EODHD scraper for verification
3. View logs at: https://github.com/zubbyik/zubbyik-openagile_frappe_update/actions

### Setup
See [`CI_CD_SETUP.md`](file:///home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/egbuna_estate_account_streamlight/estate-portfolio/CI_CD_SETUP.md) for initial configuration instructions.

### Manual Deployment
If needed, you can still deploy manually:
```bash
ssh zubbyik@185.216.177.250
cd ~/openagile/egbuna_estate_account_streamlight/estate-portfolio
./deploy.sh
```

## UI Features

### Price Update Button
The Streamlit app includes a one-click price update feature:

1. Navigate to **Settings** → **Price Scraper** tab
2. Click **"✨ Run EODHD Scraper"** button
3. Watch real-time progress with spinner
4. View summary: "X updated, Y failed"
5. Expand **"📋 View Details"** to see last 10 successful updates

**Features:**
- Runs `eodhd_scraper.py` via subprocess
- Shows real-time output and error messages
- 5-minute timeout protection
- Displays detailed logs of updated stocks
- No SSH access required

### Application Access
- **Dashboard:** https://estate.zubbystudio.shop
- **Features:** Portfolio valuation, holdings tracking, dividend management, tax reports
- **Real-time Updates:** Current prices, unrealized gains/losses, sector allocation


