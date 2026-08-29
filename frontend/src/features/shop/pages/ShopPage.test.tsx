import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { useEffect } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ShopDisplayItem } from '@/shared/shop/model/shopPresentation'

vi.mock('@/features/shop/components/CompanionShop', () => ({
  CompanionShop: ({
    companions,
    onAction,
  }: {
    companions: ShopDisplayItem[]
    onAction: (item: ShopDisplayItem) => void
  }) => {
    const companion = companions[0]
    if (!companion) return null
    return (
      <section>
        <output data-testid="shop-companion-state">
          {companion.owned ? 'owned' : 'unowned'}|{companion.active ? 'active' : 'inactive'}
        </output>
        <button type="button" onClick={() => onAction(companion)}>
          Buy companion
        </button>
      </section>
    )
  },
}))

vi.mock('@/features/shop/components/StoryShop', () => ({
  StoryShop: () => null,
}))

vi.mock('@/features/shop/components/ShopTabs', () => ({
  ShopTabs: ({ balance }: { balance: number }) => (
    <output data-testid="shop-balance">{balance}</output>
  ),
}))

import { ShopPage } from '@/features/shop/pages/ShopPage'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import {
  shopApi,
  type ShopCatalog,
  type ShopPurchaseResult,
} from '@/shared/shop/api/shopApi'
import { walletApi } from '@/shared/wallet/api/walletApi'
import { useWalletSummary } from '@/shared/wallet/hooks/useWallet'

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((promiseResolve) => {
    resolve = promiseResolve
  })
  return { promise, resolve }
}

function makeCatalog({ owned, active }: { owned: boolean; active: boolean }): ShopCatalog {
  return {
    active_companion: active ? 'blue' : null,
    purchases_enabled: true,
    items: [
      {
        kind: 'companion',
        slug: 'blue',
        label: 'Blue',
        price: 150,
        owned,
        active,
      },
    ],
  }
}

function SharedObservers({ snapshots }: { snapshots: string[] }) {
  const wallet = useWalletSummary()
  const loadout = usePlayerLoadout()
  const snapshot = `${wallet.data?.balance ?? 'pending'}|${loadout.hasCompanion ? loadout.companionSlug : 'none'}`

  useEffect(() => {
    snapshots.push(snapshot)
  }, [snapshot, snapshots])

  return <output data-testid="shared-observers">{snapshot}</output>
}

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('ShopPage purchase cache convergence', () => {
  it('awaits both stale-read cancellations, installs one atomic snapshot, and ignores late results', async () => {
    const oldCatalog = makeCatalog({ owned: false, active: false })
    const purchasedCatalog = makeCatalog({ owned: true, active: true })
    const purchaseResult: ShopPurchaseResult = {
      owned: true,
      shop: purchasedCatalog,
      wallet: { balance: 0 },
    }
    const staleCatalog = deferred<ShopCatalog>()
    const staleWallet = deferred<{ balance: number }>()
    const catalogCancelGate = deferred<void>()
    const walletCancelGate = deferred<void>()
    const requestLog: string[] = []
    const snapshots: string[] = []

    const catalogRequest = vi
      .spyOn(shopApi, 'catalog')
      .mockImplementationOnce(async () => {
        requestLog.push('catalog:get:initial')
        return oldCatalog
      })
      .mockImplementationOnce(() => {
        requestLog.push('catalog:get:stale')
        return staleCatalog.promise
      })
      .mockImplementation(async () => {
        requestLog.push('catalog:get:unexpected')
        throw new Error('Unexpected catalog read after purchase')
      })
    const walletRequest = vi
      .spyOn(walletApi, 'summary')
      .mockImplementationOnce(async () => {
        requestLog.push('wallet:get:initial')
        return { balance: 150 }
      })
      .mockImplementationOnce(() => {
        requestLog.push('wallet:get:stale')
        return staleWallet.promise
      })
      .mockImplementation(async () => {
        requestLog.push('wallet:get:unexpected')
        throw new Error('Unexpected wallet read after purchase')
      })
    vi.spyOn(shopApi, 'purchase').mockImplementation(async () => {
      requestLog.push('purchase:post')
      return purchaseResult
    })

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })
    const realCancelQueries = queryClient.cancelQueries.bind(queryClient)
    const cancelQueries = vi.spyOn(queryClient, 'cancelQueries').mockImplementation(
      async (filters, options) => {
        await realCancelQueries(filters, options)
        if (filters?.queryKey?.[0] === queryKeys.shopCatalog[0]) {
          requestLog.push('catalog:cancel:start')
          await catalogCancelGate.promise
          requestLog.push('catalog:cancel:finish')
          return
        }
        requestLog.push('wallet:cancel:start')
        await walletCancelGate.promise
        requestLog.push('wallet:cancel:finish')
      },
    )

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/shop?tab=companions']}>
          <ShopPage />
          <SharedObservers snapshots={snapshots} />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('shared-observers')).toHaveTextContent('150|none'))
    expect(screen.getByTestId('shop-balance')).toHaveTextContent('150')
    expect(screen.getByTestId('shop-companion-state')).toHaveTextContent('unowned|inactive')

    let catalogRefetch!: Promise<void>
    let walletRefetch!: Promise<void>
    act(() => {
      catalogRefetch = queryClient.refetchQueries({ queryKey: queryKeys.shopCatalog })
      walletRefetch = queryClient.refetchQueries({ queryKey: queryKeys.wallet })
    })
    await waitFor(() => {
      expect(catalogRequest).toHaveBeenCalledTimes(2)
      expect(walletRequest).toHaveBeenCalledTimes(2)
    })

    fireEvent.click(screen.getByRole('button', { name: 'Buy companion' }))
    await waitFor(() => expect(requestLog).toContain('wallet:cancel:start'))
    expect(screen.getByTestId('shared-observers')).toHaveTextContent('150|none')

    await act(async () => catalogCancelGate.resolve())
    expect(screen.getByTestId('shared-observers')).toHaveTextContent('150|none')

    await act(async () => walletCancelGate.resolve())
    await waitFor(() => expect(screen.getByTestId('shared-observers')).toHaveTextContent('0|blue'))
    expect(screen.getByTestId('shop-balance')).toHaveTextContent('0')
    expect(screen.getByTestId('shop-companion-state')).toHaveTextContent('owned|active')
    expect(cancelQueries).toHaveBeenCalledTimes(2)

    await act(async () => {
      staleCatalog.resolve(oldCatalog)
      staleWallet.resolve({ balance: 150 })
      await Promise.all([catalogRefetch, walletRefetch])
    })

    expect(queryClient.getQueryData(queryKeys.shopCatalog)).toEqual(purchasedCatalog)
    expect(queryClient.getQueryData(queryKeys.wallet)).toEqual({ balance: 0 })
    expect(screen.getByTestId('shared-observers')).toHaveTextContent('0|blue')
    expect(snapshots).not.toContain('150|blue')
    expect(snapshots).not.toContain('0|none')
    expect(requestLog.slice(requestLog.indexOf('purchase:post') + 1)).not.toEqual(
      expect.arrayContaining(['catalog:get:unexpected', 'wallet:get:unexpected']),
    )
    expect(requestLog.filter((entry) => entry.includes(':get:'))).toEqual([
      'catalog:get:initial',
      'wallet:get:initial',
      'catalog:get:stale',
      'wallet:get:stale',
    ])
    queryClient.clear()
  })
})
