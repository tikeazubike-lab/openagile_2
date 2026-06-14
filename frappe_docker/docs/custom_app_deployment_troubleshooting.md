# Frappe Custom App Deployment & Troubleshooting Guide

**Date:** December 24, 2025
**Project:** OpenAgile Board - Frappe/ERPNext Stack
**Context:** Deploying custom apps (`education`, `library_management`, `edu_theme`) with a Vue.js landing page in a Docker Compose environment using `frappe_docker`.

---

## 1. The Challenge

We aimed to deploy a custom Vue.js landing page within the `edu_theme` app. While the stack was operational, we encountered two critical blocking issues:

1.  **Frontend Assets 404:** Nginx returned 404 for custom app assets (`/assets/edu_theme/...`), causing the landing page to load without styles or scripts (MIME type errors).
2.  **Backend 500/502 Errors:** The backend container crashed or returned internal server errors when accessing the landing page route.

## 2. Root Cause Analysis

### A. Frontend Assets 404 (The Symlink Problem)
*   **Observation:** Files existed in the backend container and on the host, but were invisible to the frontend (Nginx) container.
*   **Mechanism:** Frappe's `bench build` creates symlinks in `sites/assets/` pointing to `../../apps/<app_name>/...`.
*   **Failure:** In Docker, `sites/` is a bind mount. The symlink points to a path (`/home/frappe/frappe-bench/apps/...`) that exists in the *backend* container but NOT necessarily in the *frontend* container (or the frontend container has a different view of the filesystem due to volume mount timing).
*   **Result:** Nginx follows the symlink into a non-existent path and returns 404.

### B. Backend 500/502 Errors (The Persistence Problem)
*   **Observation:** `bench list-apps` failed with `ModuleNotFoundError: No module named 'education'`.
*   **Mechanism:** We mount the `apps/` directory to `/home/frappe/frappe-bench/apps` so the code is present. However, the *Python environment* (`env/`) is inside the container and is **not persisted** by default in our setup.
*   **Failure:** When the container restarts (e.g., during troubleshooting), the `pip install -e ...` links are lost. The apps exist on disk, but Python doesn't know about them.
*   **Result:** Gunicorn fails to import the app modules, leading to boot loops or 500 errors.

### C. Database Connectivity (Access Denied)
*   **Observation:** `OperationalError: (1045, "Access denied for user 'education_db'...")`.
*   **Mechanism:** The MariaDB user `education_db` was restricted to a specific IP or host that didn't match the backend container's new internal IP after a restart.
*   **Result:** Backend could not connect to the database.

---

## 3. The Solution

### A. Fixing Frontend Assets (Direct Mounts)
Instead of relying on fragile symlinks between containers, we explicitly mounted the public asset directories of our custom apps into the frontend container.

**File:** `frappe_docker/overrides/compose.frontend-custom-apps.yaml`
```yaml
services:
  frontend:
    volumes:
      # Mount custom app public directories directly (bypasses symlink issue)
      - ./apps/edu_theme/edu_theme/public:/home/frappe/frappe-bench/sites/assets/edu_theme:ro
      - ./apps/education/education/public:/home/frappe/frappe-bench/sites/assets/education:ro
      - ./apps/library_management/library_management/public:/home/frappe/frappe-bench/sites/assets/library_management:ro
```
*This ensures Nginx sees the actual files, not broken links.*

### B. Fixing Backend Persistence (Automated Install)
We updated the deployment workflow to ensure apps are installed into the Python environment every time the stack is deployed.

**Command:**
```bash
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/library_management
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/education
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/edu_theme
```
*Note: We use the full path to the bench's pip to avoid installing into the system python.*

### C. Fixing Database Permissions
We broadened the permissions for the site's database user to allow connections from any container IP in the docker network.

**Command:**
```sql
GRANT ALL PRIVILEGES ON education_db.* TO 'education_db'@'%' IDENTIFIED BY 'PASSWORD';
FLUSH PRIVILEGES;
```

---

## 4. Final Deployment Workflow

To deploy the stack with all fixes applied, use the master script:

```bash
cd frappe_docker
./deploy-compose.sh
```

**This script now:**
1.  Stops existing services.
2.  Starts services with **all** overrides (including the frontend asset fix).
3.  Waits for services to initialize.
4.  **Automatically installs custom apps** via `pip` to ensure backend stability.
5.  Checks database status.

---

## 5. Verification

*   **Landing Page:** `https://edu.erpnext.zubbystudio.shop/landing` (Returns 200 OK)
*   **Assets:** `https://edu.erpnext.zubbystudio.shop/assets/edu_theme/frontend/assets/main-....js` (Returns 200 OK)
*   **Backend:** `docker compose exec backend bench list-apps` (Shows all apps installed)
