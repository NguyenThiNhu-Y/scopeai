import { defineConfig } from 'vite';

/**
* Config dành riêng cho Preview (podman-compose) — KHÔNG dùng cho dev.
 * - allowedHosts: true — app chạy sau reverse proxy hostname động.
 * - proxy /api -> backend:8000 — dùng tên service của compose (bridge network).
 * - port 3000 — KHÔNG dùng 5173: cổng 5173 bị môi trường session chặn (egress gateway).
 */
export default defineConfig({
  preview: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: true,
    proxy: {
      '/api': { target: 'http://backend:8000', changeOrigin: true },
    },
  },
});
