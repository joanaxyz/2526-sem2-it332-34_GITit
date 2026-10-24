import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'

import type { HomeView } from '@/features/home/components/home-hub/homeViews'
import {
  HOME_ASSET_BUDGET_MS,
  homeAssetManifest,
  warmHomeAssets,
} from '@/features/home/utils/homeAssets'
import { learnedSkillsQueryOptions } from '@/features/skills/api/skillsApi'
import { shopCatalogQueryOptions } from '@/shared/shop/api/shopApi'

/** Set once Home has warmed its art, so returning to it later opens at once. */
let warmedThisSession = false

/**
 * Keep Home behind its loading screen until the panels it opens on have their
 * data and art: the equipped companion, roster and spellbook, plus every image
 * they paint. Without it the page opened on skeletons and empty frames that
 * filled in one at a time.
 *
 * The gate only closes once per mount. Switching views, equipping a companion
 * or a background refetch never sends an open Home back to the loading screen.
 * A failed request does not hold it either; the panel shows its own error.
 * Later visits in the same session only wait on data, since the art is cached.
 */
export function useHomeAssetGate({ view }: { view: HomeView }): boolean {
  const catalog = useQuery({
    ...shopCatalogQueryOptions(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  })
  // Prefetched into the cache the spellbook reads, not rendered here.
  const skills = useQuery(learnedSkillsQueryOptions())
  const dataSettled = !catalog.isPending && !skills.isPending

  const [ready, setReady] = useState(() => warmedThisSession)
  const startedRef = useRef(false)
  const entryViewRef = useRef(view)
  const openedRef = useRef(false)

  useEffect(() => {
    if (!dataSettled || startedRef.current || warmedThisSession) return
    startedRef.current = true
    const manifest = homeAssetManifest({ catalog: catalog.data, view: entryViewRef.current })
    void warmHomeAssets(manifest, { timeoutMs: HOME_ASSET_BUDGET_MS }).then(() => {
      warmedThisSession = true
      setReady(true)
    })
  }, [catalog.data, dataSettled])

  if (ready && dataSettled) openedRef.current = true
  return openedRef.current
}
