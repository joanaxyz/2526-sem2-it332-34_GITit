import gitCoinImage from '@/assets/images/GIT_coin.png'
import { cn } from '@/shared/utils/cn'

/**
 * The GitCoin: shared PNG asset for every wallet and reward coin.
 */
export function GitCoinIcon({ className }: { className?: string }) {
  return <img src={gitCoinImage} alt="GitCoin" className={cn('git-coin-icon shrink-0', className)} />
}
