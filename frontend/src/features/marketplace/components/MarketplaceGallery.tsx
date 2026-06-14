import { Check } from 'lucide-react'

import type { MarketplaceListing } from '@/features/marketplace/api/marketplaceApi'
import { listingSigil, listingTitle } from '@/features/marketplace/categories'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { cn } from '@/shared/utils/cn'

export function MarketplaceGallery({
  listings,
  balance,
  onBuy,
}: {
  listings: MarketplaceListing[]
  balance: number
  onBuy: (listing: MarketplaceListing) => void
}) {
  if (!listings.length) {
    return <p className="market-empty">Nothing here yet — check another category.</p>
  }

  return (
    <div className="market-gallery">
      {listings.map((listing) => {
        const Sigil = listingSigil(listing)
        const unlocked = listing.owned || listing.entitled
        const affordable = balance >= listing.price
        return (
          <article key={listing.id} className={cn('market-plaque', unlocked && 'is-owned')}>
            <span className="market-plaque-sigil" aria-hidden="true">
              <Sigil className="size-9" />
            </span>
            <div className="market-plaque-body">
              <h3 className="market-plaque-title">{listingTitle(listing)}</h3>
              <span className="market-plaque-kind">{listing.item.kind ?? listing.item_kind.replace('_', ' ')}</span>
            </div>
            <div className="market-plaque-foot">
              {unlocked ? (
                <span className="market-owned-tag">
                  <Check className="size-3.5" aria-hidden="true" />
                  In your collection
                </span>
              ) : (
                <>
                  <span className="market-price">
                    {listing.price}
                    <GitCoinIcon className="size-4" />
                  </span>
                  <button
                    type="button"
                    className="market-buy"
                    disabled={!affordable}
                    onClick={() => onBuy(listing)}
                  >
                    {affordable ? 'Acquire' : 'Too costly'}
                  </button>
                </>
              )}
            </div>
          </article>
        )
      })}
    </div>
  )
}
