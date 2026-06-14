#!/bin/bash
# Force Fix Symlink Issue - Recreate Frontend Container
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Investigating symlink issue...${NC}"

# Check symlinks on host
echo -e "${YELLOW}1. Symlinks on HOST filesystem:${NC}"
ls -la ./sites/assets/ | grep -E "edu_theme|education|library"

# Check backend view
echo -e "${YELLOW}2. Backend container view:${NC}"
docker compose exec backend ls -la /home/frappe/frappe-bench/sites/assets/ | grep -E "edu_theme|education|library"

# Check frontend view
echo -e "${YELLOW}3. Frontend container view (BEFORE fix):${NC}"
docker compose exec frontend ls -la /home/frappe/frappe-bench/sites/assets/ | grep -E "edu_theme|education|library" || echo "NOT VISIBLE IN FRONTEND"

echo
echo -e "${YELLOW}Issue confirmed: Frontend container can't see symlinks${NC}"
echo

# Solution 1: Stop and recreate frontend container (forces volume remount)
echo -e "${YELLOW}Attempting Fix 1: Recreate frontend container...${NC}"
docker compose stop frontend
docker compose rm -f frontend
docker compose up -d frontend

sleep 5

echo -e "${YELLOW}Checking if Fix 1 worked...${NC}"
docker compose exec frontend ls -la /home/frappe/frappe-bench/sites/assets/ | grep -E "edu_theme|education|library" && {
    echo -e "${GREEN}✓ Fix 1 worked! Symlinks now visible${NC}"
    exit 0
} || {
    echo -e "${RED}✗ Fix 1 didn't work${NC}"
}

# Solution 2: Copy assets physically instead of using symlinks
echo
echo -e "${YELLOW}Attempting Fix 2: Physical copy instead of symlinks...${NC}"
echo "This creates actual directories instead of symlinks"

# Remove symlinks and copy actual files
docker compose exec backend bash -c '
    cd /home/frappe/frappe-bench/sites/assets
    
    # Remove symlinks
    rm -f edu_theme education library_management
    
    # Copy actual directories
    cp -r /home/frappe/frappe-bench/apps/edu_theme/edu_theme/public edu_theme
    cp -r /home/frappe/frappe-bench/apps/education/education/public education
    cp -r /home/frappe/frappe-bench/apps/library_management/library_management/public library_management
    
    # Fix permissions
    chown -R frappe:frappe edu_theme education library_management
'

echo -e "${YELLOW}Restarting frontend...${NC}"
docker compose restart frontend
sleep 5

echo -e "${YELLOW}Checking if Fix 2 worked...${NC}"
docker compose exec frontend ls -la /home/frappe/frappe-bench/sites/assets/ | grep -E "edu_theme|education|library" && {
    echo -e "${GREEN}✓ Fix 2 worked! Assets now visible${NC}"
    echo
    echo -e "${YELLOW}Testing HTTP access...${NC}"
    curl -I https://edu.erpnext.zubbystudio.shop/assets/edu_theme/frontend/assets/index.js
    exit 0
} || {
    echo -e "${RED}✗ Fix 2 didn't work either${NC}"
}

# Solution 3: Modify docker-compose to use volumes instead of bind mount for sites
echo
echo -e "${YELLOW}Fix 3 required: Change from bind mount to named volume${NC}"
echo "This is a more significant change. Do you want to proceed? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Backing up current setup...${NC}"
    cp compose.yaml compose.yaml.backup.$(date +%Y%m%d_%H%M%S)
    
    echo -e "${YELLOW}This will require manual docker-compose.yml edit${NC}"
    echo "Change from:"
    echo "  - ./sites:/home/frappe/frappe-bench/sites"
    echo "To:"
    echo "  - sites:/home/frappe/frappe-bench/sites"
    echo
    echo "Then run: docker compose down && docker compose up -d"
else
    echo "Skipping Fix 3"
fi

echo
echo -e "${RED}=== Issue Still Unresolved ===${NC}"
echo "The problem is Docker bind mounts not propagating symlinks correctly"
echo
echo "Recommended solution: Use Fix 2 (physical copy) as a workaround"
echo "For each deployment, you'll need to copy assets instead of symlinking"
