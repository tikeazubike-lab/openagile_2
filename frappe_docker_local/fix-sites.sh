#!/bin/bash
set -e
cd ~/openagile/frappe_docker

echo "🔧 Recreating sites (Final Attempt: Corrected DB host 'mariadb' and app setup sequence)..."

# Enter backend and execute cleanup/creation
docker compose exec backend bash << 'BACKEND_EOF'
cd /home/frappe/frappe-bench

# 1. Configure Multi-tenancy with CORRECT DB HOST
echo "Configuring multi-tenancy..."
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

# 2. Define All Apps for Bench (Essential for multi-tenancy setup)
echo "Defining all required apps in sites/apps.txt..."
cat > sites/apps.txt << 'APPS'
frappe
erpnext
library_management
APPS

# 3. Remove Orphaned Site Directories
echo "Removing orphaned site directories..."
# Ensure removal is safe, as we are recreating them.
rm -rf sites/erpnext.zubbystudio.shop
rm -rf sites/library.erpnext.zubbystudio.shop

# 4. Create ERPNext Site
echo "Creating ERPNext Site..."
# bench new-site will apply migrations for frappe and erpnext (the default apps)
bench new-site erpnext.zubbystudio.shop \
  --db-name main_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

bench --site erpnext.zubbystudio.shop set-config developer_mode 1
bench --site erpnext.zubbystudio.shop set-config enable_scheduler 1

# 5. Create Library Site and Install Library App
echo "Creating Library Site..."
bench new-site library.erpnext.zubbystudio.shop \
  --db-name library_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

# Install the custom app on the specific site
echo "Installing library_management app..."
bench --site library.erpnext.zubbystudio.shop install-app library_management

bench --site library.erpnext.zubbystudio.shop set-config developer_mode 1
bench --site library.erpnext.zubbystudio.shop set-config enable_scheduler 1

echo "✅ Sites and Apps configured successfully!"
BACKEND_EOF

# Restart services
echo "🔄 Restarting services..."
docker compose restart
sleep 30
echo "🎉 Deployment complete and sites fixed!"
