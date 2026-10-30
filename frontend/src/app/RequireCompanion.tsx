import { Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'

import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { ErrorState } from '@/shared/components/ErrorState'
import { storyPath } from '@/shared/navigation/routes'

/**
 * Nobody can play without a companion: no companion is free anymore, so a
 * brand-new player owns none and must buy one in the Shop first. This gate is
 * only used around playable Adventure/Challenge routes, never Home or Stories.
 */
export function RequireCompanion({ children }: { children: ReactElement }) {
  const { hasCompanion, isLoading, isError, error } = usePlayerLoadout()

  if (isLoading) {
    return (
      <LoadingScreen
        description="Checking your adventuring party."
        label="Loading"
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
    return <Navigate replace to={`${storyPath()}?companion-required=1`} />
  }

  return children
}
