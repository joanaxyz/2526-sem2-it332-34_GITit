import { Crown, Gift, Sparkles, WalletCards } from 'lucide-react'

import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import type { CoinTransactionEntry } from '@/shared/wallet/api/walletApi'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { errorMessage, formatCoins, formatTransactionDate, formatTransactionReason } from '@/features/shop/utils/shopDisplay'

export function GitCoinWallet({
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
  return (
    <section className="shop-view shop-view--coins" aria-labelledby="gitcoin-wallet-title">
      <header className="shop-coin-hero">
        <div className="shop-coin-hero-copy">
          <p className="shop-detail-eyebrow">Progress wallet</p>
          <h1 id="gitcoin-wallet-title">Your earned GitCoins</h1>
          <p>GitCoins come from progress and rewards. They cannot be purchased with cash.</p>
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
            <small>GitCoins are earned through progress and spent on unlocks.</small>
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
