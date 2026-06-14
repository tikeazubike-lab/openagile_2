# Tech Stack Inventory

> **Author:** Zubby Ikechukwu  
> **Date:** 2026-02-17  
> **Purpose:** Comprehensive audit of all tools and technologies used across the OpenAgile ecosystem, rated by proficiency and recency, with proof-of-competence notes for high-proficiency items.

---

## Inventory

| # | Tool / Tech | Proficiency (1–5) | Last Used | Category |
|---|---|:---:|---|---|
| 1 | **Docker** | 5 | Feb 2026 | Infrastructure |
| 2 | **Docker Compose** | 5 | Feb 2026 | Infrastructure |
| 3 | **Traefik** (Reverse Proxy) | 4 | Feb 2026 | Infrastructure |
| 4 | **Nginx** | 3 | Dec 2025 | Infrastructure |
| 5 | **Portainer** | 3 | Dec 2025 | Infrastructure |
| 6 | **Frappe Framework** | 4 | Dec 2025 | ERP / Web Framework |
| 7 | **ERPNext** | 4 | Dec 2025 | ERP |
| 8 | **OpenProject** | 2 | Dec 2025 | Project Management |
| 9 | **Ghost CMS** | 2 | Jan 2026 | CMS / Blogging |
| 10 | **WordPress** | 2 | 2024 | CMS / Blogging |
| 11 | **Linux (Ubuntu/Debian)** | 4 | Feb 2026 | Operating Systems |
| 12 | **SSH** | 4 | Feb 2026 | DevOps |
| 13 | **DNS Management** (Cloudflare) | 4 | Feb 2026 | Networking |
| 14 | **n8n** | 3 | Dec 2025 | Automation |
| 15 | **Git** | 4 | Feb 2026 | Version Control |
| 16 | **Gitea** | 3 | Dec 2025 | Version Control |
| 17 | **GitHub Actions** (CI/CD) | 4 | Dec 2025 | DevOps |
| 18 | **Python** | 4 | Feb 2026 | Programming |
| 19 | **Streamlit** | 4 | Dec 2025 | Data Apps / Frontend |
| 20 | **PostgreSQL** | 4 | Feb 2026 | Databases |
| 21 | **MariaDB / MySQL** | 3 | Dec 2025 | Databases |
| 22 | **Redis** | 3 | Dec 2025 | Databases / Caching |
| 23 | **JavaScript / TypeScript** | 3 | Feb 2026 | Programming |
| 24 | **React** (Vite) | 2 | Jan 2026 | Frontend |
| 25 | **Vue.js 3** (Vite) | 3 | Dec 2025 | Frontend |
| 26 | **HTML / CSS** | 3 | Jan 2026 | Frontend |
| 27 | **Bash / Shell Scripting** | 4 | Feb 2026 | Automation |
| 28 | **Prometheus** | 2 | Dec 2025 | Monitoring |
| 29 | **Grafana** | 2 | Dec 2025 | Monitoring |
| 30 | **Wiki.js** | 2 | Dec 2025 | Documentation |
| 31 | **Woodpecker CI** | 2 | Dec 2025 | CI/CD |
| 32 | **Obsidian** | 4 | Feb 2026 | Knowledge Management |
| 33 | **Email Infrastructure** (DKIM, SPF, DMARC) | 4 | Feb 2026 | Email / DNS |
| 34 | **yt-dlp / whisper.cpp** | 2 | Feb 2026 | Media / Transcription |
| 35 | **Zapier** | 1 | 2024 | Automation |
| 36 | **Upwork** (Freelance Platform) | 3 | Feb 2026 | Business |
| 37 | **Virtual Machine Manager / KVM** | 2 | Feb 2026 | Virtualization |
| 38 | **Cloudflare** (CDN, DNS, SSL) | 4 | Feb 2026 | Infrastructure |

---

## Proof of Competence (Items Rated 4–5)

For each high-proficiency item, one specific problem solved:

### Docker (5)
**Problem solved:** Resolved persistent 500/502 backend errors in the Frappe/ERPNext stack caused by custom apps (`education`, `library_management`, `edu_theme`) not being pip-installed into the container's virtual environment. Diagnosed that `bench build` fails if *any* app in `sites/apps.txt` is missing from Python's environment, even if unused by the current site. Built an automated `deploy-compose.sh` script that handles multi-file compose overlays and post-deploy pip installs.

### Docker Compose (5)
**Problem solved:** Designed and maintained a multi-layered Docker Compose architecture for the entire OpenAgile ecosystem — using base compose files combined with 5+ override files (`compose.databases.yaml`, `compose.external-traefik.yaml`, `compose.persist-apps.yaml`, `compose.frontend-custom-apps.yaml`) to cleanly separate concerns (databases, networking, persistence, custom frontend assets) without monolithic config files.

### Traefik (4)
**Problem solved:** Configured Traefik as the single ingress point for 10+ services across two separate Docker Compose stacks (main OpenAgile stack + Frappe sub-stack). Solved cross-stack routing by connecting the Frappe stack to the main Traefik instance via an external Docker network (`openagile_openagile_network`) with custom labels, SSL termination via Cloudflare, and per-service middleware routing.

### Frappe Framework (4)
**Problem solved:** Debugged and resolved broken asset loading (404/MIME errors) on the education site (`edu.erpnext.zubbystudio.shop`) by diagnosing that custom app asset symlinks don't survive Docker volume mounts. Created a dedicated compose override (`compose.frontend-custom-apps.yaml`) to directly mount custom app asset directories, bypassing the symlink limitation entirely.

