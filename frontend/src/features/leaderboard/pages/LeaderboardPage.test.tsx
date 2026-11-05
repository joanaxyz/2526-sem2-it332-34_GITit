import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { leaderboardApi, type Leaderboard } from '@/features/leaderboard/api/leaderboardApi'
import { LeaderboardPage } from '@/features/leaderboard/pages/LeaderboardPage'

const board: Leaderboard = {
  category: 'xp',
  entries: [
    { rank: 1, username: 'ada', value: 3200, is_you: false },
    { rank: 2, username: 'linus', value: 600, is_you: true },
  ],
  you: { rank: 2, value: 600, hidden: false },
}

function renderPage() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <LeaderboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LeaderboardPage', () => {
  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('ranks by XP first and names each learner’s rank', async () => {
    const get = vi.spyOn(leaderboardApi, 'get').mockResolvedValue(board)
    renderPage()

    expect((await screen.findByText('ada')).closest('li')).toHaveTextContent('Rank IV · Baron')
    expect(get).toHaveBeenCalledWith('xp')
    expect(screen.getByRole('button', { name: 'XP' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('linus (you)')).toBeInTheDocument()
    expect(screen.queryByText(/Your rank/)).not.toBeInTheDocument()
  })

  it('offers exactly three categories, and no KPI or mastery board', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue(board)
    renderPage()

    const tabs = await screen.findByRole('group', { name: 'Leaderboard category' })
    expect(within(tabs).getAllByRole('button').map((tab) => tab.textContent)).toEqual([
      'XP', 'Perfect Clears', 'Challenge Gates',
    ])
  })

  it('switches category and drops the XP rank from other boards', async () => {
    const get = vi.spyOn(leaderboardApi, 'get').mockResolvedValue({ ...board, category: 'gates' })
    renderPage()
    await screen.findByText('ada')

    fireEvent.click(screen.getByRole('button', { name: 'Challenge Gates' }))

    await vi.waitFor(() => expect(get).toHaveBeenCalledWith('gates'))
    expect(screen.queryByText(/Rank IV/)).not.toBeInTheDocument()
  })

  it('pins your place when you are outside the top entries', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue({
      ...board,
      entries: [board.entries[0]],
      you: { rank: 14, value: 230, hidden: false },
    })
    renderPage()

    expect(await screen.findByText('#14')).toBeInTheDocument()
    expect(screen.getByText(/230 XP/)).toBeInTheDocument()
  })

  it('tells a hidden learner how to come back', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue({
      ...board,
      entries: [board.entries[0]],
      you: { rank: null, value: 600, hidden: true },
    })
    renderPage()

    expect(await screen.findByRole('link', { name: 'Change this in Settings' })).toHaveAttribute('href', '/settings')
  })

  it('says so when nobody is on a board', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue({
      ...board,
      entries: [],
      you: { rank: null, value: 0, hidden: false },
    })
    renderPage()

    expect(await screen.findByText('No one is on this board yet.')).toBeInTheDocument()
  })
})
