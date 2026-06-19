#!/bin/bash
set -e

APP_NAME="edu_theme"
JS_FILE="main-CeshOzD5.js"
CSS_FILE="main-uSrhrlA-.css"
 
echo ">>> Deploying Edu Theme Assets (COPY METHOD)..."

# 1. Ensure landing.html has the correct hashes
LANDING_PAGE="apps/$APP_NAME/$APP_NAME/www/landing.html"
sed -i "s|/assets/$APP_NAME/frontend/assets/main-.*\.js|/assets/$APP_NAME/frontend/assets/$JS_FILE|g" "$LANDING_PAGE"
sed -i "s|/assets/$APP_NAME/frontend/assets/main-.*\.css|/assets/$APP_NAME/frontend/assets/$CSS_FILE|g" "$LANDING_PAGE"

# 2. Fix permissions on the source (just in case)
docker compose exec --user root backend chown -R 1000:1000 /home/frappe/frappe-bench/apps/$APP_NAME
 
# 3. Remove the symlink and Create Physical Directory
# We must remove the symlink first, otherwise 'mkdir' fails
docker compose exec backend rm -f /home/frappe/frappe-bench/sites/assets/$APP_NAME

# Create the directory structure in 'sites/assets'
docker compose exec backend mkdir -p /home/frappe/frappe-bench/sites/assets/$APP_NAME

# 4. Copy the files
echo ">>> Copying files..."
docker compose exec backend cp -r /home/frappe/frappe-bench/apps/$APP_NAME/$APP_NAME/public/. /home/frappe/frappe-bench/sites/assets/$APP_NAME/
 
# 5. Verify Nginx can see it now
echo ">>> Verifying Nginx access..."
docker compose exec frontend ls -R /home/frappe/frappe-bench/sites/assets/$APP_NAME

# 6. Clear Cache
docker compose exec backend bench --site edu.erpnext.zubbystudio.shop clear-cache

echo ">>> Deployment Complete! ✅"
