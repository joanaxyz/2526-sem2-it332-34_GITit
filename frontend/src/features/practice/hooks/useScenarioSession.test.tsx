import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { useScenarioSession } from '@/features/practice/hooks/useScenarioSession'
import type { ScenarioSession } from '@/features/practice/types'
import { writeSessionBootstrap } from '@/features/scenarios/utils/sessionBootstrap'
import { queryKeys } from '@/shared/api/queryKeys'

vi.mock('@/features/practice/api/practiceApi', () => ({
  practiceApi: {
    getSession: vi.fn(),
  },
}))

const bootstrapSession = { id: 7, status: 'started', steps: [] } as ScenarioSession

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  }
}

describe('useScenarioSession', () => {
  it('uses session bootstrap as initial data before the network request resolves', async () => {
    writeSessionBootstrap(bootstrapSession)
    vi.mocked(practiceApi.getSession).mockImplementation(
      () => new Promise(() => {}),
    )

    const { result } = renderHook(() => useScenarioSession(7), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.session).toEqual(bootstrapSession)
      expect(result.current.query.isLoading).toBe(false)
    })
  })

  it('prefers react-query cache over bootstrap', async () => {
    const cachedSession = { id: 7, status: 'completed', steps: [] } as ScenarioSession
    writeSessionBootstrap(bootstrapSession)
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    queryClient.setQueryData(queryKeys.scenarioSession(7), cachedSession)
    vi.mocked(practiceApi.getSession).mockImplementation(
      () => new Promise(() => {}),
    )

    function Wrapper({ children }: { children: React.ReactNode }) {
      return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    }

    const { result } = renderHook(() => useScenarioSession(7), { wrapper: Wrapper })

    await waitFor(() => {
      expect(result.current.session).toEqual(cachedSession)
    })
  })
})
