#!/bin/bash
set -e
cd ~/openagile/frappe_docker

echo "⚙️  Starting final site setup and configuration..."

# Enter backend and execute setup
docker compose exec backend bash << 'BACKEND_EOF'
cd /home/frappe/frappe-bench

# 1. Configure Multi-tenancy with CORRECT DB HOST (mariadb)
echo "Configuring common_site_config.json..."
cat > sites/common_site_config.json << 'JSON'
{
 "db_host": "mariadb",
 "db_port": 3306,
 "redis_cache": "redis://redis-cache:6379",
 "redis_queue": "redis://redis-queue:6379",
 "redis_socketio": "redis://redis-socketio:6379",
 "dns_multitenant": true,
 "serve_default_site": false
}
JSON

# 2. Define CORE Apps ONLY (Frappe and ERPNext) for new-site
# This avoids the ModuleNotFoundError on library_management during the new-site command.
echo "Setting sites/apps.txt to core apps only..."
cat > sites/apps.txt << 'APPS'
frappe
erpnext
APPS

# 3. Remove Orphaned Site Directories
echo "Removing orphaned site directories..."
rm -rf sites/erpnext.zubbystudio.shop
rm -rf sites/library.erpnext.zubbystudio.shop

# 4. Create ERPNext Site (The main ERP site)
echo "Creating ERPNext Site (main_erpnext)..."
bench new-site erpnext.zubbystudio.shop \
  --db-name main_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

bench --site erpnext.zubbystudio.shop set-config developer_mode 1
bench --site erpnext.zubbystudio.shop set-config enable_scheduler 1

# 5. Create Library Site
echo "Creating Library Site (library_erpnext)..."
bench new-site library.erpnext.zubbystudio.shop \
  --db-name library_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

bench --site library.erpnext.zubbystudio.shop set-config developer_mode 1
bench --site library.erpnext.zubbystudio.shop set-config enable_scheduler 1

# 6. Install the Custom App (library_management) on the Library Site
# This is the correct moment to install non-core apps.
echo "Installing library_management app on library.erpnext.zubbystudio.shop..."
bench --site library.erpnext.zubbystudio.shop install-app library_management

# 7. Update sites/apps.txt to include ALL apps for running the bench
echo "Updating sites/apps.txt with all apps for runtime..."
cat > sites/apps.txt << 'ALL_APPS'
frappe
erpnext
library_management
ALL_APPS

echo "✅ Sites and Apps configured successfully!"
BACKEND_EOF

# Restart services to apply new configurations and links
echo "🔄 Restarting services..."
docker compose restart
sleep 30
echo "🎉 Deployment complete and sites fixed!"
