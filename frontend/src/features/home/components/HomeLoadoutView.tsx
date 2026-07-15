import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Compass, Map as MapIcon, ShoppingBag, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { shopApi } from '@/features/shop/api/shopApi'
import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
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
          <span>Owned collection</span>
          <h2>Choose your companion</h2>
          <p>Your equipped companion appears in Home, Adventures, Challenges, and the top navigation.</p>
        </div>
        <Link to={`${SHOP_ROUTE}?tab=companions`}><ShoppingBag aria-hidden="true" />Find companions</Link>
      </header>

      <section className="ref-panel home-loadout-panel">
        <header className="ref-panel-head"><Sparkles aria-hidden="true" />Companion loadout</header>
        {companions.length ? (
          <>
            <div className="shop-stage shop-stage--portrait home-loadout-stage" data-tone={selectedCompanion?.tone}>
              <ShopCarousel
                className="shop-portrait-carousel"
                ariaLabel="Owned companions"
                items={companions}
                index={companionIndex}
                onIndexChange={setCompanionIndex}
                getKey={(companion) => companion.slug}
                renderSlide={(companion, _i, active) => {
                  const avatar = companionAvatar(companion.slug, companion.art)
                  return (
                  <article className="shop-portrait-slide" data-tone={companion.tone} data-active={active}>
                    <div className="shop-portrait-art">
                      {avatar ? <img src={avatar} alt={companion.label} loading="lazy" /> : null}
                    </div>
                    <div className="shop-portrait-caption">
                      <span className="shop-status-chip" data-state={companion.active ? 'equipped' : 'owned'}>
                        {statusLabel(companion)}
                      </span>
                      <h2 className="shop-portrait-title">{companion.label}</h2>
                    </div>
                  </article>
                  )
                }}
              />
              {companions.length > 1 ? (
              <div className="shop-portrait-thumbs" role="tablist" aria-label="Companion quick select">
                {companions.map((companion, thumbIndex) => {
                  const avatar = companionAvatar(companion.slug, companion.art)
                  return (
                  <button
                    key={companion.slug}
                    type="button"
                    role="tab"
                    aria-selected={thumbIndex === companionIndex}
                    aria-label={`Select ${companion.label}`}
                    className="shop-portrait-thumb"
                    data-active={thumbIndex === companionIndex}
                    onClick={() => setCompanionIndex(thumbIndex)}
                  >
                    {avatar ? <img src={avatar} alt="" loading="lazy" /> : null}
                  </button>
                  )
                })}
              </div>
              ) : null}
            </div>

            {selectedCompanion ? (
              <div className="home-loadout-action">
                <div>
                  <span>{selectedCompanion.active ? 'Currently equipped' : 'Selected'}</span>
                  <strong>{selectedCompanion.label}</strong>
                </div>
                <button
                  type="button"
                  className="shop-primary-action"
                  disabled={selectedCompanion.active || equip.isPending}
                  onClick={() => equip.mutate(selectedCompanion.slug)}
                >
                  {selectedCompanion.active ? <CheckCircle2 aria-hidden="true" /> : null}
                  {selectedCompanion.active
                    ? 'Equipped'
                    : equip.isPending && equip.variables === selectedCompanion.slug
                      ? 'Equipping'
                      : 'Equip companion'}
                </button>
              </div>
            ) : null}
          </>
        ) : (
          <div className="home-loadout-empty">
            <p>You do not own a companion yet. Buy one before starting an Adventure or Challenge.</p>
            <Link to={`${SHOP_ROUTE}?tab=companions&required=1`}>Choose a companion</Link>
          </div>
        )}
        {equip.isError ? <p className="home-loadout-error">{equip.error.message}</p> : null}
      </section>

      <section className="ref-panel home-loadout-panel">
        <header className="ref-panel-head"><Compass aria-hidden="true" />Your stories</header>
        <p className="home-loadout-copy">Stories are entered from the Stories screen; they are not equipped like companions.</p>
        {stories.length ? (
          <>
            <div className="shop-stage home-loadout-stage" data-tone={selectedStory?.tone}>
              <ShopCarousel
                className="shop-story-carousel"
                ariaLabel="Owned stories"
                items={stories}
                index={storyIndex}
                onIndexChange={setStoryIndex}
                getKey={(story) => story.slug}
                renderSlide={(story, _i, active) => (
                  <article className="shop-world-slide" data-tone={story.tone} data-active={active}>
                    <div className="shop-world-art">
                      {story.art ? <img src={story.art} alt={`${story.label} map`} loading="lazy" /> : null}
                    </div>
                    <div className="shop-world-caption">
                      <span className="shop-status-chip" data-state="owned">Owned</span>
                      <h2 className="shop-world-title">{story.label}</h2>
                      <p className="shop-world-sub">Story Map &amp; Battle World</p>
                    </div>
                  </article>
                )}
              />
            </div>

            {selectedStory ? (
              <div className="home-loadout-action">
                <div>
                  <span>Selected story</span>
                  <strong>{selectedStory.label}</strong>
                </div>
                <Link className="shop-primary-action" to={storyPath(selectedStory.slug)}>
                  <MapIcon aria-hidden="true" />
                  Open story map
                </Link>
              </div>
            ) : null}
          </>
        ) : (
          <div className="home-loadout-empty">
            <p>You do not own a story yet. Add one from the Shop to start an adventure.</p>
            <Link to={`${SHOP_ROUTE}?tab=stories`}>Find a story</Link>
          </div>
        )}
        <div className="home-loadout-links">
          <Link to={STORIES_ROUTE}>Choose another story</Link>
          <Link to={`${SHOP_ROUTE}?tab=stories`}>Find more stories</Link>
          <Link to={HOME_ROUTE}>Back to overview</Link>
        </div>
      </section>
    </section>
  )
}
