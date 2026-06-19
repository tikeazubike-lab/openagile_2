#!/bin/bash
# EPM v3 — Test Drive Deployment Script
# Executed directly on Netcup VPS
set -e

PROJECT_DIR="/home/zubbyik/openagile_2/egbuna_estate_account_streamlight/estate-portfolio"

echo "========================================"
echo "EPM v3 — Test Drive Deployment"
echo "========================================"
echo ""

cd "$PROJECT_DIR" || exit 1

echo "📦 Pulling latest changes from GitHub..."
git pull origin main

if git diff HEAD@{1} --name-only | grep -qE 'Dockerfile.v3|requirements.txt'; then
    echo "🔨 Detected changes in dependencies, rebuilding images..."
    docker compose -f docker-compose.v3.yml up -d --build epm_v3
else
    echo "♻️  No dependency changes, restarting..."
    docker compose -f docker-compose.v3.yml up -d
fi

echo "⏳ Waiting for services to stabilize..."
sleep 10

echo "🏥 Running health check..."
if docker compose -f docker-compose.v3.yml ps | grep -q "Up"; then
    echo "✅ Containers are running"
    docker compose -f docker-compose.v3.yml ps
else
    echo "❌ Some containers failed to start"
    docker compose -f docker-compose.v3.yml ps
    exit 1
fi

echo ""
echo "========================================"
echo "✨ Deployment Complete!"
echo "========================================"
echo "Dashboard: https://testdrive.epm.zubbystudio.shop"
echo ""
