#!/bin/bash
set -e

# Configuration
APP_NAME="edu_theme"
FRONTEND_DIR="apps/$APP_NAME/frontend"
APP_PUBLIC_DIR="apps/$APP_NAME/$APP_NAME/public"
WWW_DIR="apps/$APP_NAME/$APP_NAME/www"
CONTAINER_USER="frappe" # Default user in the container

echo ">>> Starting Frontend Setup for $APP_NAME..."

# Verification Checks
if [ ! -d "apps/$APP_NAME" ]; then
    echo "❌ Error: App directory 'apps/$APP_NAME' not found."
    echo "   Please run: docker compose exec backend bench new-app $APP_NAME"
    exit 1
fi

echo "✅ App '$APP_NAME' found."

# Create Frontend Directory Structure (On Host to ensure persistence)
echo ">>> Creating frontend directory structure..."
mkdir -p "$FRONTEND_DIR/src/components"
mkdir -p "$FRONTEND_DIR/src/assets"

# Create Configuration Files

# --- package.json ---
cat > "$FRONTEND_DIR/package.json" <<EOF
{
  "name": "edu-theme-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "lucide-vue-next": "^0.344.0" 
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "vite": "^5.2.0"
  }
}
EOF

# --- vite.config.js ---
cat > "$FRONTEND_DIR/vite.config.js" <<EOF
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: path.resolve(__dirname, '../$APP_NAME/public/frontend'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'src/main.js'),
    },
  },
})
EOF

# --- tailwind.config.js ---
cat > "$FRONTEND_DIR/tailwind.config.js" <<EOF
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': '#1e3a8a',
        'brand-yellow': '#fbbf24',
      }
    },
  },
  plugins: [],
}
EOF

# --- postcss.config.js ---
cat > "$FRONTEND_DIR/postcss.config.js" <<EOF
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# --- style.css (Tailwind Directives) ---
cat > "$FRONTEND_DIR/src/style.css" <<EOF
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF

# --- src/main.js ---
cat > "$FRONTEND_DIR/src/main.js" <<EOF
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')
EOF

# --- src/App.vue (Base Layout) ---
cat > "$FRONTEND_DIR/src/App.vue" <<EOF
<script setup>
import Navbar from './components/Navbar.vue'
import Hero from './components/Hero.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col font-sans text-slate-900">
    <Navbar />
    <main class="flex-grow">
      <Hero />
    </main>
    <Footer />
  </div>
</template>
EOF

# --- src/components/Navbar.vue ---
cat > "$FRONTEND_DIR/src/components/Navbar.vue" <<EOF
<template>
  <nav class="bg-white shadow-sm py-4 sticky top-0 z-50">
    <div class="container mx-auto px-6 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="bg-brand-yellow text-brand-blue font-bold px-3 py-1 rounded">EDUMA</div>
      </div>
      <div class="hidden md:flex space-x-8 text-gray-600 font-medium text-sm uppercase tracking-wide">
        <a href="#" class="hover:text-brand-blue transition">Home</a>
        <a href="#" class="hover:text-brand-blue transition">Courses</a>
        <a href="#" class="hover:text-brand-blue transition">Admissions</a>
        <a href="#" class="hover:text-brand-blue transition">News</a>
        <a href="#" class="hover:text-brand-blue transition">Contact</a>
      </div>
      <div class="flex items-center gap-4 text-sm font-semibold">
        <a href="/login" class="text-gray-600 hover:text-brand-blue transition">LOGIN</a>
        <a href="/app" class="bg-brand-blue text-white px-5 py-2 rounded hover:bg-blue-800 transition shadow-lg shadow-blue-900/20">
          DESK
        </a>
      </div>
    </div>
  </nav>
</template>
EOF

