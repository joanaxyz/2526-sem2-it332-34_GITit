/**
 * Config-driven spritesheet animation definitions.
 *
 * A `SpriteAnimation` describes one sheet (e.g. idle, walk) laid out as a
 * uniform grid of frames, read left->right, top->bottom. New animations are
 * added by config only.
 */
export type SpriteAnimation = {
  /** Stable identifier, e.g. "character1.idle". */
  name: string
  /** Spritesheet URL (served from /public). */
  src: string
  /** Single frame size in source pixels. */
  frameWidth: number
  frameHeight: number
  /** Grid layout of the sheet. */
  columns: number
  rows: number
  /** Frames actually used (may be < columns x rows). */
  frameCount: number
  /** Default playback speed. */
  fps: number
  /** Loop forever (true) or hold the last frame (false). */
  loop: boolean
  /** Render-size multiplier that normalizes sheets of different source
   *  resolutions to one on-screen size (e.g. a 1254px pose next to 256px
   *  animation frames). Defaults to 1. */
  displayScale?: number
}

/** A playable sub-range of a sheet, e.g. the windup frames of an attack.
 *  `loop: true` cycles [from, to] until the next swap; otherwise playback
 *  stops at `to` and fires the pending onComplete. */
export type FrameSegment = {
  from: number
  to: number
  loop?: boolean
}

/** Imperative API exposed by SpriteAnimator via ref - drives companion sprites
 *  (play/pause, swap animation, flip facing). */
export type SpriteAnimatorHandle = {
  play: () => void
  pause: () => void
  isPlaying: () => boolean
  /** Jump to a specific frame (clamped). Pauses are respected. */
  goToFrame: (frame: number) => void
  /** Current frame index of the running animation. */
  getFrame: () => number
  /** Swap the running animation (e.g. idle -> walk) without remounting and
   *  start playing it. `onComplete` fires once when a non-looping animation
   *  (or the given segment) reaches its last frame; it is dropped if another
   *  swap happens first. `segment` restricts playback to a frame range. */
  setAnimation: (
    animation: SpriteAnimation,
    opts?: { onComplete?: () => void; segment?: FrameSegment },
  ) => void
  /** Play a frame range of the CURRENT sheet (battle attack/effect phases). Replaces
   *  any pending onComplete without firing it, like setAnimation. */
  playSegment: (segment: FrameSegment, opts?: { onComplete?: () => void }) => void
  /** Face left (true) or right (false). */
  setFlipX: (flipped: boolean) => void
}

/** Every locomotion sheet the companion sprite controller knows how to drive.
 *  The pipeline is deliberately small: idle + run only (walk/fly/float/battle
 *  variants were removed with the 2026-07 sheet cutover). */
export type MoveName = 'idle' | 'run'

/**
 * A companion sprite: sprite sheets plus movement tuning. The controller
 * consumes this shape only, so new companions are pure config.
 *
 * `idle` and `run` are both required.
 */
export type CompanionSpriteDefinition = {
  id: string
  sprites: Record<MoveName, SpriteAnimation>
  /** One-shot fidget animations played at random while idle on the ground
   *  (random1, random2,  sheets). Empty array = no fidgets. */
  randoms: SpriteAnimation[]
  metrics: {
    /** Display scale relative to source frame size. */
    scale: number
    /** Ground speed in px/s. */
    walkSpeed: number
    /** Ground sprint speed in px/s, used for long moves along a ledge.
     *  Defaults to 2x walkSpeed. */
    runSpeed?: number
    /** Source-pixel gap between the frame's bottom edge and the visual feet
     *  (multiplied by `scale` at render time). */
    footOffset: number
    /** Clicks farther than this (px) teleport instead of travelling.
     *  Defaults to max(2400, 2 x viewport height). */
    teleportDistance?: number
  }
}
