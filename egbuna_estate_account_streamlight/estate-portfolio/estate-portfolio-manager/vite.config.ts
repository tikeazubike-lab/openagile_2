// EPM Phase 2 — Plain Vite SPA config.
// Replaces TanStack Start / Cloudflare Workers scaffold from Lovable.dev.
// TanStack Router file-based routing is kept (client-side only).
// Build output: dist/ → copied into backend/app/static/ by Dockerfile.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    // Route code-splitting — must come BEFORE react()
    TanStackRouterVite({
      target: "react",
      autoCodeSplitting: true,
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/routeTree.gen.ts",
    }),
    tailwindcss(),
    react(),
    tsconfigPaths(),
  ],

  build: {
    outDir: "dist",
    // Emit relative asset paths so FastAPI StaticFiles can serve them
    // regardless of the path prefix Traefik uses.
    assetsDir: "assets",
  },

  server: {
    port: 5173,
    // Proxy /api/* to the local FastAPI backend during development.
    // Start FastAPI with: uvicorn app.main:app --port 8000
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
