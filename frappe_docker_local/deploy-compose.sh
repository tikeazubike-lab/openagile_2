#!/bin/bash
set -e

cd ~/openagile/frappe_docker

echo "🚀 Deploying Frappe with compose.yaml + overrides..."

# Stop any existing services
docker compose down 2>/dev/null || true

# Start with ALL overrides
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  -f overrides/compose.persist-apps.yaml \
  up -d

echo "⏳ Waiting for services to start..."
sleep 60

echo "📊 Service Status:"
docker compose ps

echo ""
echo "🔍 Checking databases..."
docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;" 2>&1 | grep -E "main_erpnext|library_erpnext|Database" || echo "⚠️  Site databases need to be created"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. If databases are missing, run: ./recreate-sites.sh"
echo "2. Test access: https://erpnext.zubbystudio.shop"
