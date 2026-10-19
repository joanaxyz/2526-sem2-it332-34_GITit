import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { LearningChapter } from '@/features/story-map/types'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { queryKeys } from '@/shared/api/queryKeys'

import { ChapterProgressRewards } from './ChapterProgressRewards'

const chapter: LearningChapter = {
  id: 1, slug: 'module-1', number: 1, title: 'Module 1', description: '', sort_order: 1,
  is_playable: true, is_orientation: false, locked: false, lock_reason: '', story: null,
  command_skill_count: 1, adventure_level_count: 4, challenge_count: 0,
  level_completion: { numerator: 2, denominator: 4, value: 50 },
  chest_schedule: [{ threshold: 25, coins: 25 }, { threshold: 50, coins: 60 }, { threshold: 75, coins: 100 }, { threshold: 100, coins: 150 }],
}

function summary(): ApiSchemas['ChapterChestRewards'] {
  return {
    balance: 25, coins_awarded: 0,
    results: chapter.chest_schedule.map((chest) => ({ ...chest, unlocked: chest.threshold <= 50, claimed: chest.threshold === 25 })),
  }
}

function renderRewards(preview = false) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const invalidate = vi.spyOn(client, 'invalidateQueries')
  render(<QueryClientProvider client={client}><ChapterProgressRewards chapter={chapter} preview={preview} /></QueryClientProvider>)
  return { client, invalidate }
}

