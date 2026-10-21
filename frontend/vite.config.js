import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'
import { readFileSync, writeFileSync } from 'node:fs'

const frontendRoot = fileURLToPath(new URL('.', import.meta.url))

function deploymentConfig(backendOrigin) {
  return {
    name: 'windows-nginx-config',
    apply: 'build',
    writeBundle() {
      if (!backendOrigin) throw new Error('Set BACKEND_ORIGIN in frontend/.env.production before building.')
      const backend = new URL(backendOrigin)
      if (backend.protocol !== 'http:' || backend.username || backend.password ||
          backend.pathname !== '/' || backend.search || backend.hash) {
        throw new Error('BACKEND_ORIGIN must be an HTTP origin such as http://100.100.100.20:8000.')
      }
      const template = readFileSync(new URL('./nginx.conf.template', import.meta.url), 'utf8')
      writeFileSync(new URL('./nginx.conf', import.meta.url), template.replaceAll('__BACKEND_ORIGIN__', backend.origin))
      console.info(`Generated frontend/nginx.conf: /api -> ${backend.origin}`)
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, frontendRoot, '')
  return {
    plugins: [vue(), deploymentConfig(env.BACKEND_ORIGIN)],
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
  }
})
