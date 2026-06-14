/**
 * Config-driven spritesheet animation definitions.
 *
 * A `SpriteAnimation` describes one sheet (e.g. idle, walk) laid out as a
 * uniform grid of frames, read left->right, top->bottom. New animations are
 * added by config only - see `characters.ts`.
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
}

/** A playable sub-range of a sheet, e.g. the windup frames of a cast.
 *  `loop: true` cycles [from, to] until the next swap; otherwise playback
 *  stops at `to` and fires the pending onComplete. */
export type FrameSegment = {
  from: number
  to: number
  loop?: boolean
}

/** Imperative API exposed by SpriteAnimator via ref - drives the tower-page
 *  character (play/pause, swap animation, flip facing). */
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
  /** Play a frame range of the CURRENT sheet (battle cast phases). Replaces
   *  any pending onComplete without firing it, like setAnimation. */
  playSegment: (segment: FrameSegment, opts?: { onComplete?: () => void }) => void
  /** Face left (true) or right (false). */
  setFlipX: (flipped: boolean) => void
}

/** Every move the character controller knows how to drive. */
export type MoveName =
  | 'idle'
  | 'walk'
  | 'run'
  | 'fly'
  | 'float'
  | 'dive'
  | 'take_off'
  | 'land'

/**
 * A playable character: sprite sheets plus movement tuning. The controller
 * consumes this shape only, so new characters are pure config.
 *
 * `idle`, `walk` and `fly` are required; everything else degrades:
 * run->walk, float->fly, dive->fly tilted nose-down, and the
 * take_off/land transitions are skipped entirely when their sheet is absent.
 */
export type CharacterDefinition = {
  id: string
  sprites: Partial<Record<MoveName, SpriteAnimation>> &
    Record<'idle' | 'walk' | 'fly', SpriteAnimation>
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
    /** Air speed in px/s. */
    flySpeed: number
    /** Source-pixel gap between the frame's bottom edge and the visual feet
     *  (multiplied by `scale` at render time). */
    footOffset: number
    /** Clicks farther than this (px) teleport instead of travelling.
     *  Defaults to max(2400, 2 x viewport height). */
    teleportDistance?: number
    /** take_off sheet frame at which the character is airborne: earlier
     *  frames rise straight up, later ones travel toward the target.
     *  Omit to head for the target from the first frame. */
    takeOffAirborneFrame?: number
    /** Vertical lift speed in px/s during pre-airborne take_off frames.
     *  Defaults to the controller's standard takeoff lift. */
    takeOffLiftSpeed?: number
    /** land sheet frame at which the character starts dropping straight
     *  down: earlier frames brake at a hover point above the ledge, later
     *  ones descend vertically onto it. Omit to land standing in place. */
    landFallFrame?: number
  }
}
