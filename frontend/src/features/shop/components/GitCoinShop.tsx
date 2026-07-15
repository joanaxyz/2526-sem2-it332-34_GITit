import { CheckCircle2, Crown, Gift, Sparkles, WalletCards } from 'lucide-react'
import { useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { paymentsApi } from '@/features/shop/api/paymentsApi'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import type { CoinTransactionEntry } from '@/shared/wallet/api/walletApi'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { errorMessage, formatCoins, formatTransactionDate, formatTransactionReason } from '@/features/shop/utils/shopDisplay'

/* GitCoin ----------------------------------------------------------------- */

function packBadge(index: number, total: number): string | null {
  if (total >= 3 && index === total - 1) return 'Best Value'
  if (total >= 2 && index === Math.floor((total - 1) / 2)) return 'Most Popular'
  return null
}

export function GitCoinShop({
  balance,
  recent,
  walletError,
  walletPending,
}: {
  balance: number
  recent: CoinTransactionEntry[]
  walletError: unknown
  walletPending: boolean
}) {
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const checkoutStatus = searchParams.get('checkout')
  const packs = useQuery({ queryKey: queryKeys.gitcoinPacks, queryFn: paymentsApi.packs, staleTime: 5 * 60 * 1000 })
  const checkout = useMutation({
    mutationFn: (packSlug: string) => paymentsApi.checkout(packSlug),
    onSuccess: (result) => {
      window.location.href = result.checkout_url
    },
  })

  useEffect(() => {
    if (checkoutStatus === 'success') {
      queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
    }
  }, [checkoutStatus, queryClient])

  function dismissCheckoutBanner() {
    const next = new URLSearchParams(searchParams)
    next.delete('checkout')
    setSearchParams(next, { replace: true })
  }

  const packItems = packs.data?.items ?? []

  return (
    <section className="shop-view shop-view--coins" aria-labelledby="gitcoin-shop-title">
      {checkoutStatus === 'success' ? (
        <div className="shop-checkout-banner is-success" role="status">
          <CheckCircle2 aria-hidden="true" />
          <span>Payment received — your GitCoins are on the way.</span>
          <button type="button" onClick={dismissCheckoutBanner}>
            Dismiss
          </button>
        </div>
      ) : null}
      {checkoutStatus === 'cancel' ? (
        <div className="shop-checkout-banner is-cancel" role="status">
          <span>Checkout canceled — no charge was made.</span>
          <button type="button" onClick={dismissCheckoutBanner}>
            Dismiss
          </button>
        </div>
      ) : null}

      <header className="shop-coin-hero">
        <div className="shop-coin-hero-copy">
          <p className="shop-detail-eyebrow">GitCoin Store</p>
          <h1 id="gitcoin-shop-title">Top up your vault</h1>
          <p>Spend GitCoins on stories you can enter and companions you can equip — or earn more by clearing the story.</p>
        </div>
        <div className="shop-coin-balance-card" aria-label="Current balance">
          <div className="shop-coin-balance-art" aria-hidden="true">
            <GitCoinIcon />
          </div>
          <span>
            <small>Balance</small>
            <strong>{walletPending ? '—' : formatCoins(balance)}</strong>
          </span>
        </div>
      </header>

      <section className="shop-store" aria-label="GitCoin packs">
        {packs.isPending ? <LoadingState label="Loading packs" variant="inline" /> : null}
        {packs.isError ? <ErrorState title="Could not load packs" description={errorMessage(packs.error)} /> : null}
        {packItems.length > 0 ? (
          <div className="shop-store-grid">
            {packItems.map((pack, i) => {
              const badge = packBadge(i, packItems.length)
              const stack = Math.min(4, i + 1)
              const rate = pack.price_cents > 0 ? Math.round(pack.coins / (pack.price_cents / 100)) : 0
              return (
                <article className="shop-store-tile" key={pack.slug} data-featured={badge === 'Best Value'}>
                  {badge ? <span className="shop-store-badge">{badge}</span> : null}
                  <div className="shop-store-coins" aria-hidden="true">
                    {Array.from({ length: stack }).map((_, layer) => (
                      <GitCoinIcon key={layer} />
                    ))}
                  </div>
                  <strong className="shop-store-amount">{formatCoins(pack.coins)}</strong>
                  <span className="shop-store-label">{pack.label}</span>
                  {rate > 0 ? <span className="shop-store-rate">{formatCoins(rate)} coins / $1</span> : null}
                  <button
                    type="button"
                    className="shop-store-buy"
                    disabled={checkout.isPending}
                    onClick={() => checkout.mutate(pack.slug)}
                  >
                    ${(pack.price_cents / 100).toFixed(2)}
                  </button>
                </article>
              )
            })}
          </div>
        ) : null}
        {checkout.isError ? <ErrorState title="Checkout failed" description={errorMessage(checkout.error)} /> : null}
        <p className="shop-purchase-note">
          <span aria-hidden="true">i</span>
          Test-mode Stripe checkout — use card 4242 4242 4242 4242 with any future date and CVC.
        </p>
      </section>

      <div className="shop-coin-side">
        <aside className="ref-panel shop-earn-panel" aria-label="Ways to earn GitCoins">
          <header className="ref-panel-head">Earn in play</header>
          <div className="shop-earn-list">
            <span><Sparkles aria-hidden="true" /> Clear adventure levels</span>
            <span><Gift aria-hidden="true" /> Open chapter chests</span>
            <span><Crown aria-hidden="true" /> Receive plan stipends</span>
          </div>
          <div className="shop-earn-foot">
            <WalletCards aria-hidden="true" />
            <small>GitCoins are a reward for progress — every purchase here is optional.</small>
          </div>
        </aside>

        <section className="ref-panel shop-ledger-panel" aria-labelledby="gitcoin-ledger-title">
          <header className="ref-panel-head" id="gitcoin-ledger-title">
            Recent activity
          </header>
          {walletError ? <ErrorState title="Could not load wallet" description={errorMessage(walletError)} /> : null}
          {!walletError && walletPending ? <LoadingState label="Loading wallet" variant="inline" /> : null}
          {!walletError && !walletPending && recent.length === 0 ? (
            <EmptyState title="No wallet activity yet" description="Earn GitCoins by clearing published encounters." />
          ) : null}
          {!walletError && !walletPending && recent.length > 0 ? (
            <div className="shop-ledger-list">
              {recent.map((entry, i) => (
                <div className="shop-ledger-row" key={`${entry.created_at}-${entry.reason}-${i}`}>
                  <span>
                    <strong>{formatTransactionReason(entry.reason)}</strong>
                    <small>{formatTransactionDate(entry.created_at)}</small>
                  </span>
                  <b data-negative={entry.amount < 0}>
                    {entry.amount > 0 ? '+' : ''}
                    {formatCoins(entry.amount)}
                  </b>
                </div>
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </section>
  )
}
