#!/bin/bash
set -e

cd ~/openagile/frappe_docker

echo "🚀 Deploying Frappe with compose.yaml + overrides..."

# Stop any existing services
docker compose down 2>/dev/null || true

# Start with ALL overrides including frontend custom apps fix
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  -f overrides/compose.persist-apps.yaml \
  -f overrides/compose.frontend-custom-apps.yaml \
  up -d

echo "⏳ Waiting for services to start (60s)..."
sleep 60

echo "📦 Installing custom apps into Python environment (Persistence Fix)..."
# We loop through the apps to ensure they are installed. 
# Using || true to prevent script failure if already installed, though pip is idempotent. 
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/library_management
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/education
docker compose exec backend /home/frappe/frappe-bench/env/bin/pip install -e apps/edu_theme

echo "🔄 Restarting backend to load new apps..."
docker compose restart backend

echo "📊 Service Status:"
docker compose ps


echo ""
echo "🔍 Checking databases..."
docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;" 2>&1 | grep -E "main_erpnext|library_erpnext|Database" || echo "⚠️  Site databases need to be created"



echo ""
echo "✅ Deployment complete!"
echo "   Landing Page: https://edu.erpnext.zubbystudio.shop/landing"
echo ""
echo "Next steps:"
echo "1. If databases are missing, run: ./recreate-sites.sh"
echo "2. Test access: https://erpnext.zubbystudio.shop"