import { useSyncExternalStore } from 'react'

/** Live `matchMedia` match for `query`; false where matchMedia is unavailable (tests, SSR). */
export function useMediaQuery(query: string) {
  return useSyncExternalStore(
    (notify) => {
      const list = window.matchMedia?.(query)
      list?.addEventListener('change', notify)
      return () => list?.removeEventListener('change', notify)
    },
    () => window.matchMedia?.(query).matches ?? false,
    () => false,
  )
}
