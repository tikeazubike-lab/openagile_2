#!/bin/bash
set -e

# Bridge Project Setup Script
# Creates thrive-tech-hub-learning with production-grade stack

PROJECT_NAME="thrive-tech-hub-learning"
BASE_DIR="/home/zubbyik/dev/obsidan_global/docker_compose_projects/openagile"
PROJECT_DIR="$BASE_DIR/$PROJECT_NAME"

echo "🚀 Setting up $PROJECT_NAME..."

# Create project directory
cd "$BASE_DIR"
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Project directory already exists. Removing..."
    rm -rf "$PROJECT_DIR"
fi

# Initialize Vite project
npm create vite@latest "$PROJECT_NAME" -- --template react-ts

cd "$PROJECT_DIR"

# Install core dependencies
echo "📦 Installing core dependencies..."
npm install

# Install React Router
echo "📦 Installing React Router..."
npm install react-router-dom

# Install TanStack Query
echo "📦 Installing TanStack Query..."
npm install @tanstack/react-query

# Install Tailwind CSS
echo "📦 Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Shadcn UI dependencies
echo "📦 Installing Shadcn UI dependencies..."
npm install class-variance-authority clsx tailwind-merge
npm install lucide-react

# Install Ghost Content API
echo "📦 Installing Ghost Content API..."
npm install @tryghost/content-api

# Install testing dependencies
echo "📦 Installing testing dependencies..."
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom

# Create directory structure
echo "📁 Creating project structure..."
mkdir -p src/{components/{ui,layout,features},pages,lib,hooks,types,test}
mkdir -p public/images

# Create Tailwind config
cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

export default {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config
EOF

# Create components.json for Shadcn
cat > components.json << 'EOF'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
EOF

# Install Tailwind animate plugin
npm install -D tailwindcss-animate

# Create .env.example
cat > .env.example << 'EOF'
# Ghost CMS Configuration
VITE_GHOST_API_URL=http://localhost:2368
VITE_GHOST_CONTENT_API_KEY=your_content_api_key_here

# Environment
VITE_ENV=development
EOF

# Create .gitignore additions
cat >> .gitignore << 'EOF'

# Environment variables
.env.local
.env.production

# OS
.DS_Store
Thumbs.db
EOF

echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "  cd $PROJECT_DIR"
echo "  npm run dev"
echo ""
echo "🎯 Phase 1 Learning Objectives:"
echo "  - React Router v6 routing"
echo "  - Tailwind CSS styling"
echo "  - Shadcn UI components"
echo "  - TypeScript patterns"
