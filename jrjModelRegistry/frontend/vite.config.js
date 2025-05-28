import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: '.',  // Optional if you're inside frontend already
  build: {
    sourcemap: true,
    outDir: 'dist',
    emptyOutDir: true,
  },
  base: './', // Important: makes relative paths for deployment under FastAPI
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
})
