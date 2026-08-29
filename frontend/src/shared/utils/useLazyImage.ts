import { useEffect, useState } from 'react'

type ImageLoader = () => Promise<{ default: string }>

/**
 * Resolves one image out of a fixed set of dynamic-import loaders, so only
 * the variant actually needed for `key` is fetched instead of bundling every
 * variant into the importing component's chunk. `loaders` must be a stable
 * (module-level) object — its identity is an effect dependency.
 */
export function useLazyImage(key: string | null, loaders: Record<string, ImageLoader>): string | null {
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    if (!key) {
      setSrc(null)
      return
    }
    const loader = loaders[key]
    if (!loader) {
      setSrc(null)
      return
    }
    let cancelled = false
    loader().then((module) => {
      if (!cancelled) setSrc(module.default)
    })
    return () => {
      cancelled = true
    }
  }, [key, loaders])

  return src
}
