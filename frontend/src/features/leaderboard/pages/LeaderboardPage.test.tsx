import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { leaderboardApi, type Leaderboard } from '@/features/leaderboard/api/leaderboardApi'
import { LeaderboardPage } from '@/features/leaderboard/pages/LeaderboardPage'

const board: Leaderboard = {
  category: 'xp',
  entries: [
    { rank: 1, username: 'ada', companion_slug: 'white', value: 3200, is_you: false },
    { rank: 2, username: 'linus', companion_slug: 'blue', value: 600, is_you: true },
  ],
  you: { rank: 2, value: 600, hidden: false },
}

function renderPage(initialEntry = '/') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[initialEntry]}>
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
    expect(screen.getByText('linus').closest('li')).toHaveTextContent('You')
    expect(screen.getByText(/Your rank/)).toHaveTextContent('#2')
    expect(screen.getByRole('link', { name: 'Continue your journey' })).toHaveAttribute('href', '/stories/arcane-spire')
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

  it('shows the equipped companion and falls back when its image cannot load', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue(board)
    renderPage()

    const learner = (await screen.findByText('ada')).closest('li')!
    const avatar = learner.querySelector('img[src="/cosmetics/companion/white/avatar.lossless.webp"]')!
    expect(avatar).toBeInTheDocument()

    fireEvent.error(avatar)

    expect(within(learner).getByText('AD')).toBeInTheDocument()
    expect(learner.querySelector('img[src="/cosmetics/companion/white/avatar.lossless.webp"]')).toBeNull()
  })

  it('uses initials for absent and unknown companion selections', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue({
      ...board,
      entries: [
        { ...board.entries[0], companion_slug: null },
        { ...board.entries[1], companion_slug: '__proto__' },
      ],
    })
    renderPage()

    const first = (await screen.findByText('ada')).closest('li')!
    const second = screen.getByText('linus').closest('li')!
    expect(within(first).getByText('AD')).toBeInTheDocument()
    expect(within(second).getByText('LI')).toBeInTheDocument()
    expect(first.querySelector('img[src*="/cosmetics/companion/"]')).toBeNull()
    expect(second.querySelector('img[src*="/cosmetics/companion/"]')).toBeNull()
  })

  it('preserves shared places and awards the same frame to tied champions', async () => {
    vi.spyOn(leaderboardApi, 'get').mockResolvedValue({
      ...board,
      category: 'perfect_clears',
      entries: [
        { ...board.entries[0], rank: 1, value: 20 },
        { ...board.entries[1], rank: 1, value: 20 },
        { rank: 3, username: 'grace', companion_slug: null, value: 10, is_you: false },
        { rank: 3, username: 'alan', companion_slug: 'black', value: 10, is_you: false },
      ],
      you: { rank: 1, value: 20, hidden: false },
    })
    renderPage('/?category=perfect_clears')

    const first = (await screen.findByText('ada')).closest('li')!
    const second = screen.getByText('linus').closest('li')!
    expect(first).toHaveAttribute('value', '1')
    expect(second).toHaveAttribute('value', '1')
    expect(first.querySelector('img[src="/leaderboard/frame-gold.webp"]')).toBeInTheDocument()
    expect(second.querySelector('img[src="/leaderboard/frame-gold.webp"]')).toBeInTheDocument()
    expect(screen.getByText('alan').closest('li')).toHaveAttribute('value', '3')
    expect(screen.queryByText('Place 2')).not.toBeInTheDocument()
    expect(screen.queryByText(/Rank IV/)).not.toBeInTheDocument()
  })

  it('recovers from a failed request with the retry action', async () => {
    const get = vi.spyOn(leaderboardApi, 'get')
      .mockRejectedValueOnce(new Error('Connection interrupted'))
      .mockResolvedValue(board)
    renderPage()

    expect(await screen.findByText('Leaderboard unavailable')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Try again' }))

    expect(await screen.findByText('ada')).toBeInTheDocument()
    expect(get).toHaveBeenCalledTimes(2)
  })
})
