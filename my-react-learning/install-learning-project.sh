#!/bin/bash
set -e

PROJECT_DIR="/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile/thrive-tech-hub-learning"

echo "🚀 Installing dependencies for thrive-tech-hub-learning..."

cd "$PROJECT_DIR"

# Install dependencies
npm install

echo "✅ Installation complete!"
echo ""
echo "📚 To start the development server:"
echo "  cd $PROJECT_DIR"
echo "  npm run dev"
echo ""
echo "🎯 Phase 1 Complete - Foundation Setup"
echo "Next: Explore the code and start learning!"
