# OpenAgile Board - Project Documentation

## Project Overview

**OpenAgile** is a comprehensive, self-hosted platform designed for agile development, business management, and productivity. It integrates a suite of open-source tools into a unified ecosystem managed via Docker Compose.

**Core Components:**
*   **Infrastructure:** Traefik (Reverse Proxy), Portainer (Container Management), Prometheus & Grafana (Monitoring).
*   **DevOps:** Gitea (Git), Woodpecker CI (CI/CD).
*   **Productivity:** OpenProject (Project Management), Wiki.js (Documentation), n8n (Workflow Automation).
*   **ERP:** Frappe/ERPNext (Business Operating System) running as a sub-stack.

## Architecture

The project is structured into two main Docker Compose stacks:

1.  **Main Stack (`/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/docker-compose.yml`):**
    *   Hosts the core infrastructure and management tools.
    *   **Traefik** acts as the ingress controller, handling SSL termination (Cloudflare) and routing for all services.
    *   **Network:** `openagile_network` (bridge).

2.  **Frappe/ERPNext Stack (`/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/frappe_docker/`):**
    *   Hosts the ERPNext application and its custom apps (`education`, `library_management`, `edu_theme`).
    *   **Integration:** Connects to the main stack via `openagile_openagile_network` using the override file `overrides/compose.external-traefik.yaml`.
    *   **Databases:** Uses its own MariaDB and Redis containers (defined in `overrides/compose.databases.yaml`).
    *   **Frontend Assets:** Uses `overrides/compose.frontend-custom-apps.yaml` to directly mount custom app assets, bypassing symlink issues.
    *   **Vue.js Integration:** The `edu_theme` app uses a Vue.js 3 frontend (built via Vite) that consumes data from Frappe via a REST API (`get_landing_page_data`).

## Directory Structure

*   `configs/`: Configuration files for various services.
    *   `traefik/`: Static (`traefik.yml`) and dynamic (`dynamic/`) configuration.
    *   `prometheus/`, `grafana/`: Monitoring configs and dashboards.
    *   `n8n/`, `openproject/`: App-specific settings.
*   `scripts/`: Utility scripts for maintenance, backups, and setup.
    *   `backup-openagile.sh`: Automated backup script for the **Main Stack**.
    *   `init-databases.sh`: Database initialization.
    *   `migrate-nginx-to-traefik.sh`: Legacy migration tool.
*   `frappe_docker/`: The Frappe/ERPNext sub-project.
    *   `compose.yaml`: Base compose file for Frappe.
    *   `deploy-compose.sh`: **Master deployment script for the Frappe stack.**
    *   `overrides/`: Custom overrides (e.g., for Traefik integration, persistence, and frontend mounts).
    *   `apps/`: Source code for custom Frappe apps.
    *   `sites/`: Site configuration and assets.
    *   `docs/`: Project specific documentation (e.g., `custom_app_deployment_troubleshooting.md`).
*   `frappe_docker_local/`: A local backup/mirror of the `frappe_docker` directory.
*   `backups/`: Destination for automated backups from the Main Stack.

## Key Services & URLs

| Service | URL | Description |
| :--- | :--- | :--- |
| **Traefik** | `traefik.zubbystudio.shop` | Proxy Dashboard |
| **OpenProject** | `project.zubbystudio.shop` | Project Management |
| **Wiki.js** | `docs.zubbystudio.shop` | Documentation |
| **n8n** | `n8n.zubbystudio.shop` | Automation |
| **Gitea** | `git.zubbystudio.shop` | Code Hosting |
| **Woodpecker** | `ci.zubbystudio.shop` | CI/CD |
| **Grafana** | `metrics.zubbystudio.shop` | Monitoring Dashboards |
| **ERPNext** | `erpnext.zubbystudio.shop` | Main ERP Site |
| **Library** | `library.erpnext.zubbystudio.shop` | Library App Site |
| **Education** | `edu.erpnext.zubbystudio.shop` | Education App Site |

## Building and Running

### 1. Main Stack
To start the core infrastructure:
```bash
cd /home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile
docker compose up -d
```

### 2. Frappe/ERPNext Stack
**Preferred Method:** Use the deployment script which handles all necessary overrides, post-deploy setup, and app installation.
```bash
cd frappe_docker
./deploy-compose.sh
```
*This script runs the following command and automatically installs apps via pip:*
```bash
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  -f overrides/compose.persist-apps.yaml \
  -f overrides/compose.frontend-custom-apps.yaml \
  up -d
```

### 3. Developing the Custom Vue Frontend
The `edu_theme` app has a Vue.js frontend located in `apps/edu_theme/frontend`. To update it:
1.  **Edit Code:** Modify Vue components in `apps/edu_theme/frontend/src`.
2.  **Build:** Run the build command inside the backend container:
    ```bash
    docker compose exec backend bash -c "cd apps/edu_theme/frontend && npm run build"
    ```
3.  **Update Template:** If the build generates new filenames (hashing), update `apps/edu_theme/edu_theme/www/landing.html`.
4.  **Refresh:** The changes are immediately reflected on the site (due to volume mounts).

## Installed Frappe Apps
Current apps detected in `frappe_docker/sites/apps.json` and installed via pip:
*   `frappe` (v15.90.1)
*   `erpnext` (v15.90.1)
*   `education` (v15.0.0)
*   `library_management` (v0.0.1)
*   `edu_theme` (v0.0.1)

> **Important:** Custom apps must be installed in the backend container's Python environment using:
> `docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/<app_name>`

## Maintenance & Backups

*   **Logs:** `docker compose logs -f [service_name]`
*   **Main Stack Backup:** Run `./scripts/backup-openagile.sh`. This backs up:
    *   Databases: `openagile` (Postgres), `n8n`, `wikijs`, `openproject`.
    *   Volumes: `n8n_data`, `wikijs_data`, `openproject_assets`, etc.
    *   *Note: This script does NOT currently backup the Frappe stack volumes.*
*   **Diagnostics:**
    *   `./comprehensive_diagnostics.sh`: Runs a full system check.
    *   `./diagnose-directories.sh`: Verifies directory structure integrity.

## Known Issues & Resolutions (Dec 2025)
*   **Custom App Assets 404:** Solved by using `overrides/compose.frontend-custom-apps.yaml` to directly mount asset directories, bypassing Docker symlink limitations.
*   **Backend 500/502 Error:** Caused by missing Python packages for custom apps. Resolved by reinstalling apps into the `env` via pip (automated in `deploy-compose.sh`).
*   **Vue.js Integration:** Successfully implemented. Backend API (`edu_theme.api.get_landing_page_data`) serves dynamic content to the frontend.

## SDLC & Documentation Governance

**CRITICAL RULE**: All projects MUST adhere to the EPM Governance & SDLC/STLC standards.

**Document Identity System**:
Every document (Requirement, Architecture, Test, Handover, Onboarding) MUST have a standardized YAML header block:
- `type`: BR | FR | ADR | TC | AT | HO | OB
- `id`: e.g., BR-005
- `title`, `status`, `version`, `owner`

**Folder Structure**:
All documentation must be stored in the `docs/` directory of the respective project:
- `docs/requirements/`
- `docs/architecture/`
- `docs/testing/` (with `test-plans/` and `acceptance-tests/`)
- `docs/handover/`
- `docs/onboarding/`

**Branch Strategy**:
- `main` is protected (production).
- All active development happens on `test`.
- Use conventional commits: `feat`, `fix`, `docs`, `test`, `chore`.
