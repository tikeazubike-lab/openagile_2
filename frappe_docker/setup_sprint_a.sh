#!/bin/bash
# Sprint A - Session 1: Configure Frappe for Learning
# Run these commands sequentially and verify each step

set -e  # Exit on any error

echo "======================================"
echo "Sprint A Setup: Learning Environment"
echo "======================================"
echo ""

# Step 1: Create a proper named site
echo "Step 1: Creating 'learning.local' site..."
docker exec -it frappe_docker-backend-1 bench new-site learning.local \
  --admin-password admin \
  --db-name learning \
  --verbose

# Verify site creation
echo ""
echo "✅ Verifying site creation..."
docker exec -it frappe_docker-backend-1 ls sites/learning.local
echo ""

# Step 2: Install ERPNext on the new site
echo "Step 2: Installing ERPNext on learning.local..."
docker exec -it frappe_docker-backend-1 bench --site learning.local install-app erpnext

echo ""
echo "✅ ERPNext installed"
echo ""

# Step 3: Enable developer mode
echo "Step 3: Enabling developer mode..."
docker exec -it frappe_docker-backend-1 bench --site learning.local set-config developer_mode 1

# Step 4: Clear cache
echo "Step 4: Clearing cache..."
docker exec -it frappe_docker-backend-1 bench --site learning.local clear-cache

# Step 5: Restart bench
echo "Step 5: Restarting services..."
docker compose restart backend frontend

# Wait for restart
echo "Waiting 10 seconds for services to stabilize..."
sleep 10

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Verification Commands:"
echo "----------------------"
echo "1. Check developer mode:"
echo "   docker exec -it frappe_docker-backend-1 bench --site learning.local console"
echo "   Then run: frappe.conf.developer_mode"
echo "   Should return: 1"
echo ""
echo "2. List apps on site:"
echo "   docker exec -it frappe_docker-backend-1 bench --site learning.local list-apps"
echo ""
echo "3. Access site:"
echo "   http://185.216.177.250:9980"
echo "   Login: Administrator / admin"
echo ""
echo "Next Steps:"
echo "-----------"
echo "- Visit the site and login"
echo "- Verify ERPNext desk loads"
echo "- Ready to create first app!"
echo ""
