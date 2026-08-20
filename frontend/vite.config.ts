/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

// Build output lands directly in the existing FastAPI static root so the
// current single-process serving model (Python serves everything, no
// separate Node runtime) is preserved. See:
// docs/project/phases/phase_2/history/architecture/
//   claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654.md
const STATIC_ROOT = path.resolve(import.meta.dirname, "../src/margpa_runtime_llm/web/static");

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: STATIC_ROOT,
    emptyOutDir: true,
    assetsDir: "",
    // Deterministic (unhashed) output names: the FastAPI "/" route reads
    // index.html fresh on every request and serves whatever <script src=...>
    // it contains, so hashing would work at runtime too — but stable names
    // keep the asset path backend tests assert against (/assets/app.js)
    // meaningful without needing to read the build manifest.
    rollupOptions: {
      output: {
        entryFileNames: "app.js",
        chunkFileNames: "app-[name].js",
        assetFileNames: "app[extname]",
      },
    },
  },
  base: "/assets/",
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/healthz": "http://127.0.0.1:8000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/testSetup.ts"],
    css: false,
  },
});
