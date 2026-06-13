/**
 * Sequential choreography queue for the battle stage.
 *
 * The server answers a command in ~200–800ms but its choreography (cast →
 * projectile → hurt → HP drain → death) takes seconds, and the learner can
 * submit again mid-sequence. Steps are tagged `cosmetic` (flourishes safe to
 * skip) or state-snapping (HP bar values, deaths, DAG reveals — must always
 * run). `fastForward()` drops queued cosmetic steps and lets snap steps run
 * instantly, so the stage never lies about authoritative state for more than
 * the one step already playing.
 *
 * Plain class, no React: steps mutate actor refs / DOM and resolve via
 * animator onComplete callbacks or WAAPI `animation.finished`.
 */

export type StepContext = {
  /** True when the queue is being fast-forwarded: apply outcomes instantly. */
  fast: boolean
}

export type StageStep = {
  /** Safe to drop entirely on fast-forward (flights, flinches, celebrations). */
  cosmetic?: boolean
  run: (ctx: StepContext) => void | Promise<void>
}

export class BattleQueue {
  private steps: StageStep[] = []
  private draining = false
  private fastForwarded = false
  private disposed = false

  /** Append steps and start draining if idle. */
  enqueue(...steps: StageStep[]): void {
    if (this.disposed) return
    this.steps.push(...steps)
    void this.drain()
  }

  /** True while a step is running or steps are queued. */
  get busy(): boolean {
    return this.draining || this.steps.length > 0
  }

  /**
   * Skip the backlog: queued cosmetic steps are dropped, snap steps run with
   * `fast: true`. The step currently playing finishes naturally (it is at
   * most one beat long), which bounds the wait without abort plumbing.
   */
  fastForward(): void {
    this.fastForwarded = true
  }

  /** Drop everything, including snap steps. Unmount only. */
  dispose(): void {
    this.disposed = true
    this.steps = []
  }

  private async drain(): Promise<void> {
    if (this.draining) return
    this.draining = true
    try {
      while (this.steps.length > 0 && !this.disposed) {
        const step = this.steps.shift()!
        if (this.fastForwarded && step.cosmetic) continue
        try {
          await step.run({ fast: this.fastForwarded })
        } catch {
          // A failed flourish must never wedge the queue.
        }
      }
    } finally {
      this.fastForwarded = false
      this.draining = false
    }
  }
}
