#!/bin/bash
set -e

cd ~/openagile/frappe_docker

echo "🚀 Deploying Frappe Multi-Tenant Environment..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! docker network inspect openagile_openagile_network >/dev/null 2>&1; then
    echo "❌ OpenAgile network not found!"
    echo "   Start OpenAgile first: cd ~/openagile && docker compose up -d"
    exit 1
fi

echo "✅ OpenAgile network found"

# Check for Redis compatibility issues
if [ -f "data/redis-cache/dump.rdb" ]; then
    echo "⚠️  Old Redis dump files detected!"
    echo "   These may be incompatible with Redis 6.2"
    read -p "   Delete old Redis data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -f data/redis-cache/dump.rdb data/redis-queue/dump.rdb
        echo "✅ Redis data cleaned"
    fi
fi

# Stop any existing services
echo ""
echo "🛑 Stopping existing services..."
docker compose down 2>/dev/null || true

# Start with all overrides
echo ""
echo "🚀 Starting services..."
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  -f overrides/compose.persist-apps.yaml \
  up -d

echo "⏳ Waiting 60 seconds for services to initialize..."
sleep 60

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

# Check for restarting services
RESTARTING=$(docker compose ps | grep -c "Restarting" || true)
if [ "$RESTARTING" -gt 0 ]; then
    echo ""
    echo "⚠️  Warning: Some services are restarting!"
    echo "   Check logs: docker compose logs [service-name]"
fi

# Check databases
echo ""
echo "🗄️  Checking databases..."
docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;" 2>&1 | \
  grep -E "main_erpnext|library_erpnext|Database" || \
  echo "⚠️  Site databases need to be created"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "   1. If databases are missing: ./scripts/create-sites.sh"
echo "   2. If custom apps needed: ./scripts/install-custom-app.sh"
echo "   3. Test access: https://erpnext.yourdomain.com"
