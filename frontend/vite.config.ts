import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { cp } from 'node:fs/promises'
import path from 'node:path'
import type { Plugin } from 'vite'
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

function runtimePublicAssets(): Plugin {
  let publicDir: string
  let outDir: string
  let optimizedOriginals: Set<string>
  let optimizedCopies: Set<string>

  return {
    name: 'runtime-public-assets',
    apply: 'build',
    configResolved(config) {
      publicDir = config.publicDir
      outDir = path.resolve(config.root, config.build.outDir)
      const manifest = JSON.parse(readFileSync(
        path.resolve(config.root, 'src/shared/media/optimizedPublicMedia.json'), 'utf8',
      )) as Record<string, string>
      optimizedOriginals = new Set(Object.keys(manifest))
      optimizedCopies = new Set(Object.values(manifest))
      const fingerprints = JSON.parse(readFileSync(
        path.resolve(config.root, 'media-sources.json'), 'utf8',
      )) as Record<string, { target: string; sourceSha256: string; targetSha256: string }>
      for (const [source, fingerprint] of Object.entries(fingerprints)) {
        const hash = (file: string) => createHash('sha256')
          .update(readFileSync(path.resolve(config.root, file))).digest('hex')
        if (hash(source) !== fingerprint.sourceSha256 || hash(fingerprint.target) !== fingerprint.targetSha256) {
          throw new Error(`Stale optimized media: ${source}. Run python scripts/assets/optimize_delivery_media.py --apply from the repository root.`)
        }
      }
    },
    async writeBundle() {
      await cp(publicDir, outDir, {
        recursive: true,
        filter(source) {
          const parts = path.relative(publicDir, source).split(path.sep)
          const url = `/${parts.join('/')}`
          if (source.endsWith('.lossless.webp') && !optimizedCopies.has(url)) return false
          if (
            parts[0] === 'cosmetics' &&
            parts[1] === 'story-worlds' &&
            ['frostbound-citadel', 'neon-backstreets'].includes(parts[2])
          ) return false

          // Preserve authoring files locally without copying them into releases.
          return !parts.some((part) => [
            'raw', '_raw', '_shift_raw', 'pose', 'references', 'samples',
          ].includes(part)) &&
            !source.endsWith('_raw.zip') &&
            path.basename(source) !== '_diagnostics.json' &&
            !path.basename(source).startsWith('_preview-contact-sheet.') &&
            !optimizedOriginals.has(url)
        },
      })
    },
  }
}

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
  plugins: [react(), runtimePublicAssets()],
  optimizeDeps: {
    // Only the real pages. Scratch previews in the gitignored .tmp/ must never
    // break dev-server startup when the code they import moves.
    entries: ['index.html', 'diagram-review.html'],
  },
  resolve: {
    alias: [
      ...(mode === 'test'
        ? [
            {
              find: /^@\/assets\/.*$/,
              replacement: path.resolve(import.meta.dirname, './src/test/assetStub.ts'),
            },
          ]
        : []),
      { find: '@', replacement: path.resolve(import.meta.dirname, './src') },
    ],
  },
  build: {
    // The plugin copies runtime media; Vite's default copy includes source art
    // and inactive worlds even when no production code references those files.
    copyPublicDir: false,
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
              debugName: 'vendor chunks',
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
