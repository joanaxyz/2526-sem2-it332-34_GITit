import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiError } from '@/shared/api/apiError'

vi.mock('@/features/admin/api/adminApi', () => ({
  adminApi: {
    moderation: vi.fn(),
    unpublish: vi.fn(),
  },
}))

import { adminApi } from '@/features/admin/api/adminApi'

import { AdminModerationPage } from './AdminModerationPage'

const moderation = vi.mocked(adminApi.moderation)
const unpublish = vi.mocked(adminApi.unpublish)

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminModerationPage />
    </QueryClientProvider>,
  )
}

describe('AdminModerationPage destructive action', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    vi.clearAllMocks()
  })

  it('requires confirmation and surfaces a precise mutation error', async () => {
    moderation.mockResolvedValue({
      content: [
        {
          id: 17,
          kind: 'lesson',
          owner: 'learner',
          title: 'Shared lesson',
          updated_at: '2026-07-23T00:00:00Z',
        },
      ],
    })
    unpublish.mockRejectedValue(
      new ApiError('Bad Request', 400, {
        detail: ['This content is no longer in the moderation queue.'],
      }),
    )
    renderPage()
    const button = await screen.findByRole('button', { name: 'Unpublish' })

    fireEvent.click(button)
    expect(screen.getByRole('group', { name: 'Confirm unpublish Shared lesson' })).toBeInTheDocument()
    expect(unpublish).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.queryByRole('button', { name: 'Confirm unpublish' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Unpublish' }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirm unpublish' }))
    await waitFor(() => {
      expect(unpublish).toHaveBeenCalledWith(
        { kind: 'content', id: 17 },
        expect.any(Object),
      )
      expect(screen.getByRole('alert')).toHaveTextContent(
        'This content is no longer in the moderation queue.',
      )
    })
  })
})
