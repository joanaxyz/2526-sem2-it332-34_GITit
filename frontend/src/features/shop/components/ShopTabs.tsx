import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

import { formatCoins, shopTabs, type ShopTab } from '@/features/shop/utils/shopDisplay'

export function ShopTabs({
  activeTab,
  balance,
  walletPending,
  onTabChange,
}: {
  activeTab: ShopTab
  balance: number
  walletPending: boolean
  onTabChange: (tab: ShopTab) => void
}) {
  return (
    <nav className="shop-categories" aria-label="Shop sections">
      <div className="shop-tab-list" role="tablist" aria-orientation="horizontal">
        {shopTabs.map(({ id, label, description, Icon }) => {
          const active = activeTab === id
          return (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={active}
              className={active ? 'is-active' : undefined}
              onClick={() => onTabChange(id)}
            >
              {Icon ? <Icon aria-hidden="true" /> : <GitCoinIcon />}
              <span>
                <strong>{label}</strong>
                <small>{description}</small>
              </span>
            </button>
          )
        })}
      </div>
      <div className="shop-rail-balance" aria-label="GitCoin balance">
        <GitCoinIcon />
        <span>
          <small>Balance</small>
          <strong>{walletPending ? '---' : formatCoins(balance)}</strong>
        </span>
      </div>
    </nav>
  )
}
