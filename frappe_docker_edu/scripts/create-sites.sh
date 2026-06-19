#!/bin/bash
set -e

cd ~/openagile/frappe_docker

echo "🏗️  Creating Frappe Sites..."
echo ""

# Enter backend container and create sites
docker compose exec backend bash << 'BACKEND_SCRIPT'
cd /home/frappe/frappe-bench

# Configure multi-tenancy
echo "📝 Configuring multi-tenancy..."
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

# Set available apps
cat > sites/apps.txt << 'APPS'
frappe
erpnext
APPS

echo "✅ Multi-tenancy configured"
echo ""

# Test database connection
echo "🔍 Testing database connection..."
mysql -h db -u root -padmin -e "SELECT 'OK' as status;" || {
    echo "❌ Database connection failed!"
    exit 1
}
echo "✅ Database connection OK"
echo ""

# Create main ERPNext site
echo "🏗️  Creating main ERPNext site (takes 2-3 minutes)..."
bench new-site erpnext.yourdomain.com \
  --db-name main_erpnext \
  --mariadb-root-password admin \
  --admin-password 'YourStrongPassword123!' \
  --mariadb-user-host-login-scope='%'

bench --site erpnext.yourdomain.com set-config developer_mode 1
bench --site erpnext.yourdomain.com set-config enable_scheduler 1

echo "✅ Main site created"
echo ""

# Install ERPNext
echo "📦 Installing ERPNext app (takes 2-5 minutes)..."
bench --site erpnext.yourdomain.com install-app erpnext

echo "✅ ERPNext installed"
echo ""

# Create library site
echo "🏗️  Creating library site (takes 2-3 minutes)..."
bench new-site library.erpnext.yourdomain.com \
  --db-name library_erpnext \
  --mariadb-root-password admin \
  --admin-password 'YourStrongPassword123!' \
  --mariadb-user-host-login-scope='%'

bench --site library.erpnext.yourdomain.com set-config developer_mode 1
bench --site library.erpnext.yourdomain.com set-config enable_scheduler 1

echo "✅ Library site created"
echo ""

# Build assets (CRITICAL for proper styling)
echo "🎨 Building frontend assets (takes 2-5 minutes)..."
bench build --force

# MANDATORY: Clear cache after build
echo "🧹 Clearing caches..."
bench --site erpnext.yourdomain.com clear-cache
bench --site erpnext.yourdomain.com clear-website-cache
bench --site library.erpnext.yourdomain.com clear-cache
bench --site library.erpnext.yourdomain.com clear-website-cache

echo ""
echo "✅ All sites created successfully!"
echo ""
echo "📊 Installed Apps:"
bench --site erpnext.yourdomain.com list-apps
echo ""
bench --site library.erpnext.yourdomain.com list-apps

BACKEND_SCRIPT

echo ""
echo "🔄 Restarting services..."
docker compose restart

echo "⏳ Waiting 30 seconds for services..."
sleep 30

echo ""
echo "✅ Site creation complete!"
echo ""
echo "🌐 Access your sites:"
echo "   Main: https://erpnext.yourdomain.com"
echo "   Library: https://library.erpnext.yourdomain.com"
echo "   Login: Administrator / YourStrongPassword123!"
