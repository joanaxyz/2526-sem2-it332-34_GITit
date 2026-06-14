import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import type { MarketplaceListing } from '@/features/marketplace/api/marketplaceApi'
import { Button } from '@/shared/components/Button'

export function PurchaseConfirm({
  listing,
  title,
  balance,
  isPending,
  error,
  onConfirm,
  onCancel,
}: {
  listing: MarketplaceListing
  title: string
  balance: number
  isPending: boolean
  error: string | null
  onConfirm: () => void
  onCancel: () => void
}) {
  const affordable = balance >= listing.price

  return (
    <div className="upload-dialog-backdrop" role="dialog" aria-modal="true" aria-label="Confirm purchase">
      <div className="upload-dialog purchase-confirm">
        <h2 className="editor-rail-title">Acquire this relic?</h2>
        <p className="purchase-confirm-item">{title}</p>

        <div className="purchase-confirm-cost">
          <span>Cost</span>
          <span className="purchase-confirm-price">
            {listing.price}
            <GitCoinIcon className="size-5" />
          </span>
        </div>
        <div className="purchase-confirm-cost">
          <span>Your balance</span>
          <span className="purchase-confirm-price">
            {balance}
            <GitCoinIcon className="size-5" />
          </span>
        </div>

        {!affordable ? <p className="editor-warning is-error">Not enough GitCoins.</p> : null}
        {error ? <p className="editor-warning is-error">{error}</p> : null}

        <footer className="upload-dialog-foot">
          <Button variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button size="sm" disabled={!affordable || isPending} onClick={onConfirm}>
            {isPending ? 'Spending…' : `Spend ${listing.price}`}
          </Button>
        </footer>
      </div>
    </div>
  )
}
