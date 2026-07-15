import { afterEach, describe, expect, it, vi } from 'vitest'

import type { AdventureRun } from '@/features/adventures/types'

const mocks = vi.hoisted(() => ({
  startRun: vi.fn(),
}))

vi.mock('@/features/adventures/api/adventuresApi', () => ({
  adventuresApi: {
    startRun: mocks.startRun,
  },
}))

describe('startAdventureRun', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('shares an in-flight level start across concurrent callers', async () => {
    const { startAdventureRun } = await import('./useAdventureRun')
    const firstRun = { id: 101 } as AdventureRun
    const secondRun = { id: 102 } as AdventureRun
    let resolveStart: (run: AdventureRun) => void = () => {}
    const pendingStart = new Promise<AdventureRun>((resolve) => {
      resolveStart = resolve
    })
    mocks.startRun.mockReturnValueOnce(pendingStart)

    const first = startAdventureRun(501)
    const second = startAdventureRun(501)

    expect(mocks.startRun).toHaveBeenCalledTimes(1)
    expect(mocks.startRun).toHaveBeenCalledWith(501)

    resolveStart(firstRun)
    await expect(first).resolves.toBe(firstRun)
    await expect(second).resolves.toBe(firstRun)

    mocks.startRun.mockResolvedValueOnce(secondRun)
    await expect(startAdventureRun(501)).resolves.toBe(secondRun)
    expect(mocks.startRun).toHaveBeenCalledTimes(2)
  })
})
