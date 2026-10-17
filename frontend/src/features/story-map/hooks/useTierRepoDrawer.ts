import { useRef, useState } from 'react'

import { useMediaQuery } from '@/features/story-map/hooks/useMediaQuery'
import { repositoryGraphSignature } from '@/features/story-map/utils/repositoryGraphSignature'
import type { RepositorySnapshot } from '@/shared/level/types'

/** Matches the two-column tier layout in tier-workspace-responsive.css. */
const TIER_DRAWER_QUERY = '(min-width: 700px) and (max-width: 1099.98px)'

/**
 * Between 700 and 1099px the repository graph lives in a slide-over drawer
 * opened from the stats bar. Tracks whether it is open, counts openings (each
 * one refits the diagrams) and flags graph changes made while it was closed.
 */
export function useTierRepoDrawer(snapshot: RepositorySnapshot | undefined) {
  const drawerMode = useMediaQuery(TIER_DRAWER_QUERY)
  const [requestedOpen, setRequestedOpen] = useState(false)
  const [openCount, setOpenCount] = useState(0)
  const [seenSignature, setSeenSignature] = useState<string | null>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)
  const signature = snapshot ? repositoryGraphSignature(snapshot) : null
  const open = drawerMode && requestedOpen

  // Adjusted during render: a drawer left open is closed when the layout
  // stops using it, and whatever the learner can currently see counts as seen.
  if (!drawerMode && requestedOpen) setRequestedOpen(false)
  if (signature !== null && seenSignature !== signature && (seenSignature === null || !drawerMode || open)) {
    setSeenSignature(signature)
  }

  return {
    drawerMode,
    open,
    openCount,
    /** The graph changed since the learner last saw it. */
    hasUpdate: drawerMode && !open && seenSignature !== null && signature !== seenSignature,
    buttonRef,
    openDrawer: () => {
      setRequestedOpen(true)
      setOpenCount((count) => count + 1)
    },
    closeDrawer: () => {
      setRequestedOpen(false)
      requestAnimationFrame(() => buttonRef.current?.focus())
    },
  }
}
