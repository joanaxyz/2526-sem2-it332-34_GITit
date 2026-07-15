import { forwardRef, useCallback, useEffect, useImperativeHandle, useLayoutEffect, useMemo, useRef } from 'react'

import { playMonsterHurtSound } from '@/shared/audio/battleAudio'
import { definitionForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster } from '@/shared/battle/types'
import { monsterSkin } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimatorHandle } from '@/shared/sprites/types'
import {
  finishElementAnimation,
  playOneShotAndHold,
  playOneShotAndRestore,
  playOneShotSprite,
  readElementTranslateX,
} from './actorPlayback'
import { cn } from '@/shared/utils/cn'

export type MonsterAttackOptions = {
  approachPx?: number
  /** `complete` is the gameplay default: effects fire only after the attack strip. */
  resolveAt?: 'impact' | 'complete'
  /** Pass false when the director wants to fire an effect before the monster retreats. */
  recover?: boolean
}

type NormalizedMonsterAttackOptions = {
  approachPx?: number
  resolveAt: 'impact' | 'complete'
  recover: boolean
}

export type MonsterActorHandle = {
  /**
   * Play the monster attack. Melee species blink to striking range first, and authored
   * flyers arc through their attack strip. By default the promise resolves only
   * after the full attack strip completes, so monster effects/projectiles start
   * after the monster animation rather than at the old hit/launch frame.
   */
  attack: (options?: number | MonsterAttackOptions) => Promise<void>
  /** Return from the post-attack position back to the duel lane. */
  recover: () => Promise<void>
  hurt: () => Promise<void>
  /** Death strip, then hold the final frame. */
  die: () => Promise<void>
  /**
   * Park off-screen to the right (duel slot stays centred; only translateX moves
   * the sprite). Called before the travel pan so nothing flashes in the middle.
   */
  prepOffscreen: (offsetPx: number) => void
  /** Entrance: slide in from offstage; `toPx` is the wide-frame hold (right edge). */
  walkIn: (fromPx?: number, ms?: number, toPx?: number) => Promise<void>
  /** Ease from the wide-frame hold into the centered duel slot. */
  slideTo: (toPx: number, ms?: number) => Promise<void>
  element: () => HTMLDivElement | null
}

/**
 * One monster on the stage: sprite only, all verbs imperative.
 * Source strips face right; the duel places monsters to Blue's right, so they
 * default to facing left.
 */
export const MonsterActor = forwardRef<
  MonsterActorHandle,
  {
    monster: BattleMonster
    /** Extra multiplier on the species' own scale (bosses pass >1). */
    scale?: number
    facing?: 'left' | 'right'
    /** Hide the actor until the director's entrance choreography reveals it. */
    stagedHidden?: boolean
    className?: string
    storyWorld: StoryWorldDef
  }
