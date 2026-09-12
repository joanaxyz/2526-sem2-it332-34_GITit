import { CheckCircle2, Sparkles } from 'lucide-react'
import { useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { notifyManager, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { CompanionShop } from '@/features/shop/components/CompanionShop'
import {
  actionDisabled,
  errorMessage,
  formatCoins,
} from '@/features/shop/utils/shopDisplay'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { HOME_ROUTE, storyPath } from '@/shared/navigation/routes'
import {
  shopApi,
  shopCatalogQueryOptions,
  type ShopKind,
} from '@/shared/shop/api/shopApi'
import {
  hasLocalDefinition,
  toDisplayItem,
  type ShopDisplayItem,
} from '@/shared/shop/model/shopPresentation'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { useWalletSummary } from '@/shared/wallet/hooks/useWallet'
import { ShopOnboarding } from '@/features/onboarding/components/ShopOnboarding'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'

export function ShopPage() {
  const onboarding = useAppOnboarding()
  const guidedSetup = onboarding && ['shop', 'purchase'].includes(onboarding.phase)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const shop = useQuery(shopCatalogQueryOptions())
  const wallet = useWalletSummary()
  const balance = wallet.data?.balance ?? 0
  const onboardingRequired = searchParams.get('required') === '1'
  const hasCompanion = Boolean(shop.data?.active_companion)
  const purchasesEnabled = shop.data?.purchases_enabled ?? true

  const purchase = useMutation({
    mutationFn: ({ kind, slug }: { kind: ShopKind; slug: string }) => shopApi.purchase(kind, slug),
    onSuccess: async (result) => {
      await Promise.all([
        queryClient.cancelQueries({ queryKey: queryKeys.shopCatalog }),
        queryClient.cancelQueries({ queryKey: queryKeys.wallet }),
      ])
      notifyManager.batch(() => {
        queryClient.setQueryData(queryKeys.shopCatalog, result.shop)
        queryClient.setQueryData(queryKeys.wallet, result.wallet)
      })
    },
  })
  const companions = useMemo(
    () => (shop.data?.items ?? []).filter(hasLocalDefinition).map(toDisplayItem),
    [shop.data],
  )

  const actionError = purchase.error
  const pending = purchase.isPending

  function act(item: ShopDisplayItem) {
    if (item.owned) {
      navigate(`${HOME_ROUTE}?tab=loadout`)
      return
    }
    if (actionDisabled(item, pending, balance, wallet.isPending, purchasesEnabled)) return
    purchase.mutate({ kind: item.kind, slug: item.slug })
  }

  return (
    <div className="shop-ref-page">
      <div className="shop-ref-backdrop" aria-hidden="true" />

      <div className="shop-ref-layout">
        <header className="shop-page-header">
          <div className="shop-page-title">
            <span>Citadel quartermaster</span>
            <h1>Armory</h1>
            <p>Choose your adventurer for the journey ahead.</p>
          </div>
          <div className="shop-rail-balance" aria-label="GitCoin balance" data-onboarding="shop-balance">
            <GitCoinIcon />
            <span>
              <small>Balance</small>
              <strong>{wallet.isPending ? '---' : formatCoins(balance)}</strong>
            </span>
          </div>
        </header>

        <ShopOnboarding
          ready={shop.isSuccess && wallet.isSuccess}
          ownsCompanion={companions.some((item) => item.owned)}
          canBuy={purchasesEnabled && companions.some((item) => !item.owned && item.price <= balance)}
        />

        {onboardingRequired && !guidedSetup ? (
          <div className="shop-onboarding-banner" role="status">
            {hasCompanion ? (
              <>
                <CheckCircle2 aria-hidden="true" />
                <span>Your adventurer is ready. Head to the Map to take on your first level.</span>
                <Link className="shop-onboarding-cta" to={storyPath()}>
                  To the Map
                </Link>
              </>
            ) : (
              <>
                <Sparkles aria-hidden="true" />
                <span>Choose your first companion below — you can't start an adventure without one.</span>
              </>
            )}
          </div>
        ) : null}

        {!purchasesEnabled ? (
          <div className="shop-onboarding-banner" role="status">
            <span>Purchases are temporarily paused. You can still browse the companions you own.</span>
          </div>
        ) : null}

        {shop.isPending ? (
          <section className="shop-view">
            <LoadingState label="Loading shop" description="Fetching your companions." />
          </section>
        ) : null}

        {shop.isError ? (
          <section className="shop-view shop-error-panel">
            <ErrorState title="Could not load shop" description={errorMessage(shop.error)} />
          </section>
        ) : null}

        {actionError ? (
          <section className="shop-action-error" aria-live="assertive">
            <ErrorState title="Shop action failed" description={errorMessage(actionError)} />
          </section>
        ) : null}

        {shop.isSuccess ? (
          <CompanionShop
            balance={balance}
            companions={companions}
            onAction={act}
            pending={pending}
            purchasesEnabled={purchasesEnabled}
            walletPending={wallet.isPending}
          />
        ) : null}
      </div>
    </div>
  )
}
