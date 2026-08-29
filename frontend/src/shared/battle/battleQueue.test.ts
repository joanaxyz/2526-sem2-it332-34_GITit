import { describe, expect, it } from 'vitest'

import { BattleQueue } from '@/shared/battle/battleQueue'

const tick = (ms = 30) => new Promise((resolve) => setTimeout(resolve, ms))

describe('BattleQueue fast-forward', () => {
  it('fast-forwards only the queued backlog, not commands enqueued afterward', async () => {
    const queue = new BattleQueue()
    const fast: Record<string, boolean> = {}
    let releaseCurrent: () => void = () => {}

    queue.enqueue(
      {
        run: (ctx) => {
          fast.current = ctx.fast
          return new Promise<void>((resolve) => {
            releaseCurrent = resolve
          })
        },
      },
      { run: (ctx) => void (fast.backlog1 = ctx.fast) },
      { run: (ctx) => void (fast.backlog2 = ctx.fast) },
    )

    await Promise.resolve() // let the first (blocking) step start
    queue.fastForward() // only backlog1 + backlog2 should skip
    // A new command submitted now: it must still animate at full speed.
    queue.enqueue({ run: (ctx) => void (fast.newCommand = ctx.fast) })
    releaseCurrent()
    await tick()

    expect(fast.backlog1).toBe(true)
    expect(fast.backlog2).toBe(true)
    expect(fast.newCommand).toBe(false)
  })

  it('drops cosmetic backlog steps on fast-forward but always runs snap steps', async () => {
    const queue = new BattleQueue()
    const ran: string[] = []
    let releaseCurrent: () => void = () => {}

    queue.enqueue(
      {
        run: () =>
          new Promise<void>((resolve) => {
            releaseCurrent = resolve
          }),
      },
      { cosmetic: true, run: () => void ran.push('cosmetic') },
      { run: () => void ran.push('snap') },
    )

    await Promise.resolve()
    queue.fastForward()
    releaseCurrent()
    await tick()

    expect(ran).toEqual(['snap'])
  })
})
