import { CheckCircle2 } from 'lucide-react'
import { useState } from 'react'

import { CompanionPosePreview, CompanionSkillPreview } from '@/features/shop/components/CompanionCombatPreview'
import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
import { actionDisabled, compactActionLabel, statusLabel, type ShopDisplayItem } from '@/features/shop/utils/shopDisplay'
import { EmptyState } from '@/shared/components/EmptyState'

/* Companions -------------------------------------------------------------- */

export function CompanionShop({
  balance,
  companions,
  onAction,
  pending,
  walletPending,
}: {
  balance: number
  companions: ShopDisplayItem[]
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  walletPending: boolean
}) {
  const [index, setIndex] = useState(0)
  const selected = companions[Math.min(index, companions.length - 1)]

  if (!selected) {
    return (
      <section className="shop-view shop-empty-panel">
        <EmptyState title="No characters available" description="The shop catalog has no companions right now." />
      </section>
    )
  }

  return (
    <section className="shop-view shop-view--companions" aria-labelledby="companion-shop-title">
      <div className="shop-stage shop-stage--portrait" data-tone={selected.tone}>
        <ShopCarousel
          className="shop-portrait-carousel"
          ariaLabel="Companion portraits"
          items={companions}
          index={index}
          onIndexChange={setIndex}
          getKey={(companion) => companion.slug}
          renderSlide={(companion, _i, active) => (
            <article className="shop-portrait-slide" data-tone={companion.tone} data-active={active}>
              <div className="shop-portrait-art">
                {companion.art ? <img src={companion.art} alt={companion.label} loading="lazy" /> : null}
              </div>
              <div className="shop-portrait-caption">
                <span className="shop-status-chip" data-state={companion.active ? 'equipped' : companion.owned ? 'owned' : 'locked'}>
                  {statusLabel(companion)}
                </span>
                <h2 id={active ? 'companion-shop-title' : undefined} className="shop-portrait-title">{companion.label}</h2>
              </div>
            </article>
          )}
        />
        <div className="shop-portrait-thumbs" role="tablist" aria-label="Companion quick select">
          {companions.map((companion, thumbIndex) => (
            <button
              key={companion.slug}
              type="button"
              role="tab"
              aria-selected={thumbIndex === index}
              aria-label={`Select ${companion.label}`}
              className="shop-portrait-thumb"
              data-active={thumbIndex === index}
              onClick={() => setIndex(thumbIndex)}
            >
              {companion.art ? <img src={companion.art} alt="" loading="lazy" /> : null}
            </button>
          ))}
        </div>
        <CompanionActionDock
          balance={balance}
          companion={selected}
          onAction={onAction}
          pending={pending}
          walletPending={walletPending}
        />
      </div>

      <CompanionPreviewSuite companionSlug={selected.slug} key={selected.slug} />
    </section>
  )
}

function CompanionActionDock({
  balance,
  companion,
  onAction,
  pending,
  walletPending,
}: {
  balance: number
  companion: ShopDisplayItem
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  walletPending: boolean
}) {
  return (
    <div className="shop-stage-action-dock" aria-label={`${companion.label} purchase status`}>
      <button
        type="button"
        className="shop-stage-action-button"
        disabled={actionDisabled(companion, pending, balance, walletPending)}
        onClick={() => onAction(companion)}
      >
        {companion.owned ? <CheckCircle2 aria-hidden="true" /> : null}
        {compactActionLabel(companion, balance, walletPending)}
      </button>
    </div>
  )
}

function CompanionPreviewSuite({ companionSlug }: { companionSlug: string }) {
  return (
    <div className="shop-companion-preview-suite">
      <CompanionPosePreview companionSlug={companionSlug} />
      <CompanionSkillPreview companionSlug={companionSlug} />
    </div>
  )
}
