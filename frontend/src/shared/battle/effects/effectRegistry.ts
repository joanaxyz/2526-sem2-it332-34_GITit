import type { SpriteAnimation } from '@/shared/sprites/types'

/**
 * Per-git-skill spell effects. Each effect builds throwaway DOM inside the
 * stage's overlay layer and animates it with the Web Animations API
 * (transform/opacity only). The returned promise resolves at IMPACT so the
 * battle queue can chain the hurt reaction; trailing sparkle cleanup runs on
 * without blocking.
 */

export type EffectContext = {
  /** Absolutely-positioned overlay (`contain: strict`, pointer-events none). */
  layer: HTMLElement
  /** Launch point, layer-local px. */
  from: { x: number; y: number }
  /** Impact point, layer-local px. */
  to: { x: number; y: number }
}

export type BattleEffect = (ctx: EffectContext) => Promise<void>

function el(layer: HTMLElement, style: Partial<CSSStyleDeclaration>): HTMLDivElement {
  const node = document.createElement('div')
  Object.assign(node.style, {
    position: 'absolute',
    left: '0',
    top: '0',
    pointerEvents: 'none',
    ...style,
  })
  layer.appendChild(node)
  return node
}

function animate(node: HTMLElement, keyframes: Keyframe[], options: KeyframeAnimationOptions): Promise<void> {
  return node.animate(keyframes, options).finished.then(
    () => undefined,
    () => undefined,
  )
}

function burst(layer: HTMLElement, at: { x: number; y: number }, color: string, size = 36): void {
  const ring = el(layer, {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    border: `2px solid ${color}`,
    boxShadow: `0 0 18px ${color}`,
    transform: `translate(${at.x - size / 2}px, ${at.y - size / 2}px) scale(0.3)`,
    opacity: '1',
  })
  void animate(
    ring,
    [
      { transform: `translate(${at.x - size / 2}px, ${at.y - size / 2}px) scale(0.3)`, opacity: 1 },
      { transform: `translate(${at.x - size / 2}px, ${at.y - size / 2}px) scale(2.1)`, opacity: 0 },
    ],
    { duration: 280, easing: 'ease-out' },
  ).finally(() => ring.remove())
}

/** commit — Seal of Record: an amber rune disc arcs in and stamps the target. */
const commitSeal: BattleEffect = async ({ layer, from, to }) => {
  const size = 22
  const disc = el(layer, {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    background: 'radial-gradient(circle at 35% 35%, #fde68a, #f59e0b 70%)',
    border: '2px solid rgba(253,230,138,0.9)',
    boxShadow: '0 0 14px rgba(245,158,11,0.8)',
  })
  const midX = (from.x + to.x) / 2
  const arcY = Math.min(from.y, to.y) - 46
  await animate(
    disc,
    [
      { transform: `translate(${from.x - size / 2}px, ${from.y - size / 2}px) rotate(0deg) scale(0.7)` },
      { transform: `translate(${midX - size / 2}px, ${arcY - size / 2}px) rotate(360deg) scale(1)`, offset: 0.55 },
      { transform: `translate(${to.x - size / 2}px, ${to.y - size / 2}px) rotate(720deg) scale(1)` },
    ],
    { duration: 460, easing: 'ease-in' },
  )
  disc.remove()
  burst(layer, to, 'rgba(245,158,11,0.85)')
}

/** merge — Converging Streams: two streaks meet exactly at the target. */
const mergeStreams: BattleEffect = async ({ layer, from, to }) => {
  const mk = (offsetY: number, color: string) => {
    const streak = el(layer, {
      width: '60px',
      height: '3px',
      borderRadius: '2px',
      background: `linear-gradient(to left, ${color}, transparent)`,
      boxShadow: `0 0 8px ${color}`,
    })
    return animate(
      streak,
      [
        { transform: `translate(${from.x}px, ${from.y + offsetY}px)` },
        { transform: `translate(${(from.x + to.x) / 2 - 30}px, ${(from.y + to.y) / 2 + offsetY * 0.4}px)`, offset: 0.6 },
        { transform: `translate(${to.x - 54}px, ${to.y}px)` },
      ],
      { duration: 500, easing: 'ease-in' },
    ).finally(() => streak.remove())
  }
  await Promise.all([mk(-18, 'rgba(0,245,212,0.95)'), mk(18, 'rgba(192,132,252,0.95)')])
  burst(layer, to, 'rgba(255,255,255,0.9)', 44)
}

