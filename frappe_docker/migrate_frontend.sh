#!/bin/bash
set -e

# Configuration
APP_NAME="edu_theme"
TARGET_DIR="apps/$APP_NAME/frontend"
SOURCE_TEMPLATE="new_vue_website_for_reference2"
PUBLIC_OUT_DIR="../$APP_NAME/public/frontend"

echo ">>> Starting Frontend Migration to v0.2.0 (TypeScript/Shadcn)..."

# 1. Backup Existing Frontend
if [ -d "$TARGET_DIR" ]; then
    echo ">>> Backing up existing frontend to ${TARGET_DIR}_legacy..."
    rm -rf "${TARGET_DIR}_legacy"
    mv "$TARGET_DIR" "${TARGET_DIR}_legacy"
fi

# 2. Copy New Template
echo ">>> Copying new template files..."
mkdir -p "$TARGET_DIR"
cp -r "$SOURCE_TEMPLATE"/* "$TARGET_DIR/"
cp "$SOURCE_TEMPLATE"/.gitignore "$TARGET_DIR/" 2>/dev/null || true

# 3. Configure Vite for Frappe Integration
# We need to ensure the build output goes to the Frappe app's public folder
# and that we generate a manifest.
echo ">>> Configuring vite.config.ts for Frappe..."
cat > "$TARGET_DIR/vite.config.ts" <<EOF
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8080
  },
  build: {
    outDir: path.resolve(__dirname, '$PUBLIC_OUT_DIR'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.ts'), // Changed to .ts
    },
  },
})
EOF

# Ensure main entry point matches Vite config (src/main.ts vs src/main.js)
if [ -f "$TARGET_DIR/src/main.js" ]; then
    mv "$TARGET_DIR/src/main.js" "$TARGET_DIR/src/main.ts"
fi

# 4. Build Process (Inside Container)
echo ">>> Building Frontend inside backend container..."
# We use the container to ensure node/npm environment is consistent
docker compose exec backend bash -c "cd /home/frappe/frappe-bench/apps/$APP_NAME/frontend && npm install && npm run build"

# 5. Asset Deployment (The Fix)
# Automatically detect the new hashes and update landing.html
echo ">>> Deploying Assets to Site Volume..."

MANIFEST_FILE="apps/$APP_NAME/$APP_NAME/public/frontend/.vite/manifest.json"

# Python script to parse manifest and extract filenames
# We run this on the host to get variables for the sed command
if [ -f "$MANIFEST_FILE" ]; then
    # Extract CSS and JS filenames using grep/sed (simple parsing)
    # Looking for: "file": "assets/index-CX...js"
    # Note: The new template likely outputs 'index' or 'main' depending on rollup input.
    
    # Let's verify the actual files generated
    JS_FILE=$(ls apps/$APP_NAME/$APP_NAME/public/frontend/assets/*.js | head -n 1 | xargs basename)
    CSS_FILE=$(ls apps/$APP_NAME/$APP_NAME/public/frontend/assets/*.css | head -n 1 | xargs basename)
    
    echo "    Detected JS: $JS_FILE"
    echo "    Detected CSS: $CSS_FILE"
    
    LANDING_PAGE="apps/$APP_NAME/$APP_NAME/www/landing.html"
    
    # Update landing.html
    # We assume standard Frappe /assets/ path structure
    sed -i "s|/assets/$APP_NAME/frontend/assets/.*\.js|/assets/$APP_NAME/frontend/assets/$JS_FILE|g" "$LANDING_PAGE"
    sed -i "s|/assets/$APP_NAME/frontend/assets/.*\.css|/assets/$APP_NAME/frontend/assets/$CSS_FILE|g" "$LANDING_PAGE"
    
    # THE CRITICAL COPY STEP (Fixes 404s)
    echo "    Copying files to sites/assets/ volume..."
    # Ensure destination exists
    sudo mkdir -p sites/assets/$APP_NAME
    sudo cp -r apps/$APP_NAME/$APP_NAME/public/* sites/assets/$APP_NAME/
    sudo chown -R 1000:1000 sites/assets/$APP_NAME
    
    echo ">>> Clearing Cache..."
    docker compose exec backend bench --site edu.erpnext.zubbystudio.shop clear-cache
    
    echo "✅ Migration Complete!"
    echo "   Verify at: https://edu.erpnext.zubbystudio.shop/landing"
else
    echo "❌ Error: Build manifest not found. Build may have failed."
    exit 1
fi
