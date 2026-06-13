import path from 'node:path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // Sprite strips are tiny PNGs (often <4KB) but there are hundreds of
    // them; base64-inlining them balloons the battle JS chunk. Serve them as
    // real files so the browser caches each sheet independently.
    assetsInlineLimit: (filePath) =>
      filePath.includes(`${path.sep}sprites${path.sep}`) || filePath.includes('/sprites/')
        ? false
        : undefined,
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
