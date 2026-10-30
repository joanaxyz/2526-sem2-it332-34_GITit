import { QueryClient, QueryClientProvider, focusManager, useQueryClient } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { useEffect, useState } from 'react'
import { Outlet, RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { HomeResultsPanel } from '@/features/home/components/home-stats/HomeResultsPanel'
import { queryKeys } from '@/shared/api/queryKeys'
import { useWalletSummary } from '@/shared/wallet/hooks/useWallet'
import { Component, HomePreviewLayout } from './HomePreviewPage'

const network = vi.hoisted(() => ({ performance: vi.fn(), wallet: vi.fn() }))
vi.mock('@/features/performance/api/performanceApi', () => ({ performanceApi: { summary: network.performance } }))
vi.mock('@/shared/wallet/api/walletApi', () => ({ walletApi: { summary: network.wallet } }))

// Keep the real record query and layout wallet query. Replace unrelated art,
// onboarding, profile and activity components so this tests fixture lifetime.
vi.mock('@/features/home/components/HomeHubView', () => ({
  HomeHubView: ({ playerName }: { playerName: string }) => <PreviewHub playerName={playerName} />,
}))
vi.mock('@/app/layouts/HomeLayout', () => ({
  HomeLayout: () => <><LayoutWallet /><Outlet /></>,
}))

let previewClient: QueryClient | undefined
const parentClients: QueryClient[] = []

function LayoutWallet() {
  const wallet = useWalletSummary()
  return <output data-testid="layout-wallet">{wallet.data?.balance}</output>
}

function PreviewHub({ playerName }: { playerName: string }) {
  const client = useQueryClient()
  useEffect(() => { previewClient = client }, [client])
  const [showRecord, setShowRecord] = useState(true)
  return <>
    <output data-testid="preview-name">{playerName}</output>
    <button onClick={() => setShowRecord((value) => !value)}>Toggle record</button>
    {showRecord ? <HomeResultsPanel /> : null}
  </>
}

function renderPreview() {
  const parentClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  parentClients.push(parentClient)
  const sentinel = { authenticated: 'untouched' }
  parentClient.setQueryData(queryKeys.performanceSummary, sentinel)
  parentClient.setQueryData(queryKeys.wallet, { balance: 9999 })
  const router = createMemoryRouter([
    { path: '/design-preview/home', element: <HomePreviewLayout />, children: [{ index: true, element: <Component /> }] },
    { path: '/outside', element: <p>Outside preview</p> },
  ], { initialEntries: ['/design-preview/home?view=progress'] })
  render(<QueryClientProvider client={parentClient}><RouterProvider router={router} /></QueryClientProvider>)
  return { router, parentClient, sentinel }
}

afterEach(() => {
  cleanup()
  parentClients.splice(0).forEach((client) => client.clear())
  previewClient = undefined
  focusManager.setFocused(undefined)
  vi.restoreAllMocks()
  vi.clearAllMocks()
})

describe('DEV Home preview fixture isolation', () => {
  it('retains fixtures after staleness, invalidation, focus and record/page remounts without a request', async () => {
    network.performance.mockRejectedValue(new Error('Preview must not call the API'))
    network.wallet.mockRejectedValue(new Error('Preview shell must not call the API'))
    const { router, parentClient, sentinel } = renderPreview()
    expect(within(screen.getByRole('group', { name: 'Overall KPIs' })).getByText('75.4%')).toBeInTheDocument()
    expect(screen.getByTestId('layout-wallet')).toHaveTextContent('1240')
    expect(previewClient).not.toBe(parentClient)

    vi.spyOn(Date, 'now').mockReturnValue(Date.now() + 10 * 60_000)
    await act(async () => {
      await previewClient!.invalidateQueries()
      focusManager.setFocused(false)
      focusManager.setFocused(true)
    })
    fireEvent.click(screen.getByRole('button', { name: 'Toggle record' }))
    expect(screen.queryByRole('group', { name: 'Overall KPIs' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Toggle record' }))
    expect(within(screen.getByRole('group', { name: 'Overall KPIs' })).getByText('75.4%')).toBeInTheDocument()

    await act(async () => { await router.navigate('/outside') })
    await act(async () => { await router.navigate('/design-preview/home?view=progress') })
    expect(within(screen.getByRole('group', { name: 'Overall KPIs' })).getByText('75.4%')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(network.performance).not.toHaveBeenCalled()
    expect(network.wallet).not.toHaveBeenCalled()
    expect(parentClient.getQueryData(queryKeys.performanceSummary)).toBe(sentinel)
    expect(parentClient.getQueryData(queryKeys.wallet)).toEqual({ balance: 9999 })
    expect(parentClient.getDefaultOptions().queries?.enabled).toBeUndefined()
  })

  it('switches rich and empty fixtures in both directions without changing the authenticated cache', async () => {
    const { router, parentClient, sentinel } = renderPreview()
    const richClient = previewClient
    await act(async () => { await router.navigate('/design-preview/home?view=progress&empty=1') })
    expect(previewClient).not.toBe(richClient)
    expect(screen.getByTestId('preview-name')).toHaveTextContent('newcomer')
    expect(screen.getByTestId('layout-wallet')).toHaveTextContent('0')
    const readings = screen.getByRole('group', { name: 'Overall KPIs' })
    expect(within(readings).getAllByText('—')).toHaveLength(5)
    expect(within(readings).getAllByText('Not measured yet')).toHaveLength(5)

    await act(async () => { await router.navigate('/design-preview/home?view=progress') })
    expect(screen.getByTestId('preview-name')).toHaveTextContent('Learner')
    expect(screen.getByTestId('layout-wallet')).toHaveTextContent('1240')
    expect(within(screen.getByRole('group', { name: 'Overall KPIs' })).getByText('75.4%')).toBeInTheDocument()
    expect(network.performance).not.toHaveBeenCalled()
    expect(network.wallet).not.toHaveBeenCalled()
    expect(parentClient.getQueryData(queryKeys.performanceSummary)).toBe(sentinel)
  })
})
