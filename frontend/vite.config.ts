import path from 'node:path'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

function vendorChunkName(moduleId: string): string | null {
  const normalizedId = moduleId.replace(/\\/g, '/')
  if (!normalizedId.includes('/node_modules/')) return null

  if (/\/node_modules\/(?:react|react-dom|react-router|react-router-dom|scheduler)\//.test(normalizedId)) {
    return 'vendor-react'
  }
  if (/\/node_modules\/(?:reactflow|@reactflow|dagre)\//.test(normalizedId)) {
    return 'vendor-flow'
  }
  if (/\/node_modules\/(?:@tanstack|zustand)\//.test(normalizedId)) {
    return 'vendor-state'
  }
  if (/\/node_modules\/(?:@hookform|react-hook-form|zod)\//.test(normalizedId)) {
    return 'vendor-forms'
  }
  if (
    /\/node_modules\/(?:@radix-ui|lucide-react|sonner|class-variance-authority|clsx)\//.test(
      normalizedId,
    )
  ) {
    return 'vendor-ui'
  }
  return 'vendor-misc'
}

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
    rolldownOptions: {
      output: {
        // Keep stable third-party dependencies out of the application entry
        // chunk while avoiding a request per package.
        codeSplitting: {
          groups: [
            {
              name: vendorChunkName,
            },
          ],
        },
      },
    },
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
