#!/bin/bash
set -e

cd ~/openagile/frappe_docker

if [ -z "$1" ]; then
    echo "Usage: ./scripts/install-custom-app.sh <app-name> <site-name>"
    echo "Example: ./scripts/install-custom-app.sh library_management library.erpnext.yourdomain.com"
    exit 1
fi

APP_NAME=$1
SITE_NAME=${2:-"library.erpnext.yourdomain.com"}

echo "📦 Installing custom app: $APP_NAME to site: $SITE_NAME"
echo ""

docker compose exec backend bash << BACKEND_SCRIPT
cd /home/frappe/frappe-bench

# Check if app exists
if [ ! -d "apps/$APP_NAME" ]; then
    echo "❌ App directory not found: apps/$APP_NAME"
    echo "   Create it first with: bench new-app $APP_NAME"
    exit 1
fi

echo "✅ App directory found"
echo ""

# Critical: Run setup requirements (replaces deprecated bench link-app)
echo "🔗 Setting up app requirements..."
bench setup requirements

# Build the app
echo "🎨 Building app assets..."
bench build --force

# Install app to site
echo "📥 Installing $APP_NAME to $SITE_NAME..."
bench --site $SITE_NAME install-app $APP_NAME

# MANDATORY: Aggressive cache clearing
echo "🧹 Clearing all caches..."
bench --site $SITE_NAME clear-cache
bench --site $SITE_NAME clear-website-cache

# Verify installation
echo ""
echo "✅ Verification:"
bench --site $SITE_NAME list-apps

echo ""
echo "✅ App installed successfully!"
echo "   Remember to clear your browser cache (Ctrl+Shift+R)"

BACKEND_SCRIPT

echo ""
echo "🔄 Restarting services..."
docker compose restart

echo "⏳ Waiting 30 seconds..."
sleep 30

echo ""
echo "✅ Installation complete!"
echo "   Access: https://$SITE_NAME"
