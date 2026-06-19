# Project Report: Estate Portfolio Manager (Streamlit MVP)

**Date:** December 28, 2025  
**Project Lead:** OpenAgile Integration Architect  
**Tech Stack:** Streamlit (Python), PostgreSQL, Docker Compose, Traefik, Obsidian (Data Source)  
**Total Development Time:** ~5.5 Hours

---

## 1. Executive Summary
This report details the end-to-end development lifecycle of the "Estate Portfolio Manager," a self-hosted financial dashboard designed to visualize asset data stored in a personal Knowledge Management System (Obsidian). The project successfully bridged unstructured Markdown data with a structured SQL database, deploying a reactive web application within a complex, existing microservices infrastructure (OpenAgile).

## 2. Steps Taken to Achievement

### Phase 1: Requirements & Scaffolding
*   **Analysis:** Identified the need to parse local Markdown files (Obsidian Vault) containing unstructured financial data (Tickers, Shares, Prices) and present them in a web interface.
*   **Architecture:** Designed a two-container stack:
    *   `postgres`: Relational storage for companies, holdings, and dividends.
    *   `streamlit`: Frontend UI and execution environment for automation scripts.
*   **Scaffolding:** Generated `docker-compose.yml`, `app.py` (dashboard logic), `init_db.sql` (schema), and `import_obsidian.py` (ETL script).

### Phase 2: Infrastructure Integration
*   **Traefik Integration:** Configured Docker labels to expose the application securely via HTTPS (`estate.zubbystudio.shop`) using the existing Traefik reverse proxy and Cloudflare DNS challenges.
*   **Networking:** Integrated the new stack into the pre-existing `openagile_openagile_network` to ensure internal connectivity and SSL termination.

### Phase 3: Data Pipeline Implementation
*   **Parsing Logic:** Developed a Python script to parse YAML frontmatter from Obsidian notes.
*   **Refinement:** Refactored the script to handle complex edge cases (nested wiki links, missing fields, zero-cost holdings).
*   **Automation:** Established a workflow where running `docker compose exec ... import_obsidian.py` synchronizes the live dashboard with the local vault.

---

## 3. Bottlenecks & Resolutions

During the deployment, we encountered several "sticky" areas common in DevOps integration. Here is how they were resolved:

| **Bottleneck** | **Root Cause** | **Resolution** |
| :--- | :--- | :--- |
| **Traefik 502/TLS Errors** | The container was on a default network (`estate_network`) isolated from the Traefik proxy. | **Fix:** Aligned the service to use the external `openagile_openagile_network` and added specific `traefik.docker.network` labels. |
| **Database Auth Failures** | Postgres creates the default user *once* on init. Changing `.env` later caused a mismatch between the App and DB. | **Fix:** Performed a hard reset of the database volume (`docker volume rm`) and hardcoded `env_file: .env` in Docker Compose to ensure consistency. |
| **Schema Truncation** | Some ticker symbols (e.g., `NASCON.LG`) exceeded the initial `VARCHAR(10)` limit. | **Fix:** Updated schema to `VARCHAR(20)` and added safety truncation in the import script. |
| **Data Parsing Crashes** | The YAML parser treated unquoted links (e.g., `[[Link]]`) as nested lists, crashing the `set()` operation. | **Fix:** Implemented a recursive "flattener" function to convert nested lists/links into clean strings. |
| **Streamlit Caching** | The browser displayed old errors despite code fixes because the container held cached bytecode. | **Fix:** Used `docker compose up -d --force-recreate` to ensure the running container reflected the latest code on disk. |

---

## 4. Implementation Guide: Setting up a Similar Project

For future freelance gigs or internal modules, follow this streamlined workflow to replicate this success in **under 4 hours**.

### **Step 1: Environment & Schema Design (Time: 45 mins)**
*   **Define Data Types Early:** Be generous with database limits (`VARCHAR(255)` for names, `VARCHAR(20)` for codes) to avoid truncation issues later.
*   **Environment Variables:** Use a single `.env` file and reference it explicitly in `docker-compose.yml` using `env_file:`. This prevents "silent" default credential usage.

### **Step 2: Infrastructure Configuration (Time: 30 mins)**
*   **Network Pre-Check:** Before writing `docker-compose.yml`, run `docker network ls` on the server. Use the *exact* external network name.
*   **Traefik Labels:** Always include:
    *   `traefik.docker.network=[your_network_name]`
    *   Router for HTTP -> HTTPS redirect.
    *   Router for HTTPS with TLS resolver.

### **Step 3: Application Logic & Defensive Coding (Time: 1.5 - 2 Hours)**
*   **Type Safety:** When reading from SQL to Pandas, always use `pd.to_numeric(..., errors='coerce')` before performing math. Never assume SQL `COUNT/SUM` returns an integer directly.
*   **Null Handling:** In SQL queries, wrap aggregations in `COALESCE(SUM(col), 0)` to handle empty tables gracefully.
*   **Data Ingestion:** If parsing external files (Markdown/YAML), assume fields can be missing, lists, or strings. Write a "cleaner" function immediately.

### **Step 4: Deployment & Verification (Time: 45 mins)**
*   **Volume Mounts:** Ensure host directories (like `./NigerianStocks`) are correctly mounted to the container path expected by your scripts (`/app/NigerianStocks`).
*   **Force Recreate:** When deploying code changes to a stateful container (like Streamlit), prefer `--force-recreate` to clear internal caches.

---

## 5. Time Allocation Estimate (Freelance Proposal)

| **Task Phase** | **Estimated Time** | **Deliverables** |
| :--- | :--- | :--- |
| **1. Requirements & Database Design** | 1 Hour | ER Diagram, SQL Schema, Project Structure |
| **2. Core Dashboard Development** | 2.5 Hours | Interactive UI (Streamlit/React), Charts, Metrics |
| **3. Infrastructure & Security** | 1.5 Hours | Docker Compose, SSL/HTTPS, Reverse Proxy Config |
| **4. Data Integration (ETL)** | 1.5 Hours | Scripts to ingest data from CSV/API/Markdown |
| **5. Testing & Refinement** | 1 Hour | Bug fixes, Mobile responsiveness check |
| **TOTAL** | **~7.5 Hours** | **Production-Ready MVP** |

---

**Generated by:** Gemini CLI (OpenAgile Integration Architect)
