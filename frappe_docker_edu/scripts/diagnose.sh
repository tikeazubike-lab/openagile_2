#!/bin/bash

cd ~/openagile/frappe_docker

echo "🔍 Frappe Multi-Tenant Diagnostic Report v3.1"
echo "=============================================="
echo ""

# Service status
echo "📊 Service Status:"
docker compose ps
echo ""

# Redis health
echo "🔴 Redis Health:"
docker exec frappe_docker-redis-cache-1 redis-cli ping 2>/dev/null && echo "  ✅ redis-cache: OK" || echo "  ❌ redis-cache: FAILED"
docker exec frappe_docker-redis-queue-1 redis-cli ping 2>/dev/null && echo "  ✅ redis-queue: OK" || echo "  ❌ redis-queue: FAILED"
echo ""

# Database health
echo "🗄️  Database Health:"
docker compose exec db mysql -u root -padmin -e "SELECT 'OK' as status;" 2>/dev/null && echo "  ✅ MariaDB: OK" || echo "  ❌ MariaDB: FAILED"
echo ""

# Sites
echo "🌐 Sites:"
docker compose exec backend ls -la /home/frappe/frappe-bench/sites/ 2>/dev/null | grep -E "zubbystudio|yourdomain" || echo "  ⚠️  No sites found"
echo ""

# Databases
echo "🗃️  Databases:"
docker compose exec db mysql -u root -padmin -e "SHOW DATABASES;" 2>/dev/null | grep -E "main_erpnext|library_erpnext" || echo "  ⚠️  No site databases"
echo ""

# Asset bundles (critical for styling)
echo "🎨 Asset Bundles:"
ACTUAL_BUNDLES=$(docker compose exec backend ls /home/frappe/frappe-bench/apps/frappe/frappe/public/dist/js/ 2>/dev/null | grep frappe-web)
if [ -n "$ACTUAL_BUNDLES" ]; then
    echo "$ACTUAL_BUNDLES"
else
    echo "  ⚠️  No bundles found - Run: bench build"
fi
echo ""

# Asset hash check (improved with better error handling)
echo "🔍 Asset Hash Verification:"
ACTUAL_HASH=$(docker compose exec backend ls /home/frappe/frappe-bench/apps/frappe/frappe/public/dist/js/ 2>/dev/null | grep -o 'frappe-web.bundle.[^.]*' | head -1)

if [ -n "$ACTUAL_HASH" ]; then
    echo "  Actual bundle: $ACTUAL_HASH.js"
    
    # Try to fetch HTML - with proper error handling
    HTML_HASH=$(curl -s --max-time 5 https://library.erpnext.zubbystudio.shop 2>/dev/null | grep -o 'frappe-web.bundle.[^"]*\.js' | head -1)
    
    if [ -n "$HTML_HASH" ]; then
        echo "  HTML references: $HTML_HASH"
        
        if [ "$ACTUAL_HASH.js" == "$HTML_HASH" ]; then
            echo "  ✅ Asset hashes match!"
        else
            echo "  ❌ Asset hash MISMATCH"
            echo "     Run: bench build --force && bench --site all clear-cache"
        fi
    else
        # Check if sites are actually accessible
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 https://library.erpnext.zubbystudio.shop 2>/dev/null)
        
        if [ "$HTTP_CODE" == "200" ]; then
            echo "  ✅ Site accessible (HTTP 200) but couldn't parse HTML"
            echo "     This is normal - asset verification skipped"
        else
            echo "  ⚠️  Could not fetch HTML (HTTP $HTTP_CODE)"
            echo "     Check if sites are accessible via browser"
        fi
    fi
else
    echo "  ⚠️  No actual bundle found - assets not built"
fi
echo ""

# Network connectivity (improved with better tool detection)
echo "🌐 Network Connectivity:"

# Test using MySQL client instead of ping (more reliable)
docker compose exec backend mysql -h db -u root -padmin -e "SELECT 1" >/dev/null 2>&1 && \
    echo "  ✅ backend → db (via MySQL)" || \
    echo "  ❌ backend → db"

# Test Redis using redis-cli if available
docker compose exec backend bash -c "command -v redis-cli >/dev/null 2>&1" && {
    docker compose exec backend redis-cli -h redis-cache ping >/dev/null 2>&1 && \
        echo "  ✅ backend → redis-cache" || \
        echo "  ❌ backend → redis-cache"
    docker compose exec backend redis-cli -h redis-queue ping >/dev/null 2>&1 && \
        echo "  ✅ backend → redis-queue" || \
        echo "  ❌ backend → redis-queue"
} || {
    # Fallback: Use telnet-style connection test via Python
    docker compose exec backend python3 -c "
import socket
def test_connection(host, port):
    try:
        socket.create_connection((host, port), timeout=2)
        return True
    except:
        return False

print('  ✅ backend → redis-cache' if test_connection('redis-cache', 6379) else '  ❌ backend → redis-cache')
print('  ✅ backend → redis-queue' if test_connection('redis-queue', 6379) else '  ❌ backend → redis-queue')
" 2>/dev/null || echo "  ⚠️  Could not test Redis connectivity (no tools available)"
}
echo ""

# Common issues check
echo "⚠️  Common Issues Check:"

# Check for Redis RDB format issues
REDIS_LOGS=$(docker logs frappe_docker-redis-cache-1 2>&1 | tail -10)
if echo "$REDIS_LOGS" | grep -q "Can't handle RDB format"; then
    echo "  ❌ CRITICAL: Redis RDB format incompatibility detected!"
    echo "     Solution: docker compose down && sudo rm -f data/redis-*/dump.rdb && docker compose up -d"
fi

# Check for restarting services
RESTARTING=$(docker compose ps | grep -c "Restarting" || true)
if [ "$RESTARTING" -gt 0 ]; then
    echo "  ⚠️  $RESTARTING service(s) constantly restarting"
    
    # Identify which service
    RESTARTING_SERVICE=$(docker compose ps | grep "Restarting" | awk '{print $1}' | head -1)
    if [ -n "$RESTARTING_SERVICE" ]; then
        echo "     Service: $RESTARTING_SERVICE"
        echo "     Check logs: docker logs $RESTARTING_SERVICE --tail=30"
    fi
fi

# Check for common config issues
DB_HOST=$(docker compose exec backend cat /home/frappe/frappe-bench/sites/common_site_config.json 2>/dev/null | grep -o '"db_host": "[^"]*"' | cut -d'"' -f4)
if [ -n "$DB_HOST" ]; then
    echo "  ℹ️  Database host configured as: $DB_HOST"
    if [ "$DB_HOST" != "db" ] && [ "$DB_HOST" != "mariadb" ]; then
        echo "     ⚠️  Non-standard database host - verify it matches your service name"
    fi
fi

echo ""
echo "✅ Diagnostic complete!"
echo ""
echo "📋 Summary:"
echo "   Services: $(docker compose ps --filter "status=running" | tail -n +2 | wc -l)/$(docker compose ps | tail -n +2 | wc -l) running"
echo "   Redis: $(docker exec frappe_docker-redis-cache-1 redis-cli ping 2>/dev/null || echo 'DOWN')"
echo "   Database: $(docker compose exec db mysql -u root -padmin -e "SELECT 'UP' as status;" 2>/dev/null | tail -1 || echo 'DOWN')"
echo "   Sites: $(docker compose exec backend ls /home/frappe/frappe-bench/sites/ 2>/dev/null | grep -c "zubbystudio\|yourdomain" || echo '0')"
