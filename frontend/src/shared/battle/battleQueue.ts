/**
 * Sequential choreography queue for the battle stage.
 *
 * The server answers a command in ~200-800ms but its choreography (attack ->
 * projectile -> hurt -> HP drain -> death) takes seconds, and the learner can
 * submit again mid-sequence. Steps are tagged `cosmetic` (flourishes safe to
 * skip) or state-snapping (HP bar values, deaths, DAG reveals - must always
 * run). `fastForward()` drops queued cosmetic steps and lets snap steps run
 * instantly, so the stage never lies about authoritative state for more than
 * the one step already playing.
 *
 * fastForward only skips the BACKLOG that exists at the moment it is called.
 * Steps enqueued afterwards (the new command the learner is now watching) play
 * at full animation - otherwise, submitting at a steady pace would leave the
 * queue perpetually fast-forwarded and no attack (yours or the monster's) would
 * ever animate.
 *
 * Plain class, no React: steps mutate actor refs / DOM and resolve via
 * animator onComplete callbacks or WAAPI `animation.finished`.
 */

type StepContext = {
  /** True when the queue is being fast-forwarded: apply outcomes instantly. */
  fast: boolean
}

export type StageStep = {
  /** Safe to drop entirely on fast-forward (flights, flinches, celebrations). */
  cosmetic?: boolean
  run: (ctx: StepContext) => void | Promise<void>
}

const COSMETIC_STEP_TIMEOUT_MS = 3200

function reportChoreographyError(error: unknown): void {
  if (!import.meta.env.DEV) return
  console.error('[battleQueue] Choreography step failed; queue recovered.', error)
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export class BattleQueue {
  private steps: StageStep[] = []
  private draining = false
  /** How many of the currently-queued steps still run in fast-forward. Only the
   *  backlog at fastForward() time is skipped; later steps animate normally. */
  private fastForwardRemaining = 0
  private disposed = false
  private releaseCurrentCosmetic: (() => void) | null = null
  private busyListeners = new Set<(busy: boolean) => void>()
  private busySnapshot = false

  subscribe(listener: (busy: boolean) => void): () => void {
    this.busyListeners.add(listener)
    listener(this.busy)
    return () => {
      this.busyListeners.delete(listener)
    }
  }

  /** Append steps and start draining if idle. */
  enqueue(...steps: StageStep[]): void {
    if (this.disposed) return
    this.steps.push(...steps)
    this.notifyBusy()
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
    // Skip only what is already queued; a command submitted after this still
    // plays its full choreography.
    this.fastForwardRemaining = this.steps.length
    this.releaseCurrentCosmetic?.()
  }

  /** React dev StrictMode remounts effects without recreating memoized state. */
  revive(): void {
    this.disposed = false
    this.notifyBusy()
  }

  /** Drop everything, including snap steps. Unmount only. */
  dispose(): void {
    this.disposed = true
    this.steps = []
    this.releaseCurrentCosmetic?.()
    this.releaseCurrentCosmetic = null
    this.notifyBusy()
  }

  private notifyBusy(): void {
    const next = this.busy
    if (next === this.busySnapshot) return
    this.busySnapshot = next
    for (const listener of this.busyListeners) listener(next)
  }

  private async drain(): Promise<void> {
    if (this.draining) return
    this.draining = true
    this.notifyBusy()
    try {
      while (this.steps.length > 0 && !this.disposed) {
        const step = this.steps.shift()!
        const fast = this.fastForwardRemaining > 0
        if (fast) this.fastForwardRemaining--
        if (fast && step.cosmetic) continue
        try {
          const run = Promise.resolve(step.run({ fast }))
          if (step.cosmetic) {
            let release: (() => void) | null = null
            const interrupted = new Promise<void>((resolve) => {
              release = resolve
              this.releaseCurrentCosmetic = resolve
            })
            await Promise.race([run, wait(COSMETIC_STEP_TIMEOUT_MS), interrupted])
            if (this.releaseCurrentCosmetic === release) this.releaseCurrentCosmetic = null
          } else {
            await run
          }
        } catch (error) {
          // A failed flourish must never wedge the queue, but keep it visible in dev.
          reportChoreographyError(error)
        }
      }
    } finally {
      this.fastForwardRemaining = 0
      this.draining = false
      this.notifyBusy()
    }
  }
}
