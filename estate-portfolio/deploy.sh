#!/bin/bash
# Estate Portfolio Manager - Server Deployment Script
# This script is executed on the OpenAgile server during CI/CD deployment

set -e  # Exit on any error

PROJECT_DIR="/home/zubbyik/openagile/egbuna_estate_account_streamlight/estate-portfolio"

echo "================================"
echo "Estate Portfolio Deployment"
echo "================================"
echo ""

# Navigate to project directory
cd "$PROJECT_DIR" || exit 1

# Pull latest changes
echo "📦 Pulling latest changes from GitHub..."
git pull origin main

# Check if Dockerfile or requirements changed
if git diff HEAD@{1} --name-only | grep -qE 'Dockerfile|requirements.txt'; then
    echo "🔨 Detected changes in dependencies, rebuilding images..."
    REBUILD_FLAG="--build"
else
    echo "♻️  No dependency changes, using cached images..."
    REBUILD_FLAG=""
fi

# Restart containers
echo "🚀 Restarting containers..."
docker compose up -d $REBUILD_FLAG

# Wait for services to be ready
echo "⏳ Waiting for services to stabilize..."
sleep 10

# Health check
echo "🏥 Running health check..."
if docker compose ps | grep -q "Up"; then
    echo "✅ Containers are running"
    docker compose ps
else
    echo "❌ Some containers failed to start"
    docker compose ps
    exit 1
fi

echo ""
echo "================================"
echo "✨ Deployment Complete!"
echo "================================"
echo "Dashboard: https://estate.zubbystudio.shop"
echo ""
