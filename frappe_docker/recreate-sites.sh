#!/bin/bash
set -e

cd ~/openagile/frappe_docker

echo "🗄️  Recreating Frappe sites with databases..."

# Check if databases exist
DB_CHECK=$(docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;" 2>&1 | grep -c "main_erpnext" || echo "0")

if [ "$DB_CHECK" -eq "0" ]; then
    echo "⚠️  Databases missing, will recreate sites..."
    
    # Enter backend container
    docker compose exec backend bash << 'BACKEND_SCRIPT'
cd /home/frappe/frappe-bench

# Configure multi-tenancy
cat > sites/common_site_config.json << 'JSON'
{
 "db_host": "db",
 "db_port": 3306,
 "redis_cache": "redis://redis-cache:6379",
 "redis_queue": "redis://redis-queue:6379",
 "redis_socketio": "redis://redis-socketio:6379",
 "dns_multitenant": true,
 "serve_default_site": false
}
JSON

# Set apps
cat > sites/apps.txt << 'APPS'
frappe
erpnext
APPS

# Remove old site directories if they exist
rm -rf sites/erpnext.zubbystudio.shop
rm -rf sites/library.erpnext.zubbystudio.shop

# Create ERPNext site
echo "Creating ERPNext site..."
bench new-site erpnext.zubbystudio.shop \
  --db-name main_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

bench --site erpnext.zubbystudio.shop set-config developer_mode 1
bench --site erpnext.zubbystudio.shop set-config enable_scheduler 1

# Create Library site
echo "Creating Library site..."
bench new-site library.erpnext.zubbystudio.shop \
  --db-name library_erpnext \
  --mariadb-root-password admin \
  --admin-password '!1Winner75' \
  --mariadb-user-host-login-scope='%'

bench --site library.erpnext.zubbystudio.shop set-config developer_mode 1
bench --site library.erpnext.zubbystudio.shop set-config enable_scheduler 1

echo "✅ Sites created successfully!"
BACKEND_SCRIPT

else
    echo "✅ Databases already exist, skipping site creation"
fi

# Restart services
echo "🔄 Restarting services..."
docker compose restart

sleep 30

echo ""
echo "🎉 Sites ready!"
echo "Main Site: https://erpnext.zubbystudio.shop"
echo "Library Site: https://library.erpnext.zubbystudio.shop"
echo "Login: Administrator / !1Winner75"