>(function MonsterActor({ monster, scale = 1, facing = 'left', stagedHidden = false, className, storyWorld }, ref) {
  const def = useMemo(
    () => definitionForMonster(monster, monsterSkin(storyWorld, monster.species)),
    [monster, storyWorld],
  )
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const idleSpriteRef = useRef(def.sprites.idle)
  const deadRef = useRef(!monster.alive)
  const busyRef = useRef(false)
  // Each verb that sets a new pose claims a token; the deferred idle-restore of
  // a hurt flinch (it outlives the beat that awaits it) only applies when no
  // newer verb has taken the stage since. Without this, the overlapping flinches
  // of a sustained effect flash back to idle mid-hit.
  const poseTokenRef = useRef(0)
  const direction = facing === 'left' ? -1 : 1
  idleSpriteRef.current = def.sprites.idle

  const claimPose = useCallback(() => {
    poseTokenRef.current += 1
    return poseTokenRef.current
  }, [])

  const freezeDeathFrame = useCallback(() => {
    const node = wrapRef.current
    const sprite = spriteRef.current
    if (!node || !sprite) return
    node.style.opacity = '1'
    sprite.setAnimation(def.sprites.death)
    sprite.pause()
    sprite.goToFrame(def.sprites.death.frameCount - 1)
  }, [def.sprites.death])

  useEffect(() => {
    const wasDead = deadRef.current
    deadRef.current = !monster.alive
    if (!monster.alive && wrapRef.current) {
      // Mounted, resolved, or fast-forwarded into death: hold the corpse on the
      // final frame so the outcome modal never hides the last beat.
      busyRef.current = false
      freezeDeathFrame()
    } else if (wasDead && wrapRef.current) {
      // A new level can reuse a monster id. In that case React keeps this actor
      // mounted, including the paused death animator left by its previous
      // encounter. Restore the actor before the next entrance so it cannot remain
      // invisibly parked in the new encounter.
      busyRef.current = false
      wrapRef.current.style.opacity = stagedHidden ? '0' : '1'
      wrapRef.current.style.transform = 'translateX(0)'
      spriteRef.current?.play()
      spriteRef.current?.setAnimation(idleSpriteRef.current)
    }
  }, [freezeDeathFrame, monster.alive, stagedHidden])

  // Entrances hide before paint; remounted already-staged actors stay visible.
  useLayoutEffect(() => {
    if (!monster.alive) return
    const node = wrapRef.current
    if (!node) return
    node.style.opacity = stagedHidden ? '0' : '1'
  }, [monster.alive, monster.id, stagedHidden])

  function rest() {
    if (!deadRef.current) spriteRef.current?.setAnimation(idleSpriteRef.current)
  }

  function normalizeAttackOptions(options?: number | MonsterAttackOptions): NormalizedMonsterAttackOptions {
    if (typeof options === 'number') {
      return { approachPx: options, resolveAt: 'complete', recover: true }
    }
    return {
      approachPx: options?.approachPx,
      resolveAt: options?.resolveAt ?? 'complete',
      recover: options?.recover ?? true,
    }
  }

  function wait(ms: number): Promise<void> {
    return new Promise((resolve) => window.setTimeout(resolve, Math.max(0, ms)))
  }

  // Melee repositioning is a blink, not a run: fade out in place, reappear at
  // the target offset. Flyers keep their authored arc instead.
  async function blinkTo(node: HTMLElement, transform: string): Promise<void> {
    const fadeMs = 130
    const out = node.animate([{ opacity: 1 }, { opacity: 0 }], {
      duration: fadeMs,
      easing: 'ease-in',
      fill: 'forwards',
    })
    await finishElementAnimation(out, fadeMs)
    node.style.opacity = '0'
    out.cancel()
    node.style.transform = transform
    const reappear = node.animate([{ opacity: 0 }, { opacity: 1 }], {
      duration: fadeMs,
      easing: 'ease-out',
      fill: 'forwards',
    })
    await finishElementAnimation(reappear, fadeMs)
    node.style.opacity = '1'
    reappear.cancel()
  }

  function recoverFromAttack(): Promise<void> {
    const node = wrapRef.current
    const flight = def.attack.flight
    const shouldMoveBack = def.attack.kind === 'melee' || Boolean(flight)
    if (!node || !shouldMoveBack) {
      busyRef.current = false
      rest()
      return Promise.resolve()
    }

    rest()
    if (!flight) {
      // Melee blinked in, so blink back home rather than sliding across the lane.
      return blinkTo(node, 'translateX(0)').finally(() => {
        busyRef.current = false
        rest()
      })
    }
    const ms = 420
    const back = node.animate(
      [{ transform: node.style.transform || 'translateX(0)' }, { transform: 'translateX(0)' }],
      { duration: ms, easing: 'cubic-bezier(0.16, 1, 0.3, 1)', fill: 'forwards' },
    )
    return finishElementAnimation(back, ms).finally(() => {
      node.style.transform = 'translateX(0)'
      back.cancel()
      busyRef.current = false
      rest()
    })
  }

  async function performAttack(options?: number | MonsterAttackOptions): Promise<void> {
    const sprite = spriteRef.current
    const node = wrapRef.current
    if (!sprite) return

    const { approachPx, resolveAt, recover } = normalizeAttackOptions(options)
    const token = claimPose()
    busyRef.current = true

    const anim = def.sprites.attack
    const contactFrame = def.attack.kind === 'melee' ? def.attack.hitFrame : def.attack.launchFrame
    const msPerFrame = 1000 / anim.fps
    const impactMs = Math.max(1, contactFrame) * msPerFrame
    const flight = def.attack.flight

    if (!flight && def.attack.kind === 'melee' && node) {
      // Blink to striking range before playing the authored attack strip. The
      // effect is still delayed until after the strip, not this reposition beat.
      const approach = Math.max(def.attack.lungePx, approachPx ?? 0)
      rest()
      await blinkTo(node, `translateX(${direction * approach}px)`)
    }

    if (flight && node) {
      const x = Math.round(direction * flight.distancePx)
      const lift = -Math.round(flight.liftPx)
      const hold = `translate(${x}px, ${Math.round(lift * 0.42)}px)`
      const flightMs = Math.max(260, Math.min(720, impactMs))
      const takeoff = node.animate(
        [
          { transform: 'translateX(0)', offset: 0 },
          { transform: `translate(${Math.round(x * 0.62)}px, ${lift}px)`, offset: 0.62 },
          { transform: hold, offset: 1 },
        ],
        { duration: flightMs, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
      )
      void finishElementAnimation(takeoff, flightMs).finally(() => {
        node.style.transform = hold
        takeoff.cancel()
      })
    }

    const fullAttack = playOneShotSprite(sprite, anim)
    if (resolveAt === 'impact') {
      await Promise.race([wait(impactMs), fullAttack])
      void fullAttack.finally(() => {
        if (token !== poseTokenRef.current) return
        if (recover) void recoverFromAttack()
        else rest()
      })
      return
    }

    await fullAttack
    if (token !== poseTokenRef.current) return
    if (recover) await recoverFromAttack()
    else rest()
  }

  useImperativeHandle(ref, () => ({
    attack: (options?: number | MonsterAttackOptions) => performAttack(options),
    recover: () => recoverFromAttack(),

    hurt: () => {
      busyRef.current = true
      const token = claimPose()
      playMonsterHurtSound()
      const restIfCurrent = () => {
        if (token === poseTokenRef.current) rest()
      }
      return playOneShotAndRestore(spriteRef.current, def.sprites.hurt, restIfCurrent, 900).finally(() => {
        busyRef.current = false
      })
    },

    die: async () => {
      claimPose()
      if (deadRef.current) {
        // The finishing-blow beat already played the strip; just keep the corpse.
        freezeDeathFrame()
        return
      }
      busyRef.current = true
      deadRef.current = true
      // No cap: the death strip is the payoff beat and must finish naturally.
      await playOneShotAndHold(spriteRef.current, def.sprites.death)
      const node = wrapRef.current
      if (node) node.style.opacity = '1'
      busyRef.current = false
    },

    prepOffscreen: (offsetPx: number) => {
      busyRef.current = true
      const node = wrapRef.current
      if (node) {
        node.style.opacity = '0'
        node.style.transform = `translateX(${offsetPx}px)`
      }
    },

    walkIn: (fromPx = 160, ms = 1100, toPx = 0) =>
      new Promise<void>((resolve) => {
        const node = wrapRef.current
        const sprite = spriteRef.current
        if (!node || !sprite) return resolve()
        busyRef.current = true
        rest()
        node.style.transform = `translateX(${fromPx}px)`
        node.style.opacity = '1'
        const entrance = node.animate(
          // Peek from beyond the right rim into a partial hold — not the centred
          // duel lane (`toPx` back to 0 happens on the camera-lock beat).
          [
            { transform: `translateX(${fromPx}px)`, opacity: 0.15 },
            { transform: `translateX(${toPx}px)`, opacity: 1 },
          ],
          { duration: ms, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
        )
        finishElementAnimation(entrance, ms)
          .catch(() => {})
          .finally(() => {
            node.style.opacity = '1'
            node.style.transform = `translateX(${toPx}px)`
            entrance.cancel()
            busyRef.current = false
            rest()
            resolve()
          })
      }),

    slideTo: (toPx, ms = 820) =>
      new Promise<void>((resolve) => {
        const node = wrapRef.current
        if (!node) return resolve()
        busyRef.current = true
        const fromPx = readElementTranslateX(node)
        if (fromPx === toPx) {
          busyRef.current = false
          resolve()
          return
        }
        const glide = node.animate(
          [{ transform: `translateX(${fromPx}px)` }, { transform: `translateX(${toPx}px)` }],
          { duration: ms, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' },
        )
        finishElementAnimation(glide, ms)
          .then(() => {
            node.style.transform = `translateX(${toPx}px)`
            glide.cancel()
          })
          .catch(() => {})
          .finally(() => {
            busyRef.current = false
            rest()
            resolve()
          })
      }),

    element: () => wrapRef.current,
  }))

  const effectiveScale = def.metrics.scale * scale
  return (
    <div
      ref={wrapRef}
      className={cn('relative', className)}
    >
      <div className="battle-monster-roam">
        <SpriteAnimator
          ref={spriteRef}
          animation={def.sprites.idle}
          scale={effectiveScale}
          pixelated
          anchorToPixelBounds
          layoutAnimation={def.sprites.idle}
          pixelAnchorAnimation={def.sprites.idle}
          pixelAnchorFallback={{ bottomOffset: def.metrics.footOffset }}
          flipX={facing === 'left'}
          aria-label={def.label}
        />
      </div>
    </div>
  )
})
