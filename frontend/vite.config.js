import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  // base: "/static/vue/",   // makes built filenames use /static/vue/ prefix
  base: "/",   // makes built filenames use /static/vue/ prefix
  build: {
    outDir: path.resolve(__dirname, "../backend/static/vue"),
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      // forward API and admin to Django in dev
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/admin": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
