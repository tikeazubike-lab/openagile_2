#!/bin/bash
# Comprehensive WireGuard & Traefik Diagnostic Script
# Run this on your Netcup server to identify why Traefik isn't seeing wg-easy

echo "=================================================="
echo "🛡️ WireGuard vs Traefik Diagnostic Tool"
echo "=================================================="

# 1. Check if wg-easy container is actually running
echo "---"
echo "🔍 1. Checking wg-easy container status:"
docker ps --filter "name=wg-easy" --format "table {{.Names}}\t{{.Status}}\t{{.Networks}}\t{{.Ports}}"

# 2. Check Traefik's logs for explicit errors about the wg-easy container
echo "---"
echo "📝 2. Checking Traefik logs for 'wg-easy' or 'vpn.zubbystudio.shop' errors:"
echo "(Looking for the last 50 lines of traefik logs that mention wireguard)"
docker logs traefik 2>&1 | grep -i -E "wg-easy|vpn.zubbystudio.shop" | tail -n 50 || echo "   No logs found in Traefik about wg-easy. Traefik is entirely ignoring the container."

# 3. Inspect the wg-easy container's Traefik labels
echo "---"
echo "🏷️  3. Inspecting wg-easy Traefik Labels (Does it have everything?):"
docker inspect wg-easy --format '{{range $k, $v := .Config.Labels}}{{println $k "=" $v}}{{end}}' | grep "traefik." || echo "   ERROR: Container is missing traefik labels!"

# 4. Check Network Attachment
echo "---"
echo "🌐 4. Verifying Network connectivity (Is wg-easy on the same network as Traefik?):"
echo "Traefik networks:"
docker inspect traefik --format '{{range $k, $v := .NetworkSettings.Networks}}{{println $k}}{{end}}'
echo "wg-easy networks:"
docker inspect wg-easy --format '{{range $k, $v := .NetworkSettings.Networks}}{{println $k}}{{end}}'

# 5. Check the actual wg-easy application logs
echo "---"
echo "🖥️  5. Checking wg-easy internal application logs (Did it crash on boot?):"
docker logs wg-easy --tail 20

# 6. Check .env file generation check
echo "---"
echo "🔐 6. Verifying .env generation:"
if [ -f "/home/zubbyik/openagile/wireguard/.env" ]; then
    echo "   .env file exists."
    grep -E "WG_HOST|PASSWORD_HASH" /home/zubbyik/openagile/wireguard/.env | sed 's/\(PASSWORD_HASH=\).*/\1[REDACTED]/'
else
    echo "   ERROR: .env file DOES NOT EXIST at /home/zubbyik/openagile/wireguard/.env"
fi

echo "=================================================="
echo "📋 HOW TO READ THIS OUTPUT:"
echo "1. If wg-easy is 'Restarting', it never booted properly (check step 5)."
echo "2. If Traefik logs (step 2) say 'bad network' or 'port missing', we have our answer."
echo "3. If step 4 shows they are not sharing 'openagile_openagile_network', Traefik can't proxy it."
echo "=================================================="