describe('ChapterProgressRewards', () => {
  beforeEach(() => {
    vi.spyOn(storyMapApi, 'getChapterChests').mockResolvedValue(summary())
    vi.spyOn(storyMapApi, 'openChapterChest')
  })
  afterEach(() => { cleanup(); vi.restoreAllMocks() })

  it('uses ledger status for collected, available, and locked chests', async () => {
    renderRewards()
    const collected = await screen.findByRole('button', { name: '25% chest: Collected, 25 GitCoins' })
    expect(collected).toHaveAttribute('data-claimed', 'true')
    const available = screen.getByRole('button', { name: '50% chest: Open chest, 60 GitCoins' })
    expect(available).toHaveAttribute('data-claimed', 'false')
    expect(available).toHaveAttribute('data-earned', 'true')
    const locked = screen.getByRole('button', { name: '75% chest: Locked, 100 GitCoins' })
    expect(locked).toBeDisabled()
    expect(locked).toHaveAttribute('data-earned', 'false')
    fireEvent.click(collected)
    expect(screen.getByRole('dialog')).toHaveTextContent('Already in your wallet')
    expect(storyMapApi.openChapterChest).not.toHaveBeenCalled()
  })

  it('collects through the API once, refreshes the wallet, and reveals the reward', async () => {
    let resolveOpen!: (value: ApiSchemas['ChapterChestRewards']) => void
    vi.mocked(storyMapApi.openChapterChest).mockImplementation(() => new Promise((resolve) => { resolveOpen = resolve }))
    const { client, invalidate } = renderRewards()
    const available = await screen.findByRole('button', { name: '50% chest: Open chest, 60 GitCoins' })
    fireEvent.click(available)
    await waitFor(() => expect(available).toBeDisabled())
    fireEvent.click(available)
    expect(storyMapApi.openChapterChest).toHaveBeenCalledExactlyOnceWith(1, 50)
    const paid = summary()
    paid.balance = 85
    paid.coins_awarded = 60
    paid.results[1].claimed = true
    resolveOpen(paid)
    const dialog = await screen.findByRole('dialog')
    expect(dialog).toHaveTextContent('+60 GitCoins')
    expect(dialog).toHaveTextContent('Reward collected!')
    expect(within(dialog).queryByRole('button')).not.toBeInTheDocument()
    expect(invalidate).toHaveBeenCalledWith({ queryKey: queryKeys.wallet })
    expect(client.getQueryData(queryKeys.chapterChests(1))).toEqual(paid)
    fireEvent.click(dialog)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '50% chest: Collected, 60 GitCoins' }))
    expect(storyMapApi.openChapterChest).toHaveBeenCalledTimes(1)
  })

  it.each(['backdrop', 'chest', 'reward', 'status', 'hint'])('closes the reveal when clicking its %s', async (target) => {
    renderRewards()
    fireEvent.click(await screen.findByRole('button', { name: '25% chest: Collected, 25 GitCoins' }))
    const dialog = screen.getByRole('dialog', { name: '25% progress chest' })
    expect(within(dialog).queryByRole('button')).not.toBeInTheDocument()
    expect(dialog).toHaveTextContent('25% milestone')
    const clickTarget = target === 'chest' ? within(dialog).getByRole('img', { name: 'Opened reward chest filled with GitCoins' })
      : target === 'reward' ? within(dialog).getByRole('heading', { name: '+25 GitCoins' })
      : target === 'status' ? within(dialog).getByText('Reward collected · Already in your wallet.')
      : target === 'hint' ? within(dialog).getByText('Click anywhere to close')
      : dialog
    fireEvent.click(clickTarget)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(storyMapApi.openChapterChest).not.toHaveBeenCalled()
  })

  it.each(['Escape', 'Enter', ' '])('closes the reveal with %s and restores focus to the chest', async (key) => {
    renderRewards()
    const collected = await screen.findByRole('button', { name: '25% chest: Collected, 25 GitCoins' })
    collected.focus()
    fireEvent.click(collected)
    const dialog = screen.getByRole('dialog')
    await waitFor(() => expect(dialog).toHaveFocus())
    fireEvent.keyDown(dialog, { key })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(collected).toHaveFocus()
  })

  it('locks page scrolling and keeps Tab focus inside the buttonless reveal', async () => {
    const originalOverflow = document.body.style.overflow
    renderRewards()
    const collected = await screen.findByRole('button', { name: '25% chest: Collected, 25 GitCoins' })
    collected.focus()
    fireEvent.click(collected)
    const dialog = screen.getByRole('dialog')
    await waitFor(() => expect(dialog).toHaveFocus())
    expect(document.body.style.overflow).toBe('hidden')
    expect(fireEvent.keyDown(dialog, { key: 'Tab' })).toBe(false)
    expect(dialog).toHaveFocus()
    expect(fireEvent.keyDown(dialog, { key: 'Tab', shiftKey: true })).toBe(false)
    expect(dialog).toHaveFocus()
    fireEvent.click(within(dialog).getByRole('img'))
    expect(document.body.style.overflow).toBe(originalOverflow)
    expect(collected).toHaveFocus()
  })

  it('keeps failed collections available so the player can retry', async () => {
    vi.mocked(storyMapApi.openChapterChest).mockRejectedValueOnce(new Error('Connection lost. Try again.'))
    renderRewards()
    fireEvent.click(await screen.findByRole('button', { name: '50% chest: Open chest, 60 GitCoins' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Connection lost. Try again.')
    expect(screen.getByRole('button', { name: '50% chest: Open chest, 60 GitCoins' })).toBeEnabled()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('does not infer collected rewards from progress when loading fails', async () => {
    vi.mocked(storyMapApi.getChapterChests).mockRejectedValueOnce(new Error('Offline'))
    renderRewards()
    expect(screen.getAllByRole('button').every((button) => button.hasAttribute('disabled'))).toBe(true)
    expect(await screen.findByRole('alert')).toHaveTextContent('Could not check chest rewards.')
    fireEvent.click(screen.getByRole('button', { name: 'Retry rewards' }))
    expect(await screen.findByRole('button', { name: '25% chest: Collected, 25 GitCoins' })).toBeEnabled()
  })

  it('keeps design preview rewards separate from real player requests', () => {
    renderRewards(true)
    fireEvent.click(screen.getByRole('button', { name: '25% chest: Collected, 25 GitCoins' }))
    expect(screen.getByRole('dialog')).toHaveTextContent('Preview reward')
    expect(storyMapApi.getChapterChests).not.toHaveBeenCalled()
    expect(storyMapApi.openChapterChest).not.toHaveBeenCalled()
  })
})
