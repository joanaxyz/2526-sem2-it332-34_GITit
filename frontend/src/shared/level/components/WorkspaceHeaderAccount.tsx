import { useRank } from '@/shared/progress/rank'
import { useAuthStore } from '@/shared/auth/useAuth'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { useWalletSummary } from '@/shared/wallet/hooks/useWallet'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

/** Wallet + profile cluster docked at the right edge of both workspace command bars. */
export function WorkspaceHeaderAccount() {
  const user = useAuthStore((state) => state.user)
  const wallet = useWalletSummary()
  const rank = useRank()
  const { companion } = usePlayerLoadout()
  const avatar = companion.sprites.portrait?.src ?? companion.sprites.idle?.src ?? ''

  return (
    <div className="gameplay-header-account">
      <div className="gameplay-header-wallet">
        <GitCoinIcon />
        <span>
          <strong>{wallet.isPending ? '---' : (wallet.data?.balance ?? 0).toLocaleString()}</strong>
          <small>GitCoins</small>
        </span>
      </div>
      <div className="gameplay-header-profile">
        <img src={avatar} alt="" />
        <span>
          <strong>{user?.username ?? companion.label}</strong>
          <small>{rank ? `Rank ${rank.tier.numeral}` : 'Rank —'}</small>
        </span>
      </div>
    </div>
  )
}
