import { useEffect, useRef, useState } from 'react'

import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { useWalletSummary } from '@/features/wallet/hooks/useWallet'
import { cn } from '@/shared/utils/cn'

export function WalletBadge() {
  const { data, isPending } = useWalletSummary()
  const balance = data?.balance
  const previousBalanceRef = useRef<number | null>(null)
  const [justEarned, setJustEarned] = useState(false)

  useEffect(() => {
    if (typeof balance !== 'number') return
    const previous = previousBalanceRef.current
    previousBalanceRef.current = balance
    if (previous === null || balance <= previous) return
    setJustEarned(true)
    const timer = setTimeout(() => setJustEarned(false), 900)
    return () => clearTimeout(timer)
  }, [balance])

  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-full border border-primary/25 bg-secondary/40 py-1 pl-1.5 pr-3.5',
        justEarned && 'wallet-badge-earned',
      )}
      title="GitCoins - earned by passing adventures and clearing challenges"
    >
      <GitCoinIcon className="size-6 drop-shadow-[0_0_6px_rgba(0,245,212,0.4)]" />
      <span className="text-sm font-bold tabular-nums text-primary">
        {isPending ? '---' : (balance ?? 0).toLocaleString()}
      </span>
    </div>
  )
}
