#!/bin/bash
# Define the filenames based on your 'ls' output
JS_FILE="main-CeshOzD5.js"
CSS_FILE="main-uSrhrlA-.css"
LANDING_PAGE="apps/edu_theme/edu_theme/www/landing.html"
 
echo ">>> Updating $LANDING_PAGE with build hashes..."
 
# Use sed to replace the placeholder paths with the actual hashed paths
# We add /assets/ to the path because Vite puts built files in an assets subfolder
sed -i "s|/assets/edu_theme/frontend/main.js|/assets/edu_theme/frontend/assets/$JS_FILE|g" "$LANDING_PAGE"
sed -i "s|/assets/edu_theme/frontend/style.css|/assets/edu_theme/frontend/assets/$CSS_FILE|g" "$LANDING_PAGE"

echo ">>> Done! Please check https://edu.erpnext.zubbystudio.shop/landing"

