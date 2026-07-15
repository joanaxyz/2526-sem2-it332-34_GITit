import path from 'node:path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  resolve: {
    alias: [
      ...(mode === 'test'
        ? [
            {
              find: /^@\/assets\/.*$/,
              replacement: path.resolve(__dirname, './src/test/assetStub.ts'),
            },
          ]
        : []),
      { find: '@', replacement: path.resolve(__dirname, './src') },
    ],
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
    // Bound worker creation so local and CI runs remain stable on constrained
    // runners instead of timing out while spawning one process per test file.
    pool: 'threads',
    maxWorkers: 2,
    fileParallelism: false,
  },
}))
