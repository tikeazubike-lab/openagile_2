#!/bin/bash
# Comprehensive Diagnostic for Frappe Custom App Assets
# This will help identify the exact cause of 404 errors

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Frappe Docker Assets Diagnostic ===${NC}"
echo

# Function to check and report
check() {
    local description=$1
    local command=$2
    
    echo -e "${YELLOW}▶ $description${NC}"
    eval "$command"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    echo
}

# 1. Container Status
check "Container Status" "docker compose ps"

# 2. Installed Apps
echo -e "${YELLOW}▶ Installed Apps in sites/apps.txt${NC}"
docker compose exec backend cat /home/frappe/frappe-bench/sites/apps.txt
echo

# 3. Apps Directory Structure
echo -e "${YELLOW}▶ Apps Directory in Backend Container${NC}"
docker compose exec backend ls -la /home/frappe/frappe-bench/apps/
echo

# 4. Sites Directory Structure
echo -e "${YELLOW}▶ Sites Directory Structure${NC}"
docker compose exec backend ls -la /home/frappe/frappe-bench/sites/
echo

# 5. Assets Directory in Backend
echo -e "${YELLOW}▶ Assets in Backend Container${NC}"
docker compose exec backend ls -la /home/frappe/frappe-bench/sites/assets/ | head -20
echo

# 6. Check for Custom App Assets
echo -e "${YELLOW}▶ Custom App Assets (library_management, education, edu_theme)${NC}"
for app in library_management education edu_theme; do
    echo "Checking $app:"
    docker compose exec backend ls -la /home/frappe/frappe-bench/sites/assets/$app/ 2>/dev/null || echo "  Not found or empty"
done
echo

# 7. Frontend Container Assets
echo -e "${YELLOW}▶ Frontend Container Assets Path${NC}"
docker compose exec frontend ls -la /home/frappe/frappe-bench/sites/assets/ | head -20 || {
    echo -e "${RED}Frontend container cannot access assets!${NC}"
    echo "This is the problem - frontend uses different path or volume mount issue"
}
echo

# 8. Nginx Configuration
echo -e "${YELLOW}▶ Nginx Configuration (assets location)${NC}"
docker compose exec frontend cat /etc/nginx/conf.d/frappe.conf 2>/dev/null || \
docker compose exec frontend cat /etc/nginx/nginx.conf | grep -A 10 "location /assets"
echo

# 9. Volume Mounts
echo -e "${YELLOW}▶ Volume Mounts from docker-compose.yml${NC}"
echo "Backend volumes:"
docker compose config | grep -A 5 "backend:" | grep "volumes:" -A 3
echo
echo "Frontend volumes:"
docker compose config | grep -A 5 "frontend:" | grep "volumes:" -A 3
echo

# 10. Check if apps are in bind mount or volume
echo -e "${YELLOW}▶ Checking if apps are bind-mounted${NC}"
docker compose config | grep "./apps" && {
    echo -e "${GREEN}Apps are bind-mounted from host${NC}"
    APPS_MOUNTED=true
} || {
    echo -e "${YELLOW}Apps are NOT bind-mounted (baked into image)${NC}"
    APPS_MOUNTED=false
}
echo

# 11. Check for symlinks
echo -e "${YELLOW}▶ Checking for Symlinks in Assets${NC}"
docker compose exec backend find /home/frappe/frappe-bench/sites/assets/ -type l -ls 2>/dev/null | head -10 || echo "No symlinks found"
echo

# 12. Test actual asset access
echo -e "${YELLOW}▶ Testing Asset Accessibility from Frontend${NC}"
echo "Testing if frontend can read a known asset file:"
docker compose exec frontend test -f /home/frappe/frappe-bench/sites/assets/frappe/dist/css/desk.bundle.css && \
    echo -e "${GREEN}✓ Frontend can access Frappe core assets${NC}" || \
    echo -e "${RED}✗ Frontend CANNOT access assets - Volume issue!${NC}"
echo

# 13. Check from web
echo -e "${YELLOW}▶ Testing HTTP Access${NC}"
echo "Testing Frappe core asset:"
curl -s -o /dev/null -w "Status: %{http_code}\n" https://edu.erpnext.zubbystudio.shop/assets/frappe/dist/css/desk.bundle.css 2>/dev/null || echo "Could not reach server"
echo

# 14. Recent Nginx Errors
echo -e "${YELLOW}▶ Recent Nginx 404 Errors${NC}"
docker compose logs --tail=50 frontend 2>/dev/null | grep "404" | tail -10 || echo "No recent 404 errors"
echo

# 15. File permissions
echo -e "${YELLOW}▶ Assets Directory Permissions${NC}"
docker compose exec backend ls -ld /home/frappe/frappe-bench/sites/assets/
echo

# Generate Report
echo
echo -e "${BLUE}=== Diagnostic Summary ===${NC}"
echo
echo -e "${YELLOW}Key Findings:${NC}"

# Check 1: Are custom apps installed?
apps_count=$(docker compose exec backend cat /home/frappe/frappe-bench/sites/apps.txt 2>/dev/null | wc -l)
echo "1. Installed apps: $apps_count"

# Check 2: Do asset directories exist?
if docker compose exec backend test -d /home/frappe/frappe-bench/sites/assets/library_management 2>/dev/null; then
    echo "2. library_management assets: ✓ Exist"
else
    echo "2. library_management assets: ✗ Missing"
fi

# Check 3: Can frontend access assets?
if docker compose exec frontend test -d /home/frappe/frappe-bench/sites/assets 2>/dev/null; then
    echo "3. Frontend assets access: ✓ OK"
else
    echo "3. Frontend assets access: ✗ FAILED (Volume mount issue)"
fi

# Check 4: Apps bind mount
if [ "$APPS_MOUNTED" = true ]; then
    echo "4. Apps directory: ✓ Bind-mounted (development setup)"
else
    echo "4. Apps directory: ✗ Not mounted (production setup)"
fi

echo
echo -e "${BLUE}=== Next Steps ===${NC}"
echo "1. Check the output above for any RED ✗ marks"
echo "2. If frontend cannot access assets, it's a volume mount issue"
echo "3. If assets don't exist, run: docker compose exec backend bench build"
echo "4. Share this output if you need help debugging"
