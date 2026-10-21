import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    // Kakao's registered redirect URI points at port 5173; don't silently
    // start on 5174 if that port is already occupied.
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: {
    rollupOptions: {
      input: {
        malang: fileURLToPath(new URL('./index.html', import.meta.url)),
        doji: fileURLToPath(new URL('./doji.html', import.meta.url)),
      },
    },
  },
})
