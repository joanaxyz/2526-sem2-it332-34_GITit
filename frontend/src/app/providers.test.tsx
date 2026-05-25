import { QueryClient, useQueryClient } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ApiError } from '@/shared/api/apiError'
import { AppProviders } from './providers'

function QueryClientProbe({ onClient }: { onClient: (client: QueryClient) => void }) {
  const client = useQueryClient()
  onClient(client)
  return <div>Provider ready</div>
}

describe('AppProviders', () => {
  afterEach(() => {
    cleanup()
  })

  it('provides a React Query client with conservative defaults', () => {
    let queryClient: QueryClient | undefined

    render(
      <AppProviders>
        <QueryClientProbe onClient={(client) => {
          queryClient = client
        }} />
      </AppProviders>,
    )

    expect(screen.getByText('Provider ready')).toBeInTheDocument()
    expect(queryClient).toBeDefined()
    const client = queryClient as QueryClient
    const queryDefaults = client.getDefaultOptions().queries
    const retry = queryDefaults?.retry

    expect(queryDefaults?.staleTime).toBe(30_000)
    expect(queryDefaults?.refetchOnWindowFocus).toBe(false)
    expect(typeof retry).toBe('function')
    expect(typeof retry === 'function' ? retry(0, new ApiError('Nope', 404, null)) : null).toBe(false)
    expect(typeof retry === 'function' ? retry(0, new Error('Temporary failure')) : null).toBe(true)
    expect(typeof retry === 'function' ? retry(1, new Error('Temporary failure')) : null).toBe(false)
  })
})
