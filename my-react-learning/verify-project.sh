#!/bin/bash

echo "🔍 Verifying thrive-tech-hub-learning project..."
echo ""

PROJECT_DIR="/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub-learning"

cd "$PROJECT_DIR"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Dependencies NOT installed"
    exit 1
fi

# Check key source files
files=(
    "src/App.tsx"
    "src/main.tsx"
    "src/pages/Home.tsx"
    "src/components/layout/Layout.tsx"
    "tailwind.config.ts"
    "vite.config.ts"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🎉 Project verification complete!"
echo ""
echo "📚 To start learning:"
echo "  cd $PROJECT_DIR"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:5173"
