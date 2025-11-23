import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://5.53.21.135:8021',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
