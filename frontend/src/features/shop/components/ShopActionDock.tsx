import { CheckCircle2 } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { actionDisabled, actionLabel, formatCoins } from '@/features/shop/utils/shopDisplay'
import type { ShopDisplayItem } from '@/shared/shop/model/shopPresentation'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

/* Shop action dock ---------------------------------------------------------
   Shared purchase-status control for a shop stage: a coin-price chip beside
   a primary CTA button when affordable, or just the price chip (with a
   hover/tap/focus "Need X more" hint) when not. Used by both the companion
   and story docks so their purchase UX never drifts apart. */

export function ShopActionDock({
  balance,
  item,
  onAction,
  pending,
  purchasesEnabled,
  walletPending,
}: {
  balance: number
  item: ShopDisplayItem
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  purchasesEnabled: boolean
  walletPending: boolean
}) {
  const owned = item.owned
  const label = !owned && !purchasesEnabled ? 'Purchases paused' : actionLabel(item, balance, walletPending)
  const insufficientFunds = !owned && purchasesEnabled && !walletPending && item.price > balance

  return (
    <div className="shop-purchase-dock" aria-label={`${item.label} purchase status`}>
      {!owned ? (
        insufficientFunds ? (
          <ShopPriceHint price={item.price} shortfall={item.price - balance} />
        ) : (
          <div className="shop-price-chip">
            <GitCoinIcon />
            <span>{item.price > 0 ? formatCoins(item.price) : 'Free'}</span>
          </div>
        )
      ) : null}
      {!insufficientFunds ? (
        <button
          type="button"
          className={owned ? 'shop-stage-action-button' : 'shop-purchase-button'}
          disabled={actionDisabled(item, pending, balance, walletPending, purchasesEnabled)}
          onClick={() => onAction(item)}
        >
          {owned ? <CheckCircle2 aria-hidden="true" /> : null}
          {label}
        </button>
      ) : null}
    </div>
  )
}

/**
 * The unaffordable-item price chip is its own purchase-status trigger: the
 * "Need X more" shortfall isn't a competing button, it's a hint revealed by
 * hovering, tapping, or focusing the chip - and dismissed by leaving,
 * tapping elsewhere, blurring, or Escape. A persistent sr-only description
 * carries the same shortfall to screen readers whether or not it's opened.
 */
function ShopPriceHint({ price, shortfall }: { price: number; shortfall: number }) {
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
    <div className="shop-price-chip-wrap" ref={rootRef}>
      <button
        type="button"
        className="shop-price-chip"
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
        <div className="shop-price-tooltip" aria-hidden="true">
          Need {formatCoins(shortfall)} more
        </div>
      ) : null}
    </div>
  )
}
