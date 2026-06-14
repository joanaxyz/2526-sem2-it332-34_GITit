import { forwardRef, useImperativeHandle, useRef } from 'react'

import type { CharacterBattleSheets } from '@/shared/sprites/characters'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { CharacterDefinition, SpriteAnimatorHandle } from '@/shared/sprites/types'

export type PlayerActorHandle = {
  /**
   * Play the cast sheet once and settle back to idle (idle -> cast -> idle).
   * Resolves when the sheet finishes, so the director can spawn the spell
   * effect and move on. The cast plays on the resolved outcome, not on submit.
   */
  cast: () => Promise<void>
  /**
   * A spell that made no progress: a brief placeholder beat (idle frames + a
   * small recoil) while a monster strikes the crystal. No dedicated sheet yet.
   */
  miss: () => Promise<void>
  /**
   * Level cleared - Blue takes off and rises off the top of the stage, then
   * holds in flight. Resolves once airborne so the director can restage the
   * next floor underneath him.
   */
  liftOff: () => Promise<void>
  /** Descend onto the new floor: drop in from above, land, settle to idle. */
  landIn: () => Promise<void>
  /**
   * Encounter start - Blue dashes in from the landing edge to lock range near
   * the tower, then settles to idle. The fight's first beat waits on this.
   */
  runIn: () => Promise<void>
  /** Anchor element for effect launch positions. */
  element: () => HTMLDivElement | null
}

const RISE_PX = 220
const RUN_IN_PX = 150

/**
 * Blue on the tower-defense stage. He rests on the shared idle sheet and guards
 * the crystal; combat verbs are driven imperatively by the director, so no
 * React re-renders happen mid-choreography. Climbing between levels reuses the
 * tower character's take_off / fly / land sheets.
 */
export const PlayerActor = forwardRef<
  PlayerActorHandle,
  { character: CharacterDefinition; battle: CharacterBattleSheets; scale?: number; className?: string }
>(function PlayerActor({ character, battle, scale = 0.5, className }, ref) {
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const wrapRef = useRef<HTMLDivElement | null>(null)

  function rest() {
    spriteRef.current?.setAnimation(character.sprites.idle)
  }

    useImperativeHandle(ref, () => ({
      cast: () =>
        new Promise<void>((resolve) => {
          const sprite = spriteRef.current
          if (!sprite) {
            resolve()
            return
          }
          sprite.setAnimation(battle.cast, {
            onComplete: () => {
              rest()
              resolve()
            },
          })
        }),

      miss: () =>
        new Promise<void>((resolve) => {
          const sprite = spriteRef.current
          const node = wrapRef.current
          node?.animate(
            [
              { transform: 'translateX(0)' },
              { transform: 'translateX(-10px)', offset: 0.4 },
              { transform: 'translateX(0)' },
            ],
            { duration: 420, easing: 'ease-out' },
          )
          if (!sprite) {
            resolve()
            return
          }
          sprite.setAnimation(battle.miss, {
            onComplete: () => {
              rest()
              resolve()
            },
          })
        }),

      liftOff: () =>
        new Promise<void>((resolve) => {
          const sprite = spriteRef.current
          const node = wrapRef.current
          const takeOff = character.sprites.take_off ?? character.sprites.idle
          const fly = character.sprites.fly ?? character.sprites.idle
          if (sprite) {
            sprite.setAnimation(takeOff, {
              onComplete: () => spriteRef.current?.setAnimation(fly),
            })
          }
          if (!node) {
            resolve()
            return
          }
          const rise = node.animate(
            [
              { transform: 'translateY(0)', opacity: 1 },
              { transform: `translateY(-${RISE_PX}px)`, opacity: 0.55 },
            ],
            { duration: 720, easing: 'cubic-bezier(0.45, 0, 0.55, 1)', fill: 'forwards' },
          )
          rise.finished
            .then(() => {
              node.style.transform = `translateY(-${RISE_PX}px)`
              node.style.opacity = '0.55'
              rise.cancel()
            })
            .catch(() => {})
            .finally(resolve)
        }),

      landIn: () =>
        new Promise<void>((resolve) => {
          const sprite = spriteRef.current
          const node = wrapRef.current
          sprite?.setAnimation(character.sprites.land ?? character.sprites.idle, {
            onComplete: () => rest(),
          })
          if (!node) {
            resolve()
            return
          }
          const drop = node.animate(
            [
              { transform: `translateY(-${RISE_PX}px)`, opacity: 0.55 },
              { transform: 'translateY(0)', opacity: 1 },
            ],
            { duration: 720, easing: 'cubic-bezier(0.3, 0.7, 0.4, 1)', fill: 'forwards' },
          )
          drop.finished
            .then(() => {
              node.style.transform = 'translateY(0)'
              node.style.opacity = '1'
              drop.cancel()
            })
            .catch(() => {})
            .finally(() => {
              rest()
              resolve()
            })
        }),

      runIn: () =>
        new Promise<void>((resolve) => {
          const sprite = spriteRef.current
          const node = wrapRef.current
          const run = character.sprites.run ?? character.sprites.walk ?? character.sprites.idle
          sprite?.setAnimation(run)
          if (!node) {
            resolve()
            return
          }
          const dash = node.animate(
            [{ transform: `translateX(-${RUN_IN_PX}px)` }, { transform: 'translateX(0)' }],
            { duration: 640, easing: 'cubic-bezier(0.3, 0.7, 0.3, 1)', fill: 'forwards' },
          )
          dash.finished
            .then(() => {
              node.style.transform = 'translateX(0)'
              dash.cancel()
            })
            .catch(() => {})
            .finally(() => {
              rest()
              resolve()
            })
        }),

      element: () => wrapRef.current,
    }))

    return (
      <div ref={wrapRef} className={className}>
        <SpriteAnimator
          ref={spriteRef}
          animation={character.sprites.idle}
          scale={scale}
          aria-label="Blue, your spellcaster"
        />
      </div>
    )
  },
)
