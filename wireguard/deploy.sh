#!/bin/bash
set -e

echo "Deploying WireGuard VPN (wg-easy)..."

# Ensure data directory exists
mkdir -p data

# Check if UFW is active and add rule if needed
if command -v ufw > /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        echo "Ensuring UFW allows port 51820/udp for WireGuard..."
        sudo ufw allow 51820/udp comment 'WireGuard VPN'
    fi
fi

# Pull latest image and start container
docker compose pull
docker compose up -d --remove-orphans

echo "WireGuard deployed successfully!"
echo "Check logs with: docker compose logs -f"
echo "Access the Web UI at: https://vpn.zubbystudio.shop"
