import { useCallback, type CSSProperties } from 'react'
import { Backpack, BarChart3, ChevronLeft, ChevronRight, User } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'

import { HomeLoadoutView } from '@/features/home/components/HomeLoadoutView'
import { HomeOnboarding } from '@/features/onboarding/HomeOnboarding'
import { HomeStatsView } from '@/features/home/components/HomeStatsView'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { HomeProfileWorkspace } from '@/features/home/components/home-hub/HomeProfileWorkspace'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld } from '@/shared/story-worlds/registry'

type HomeTab = 'overview' | 'loadout' | 'profile'

function homeTab(value: string | null): HomeTab {
  if (value === 'profile' || value === 'loadout') return value
  return 'overview'
}

export function HomeHubView({
  home,
  stats,
  playerName,
  gitcoins,
}: {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  gitcoins: number | null
}) {
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = homeTab(searchParams.get('tab'))
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

  const selectTab = useCallback(
    (next: HomeTab) => {
      setSearchParams(
        (current) => {
          const nextParams = new URLSearchParams(current)
          if (next === 'overview') nextParams.delete('tab')
          else nextParams.set('tab', next)
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

      <nav className="home-ref-tabs" aria-label="Home sections">
        <button
          type="button"
          className={tab === 'overview' ? 'is-active' : ''}
          aria-pressed={tab === 'overview'}
          data-onboarding="home-overview"
          onClick={() => selectTab('overview')}
        >
          <BarChart3 aria-hidden="true" />
          Overview
        </button>
        <button
          type="button"
          className={tab === 'loadout' ? 'is-active' : ''}
          aria-pressed={tab === 'loadout'}
          data-onboarding="home-loadout"
          onClick={() => selectTab('loadout')}
        >
          <Backpack aria-hidden="true" />
          Loadout
        </button>
        <button
          type="button"
          className={tab === 'profile' ? 'is-active' : ''}
          aria-pressed={tab === 'profile'}
          data-onboarding="home-profile"
          onClick={() => selectTab('profile')}
        >
          <User aria-hidden="true" />
          Profile
        </button>
      </nav>

      <HomeOnboarding
        ready={!loadoutLoading && !loadoutError}
        hasCompanion={hasCompanion}
        tab={tab}
        onSelectTab={selectTab}
      />

      {tab === 'overview' ? (
        <HomeStatsView
          home={home}
          stats={stats}
          companionRequired={companionPresentation.status === 'empty'}
        />
      ) : null}
      {tab === 'loadout' ? <HomeLoadoutView /> : null}
      <HomeProfileWorkspace
        home={home}
        stats={stats}
        playerName={playerName}
        gitcoins={gitcoins}
        hidden={tab !== 'profile'}
        companion={companionPresentation}
      />

      <div className="home-ref-arrows" aria-hidden="true">
        <ChevronLeft />
        <ChevronRight />
      </div>
    </div>
  )
}
