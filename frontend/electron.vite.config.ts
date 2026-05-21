import { resolve } from "path";

import react from "@vitejs/plugin-react";
import { defineConfig } from "electron-vite";

export default defineConfig({
  main: {
    build: {
      outDir: "dist/main",
      lib: {
        entry: "src/main/index.ts",
        formats: ["es"],
      },
    },
    publicDir: "resources",
  },
  preload: {
    build: {
      target: "node22",
      outDir: "dist/preload",
      lib: {
        entry: "src/preload/index.ts",
        formats: ["es"],
      },
    },
    publicDir: "resources",
  },
  renderer: {
    root: resolve(__dirname, "src/renderer"),
    build: {
      outDir: resolve(__dirname, "dist/renderer"),
      rollupOptions: {
        input: {
          index: resolve(__dirname, "src/renderer/index.html"),
        },
      },
    },
    server: {
      host: process.env.VITE_HOST || "localhost",
      port: Number(process.env.VITE_PORT) || 3000,
      watch: {
        usePolling: true,
      },
      proxy: {
        "/api": {
          target: process.env.VITE_API_URL || "http://localhost:8000",
          changeOrigin: true,
          ws: true,
        },
      },
    },
    define: {
      "process.env.VITE_API_URL": JSON.stringify(
        process.env.VITE_API_URL || "http://localhost:8000",
      ),
      "import.meta.env.PACKAGE_VERSION": JSON.stringify(
        process.env.npm_package_version,
      ),
    },
    resolve: {
      alias: {
        "@renderer": resolve(__dirname, "src/renderer/src"),
      },
    },
    plugins: [react()],
  },
});
