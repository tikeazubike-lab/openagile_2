#!/bin/bash
# Sync Assets to Frontend - Workaround for bind mount issue
# Run this after every `bench build` or asset change

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Syncing assets from backend to frontend...${NC}"

# Method 1: Use docker cp (works across containers)
echo "1. Copying edu_theme assets..."
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/edu_theme /tmp/
docker cp /tmp/edu_theme frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
rm -rf /tmp/edu_theme

echo "2. Copying education assets..."
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/education /tmp/
docker cp /tmp/education frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
rm -rf /tmp/education

echo "3. Copying library_management assets..."
docker cp frappe_docker-backend-1:/home/frappe/frappe-bench/sites/assets/library_management /tmp/
docker cp /tmp/library_management frappe_docker-frontend-1:/home/frappe/frappe-bench/sites/assets/
rm -rf /tmp/library_management

# Fix permissions in frontend
docker compose exec frontend chown -R frappe:frappe \
    /home/frappe/frappe-bench/sites/assets/edu_theme \
    /home/frappe/frappe-bench/sites/assets/education \
    /home/frappe/frappe-bench/sites/assets/library_management 2>/dev/null || true

echo -e "${GREEN}✓ Assets synced${NC}"

# Verify
echo "Verifying frontend can see assets..."
docker compose exec frontend ls -la /home/frappe/frappe-bench/sites/assets/ | grep -E "edu_theme|education|library"

# Test HTTP
echo "Testing HTTP access..."
curl -I https://edu.erpnext.zubbystudio.shop/assets/edu_theme/frontend/assets/index.js

echo -e "${GREEN}Done!${NC}"
