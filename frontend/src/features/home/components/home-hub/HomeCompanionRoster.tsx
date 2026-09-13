import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, ChevronRight, ShoppingBag } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { queryKeys } from '@/shared/api/queryKeys'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { SHOP_ROUTE } from '@/shared/navigation/routes'
import { playerLoadoutApi } from '@/shared/player-loadout/playerLoadoutApi'
import { shopCatalogQueryOptions } from '@/shared/shop/api/shopApi'
import { hasLocalDefinition, toDisplayItem } from '@/shared/shop/model/shopPresentation'

/** Square avatar art, falling back to portrait/idle for companions without one. */
function companionAvatar(slug: string, fallback?: string) {
  const sprites = COMPANIONS[slug]?.sprites
  return sprites?.avatar?.src ?? sprites?.portrait?.src ?? fallback
}

/**
 * Picking who fights beside you. This lives in Profile because it answers the
 * same question as the rank badge above it: who am I playing as right now.
 */
export function HomeCompanionRoster() {
  const queryClient = useQueryClient()
  const catalog = useQuery(shopCatalogQueryOptions())
  const equip = useMutation({
    mutationFn: playerLoadoutApi.equipCompanion,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.shopCatalog, result.shop)
    },
  })
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null)

  const owned = (catalog.data?.items ?? [])
    .filter(hasLocalDefinition)
    .map(toDisplayItem)
    .filter((item) => item.owned)
  const selected = owned.find((item) => item.slug === selectedSlug) ?? owned[0]

  return (
    <section className="home-roster-panel" aria-label="Companion roster">
      <header className="ref-panel-head">
        Companion
        {owned.length ? <em>{owned.length.toLocaleString()} owned</em> : null}
      </header>

      {catalog.isPending ? (
        <div className="home-roster-loading" role="status">
          <span className="sr-only">Loading your companions</span>
          {[0, 1, 2].map((slot) => (
            <i key={slot} aria-hidden="true" />
          ))}
        </div>
      ) : catalog.isError ? (
        <p className="home-roster-message" role="alert">
          Your companions could not be loaded. Reload the page to try again.
        </p>
      ) : owned.length === 0 ? (
        <div className="home-roster-empty">
          <p>You do not own a companion yet. Buy one before starting an Adventure or Challenge.</p>
          <Link className="home-roster-shop" to={`${SHOP_ROUTE}?required=1`}>
            <ShoppingBag aria-hidden="true" />
            Choose a companion
          </Link>
        </div>
      ) : (
        <>
          <div className="home-roster-list" role="tablist" aria-label="Owned companions" data-onboarding="profile-roster">
            {owned.map((companion) => {
              const avatar = companionAvatar(companion.slug, companion.art)
              return (
                <button
                  key={companion.slug}
                  type="button"
                  role="tab"
                  aria-selected={companion.slug === selected?.slug}
                  className="home-roster-item"
                  data-active={companion.slug === selected?.slug}
                  onClick={() => setSelectedSlug(companion.slug)}
                >
                  <span>{avatar ? <img src={avatar} alt="" loading="lazy" /> : null}</span>
                  <strong>{companion.label}</strong>
                  <small>{companion.active ? 'Equipped' : 'Owned'}</small>
                </button>
              )
            })}
          </div>

          {selected ? (
            <div className="home-roster-action" data-onboarding="home-equip">
              <button
                type="button"
                disabled={selected.active || equip.isPending}
                aria-busy={equip.isPending && equip.variables === selected.slug}
                onClick={() => equip.mutate(selected.slug)}
              >
                {selected.active ? <CheckCircle2 aria-hidden="true" /> : <ChevronRight aria-hidden="true" />}
                {selected.active
                  ? `${selected.label} is equipped`
                  : equip.isPending && equip.variables === selected.slug
                    ? 'Equipping'
                    : 'Equip companion'}
              </button>
              <small>{selected.active ? 'Joins your next Adventure or Challenge.' : `Send ${selected.label} into your next run instead.`}</small>
            </div>
          ) : null}

          <Link className="home-roster-shop" to={SHOP_ROUTE}>
            <ShoppingBag aria-hidden="true" />
            Find more companions
          </Link>
        </>
      )}

      {equip.isError ? (
        <p className="home-roster-message" role="alert">
          {equip.error.message}
        </p>
      ) : null}
    </section>
  )
}
