import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2,
  ChevronRight,
  Compass,
  Map as MapIcon,
  ShoppingBag,
} from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { shopApi } from '@/features/shop/api/shopApi'
import { hasLocalDefinition, statusLabel, toDisplayItem } from '@/features/shop/utils/shopDisplay'
import { queryKeys } from '@/shared/api/queryKeys'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { HOME_ROUTE, SHOP_ROUTE, STORIES_ROUTE, storyPath } from '@/shared/navigation/routes'
import { playerLoadoutApi } from '@/shared/player-loadout/playerLoadoutApi'

/** Loadout shows the square avatar art (not the tall portrait), falling back to
 *  portrait/idle for companions that have no dedicated avatar yet. */
function companionAvatar(slug: string, fallback?: string) {
  const sprites = COMPANIONS[slug]?.sprites
  return sprites?.avatar?.src ?? sprites?.portrait?.src ?? fallback
}

function companionStageArt(slug: string, fallback?: string) {
  const sprites = COMPANIONS[slug]?.sprites
  return sprites?.portrait?.src ?? sprites?.avatar?.src ?? sprites?.idle?.src ?? fallback
}

export function HomeLoadoutView() {
  const queryClient = useQueryClient()
  const catalog = useQuery({
    queryKey: queryKeys.shopCatalog,
    queryFn: shopApi.catalog,
    staleTime: 60_000,
  })
  const equip = useMutation({
    mutationFn: playerLoadoutApi.equipCompanion,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.shopCatalog, result.shop)
    },
  })
  const [companionIndex, setCompanionIndex] = useState(0)
  const [storyIndex, setStoryIndex] = useState(0)

  if (catalog.isPending) {
    return <LoadingState label="Loading loadout" description="Reading your owned companions and stories." />
  }
  if (catalog.isError || !catalog.data) {
    return <ErrorState title="Could not load loadout" description={catalog.error?.message ?? 'No loadout data was returned.'} />
  }

  const items = catalog.data.items.filter(hasLocalDefinition).map(toDisplayItem)
  const companions = items.filter((item) => item.kind === 'companion' && item.owned)
  const stories = items.filter((item) => item.kind === 'story' && item.owned)

  const selectedCompanion = companions[Math.min(companionIndex, companions.length - 1)]
  const selectedStory = stories[Math.min(storyIndex, stories.length - 1)]

  return (
    <section className="home-loadout" aria-label="Player loadout and stories">
      <header className="home-loadout-intro">
        <div>
          <span>Field inventory</span>
          <h2>Build your active loadout</h2>
          <p>Choose the companion who enters every Adventure and Challenge at your side.</p>
        </div>
        <Link to={`${SHOP_ROUTE}?tab=companions`}><ShoppingBag aria-hidden="true" />Find companions</Link>
      </header>

      <section className="home-loadout-command" aria-labelledby="home-loadout-companion-title">
        {companions.length ? (
          <>
            <div className="home-loadout-stage" data-tone={selectedCompanion?.tone}>
              <div className="home-loadout-stage-grid" aria-hidden="true" />
              {selectedCompanion ? (
                <img
                  className="home-loadout-stage-art"
                  src={companionStageArt(selectedCompanion.slug, selectedCompanion.art)}
                  alt={selectedCompanion.label}
                />
              ) : null}
              <div className="home-loadout-stage-status">
                <span className="shop-status-chip" data-state={selectedCompanion?.active ? 'equipped' : 'owned'}>
                  {selectedCompanion ? statusLabel(selectedCompanion) : 'Owned'}
                </span>
                <small>Active companion stage</small>
              </div>
            </div>

            {selectedCompanion ? (
              <div className="home-loadout-inspector">
                <header>
                  <span>{selectedCompanion.active ? 'Deployed companion' : 'Ready to deploy'}</span>
                  <h2 id="home-loadout-companion-title">{selectedCompanion.label}</h2>
                  <p>{COMPANIONS[selectedCompanion.slug]?.kit?.[0]?.description ?? 'A battle-ready companion for your next Git quest.'}</p>
                </header>
                <div className="home-loadout-action">
                  <div>
                    <span>{selectedCompanion.active ? 'Current slot' : 'Selected slot'}</span>
                    <strong>{selectedCompanion.active ? 'Companion equipped' : 'Swap active companion'}</strong>
                  </div>
                  <button
                    type="button"
                    className="shop-primary-action"
                    disabled={selectedCompanion.active || equip.isPending}
                    aria-busy={equip.isPending && equip.variables === selectedCompanion.slug}
                    onClick={() => equip.mutate(selectedCompanion.slug)}
                  >
                    {selectedCompanion.active ? <CheckCircle2 aria-hidden="true" /> : <ChevronRight aria-hidden="true" />}
                    {selectedCompanion.active
                      ? 'Equipped'
                      : equip.isPending && equip.variables === selectedCompanion.slug
                        ? 'Equipping'
                        : 'Equip companion'}
                  </button>
                </div>
              </div>
            ) : null}

            <div className="home-loadout-roster" role="tablist" aria-label="Owned companions">
              <div className="home-loadout-roster-heading">
                <span>Owned roster</span>
                <strong>{companions.length.toLocaleString()} available</strong>
              </div>
              {companions.map((companion, rosterIndex) => {
                const avatar = companionAvatar(companion.slug, companion.art)
                return (
                  <button
                    key={companion.slug}
                    type="button"
                    role="tab"
                    aria-selected={rosterIndex === companionIndex}
                    className="home-loadout-roster-item"
                    data-active={rosterIndex === companionIndex}
                    onClick={() => setCompanionIndex(rosterIndex)}
                  >
                    <span>{avatar ? <img src={avatar} alt="" loading="lazy" /> : null}</span>
                    <strong>{companion.label}</strong>
                    <small>{companion.active ? 'Equipped' : 'Owned'}</small>
                  </button>
                )
              })}
            </div>
          </>
        ) : (
          <div className="home-loadout-empty">
            <p>You do not own a companion yet. Buy one before starting an Adventure or Challenge.</p>
            <Link to={`${SHOP_ROUTE}?tab=companions&required=1`}>Choose a companion</Link>
          </div>
        )}
        {equip.isError ? <p className="home-loadout-error" role="alert">{equip.error.message}</p> : null}
      </section>

      <section className="home-loadout-worlds" aria-labelledby="home-loadout-worlds-title">
        <div className="home-loadout-worlds-copy">
          <Compass aria-hidden="true" />
          <div>
            <span>World atlas</span>
            <h2 id="home-loadout-worlds-title">Stories are entered, not equipped</h2>
            <p>Choose a destination, then open its map to continue your quest.</p>
          </div>
        </div>
        {stories.length ? (
          <>
            {selectedStory ? (
              <div className="home-loadout-world-stage" data-tone={selectedStory.tone}>
                {selectedStory.art ? <img src={selectedStory.art} alt={`${selectedStory.label} map`} loading="lazy" /> : null}
                <div>
                  <span className="shop-status-chip" data-state="owned">Owned world</span>
                  <h3>{selectedStory.label}</h3>
                  <p>Story map and battle world</p>
                </div>
                <Link className="shop-primary-action" to={storyPath(selectedStory.slug)}>
                  <MapIcon aria-hidden="true" />
                  Open story map
                </Link>
              </div>
            ) : null}
            <div className="home-loadout-world-rail" role="tablist" aria-label="Owned story worlds">
              {stories.map((story, worldIndex) => (
                <button
                  key={story.slug}
                  type="button"
                  role="tab"
                  aria-selected={worldIndex === storyIndex}
                  data-active={worldIndex === storyIndex}
                  onClick={() => setStoryIndex(worldIndex)}
                >
                  {story.art ? <img src={story.art} alt="" loading="lazy" /> : null}
                  <span>
                    <strong>{story.label}</strong>
                    <small>Owned world</small>
                  </span>
                </button>
              ))}
            </div>
          </>
        ) : (
          <div className="home-loadout-empty">
            <p>You do not own a story yet. Add one from the Shop to start an adventure.</p>
            <Link to={`${SHOP_ROUTE}?tab=stories`}>Find a story</Link>
          </div>
        )}
        <div className="home-loadout-links">
          <Link to={STORIES_ROUTE}>Browse story maps</Link>
          <Link to={`${SHOP_ROUTE}?tab=stories`}>Find more stories</Link>
          <Link to={HOME_ROUTE}>Back to overview</Link>
        </div>
      </section>
    </section>
  )
}
