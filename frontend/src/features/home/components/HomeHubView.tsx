import { useCallback, type CSSProperties } from 'react'
import { useSearchParams } from 'react-router-dom'

import { HomeFirstStepNudge } from '@/features/home/components/home-hub/HomeFirstStepNudge'
import { HomeOnboarding } from '@/features/onboarding/components/HomeOnboarding'
import { HomeStatsView } from '@/features/home/components/HomeStatsView'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { HomeProfileWorkspace } from '@/features/home/components/home-hub/HomeProfileWorkspace'
import { HomeViewSwitcher } from '@/features/home/components/home-hub/HomeViewSwitcher'
import { DEFAULT_HOME_VIEW, homeViewFromParam, type HomeView } from '@/features/home/components/home-hub/homeViews'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

export function HomeHubView({
  home,
  stats,
  playerName,
}: {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
}) {
  const [searchParams, setSearchParams] = useSearchParams()
  const view = homeViewFromParam(searchParams.get('view'))
  const {
    companion,
    companionSlug,
    hasCompanion,
    isLoading: loadoutLoading,
    isError: loadoutError,
  } = usePlayerLoadout()
  const companionPresentation: CompanionPresentation = hasCompanion
    ? { status: 'ready', definition: companion, slug: companionSlug }
    : loadoutLoading
      ? { status: 'loading' }
      : loadoutError
        ? { status: 'error' }
        : { status: 'empty' }
  const storyWorld = getStoryWorld(DEFAULT_STORY_WORLD_SLUG)
  const homeBackdropStyle = {
    '--home-theme-map': `url("${storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'}")`,
  } as CSSProperties

  const selectView = useCallback(
    (next: HomeView) => {
      setSearchParams(
        (current) => {
          const nextParams = new URLSearchParams(current)
          if (next === DEFAULT_HOME_VIEW) nextParams.delete('view')
          else nextParams.set('view', next)
          return nextParams
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )

  return (
    <div className="home-ref-screen">
      <div className="home-ref-backdrop" style={homeBackdropStyle} aria-hidden="true" />

      <HomeViewSwitcher view={view} onSelectView={selectView} />

      <HomeOnboarding
        ready={!loadoutLoading && !loadoutError}
        hasCompanion={hasCompanion}
        view={view}
        onSelectView={selectView}
      />

      {view === 'profile' ? null : <HomeStatsView home={home} stats={stats} view={view} />}
      <HomeProfileWorkspace
        home={home}
        stats={stats}
        playerName={playerName}
        hidden={view !== 'profile'}
        companion={companionPresentation}
      />

      {companionPresentation.status === 'empty' ? <HomeFirstStepNudge /> : null}
    </div>
  )
}
