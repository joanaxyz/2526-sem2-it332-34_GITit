import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'

import { preferencesApi } from '@/shared/preferences/preferencesApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'
import { applyPreferences, persistPreferences, readStoredPreferences } from '@/shared/preferences/preferences'

export function PreferencesSync() {
  const user = useAuthStore((state) => state.user)
  const query = useQuery({
    queryKey: queryKeys.preferences,
    queryFn: preferencesApi.get,
    enabled: Boolean(user),
    staleTime: 10 * 60 * 1000,
    retry: false,
  })

  useEffect(() => {
    const preferences = query.data ?? readStoredPreferences()
    applyPreferences(preferences)
    if (query.data) persistPreferences(query.data)
  }, [query.data])

  useEffect(() => {
    // matchMedia is missing in SSR/test/older-webview contexts; skip the
    // motion listener there rather than crashing the whole provider tree.
    if (typeof window.matchMedia !== 'function') return
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
    const apply = () => applyPreferences(query.data ?? readStoredPreferences())
    motion.addEventListener('change', apply)
    return () => {
      motion.removeEventListener('change', apply)
    }
  }, [query.data])

  return null
}
