import path from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// CRITICAL: These paths must match exactly for Frappe asset serving to work.
//
// base:   Public URL prefix Frappe uses when serving /assets/tutor_hub/frontend/
//         This becomes the prefix for all generated asset URLs in the built HTML/JS.
//
// outDir: Where Vite writes the build output. This directory is bind-mounted
//         into the Frappe frontend container via compose.frontend-custom-apps.yaml:
//           ./apps/tutor_hub/tutor_hub/public → /home/frappe/frappe-bench/sites/assets/tutor_hub
//
// manifest: true → generates .vite/manifest.json with hashed filenames.
//           deploy-compose.sh reads this file to update the hash tokens in www/landing.html.

export default defineConfig({
  base: "/assets/tutor_hub/frontend/",

  plugins: [react()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  build: {
    outDir: path.resolve(__dirname, "../tutor_hub/public/frontend"),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: path.resolve(__dirname, "src/main.tsx"),
    },
  },
});
