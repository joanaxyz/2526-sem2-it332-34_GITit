import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { AdventureLevelSummary, AdventureLevelTierAccess, TierTransferCheckpointRow } from '@/features/story-map/types'
import { StoryLevelTierPanel } from './StoryAdventurePanels'

afterEach(cleanup)

function tier(id: number, difficulty: AdventureLevelTierAccess['difficulty'], checkpoint: TierTransferCheckpointRow | null = null) {
  return {
    id, difficulty, locked: false, completion: null, transfer_checkpoint: checkpoint,
    scenario_progress: { completed: 0, total: 2 }, reward: { coins: 0, claimed: true },
  } as AdventureLevelTierAccess
}

function renderPanel(checkpoint: TierTransferCheckpointRow | null) {
  const open = vi.fn()
  const level = {
    id: 3, title: 'Resolving Conflicts', locked: false, is_passed: true,
    drill: { available: false, cleared: false, best_accuracy: 0 },
    tiers: [tier(1, 'easy'), tier(2, 'medium'), tier(9, 'hard', checkpoint)],
  } as unknown as AdventureLevelSummary
  render(
    <StoryLevelTierPanel
      level={level} levelNumber={1} placement="inline" panelRef={{ current: null }}
      onClose={() => {}} onStartTier={() => {}} onOpenTransfer={open} onOpenDrill={() => {}}
    />,
  )
  return open
}

describe('the level node transfer checkpoint row', () => {
  it('stays hidden until the checkpoint is assigned', () => {
    renderPanel(null)
    expect(screen.queryByText('Transfer checkpoint')).not.toBeInTheDocument()
  })

  it.each([
    ['ready', 'Start', 'One unfamiliar problem, no hints'],
    ['in_progress', 'Resume', 'First attempt in progress'],
    ['recorded', 'Practice', 'Result recorded · practice is ungraded'],
  ] as const)('offers %s without showing how the attempt went', (status, action, meta) => {
    const checkpoint = { status, run_id: status === 'in_progress' ? 42 : null }
    const open = renderPanel(checkpoint)
    expect(screen.getByText(meta)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: `Resolving Conflicts, transfer checkpoint: ${action}` }))
    expect(open).toHaveBeenCalledWith(9, checkpoint)
  })
})
