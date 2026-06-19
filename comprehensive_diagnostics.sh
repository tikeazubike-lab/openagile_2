# Create diagnostic script
cat > ~/diagnose-traefik.sh << 'EOF'
#!/bin/bash

echo "🔍 Traefik Full Diagnostics"
echo "============================"
echo ""

echo "1️⃣ Traefik Container Status:"
docker ps --filter name=traefik --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "2️⃣ Traefik Config Files:"
echo "--- Static Config (traefik.yml) ---"
docker exec traefik cat /etc/traefik/traefik.yml 2>&1 | head -20
echo ""
echo "--- Dynamic Config Directory ---"
docker exec traefik ls -la /etc/traefik/dynamic/ 2>&1
echo ""

echo "3️⃣ Certificate Storage:"
docker exec traefik ls -lh /letsencrypt/ 2>&1
echo ""

echo "4️⃣ Recent Traefik Logs:"
docker compose logs --tail=30 traefik 2>&1 | grep -v "defaulting to first"
echo ""

echo "5️⃣ Docker Networks:"
docker network ls | grep openagile
echo ""

echo "6️⃣ Service Labels Check (n8n example):"
docker inspect n8n 2>&1 | grep -A 10 '"Labels"'
echo ""

echo "7️⃣ Port Bindings:"
sudo netstat -tlnp | grep -E ":80|:443|:8080|:8082"
echo ""

echo "8️⃣ Cloudflare Environment Variables:"
docker exec traefik env | grep CF_
echo ""

echo "============================"
echo "Diagnostics Complete!"
EOF

chmod +x ~/diagnose-traefik.sh
~/diagnose-traefik.sh
