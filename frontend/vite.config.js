import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://localhost:18000',
      '/ws': {
        target: 'ws://localhost:18000',
        ws: true,
      },
    },
  },
})