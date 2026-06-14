#!/bin/bash
# Frappe/ERPNext Deployment Script
# Enhanced for CI/CD with health checks and error handling
# tutor_hub added 2026-04-10

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in CI/CD environment
CI_MODE=${CI:-false}

echo "================================"
echo "🚀 Frappe/ERPNext Deployment"
echo "================================"
echo ""

# Check for changes in dependencies (for conditional rebuilding)
REBUILD_FLAG=""
if [ -d ".git" ]; then
    if git diff HEAD@{1} --name-only 2>/dev/null | grep -qE 'Dockerfile|requirements|compose.yaml'; then
        log_info "Detected changes in dependencies, will rebuild images"
        REBUILD_FLAG="--build"
    else
        log_info "No dependency changes detected, using cached images"
    fi
fi

# Stop existing services gracefully
log_info "Stopping existing services..."
docker compose down 2>/dev/null || true

# Start services with all overrides
log_info "Starting Frappe stack with overrides..."
docker compose \
  -f compose.yaml \
  -f overrides/compose.databases.yaml \
  -f overrides/compose.external-traefik.yaml \
  -f overrides/compose.persist-apps.yaml \
  -f overrides/compose.frontend-custom-apps.yaml \
  up -d $REBUILD_FLAG

# Wait for services to initialize
log_info "Waiting for services to initialize (60s)..."
sleep 60

# ── tutor_hub React frontend build (runs on CI runner — Node.js available there) ──────────────
log_info "Building tutor_hub React frontend..."
cd apps/tutor_hub/frontend
npm ci --prefer-offline
npm run build   # outputs to ../tutor_hub/public/frontend/ per vite.config.ts
cd ../../..

# Update www/landing.html with hashed filenames from Vite manifest.
# Vite manifest: apps/tutor_hub/tutor_hub/public/frontend/.vite/manifest.json
# Placeholder tokens in landing.html: ASSET_HASH_JS and ASSET_HASH_CSS
MANIFEST_TUTOR="apps/tutor_hub/tutor_hub/public/frontend/.vite/manifest.json"
if [ ! -f "$MANIFEST_TUTOR" ]; then
  log_error "Vite manifest not found for tutor_hub — npm run build may have failed"
  exit 1
fi