# --- src/components/Hero.vue ---
cat > "$FRONTEND_DIR/src/components/Hero.vue" <<EOF
<template>
  <section class="bg-brand-blue text-white py-24 relative overflow-hidden">
    <!-- Decorative background elements -->
    <div class="absolute top-0 right-0 w-1/3 h-full bg-blue-800/20 -skew-x-12 transform translate-x-1/2"></div>
    
    <div class="container mx-auto px-6 flex flex-col md:flex-row items-center">
      <div class="md:w-3/5 z-10">
        <span class="text-brand-yellow font-bold tracking-[0.2em] uppercase text-xs mb-4 block">Welcome to the future of learning</span>
        <h1 class="text-5xl md:text-7xl font-extrabold leading-[1.1] mb-8">
          Empowering Minds <br/> Shaping <span class="text-brand-yellow underline decoration-wavy underline-offset-8">Tomorrow</span>
        </h1>
        <p class="text-blue-100 text-lg mb-10 max-w-lg leading-relaxed">
          Access world-class education portals, manage your curriculum, and track your progress through our unified digital campus.
        </p>
        <div class="flex gap-4">
          <button class="bg-brand-yellow text-brand-blue font-bold py-4 px-10 rounded shadow-xl hover:scale-105 transition active:scale-95">
            GET STARTED
          </button>
          <button class="border-2 border-white/30 hover:border-white text-white font-bold py-4 px-10 rounded transition">
            LEARN MORE
          </button>
        </div>
      </div>
      
      <div class="md:w-2/5 mt-16 md:mt-0 relative">
        <div class="bg-white/5 p-4 rounded-3xl backdrop-blur-md border border-white/10 shadow-2xl overflow-hidden aspect-square flex items-center justify-center">
           <div class="text-white/20 text-center">
             <div class="text-8xl mb-4">🎓</div>
             <span class="text-sm font-medium tracking-widest uppercase">Portal Preview</span>
           </div>
        </div>
        <!-- Floaters -->
        <div class="absolute -top-6 -left-6 bg-brand-yellow p-4 rounded-2xl shadow-lg animate-bounce">
          ✨
        </div>
      </div>
    </div>
  </section>
</template>
EOF

# --- src/components/Footer.vue ---
cat > "$FRONTEND_DIR/src/components/Footer.vue" <<EOF
<template>
  <footer class="bg-slate-900 text-slate-400 pt-16 pb-8">
    <div class="container mx-auto px-6">
      <div class="grid md:grid-cols-4 gap-12 mb-12">
        <div class="col-span-2">
          <div class="text-white font-bold text-2xl mb-6">EDUMA</div>
          <p class="max-w-sm leading-relaxed">
            The standard for modern educational institutions. Integrated with ERPNext for seamless management of students, faculty, and assets.
          </p>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6">Links</h4>
          <ul class="space-y-4 text-sm">
            <li><a href="#" class="hover:text-white transition">About Us</a></li>
            <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
            <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-bold mb-6">Contact</h4>
          <ul class="space-y-4 text-sm">
            <li>info@zubbystudio.shop</li>
            <li>+234 800 EDUMA</li>
          </ul>
        </div>
      </div>
      <div class="border-t border-slate-800 pt-8 text-center text-xs tracking-widest uppercase">
        <p>&copy; {{ new Date().getFullYear() }} Eduma. Built on Frappe Framework.</p>
      </div>
    </div>
  </footer>
</template>
EOF

# Create Frappe Web Page (Jinja Entry Point)
mkdir -p "$WWW_DIR"
cat > "$WWW_DIR/landing.html" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Education Portal</title>
    <script>
        window.csrf_token = "{{ csrf_token }}";
    </script>
    <script type="module" src="/assets/$APP_NAME/frontend/main.js"></script>
    <link rel="stylesheet" href="/assets/$APP_NAME/frontend/style.css">
</head>
<body class="m-0 p-0 overflow-x-hidden">
    <div id="app"></div>
</body>
</html>
EOF

# Install Dependencies and Build (Inside Container)
echo ">>> Installing dependencies and building assets inside the container..."
docker compose exec backend bash -c "cd /home/frappe/frappe-bench/apps/$APP_NAME/frontend && npm install && npm run build"

echo ">>> Setup Complete! ✅"
echo "    - Frontend source: apps/$APP_NAME/frontend"
echo "    - Build output:    apps/$APP_NAME/$APP_NAME/public/frontend"
echo "    - Landing Page:    $WWW_DIR/landing.html"
echo ""
echo "👉 To view the page, go to your site URL /landing"
echo "   To make it the homepage, set the 'Home Page' in 'Website Settings' to 'landing'."

