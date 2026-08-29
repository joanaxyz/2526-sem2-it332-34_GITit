import { CheckCircle2 } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { CompanionPosePreview, CompanionSkillPreview } from '@/features/shop/components/CompanionCombatPreview'
import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
import { actionDisabled, actionLabel, formatCoins } from '@/features/shop/utils/shopDisplay'
import { EmptyState } from '@/shared/components/EmptyState'
import { statusLabel, type ShopDisplayItem } from '@/shared/shop/model/shopPresentation'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

/* Companions -------------------------------------------------------------- */

export function CompanionShop({
  balance,
  companions,
  onAction,
  pending,
  purchasesEnabled,
  walletPending,
}: {
  balance: number
  companions: ShopDisplayItem[]
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  purchasesEnabled: boolean
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
          purchasesEnabled={purchasesEnabled}
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
  purchasesEnabled,
  walletPending,
}: {
  balance: number
  companion: ShopDisplayItem
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  purchasesEnabled: boolean
  walletPending: boolean
}) {
  const owned = companion.owned
  const label = !owned && !purchasesEnabled ? 'Purchases paused' : actionLabel(companion, balance, walletPending)
  const insufficientFunds = !owned && purchasesEnabled && !walletPending && companion.price > balance

  return (
    <div className="shop-companion-purchase-dock" aria-label={`${companion.label} purchase status`}>
      {!owned ? (
        insufficientFunds ? (
          <CompanionPriceHint price={companion.price} shortfall={companion.price - balance} />
        ) : (
          <div className="shop-companion-price-chip">
            <GitCoinIcon />
            <span>{companion.price > 0 ? formatCoins(companion.price) : 'Free'}</span>
          </div>
        )
      ) : null}
      {!insufficientFunds ? (
        <button
          type="button"
          className={owned ? 'shop-stage-action-button' : 'shop-companion-purchase-button'}
          disabled={actionDisabled(companion, pending, balance, walletPending, purchasesEnabled)}
          onClick={() => onAction(companion)}
        >
          {owned ? <CheckCircle2 aria-hidden="true" /> : null}
          {label}
        </button>
      ) : null}
    </div>
  )
}

/**
 * The unaffordable-companion price chip is its own purchase-status trigger:
 * the "Need X more" shortfall isn't a competing button, it's a hint revealed
 * by hovering, tapping, or focusing the chip - and dismissed by leaving,
 * tapping elsewhere, blurring, or Escape. A persistent sr-only description
 * carries the same shortfall to screen readers whether or not it's opened.
 */
function CompanionPriceHint({ price, shortfall }: { price: number; shortfall: number }) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement | null>(null)
  const descriptionId = useId()

  useEffect(() => {
    if (!open) return

    function handlePointerDown(event: PointerEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }

    document.addEventListener('pointerdown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open])

  return (
    <div className="shop-companion-price-chip-wrap" ref={rootRef}>
      <button
        type="button"
        className="shop-companion-price-chip"
        aria-expanded={open}
        aria-describedby={descriptionId}
        onPointerEnter={(event) => {
          if (event.pointerType === 'mouse') setOpen(true)
        }}
        onPointerLeave={(event) => {
          if (event.pointerType === 'mouse') setOpen(false)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={() => setOpen(true)}
      >
        <GitCoinIcon />
        <span>{formatCoins(price)}</span>
      </button>
      <span id={descriptionId} className="sr-only">{`Need ${formatCoins(shortfall)} more GitCoins`}</span>
      {open ? (
        <div className="shop-companion-price-tooltip" aria-hidden="true">
          Need {formatCoins(shortfall)} more
        </div>
      ) : null}
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
