import { renderHook } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

import { useLeaveAbandonedRun } from './useLeaveAbandonedRun'

function tierRun(status: TierRun['status']) {
  return {
    status,
    story: { slug: 'git-it-legacy' },
    chapter: { id: 4 },
  } as unknown as TierRun
}

describe('useLeaveAbandonedRun', () => {
  it('sends an abandoned run back to its map, replacing the history entry', () => {
    const navigate = vi.fn()

    renderHook(() => useLeaveAbandonedRun(tierRun('abandoned'), navigate))

    expect(navigate).toHaveBeenCalledTimes(1)
    expect(navigate.mock.calls[0][0]).toContain('chapter=4')
    expect(navigate.mock.calls[0][1]).toEqual({ replace: true })
  })

  it.each(['started', 'completed', 'failed'] as const)('leaves a %s run in place', (status) => {
    const navigate = vi.fn()

    renderHook(() => useLeaveAbandonedRun(tierRun(status), navigate))

    expect(navigate).not.toHaveBeenCalled()
  })
})
