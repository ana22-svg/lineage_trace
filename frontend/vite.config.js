import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      // Proxy API requests to the FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});