TUTOR_JS_HASH=$(python3 -c "
import json
m = json.load(open('$MANIFEST_TUTOR'))
entry = m.get('src/main.tsx', {})
fname = entry.get('file', '')
print(fname.removeprefix('assets/main-').removesuffix('.js'))
")

TUTOR_CSS_HASH=$(python3 -c "
import json
m = json.load(open('$MANIFEST_TUTOR'))
entry = m.get('src/main.tsx', {})
css_files = entry.get('css', [])
if css_files:
    fname = css_files[0]
    print(fname.removeprefix('assets/main-').removesuffix('.css'))
else:
    print('')
")

if [ -z "$TUTOR_JS_HASH" ] || [ -z "$TUTOR_CSS_HASH" ]; then
  log_error "Could not parse tutor_hub asset hashes from Vite manifest:"
  cat "$MANIFEST_TUTOR"
  exit 1
fi

TUTOR_LANDING="apps/tutor_hub/tutor_hub/www/landing.html"
# Reset placeholders first (handles re-deploys with different hashes)
sed -i 's/main-[A-Za-z0-9_-]*\.js/main-ASSET_HASH_JS.js/g' "$TUTOR_LANDING"
sed -i 's/main-[A-Za-z0-9_-]*\.css/main-ASSET_HASH_CSS.css/g' "$TUTOR_LANDING"
# Substitute actual hashes
sed -i "s/ASSET_HASH_JS/${TUTOR_JS_HASH}/g" "$TUTOR_LANDING"
sed -i "s/ASSET_HASH_CSS/${TUTOR_CSS_HASH}/g" "$TUTOR_LANDING"
log_info "✓ tutor_hub landing.html updated: JS=${TUTOR_JS_HASH} CSS=${TUTOR_CSS_HASH}"
# ──────────────────────────────────────────────────────────────────────────────

# Build Frontend Assets (Edu Theme)
log_info "Building Edu Theme Frontend..."
if docker compose exec -T backend bash -c "cd apps/edu_theme/frontend && rm -rf node_modules package-lock.json && npm install && npm run build"; then
    log_info "✓ Frontend built successfully"
else
    log_error "✗ Frontend build failed"
    exit 1
fi

# Sync Frontend Assets (Copy Method)
log_info "Syncing Frontend Assets..."
# Get generated filenames - Vite outputs to apps/edu_theme/edu_theme/public/frontend
JS_FILE=$(docker compose exec -T backend ls apps/edu_theme/edu_theme/public/frontend/assets | grep -m1 .js)
CSS_FILE=$(docker compose exec -T backend ls apps/edu_theme/edu_theme/public/frontend/assets | grep -m1 .css)

if [ -n "$JS_FILE" ]; then
    log_info "Found assets: $JS_FILE"
    
    # Update landing.html
    docker compose exec -T backend sed -i "s|/assets/edu_theme/frontend/assets/main-.*\.js|/assets/edu_theme/frontend/assets/$JS_FILE|g" apps/edu_theme/edu_theme/www/landing.html
    docker compose exec -T backend sed -i "s|/assets/edu_theme/frontend/assets/main-.*\.css|/assets/edu_theme/frontend/assets/$CSS_FILE|g" apps/edu_theme/edu_theme/www/landing.html
    
    # Prepare sites/assets directory
    docker compose exec -T backend rm -rf /home/frappe/frappe-bench/sites/assets/edu_theme
    docker compose exec -T backend mkdir -p /home/frappe/frappe-bench/sites/assets/edu_theme
    
    # Copy files
    docker compose exec -T backend cp -r /home/frappe/frappe-bench/apps/edu_theme/edu_theme/public/. /home/frappe/frappe-bench/sites/assets/edu_theme/
    log_info "✓ Assets synced to sites/assets/edu_theme"
else
    log_warn "⚠ No built assets found in apps/edu_theme/edu_theme/public/frontend/assets/"
fi

# Install custom apps into Python environment
log_info "Installing custom apps into Python environment..."
APPS=("library_management" "education" "edu_theme" "tutor_hub")
for app in "${APPS[@]}"; do
    log_info "Installing $app..."
    if docker compose exec -T backend /home/frappe/frappe-bench/env/bin/pip install -e "apps/$app" > /dev/null 2>&1; then
        log_info "✓ $app installed successfully"
    else
        log_warn "⚠ $app installation had warnings (may already be installed)"
    fi
done



# Run Bench Build
log_info "Running bench build to generate assets..."
# usage of force flag to ensure overwrite of old assets
if docker compose exec -T backend bench build --force; then
    log_info "✓ Bench build complete"
else
    log_error "✗ Bench build failed"
    exit 1
fi

# Restart backend to load apps
log_info "Restarting backend to load apps..."
docker compose restart backend

# Wait for backend to be ready
log_info "Waiting for backend to stabilize (30s)..."
sleep 30

# Clear Cache
# Clear Cache
log_info "Clearing Bench Cache..."
SITES=("erpnext.zubbystudio.shop" "library.erpnext.zubbystudio.shop" "edu.erpnext.zubbystudio.shop" "tutor.erpnext.zubbystudio.shop")
for site in "${SITES[@]}"; do
    log_info "Clearing cache for $site..."
    docker compose exec -T backend bench --site "$site" clear-cache || log_warn "Failed to clear cache for $site"
done

# Health checks
echo ""
echo "================================"
echo "🏥 Running Health Checks"
echo "================================"

# Check container status
log_info "Checking container status..."
if docker compose ps | grep -q "Up"; then
    log_info "✓ Containers are running"
    docker compose ps
else
    log_error "✗ Some containers failed to start"
    docker compose ps
    exit 1
fi

echo ""

# Check installed apps
log_info "Verifying installed apps..."
if docker compose exec -T backend bench list-apps > /dev/null 2>&1; then
    log_info "✓ Bench is operational"
    docker compose exec -T backend bench list-apps
else
    log_error "✗ Bench command failed"
    exit 1
fi

echo ""

# Check databases
log_info "Checking databases..."
if docker compose exec -T db mysql -u root -padmin -e "SHOW DATABASES;" 2>&1 | grep -qE "main_erpnext|library_erpnext|education_db"; then
    log_info "✓ Site databases found"
else
    log_warn "⚠ Some site databases may be missing"
    log_warn "  Run ./recreate-sites.sh if needed"
fi

echo ""

# Test site accessibility (only if not in CI mode, as CI will do this separately)
if [ "$CI_MODE" != "true" ]; then
    log_info "Testing site accessibility..."
    
    # Give sites a moment to be ready
    sleep 10
    
    # Test main ERPNext site
    if curl -sSf -o /dev/null -w "%{http_code}" https://erpnext.zubbystudio.shop 2>/dev/null | grep -q "200\|302"; then
        log_info "✓ ERPNext site: OK"
    else
        log_warn "⚠ ERPNext site: Not responding (may need time to start)"
    fi
    
    # Test Library site
    if curl -sSf -o /dev/null -w "%{http_code}" https://library.erpnext.zubbystudio.shop 2>/dev/null | grep -q "200\|302"; then
        log_info "✓ Library site: OK"
    else
        log_warn "⚠ Library site: Not responding (may need time to start)"
    fi
    
    # Test Education site
    if curl -sSf -o /dev/null -w "%{http_code}" https://edu.erpnext.zubbystudio.shop 2>/dev/null | grep -q "200\|302"; then
        log_info "✓ Education site: OK"
    else
        log_warn "⚠ Education site: Not responding (may need time to start)"
    fi
    
    # Test edu landing page
    if curl -sSf -o /dev/null -w "%{http_code}" https://edu.erpnext.zubbystudio.shop/landing 2>/dev/null | grep -q "200"; then
        log_info "✓ Education landing page: OK"
    else
        log_warn "⚠ Education landing page: Not responding (may need time to start)"
    fi

    # Test tutor_hub landing page
    if curl -sSf --max-time 30 -o /dev/null -w "%{http_code}" https://tutor.erpnext.zubbystudio.shop/landing 2>/dev/null | grep -q "200"; then
        log_info "✓ TutorHub landing page: OK"
    else
        log_warn "⚠ TutorHub landing page: Not responding (site may not be created yet — run bench new-site)"
    fi
fi

echo ""
echo "================================"
echo "✅ Deployment Complete!"
echo "================================"
echo ""
echo "📍 Site URLs:"
echo "   • Main ERPNext: https://erpnext.zubbystudio.shop"
echo "   • Library:      https://library.erpnext.zubbystudio.shop"
echo "   • Education:    https://edu.erpnext.zubbystudio.shop"
echo "   • Landing Page: https://edu.erpnext.zubbystudio.shop/landing"
echo ""
echo "📝 Next Steps:"
echo "   1. If databases are missing: ./recreate-sites.sh"
echo "   2. View logs: docker compose logs -f backend"
echo "   3. Monitor: docker compose ps"
echo ""

# Exit with success
exit 0