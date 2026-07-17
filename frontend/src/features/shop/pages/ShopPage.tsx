import { CheckCircle2, Sparkles } from 'lucide-react'
import { useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { shopApi, type ShopKind } from '@/features/shop/api/shopApi'
import { CompanionShop } from '@/features/shop/components/CompanionShop'
import { GitCoinWallet } from '@/features/shop/components/GitCoinWallet'
import { ShopTabs } from '@/features/shop/components/ShopTabs'
import { StoryShop } from '@/features/shop/components/StoryShop'
import {
  actionDisabled,
  errorMessage,
  hasLocalDefinition,
  isShopTab,
  toDisplayItem,
  type ShopDisplayItem,
  type ShopTab,
} from '@/features/shop/utils/shopDisplay'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { HOME_ROUTE, STORIES_ROUTE, storyPath } from '@/shared/navigation/routes'
import { walletApi } from '@/shared/wallet/api/walletApi'

export function ShopPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const shop = useQuery({ queryKey: queryKeys.shopCatalog, queryFn: shopApi.catalog, staleTime: 60 * 1000 })
  const wallet = useQuery({ queryKey: queryKeys.wallet, queryFn: walletApi.summary, staleTime: 60 * 1000 })
  const balance = wallet.data?.balance ?? 0
  const tabParam = searchParams.get('tab')
  const activeTab: ShopTab = isShopTab(tabParam) ? tabParam : 'stories'
  const onboardingRequired = searchParams.get('required') === '1'
  const hasCompanion = Boolean(shop.data?.active_companion)

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.shopCatalog })
    queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
  }

  const purchase = useMutation({
    mutationFn: ({ kind, slug }: { kind: ShopKind; slug: string }) => shopApi.purchase(kind, slug),
    onSuccess: refresh,
  })
  const catalog = useMemo(() => {
    const items = (shop.data?.items ?? []).filter(hasLocalDefinition).map(toDisplayItem)
    return {
      stories: items.filter((item) => item.kind === 'story'),
      companions: items.filter((item) => item.kind === 'companion'),
    }
  }, [shop.data])

  const actionError = purchase.error
  const pending = purchase.isPending

  function setActiveTab(tab: ShopTab) {
    const next = new URLSearchParams(searchParams)
    if (tab === 'stories') next.delete('tab')
    else next.set('tab', tab)
    setSearchParams(next, { replace: true })
  }

  function act(item: ShopDisplayItem) {
    if (item.owned) {
      navigate(item.kind === 'story' ? STORIES_ROUTE : `${HOME_ROUTE}?tab=loadout`)
      return
    }
    if (actionDisabled(item, pending, balance, wallet.isPending)) return
    purchase.mutate({ kind: item.kind, slug: item.slug })
  }

  return (
    <div className="shop-ref-page" data-shop-tab={activeTab}>
      <div className="shop-ref-backdrop" aria-hidden="true" />

      <div className="shop-ref-layout">
        <header className="shop-page-header">
          <div className="shop-page-title">
            <span>Citadel quartermaster</span>
            <h1>Armory &amp; Archives</h1>
            <p>Unlock worlds, choose your adventurer, and track the GitCoins you earn in play.</p>
          </div>
          <ShopTabs activeTab={activeTab} balance={balance} walletPending={wallet.isPending} onTabChange={setActiveTab} />
        </header>

        {onboardingRequired ? (
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

        {shop.isPending && activeTab !== 'gitcoins' ? (
          <section className="shop-view">
            <LoadingState label="Loading shop" description="Fetching your story and companion unlocks." />
          </section>
        ) : null}

        {shop.isError && activeTab !== 'gitcoins' ? (
          <section className="shop-view shop-error-panel">
            <ErrorState title="Could not load shop" description={errorMessage(shop.error)} />
          </section>
        ) : null}

        {actionError ? (
          <section className="shop-action-error" aria-live="assertive">
            <ErrorState title="Shop action failed" description={errorMessage(actionError)} />
          </section>
        ) : null}

        {activeTab === 'gitcoins' ? (
          <GitCoinWallet
            balance={balance}
            recent={wallet.data?.recent ?? []}
            walletError={wallet.error}
            walletPending={wallet.isPending}
          />
        ) : null}

        {activeTab === 'stories' && shop.isSuccess ? (
          <StoryShop
            balance={balance}
            onAction={act}
            pending={pending}
            stories={catalog.stories}
            walletPending={wallet.isPending}
          />
        ) : null}

        {activeTab === 'companions' && shop.isSuccess ? (
          <CompanionShop
            balance={balance}
            companions={catalog.companions}
            onAction={act}
            pending={pending}
            walletPending={wallet.isPending}
          />
        ) : null}
      </div>
    </div>
  )
}
