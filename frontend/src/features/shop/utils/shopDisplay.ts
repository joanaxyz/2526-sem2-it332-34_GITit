import type { ShopDisplayItem } from '@/shared/shop/model/shopPresentation'

export function formatCoins(value: number) {
  return value.toLocaleString()
}

export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'The shop action failed.'
}

export function actionLabel(item: ShopDisplayItem, balance: number, walletPending: boolean) {
  if (item.owned) return 'Manage in Loadout'
  if (item.price === 0) return 'Claim'
  if (!walletPending && item.price > balance) return `Need ${formatCoins(item.price - balance)} more`
  return 'Purchase'
}

export function actionDisabled(
  item: ShopDisplayItem,
  pending: boolean,
  balance: number,
  walletPending: boolean,
  purchasesEnabled = true,
) {
  return (
    pending
    || (!item.owned && !purchasesEnabled)
    || (!item.owned && item.price > 0 && !walletPending && item.price > balance)
  )
}
