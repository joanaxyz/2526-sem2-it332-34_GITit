import { useEffect, useMemo, useRef } from 'react'

import {
  effectSheetForSkill,
  lockedEffectForSkill,
  lockedGroundedForSkill,
} from '@/shared/battle/effects/effectRegistry'
import { reduceMotion } from '@/shared/battle/effects/skill-effects/spriteDom'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'

// The effect is LOCKED in place at the horizontal centre - it never travels. Only
// the vertical anchor still matters: grounded effects (projectile impacts, ground
// travel, feet risers) plant on the floor line; body-centered auras sit on the
// body. `lockedGroundedForSkill` owns that classification.
const TARGET_X = 0.5
const BODY_Y = 0.5
const GROUND_Y = 0.82

type SkillEffectStageProps = {
  /** Command-family key, e.g. "clone", "merge-base", "commit". */
  skill: string
  companionSlug: string
  /** Multiplier on the effect's base scale (the battle uses monster size). */
  sizeScale?: number
  /** Gap between replays of the looping effect. */
  replayGapMs?: number
  /** Draw the ground line + a target/caster stand so placement is legible. */
  showStage?: boolean
  className?: string
  'aria-label'?: string
}

/**
 * Plays a companion skill LOCKED in place with the real battle target playback
 * (grow/hold/fade, center-vs-ground anchoring) - the same core the battle panel
 * uses, minus the monster and the projectile flight. Used by the shop skill
 * preview so it reads as a real cast without flying off-screen. Honors reduced
 * motion by holding a still.
 */
export function SkillEffectStage({
  skill,
  companionSlug,
  sizeScale = 1,
  replayGapMs = 520,
  showStage = true,
  className,
  'aria-label': ariaLabel,
}: SkillEffectStageProps) {
  const rootRef = useRef<HTMLDivElement>(null)
  const frontRef = useRef<HTMLDivElement>(null)
  const backRef = useRef<HTMLDivElement>(null)
  const reduced = useMemo(() => reduceMotion(), [])
  const fallbackSheet = useMemo(() => effectSheetForSkill(skill, companionSlug), [skill, companionSlug])

  useEffect(() => {
    const front = frontRef.current
    if (!front || reduced) return
    let cancelled = false
    const loop = async () => {
      while (!cancelled) {
        const box = front.getBoundingClientRect()
        if (box.width && box.height) {
          const grounded = lockedGroundedForSkill(skill, companionSlug)
          const to = { x: box.width * TARGET_X, y: box.height * (grounded ? GROUND_Y : BODY_Y) }
          await lockedEffectForSkill(skill, companionSlug)({
            layer: front,
            backLayer: backRef.current,
            from: to,
            to,
            sizeScale,
          })
        }
        if (cancelled) break
        await new Promise((resolve) => window.setTimeout(resolve, replayGapMs))
      }
    }
    void loop()
    return () => {
      cancelled = true
    }
  }, [skill, companionSlug, sizeScale, replayGapMs, reduced])

  return (
    <div
      ref={rootRef}
      className={className}
      role="img"
      aria-label={ariaLabel}
      style={{ position: 'relative', width: '100%', height: '100%', minHeight: '15rem', overflow: 'hidden' }}
    >
      {showStage ? (
        <div
          aria-hidden
          style={{
            position: 'absolute',
            left: '8%',
            right: '8%',
            top: `${GROUND_Y * 100}%`,
            height: 1,
            background:
              'linear-gradient(90deg, transparent, rgba(var(--theme-primary-rgb),0.22) 25%, rgba(var(--theme-primary-rgb),0.22) 75%, transparent)',
          }}
        />
      ) : null}
      <div ref={backRef} className="battle-effect-layer battle-effect-layer--back" aria-hidden />
      <div ref={frontRef} className="battle-effect-layer battle-effect-layer--front" aria-hidden />
      {reduced ? (
        <div
          style={{
            position: 'absolute',
            left: `${TARGET_X * 100}%`,
            top: `${BODY_Y * 100}%`,
            transform: 'translate(-50%, -50%)',
          }}
        >
          <SpriteAnimator animation={fallbackSheet} scale={0.6} pixelated />
        </div>
      ) : null}
    </div>
  )
}
