/**
 * Config-driven spritesheet animation definitions.
 *
 * A `SpriteAnimation` describes one sheet (e.g. idle, walk) laid out as a
 * uniform grid of frames, read left→right, top→bottom. New animations are
 * added by config only — see `characters.ts`.
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
  /** Frames actually used (may be < columns × rows). */
  frameCount: number
  /** Default playback speed. */
  fps: number
  /** Loop forever (true) or hold the last frame (false). */
  loop: boolean
}

/** Imperative API exposed by SpriteAnimator via ref — built for future
 *  tower-page movement (play/pause, swap animation, flip facing). */
export type SpriteAnimatorHandle = {
  play: () => void
  pause: () => void
  isPlaying: () => boolean
  /** Jump to a specific frame (clamped). Pauses are respected. */
  goToFrame: (frame: number) => void
  /** Swap the running animation (e.g. idle → walk) without remounting. */
  setAnimation: (animation: SpriteAnimation) => void
  /** Face left (true) or right (false). */
  setFlipX: (flipped: boolean) => void
}
