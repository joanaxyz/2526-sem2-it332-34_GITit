import { Navigate, useSearchParams } from 'react-router-dom'
import type { ReactElement } from 'react'

import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { LoadingState } from '@/shared/components/LoadingState'
import { ErrorState } from '@/shared/components/ErrorState'

/**
 * Nobody can play without a companion: no companion is free anymore, so a
 * brand-new player owns none and must buy one in the Shop first. This gate is
 * only used around playable Adventure/Challenge routes, never Home or Stories.
 */
export function RequireCompanion({ children }: { children: ReactElement }) {
  const { hasCompanion, isLoading, isError, error } = usePlayerLoadout()
  const [searchParams] = useSearchParams()

  if (isLoading) {
    return (
      <LoadingState
        description="Checking your adventuring party."
        label="Loading"
        variant="screen"
      />
    )
  }

  if (isError) {
    return (
      <ErrorState
        title="Could not check companion access"
        description={error?.message ?? 'Try again shortly.'}
      />
    )
  }

  if (!hasCompanion) {
    const next = new URLSearchParams(searchParams)
    next.set('tab', 'companions')
    next.set('required', '1')
    return <Navigate replace to={`/shop?${next.toString()}`} />
  }

  return children
}
