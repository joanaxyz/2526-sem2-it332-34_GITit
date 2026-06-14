import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef } from 'react'

import { HealthBar } from '@/shared/battle/components/HealthBar'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster } from '@/shared/battle/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimatorHandle } from '@/shared/sprites/types'
import { cn } from '@/shared/utils/cn'

export type MonsterActorHandle = {
  /**
   * Play the attack strip. For melee species the wrapper lunges toward the
   * player; the promise resolves at the species' hit/launch frame so the
   * director can time the impact (or spawn the projectile), while the rest of
   * the strip and the lunge return play on without blocking.
   */
  attack: () => Promise<void>
  hurt: () => Promise<void>
  /** Death strip, hold last frame, fade out. Resolves after the fade. */
  die: () => Promise<void>
  /** Entrance: charge in from offstage left toward the crystal. */
  walkIn: (fromPx?: number, ms?: number) => Promise<void>
  element: () => HTMLDivElement | null
}

/**
 * One monster on the stage: sprite + floating HP bar, all verbs imperative.
 * Monsters face right (toward the crystal they besiege) - the source strips
 * already face right, so no flip. Blue strikes them from the left.
 */
export const MonsterActor = forwardRef<
  MonsterActorHandle,
  {
    monster: BattleMonster
    /** Extra multiplier on the species' own scale (bosses pass >1). */
    scale?: number
    className?: string
  }
>(function MonsterActor({ monster, scale = 1, className }, ref) {
  const def = useMemo(
    () => definitionForMonster(monster),
    [monster],
  )
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const deadRef = useRef(!monster.alive)

  useEffect(() => {
    deadRef.current = !monster.alive
    if (!monster.alive && wrapRef.current) {
      // Mounted (or fast-forwarded) into the dead state: corpse fades out.
      wrapRef.current.style.opacity = '0'
      spriteRef.current?.pause()
    }
  }, [monster.alive])

  function playOnce(anim: typeof def.sprites.hurt): Promise<void> {
    return new Promise((resolve) => {
      spriteRef.current?.setAnimation(anim, {
        onComplete: () => {
          if (!deadRef.current) spriteRef.current?.setAnimation(def.sprites.idle)
          resolve()
        },
      })
    })
  }

  useImperativeHandle(ref, () => ({
    attack: () =>
      new Promise<void>((resolve) => {
        const sprite = spriteRef.current
        const node = wrapRef.current
        if (!sprite) return resolve()
        const anim = def.sprites.attack
        const contactFrame = def.attack.kind === 'melee' ? def.attack.hitFrame : def.attack.launchFrame
        const msPerFrame = 1000 / anim.fps
        const lungeMs = Math.max(1, contactFrame) * msPerFrame

        if (def.attack.kind === 'melee' && node) {
          const lunge = node.animate(
            [
              { transform: 'translateX(0)' },
              { transform: `translateX(${def.attack.lungePx}px)`, offset: 0.55 },
              { transform: `translateX(${def.attack.lungePx}px)`, offset: 0.75 },
              { transform: 'translateX(0)' },
            ],
            { duration: lungeMs + 360, easing: 'ease-in-out' },
          )
          lunge.finished.catch(() => {})
        }
        sprite.setAnimation(anim, {
          onComplete: () => {
            if (!deadRef.current) sprite.setAnimation(def.sprites.idle)
          },
        })
        // Resolve at the contact/launch frame, not the end of the strip.
        window.setTimeout(resolve, lungeMs)
      }),

    hurt: () => playOnce(def.sprites.hurt),

    die: () =>
      new Promise<void>((resolve) => {
        deadRef.current = true
        spriteRef.current?.setAnimation(def.sprites.death, {
          onComplete: () => {
            const node = wrapRef.current
            if (!node) return resolve()
            const fade = node.animate([{ opacity: 1 }, { opacity: 0 }], {
              duration: 400,
              fill: 'forwards',
            })
            fade.finished
              .then(() => {
                node.style.opacity = '0'
                fade.cancel()
              })
              .catch(() => {})
              .finally(resolve)
          },
        })
      }),

    walkIn: (fromPx = 160, ms = 1100) =>
      new Promise<void>((resolve) => {
        const node = wrapRef.current
        const sprite = spriteRef.current
        if (!node || !sprite) return resolve()
        sprite.setAnimation(def.sprites.walk)
        const entrance = node.animate(
          [{ transform: `translateX(${-fromPx}px)`, opacity: 0.4 }, { transform: 'translateX(0)', opacity: 1 }],
          { duration: ms, easing: 'ease-out' },
        )
        entrance.finished
          .catch(() => {})
          .finally(() => {
            if (!deadRef.current) sprite.setAnimation(def.sprites.idle)
            resolve()
          })
      }),

    element: () => wrapRef.current,
  }))

  const effectiveScale = def.metrics.scale * scale
  const frameHeight = def.sprites.idle.frameHeight * effectiveScale

  return (
    <div
      ref={wrapRef}
      className={cn('relative', className)}
      // Sprite frames carry transparent padding below the visual feet; pull
      // the actor down so it actually stands on the stage's ground line.
      style={{ marginBottom: -def.metrics.footOffset * effectiveScale }}
    >
      <SpriteAnimator
        ref={spriteRef}
        animation={def.sprites.idle}
        scale={effectiveScale}
        pixelated
        aria-label={def.label}
      />
      <HealthBar
        value={monster.hp}
        max={monster.max_hp}
        variant={def.tier === 'boss' ? 'boss' : 'hp'}
        className={cn('absolute left-1/2 -translate-x-1/2', def.tier === 'boss' ? 'w-24' : 'w-14')}
        // Floats just above the species' visible body, not the frame box.
        style={{ bottom: frameHeight * def.metrics.hpBarFraction + 6 }}
        aria-label={`${def.label} health`}
      />
    </div>
  )
})