### ERPNext (4)
**Problem solved:** Successfully deployed a multi-site ERPNext instance (`erpnext.zubbystudio.shop`, `library.erpnext.zubbystudio.shop`, `edu.erpnext.zubbystudio.shop`) with three custom apps installed in editable mode. Resolved database "Access Denied" errors by granting correct permissions to the `education_db` user for wildcard host access.

### Linux (Ubuntu/Debian) (4)
**Problem solved:** Managed a low-resource server (<4GB RAM, CPU-only) running 15+ Docker containers. Identified and resolved OOM issues caused by Python-based AI models (`faster-whisper`) by migrating to native-compiled `whisper.cpp` (small model), keeping the system stable for production workloads.

### SSH (4)
**Problem solved:** Set up and maintained SSH-based deployment pipelines from GitHub Actions to a remote production server (Netcup). Configured secure key-based authentication for automated CI/CD deployments of the Estate Portfolio Manager.

### DNS Management / Cloudflare (4)
**Problem solved:** Configured DNS records for 10+ subdomains across the `zubbystudio.shop` domain — all routed through Cloudflare for DNS-level SSL termination and proxied to Traefik. Managed DKIM, SPF, and DMARC records for email deliverability consulting work.

### Git (4)
**Problem solved:** Managed version control across multiple interconnected projects (Frappe apps, Streamlit apps, Vue frontends) within a single workspace, including custom `.gitignore` configurations to prevent Docker volumes and sensitive `.env` files from leaking.

### GitHub Actions (CI/CD) (4)
**Problem solved:** Built a complete CI/CD pipeline for the Estate Portfolio Manager that automatically connects to the production server via SSH, pulls latest changes, rebuilds Docker containers, and runs the EODHD price scraper for verification — all triggered on push to `main`.

### Python (4)
**Problem solved:** Built the Obsidian-to-PostgreSQL import pipeline (`import_obsidian.py`) that parses YAML frontmatter from Markdown files, handles nested wiki-links (`[[Unity]]`), zero-cost holdings, and missing fields — syncing an entire investment vault into a relational database.

### Streamlit (4)
**Problem solved:** Built the Estate Portfolio Manager dashboard from scratch — a full-featured stock portfolio tracker with real-time EODHD price updates, dividend tracking, tax reports, sector allocation charts, and a one-click price scraper button with live progress feedback.

### PostgreSQL (4)
**Problem solved:** Diagnosed and resolved `FATAL: password authentication failed` errors in the Estate Portfolio Manager by performing a clean volume reset and migrating from inline credentials to `env_file`-based config. Fixed schema issues (increasing `ticker` column from `VARCHAR(10)` to `VARCHAR(20)`) for Nigerian Exchange tickers.

### Bash / Shell Scripting (4)
**Problem solved:** Created the `deploy-compose.sh` master deployment script for the Frappe stack that orchestrates multi-file compose deployment, automatically detects and pip-installs all custom apps, and handles post-startup health checks — turning a 5-step manual process into a single-command deployment.

### Obsidian (4)
**Problem solved:** Designed a hybrid Obsidian Vault + Python automation system for Nigerian stock tracking. Used Dataview plugin with JavaScript queries to render live portfolio dashboards and price history charts, all fed by automated Python scripts that update YAML frontmatter in company notes daily.

### Email Infrastructure (DKIM, SPF, DMARC) (4)
**Problem solved:** Active freelance expertise — consulted on email deliverability and migration projects, including DNS record configuration (DKIM, SPF, DMARC), domain rebranding risk assessment, and inbox placement optimization for clients.

### Cloudflare (4)
**Problem solved:** Configured Cloudflare as the DNS and SSL provider for the entire OpenAgile ecosystem. Set up SSL termination mode (Full Strict) with Traefik, Cloudflare API-based ACME certificate generation, and DNS proxy rules for all 10+ subdomains.

---

## Summary by Category

| Category | Tools | Avg Proficiency |
|---|---|:---:|
| **Infrastructure** | Docker, Docker Compose, Traefik, Nginx, Portainer, Cloudflare | 4.0 |
| **DevOps** | SSH, Git, GitHub Actions, Woodpecker CI | 3.5 |
| **Programming** | Python, JavaScript/TypeScript, Bash | 3.7 |
| **Databases** | PostgreSQL, MariaDB/MySQL, Redis | 3.3 |
| **Frontend** | React, Vue.js, HTML/CSS, Streamlit | 3.0 |
| **ERP / Business** | Frappe, ERPNext, OpenProject | 3.3 |
| **Automation** | n8n, Zapier | 2.0 |
| **Monitoring** | Prometheus, Grafana | 2.0 |
| **Email / DNS** | DKIM, SPF, DMARC, Cloudflare DNS | 4.0 |
| **Knowledge Mgmt** | Obsidian, Wiki.js | 3.0 |

---

## Key Takeaways

> [!IMPORTANT]
> **Strongest vertical:** Docker + Compose + Traefik infrastructure — end-to-end container orchestration, multi-service networking, and automated deployment.

> [!TIP]
> **Most marketable combination:** Email Infrastructure (DKIM/SPF/DMARC) + DNS (Cloudflare) + Linux server administration — this maps directly to active freelance work on Upwork.

> [!NOTE]
> **Growth areas:** React (currently 2/5), Prometheus/Grafana (2/5), and n8n automation (3/5) are the tools with the most room for skill improvement relative to their ecosystem value.