/** push — Repulsor Wave: staggered chevrons sweep into the target. */
const pushWave: BattleEffect = async ({ layer, from, to }) => {
  const flights: Promise<void>[] = []
  for (let i = 0; i < 3; i++) {
    const chevron = el(layer, {
      width: '20px',
      height: '20px',
      clipPath: 'polygon(0 0, 60% 0, 100% 50%, 60% 100%, 0 100%, 40% 50%)',
      background: 'rgba(0,245,212,0.9)',
      filter: 'drop-shadow(0 0 6px rgba(0,245,212,0.8))',
    })
    flights.push(
      animate(
        chevron,
        [
          { transform: `translate(${from.x}px, ${from.y - 10}px) scale(0.8)`, opacity: 0 },
          { transform: `translate(${from.x + 20}px, ${from.y - 10}px) scale(1)`, opacity: 1, offset: 0.15 },
          { transform: `translate(${to.x - 10}px, ${to.y - 10}px) scale(1.1)`, opacity: 1 },
        ],
        { duration: 380, easing: 'ease-in', delay: i * 80, fill: 'backwards' },
      ).finally(() => chevron.remove()),
    )
  }
  await Promise.all(flights)
  burst(layer, to, 'rgba(0,245,212,0.85)')
}

/** Default — a cyan arcane bolt. */
const arcaneBolt: BattleEffect = async ({ layer, from, to }) => {
  const size = 14
  const bolt = el(layer, {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    background: 'radial-gradient(circle at 35% 35%, #cffafe, #00f5d4 70%)',
    boxShadow: '0 0 16px rgba(0,245,212,0.9)',
  })
  await animate(
    bolt,
    [
      { transform: `translate(${from.x - size / 2}px, ${from.y - size / 2}px) scale(0.7)` },
      { transform: `translate(${to.x - size / 2}px, ${to.y - size / 2}px) scale(1)` },
    ],
    { duration: 380, easing: 'ease-in' },
  )
  bolt.remove()
  burst(layer, to, 'rgba(0,245,212,0.85)')
}

/** Cast resolved but the command missed: the spell fizzles mid-flight. */
export const fizzle: BattleEffect = async ({ layer, from, to }) => {
  const size = 12
  const dud = el(layer, {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    background: 'radial-gradient(circle at 35% 35%, #e2e8f0, #64748b 70%)',
    boxShadow: '0 0 10px rgba(148,163,184,0.7)',
  })
  const midX = from.x + (to.x - from.x) * 0.45
  const midY = from.y + (to.y - from.y) * 0.45
  await animate(
    dud,
    [
      { transform: `translate(${from.x - size / 2}px, ${from.y - size / 2}px) scale(0.8)`, opacity: 1 },
      { transform: `translate(${midX - size / 2}px, ${midY - size / 2}px) scale(0.5)`, opacity: 0.5 },
      { transform: `translate(${midX - size / 2}px, ${midY + 14 - size / 2}px) scale(0.2)`, opacity: 0 },
    ],
    { duration: 420, easing: 'ease-out' },
  )
  dud.remove()
}

/**
 * Sprite-strip projectile (monster arrows/magic, and sprite-skinned skills).
 * Renders the strip's first frame as a background and flies it from→to;
 * `hue` recolors a shared sheet per skill.
 */
export function spriteProjectile(sheet: SpriteAnimation, opts?: { hue?: number; flip?: boolean }): BattleEffect {
  return async ({ layer, from, to }) => {
    const scale = 0.6
    const w = sheet.frameWidth * scale
    const h = sheet.frameHeight * scale
    const node = el(layer, {
      width: `${w}px`,
      height: `${h}px`,
      backgroundImage: `url(${sheet.src})`,
      backgroundRepeat: 'no-repeat',
      backgroundSize: `${sheet.columns * 100}% ${sheet.rows * 100}%`,
      backgroundPosition: '0% 0%',
      imageRendering: 'pixelated',
      filter: opts?.hue ? `hue-rotate(${opts.hue}deg)` : '',
    })
    const flip = opts?.flip ? ' scaleX(-1)' : ''
    await animate(
      node,
      [
        { transform: `translate(${from.x - w / 2}px, ${from.y - h / 2}px)${flip}` },
        { transform: `translate(${to.x - w / 2}px, ${to.y - h / 2}px)${flip}` },
      ],
      { duration: 360, easing: 'linear' },
    )
    node.remove()
    burst(layer, to, 'rgba(248,180,140,0.8)', 28)
  }
}

const EFFECTS: Record<string, BattleEffect> = {
  commit: commitSeal,
  merge: mergeStreams,
  // The remote-sync family (push/pull/fetch) shares one outgoing wave: on the
  // stage every command is the player casting at the boss, so direction tracks
  // the attack, not the git data flow.
  push: pushWave,
  pull: pushWave,
  fetch: pushWave,
  default: arcaneBolt,
}

/** Resolve the effect for a command family ("commit", "merge", …). */
export function effectForSkill(skill: string): BattleEffect {
  return EFFECTS[skill] ?? EFFECTS.default
}
