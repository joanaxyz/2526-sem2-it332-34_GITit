import { renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { AdventureRun } from '@/features/adventures/types'
import { useAdventureLevelAssets } from './useAdventureLevelAssets'

const warmed = vi.hoisted(() => ({
  manifests: [] as unknown[],
  release: null as null | (() => void),
}))

vi.mock('@/shared/battle/battleAssets', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/shared/battle/battleAssets')>()
  return {
    ...actual,
    battleAssetsWarm: () => false,
    warmBattleAssets: (manifest: unknown) => {
      warmed.manifests.push(manifest)
      return new Promise<void>((resolve) => {
        warmed.release = resolve
      })
    },
  }
})

const run = {
  id: 102,
  status: 'started',
  total_waves: 1,
  current_wave: 1,
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  battle_stage: null,
  mastery: {
    commands: [
      {
        slug: 'current-directory',
        form_id: 9,
        form_slug: 'current-directory',
        skill_slug: 'git-init',
        title: 'Initialize the current folder',
        strength: 0,
        mastered_bar: 1,
        introduced: false,
        mastered: false,
      },
    ],
    commands_mastered: 0,
    total_commands: 1,
    total_achievable: 1,
    passed: false,
  },
  current_attempt: {
    id: 202,
    wave: 0,
    command_budget: { min_counted_commands: 1, max_counted_commands: 3 },
  },
} as unknown as AdventureRun

function finishWarming() {
  warmed.release?.()
  warmed.release = null
}

beforeEach(() => {
  warmed.manifests = []
  warmed.release = null
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('useAdventureLevelAssets', () => {
  it('holds the level closed until its art is decoded', async () => {
    const { result } = renderHook(() =>
      useAdventureLevelAssets({ run, companionSlug: 'blue', enabled: true }),
    )

    expect(result.current).toBe(false)

    finishWarming()

    await waitFor(() => expect(result.current).toBe(true))
  })

  it('waits for the equipped companion before claiming any art', () => {
    renderHook(() => useAdventureLevelAssets({ run, companionSlug: 'blue', enabled: false }))

    expect(warmed.manifests).toHaveLength(0)
  })

  it('opens immediately when there is no attempt to stage', () => {
    const finished = { ...run, current_attempt: null } as unknown as AdventureRun
    const { result } = renderHook(() =>
      useAdventureLevelAssets({ run: finished, companionSlug: 'blue', enabled: true }),
    )

    expect(result.current).toBe(true)
    expect(warmed.manifests).toHaveLength(0)
  })

  it('never re-gates a live run when a wave swap re-seeds the encounter', async () => {
    const { rerender, result } = renderHook(
      (props: { run: AdventureRun }) =>
        useAdventureLevelAssets({ run: props.run, companionSlug: 'blue', enabled: true }),
      { initialProps: { run } },
    )

    finishWarming()
    await waitFor(() => expect(result.current).toBe(true))

    const nextWave = {
      ...run,
      current_wave: 2,
      current_attempt: { ...run.current_attempt, id: 203, wave: 1 },
    } as unknown as AdventureRun
    rerender({ run: nextWave })

    expect(result.current).toBe(true)
    expect(warmed.manifests).toHaveLength(1)
  })
})
