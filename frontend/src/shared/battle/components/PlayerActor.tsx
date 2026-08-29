import { forwardRef, useImperativeHandle, useRef } from 'react'

import { playCompanionDeathSound, playCompanionHurtSound, playRunSound } from '@/shared/audio/battleAudio'
import type { CompanionBattleSheets } from '@/shared/cosmetics/companionRuntime'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { CompanionSpriteDefinition, SpriteAnimatorHandle } from '@/shared/sprites/types'
import {
  finishElementAnimation,
  playOneShotAndHold,
  playOneShotAndRestore,
  playOneShotSprite,
  readElementTranslateX,
} from './actorPlayback'

export type PlayerActorHandle = {
  /**
   * Play the companion attack windup. Resolves once the cast can release into
   * the skill effect and matching cast-end sheet.
   */
  attack: () => Promise<void>
  /** Play the successful cast-end sheet, or the miss sheet for mistake outcomes. */
  endAttack: (missed?: boolean) => Promise<void>
  /** Immediate submit feedback while the command resolves. */
  beginAttack: () => void
  /** Clear pending submit feedback after an error or fast cancel. */
  cancelAttack: () => void
  /** Monster strike landed: play the hurt sheet, then return to idle. */
  hurt: () => Promise<void>
  /** Blue is defeated: play death once and hold on the last frame. */
  defeat: () => Promise<void>
  /**
   * Encounter cleared: Blue runs back toward the left edge, lagging behind the
   * faster world pan, and keeps running there until the next encounter peeks.
   */
  travelBack: (ms?: number) => Promise<void>
  /** Keep Blue running at the left edge while the world finishes panning. */
  holdTravel: (ms?: number) => void
  /**
   * Approach: run from the travel edge toward the foe. Stops at `toPx` (wide
   * frame, near the right-edge monster) and settles to idle - Blue goes into
   * idle once the monster is engaged.
   */
  runIn: (toPx?: number) => Promise<void>
  /** Ease from the wide-frame hold into the centered duel slot. */
  slideTo: (toPx: number, ms?: number) => Promise<void>
  /** Snap to the resting idle pose. `visible=false` hides Blue (pre entrance). */
  reset: (visible?: boolean) => void
  /** Anchor element for effect launch positions. */
  element: () => HTMLDivElement | null
}

const TRAVEL_BACK_MS = 1180
// Blue travels / idles at this fraction of the stage width from the left edge,
// then runs back to his combat slot. The edge translate is computed from live
// geometry (not a fixed offset) so the run stays on-screen at any stage width.
const EDGE_CENTER_FRAC = 0.09
const EDGE_FALLBACK_PX = -150
const RUN_IN_MIN_MS = 840
const RUN_IN_MAX_MS = 1280
const RUN_IN_PX_PER_MS = 0.34

function runInDuration(fromPx: number, toPx: number): number {
  const distance = Math.abs(toPx - fromPx)
  return Math.round(Math.min(RUN_IN_MAX_MS, Math.max(RUN_IN_MIN_MS, distance / RUN_IN_PX_PER_MS)))
}

/**
 * Blue on the battle stage. He rests on the idle sheet in the duel; combat
 * verbs are driven imperatively by the director, so no React re-renders happen
 * mid-choreography. The battle verb vocabulary is run / idle / attack / attack
 * end / hurt / death. Companion data exposes the same `attack` verb that
 * monster actors use.
 */
export const PlayerActor = forwardRef<
  PlayerActorHandle,
  {
    companion: CompanionSpriteDefinition
    battle: CompanionBattleSheets
    label: string
    companionSlug?: string | null
    scale?: number
    className?: string
  }
>(function PlayerActor({ companion, battle, label, companionSlug, scale = 0.78, className }, ref) {
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const effectiveScale = companion.metrics.scale * scale
  // The leftward translate of the current travel cycle, captured when Blue
  // heads back so the later hold/run beats all share the same on-screen edge.
  const edgeXRef = useRef<number | null>(null)
  const defeatedRef = useRef(false)
  // Each verb that sets a new pose claims a token; the deferred idle-restores of
  // one-shots (hurt/miss run longer than the beat that awaits them) only apply
  // when no newer verb has taken the stage since.
  const poseTokenRef = useRef(0)

  function claimPose(): number {
    poseTokenRef.current += 1
    return poseTokenRef.current
  }

  function restIfCurrent(token: number): () => void {
    return () => {
      if (token === poseTokenRef.current) rest()
    }
  }

  function freezeDefeatFrame() {
    const sprite = spriteRef.current
    if (!sprite) return
    sprite.setAnimation(battle.death)
    sprite.pause()
    sprite.goToFrame(battle.death.frameCount - 1)
  }

  /** Leftward translate that parks Blue's body near the stage's left edge.
   *  Must be read while Blue is at his combat rest (translateX 0); mid-travel
   *  the cached `edgeXRef` is used instead. */
  function computeEdgeX(): number {
    const node = wrapRef.current
    const stage = node?.closest('[data-testid="battle-stage"]') as HTMLElement | null
    if (!node || !stage) return EDGE_FALLBACK_PX
    const stageBox = stage.getBoundingClientRect()
    const nodeBox = node.getBoundingClientRect()
    const nodeCenter = nodeBox.left + nodeBox.width / 2
    const targetCenter = stageBox.left + stageBox.width * EDGE_CENTER_FRAC
    // Only ever push left, and always a readable distance so the lag-behind
    // drift is visible even when Blue already sits near the left.
    return Math.min(-60, targetCenter - nodeCenter)
  }

  function rest() {
    // A corpse never stands back up; only the explicit revival verbs
    // (reset/travel/run) clear the defeat.
    if (defeatedRef.current) return
    wrapRef.current?.classList.remove('is-attacking')
    spriteRef.current?.setAnimation(companion.sprites.idle)
  }

  function setRun() {
    spriteRef.current?.setAnimation(companion.sprites.run)
  }

  useImperativeHandle(ref, () => ({
    beginAttack: () => {
      wrapRef.current?.classList.add('is-attacking')
    },

    cancelAttack: () => {
      rest()
    },

    attack: async () => {
      // Play the full attack windup. The director immediately follows with the
      // cast-end sheet while launching the skill effect, so no frozen frame is
      // held during projectile playback.
      claimPose()
      wrapRef.current?.classList.add('is-attacking')
      await playOneShotSprite(spriteRef.current, battle.attack)
    },

    endAttack: async (missed = false) => {
      const token = claimPose()
      const release = missed ? battle.miss : battle.attackEnd
      if (missed) {
        wrapRef.current?.animate(
          [
            { transform: 'translateX(0)' },
            { transform: 'translateX(-10px)', offset: 0.4 },
            { transform: 'translateX(0)' },
          ],
          { duration: 420, easing: 'ease-out' },
        )
      }
      await playOneShotAndRestore(spriteRef.current, release, restIfCurrent(token))
    },

    hurt: () => {
      const token = claimPose()
      playCompanionHurtSound(companionSlug)
      return playOneShotAndRestore(spriteRef.current, battle.hurt, restIfCurrent(token))
    },

    defeat: async () => {
      claimPose()
      if (defeatedRef.current) {
        // Already dropped at the killing blow; just keep holding the corpse.
        freezeDefeatFrame()
        return
      }
      defeatedRef.current = true
      playCompanionDeathSound(companionSlug)
      await playOneShotAndHold(spriteRef.current, battle.death)
    },

    travelBack: async (ms = TRAVEL_BACK_MS) => {
      claimPose()
      defeatedRef.current = false
      const node = wrapRef.current
      playRunSound(ms)
      setRun()
      if (!node) return
      // Run back toward the left edge, staying visible: Blue drifts left slower
      // than the faster world pan (the director scrolls the backdrop in
      // parallel), lagging until he reaches the edge.
      const edgeX = computeEdgeX()
      edgeXRef.current = edgeX
      const pushBack = node.animate(
        [
          { transform: 'translateX(0px)', opacity: 1 },
          { transform: `translateX(${edgeX}px)`, opacity: 1 },
        ],
        { duration: ms, easing: 'cubic-bezier(0.4, 0, 0.4, 1)', fill: 'forwards' },
      )
      await finishElementAnimation(pushBack, ms)
      node.style.transform = `translateX(${edgeX}px)`
      node.style.opacity = '1'
      pushBack.cancel()
    },

    holdTravel: (ms = 900) => {
      claimPose()
      defeatedRef.current = false
      const node = wrapRef.current
      playRunSound(ms)
      setRun()
      if (!node) return
      const edgeX = edgeXRef.current ?? computeEdgeX()
      edgeXRef.current = edgeX
      node.style.transform = `translateX(${edgeX}px)`
      node.style.opacity = '1'
    },

    runIn: (toPx = 0) =>
      new Promise<void>((resolve) => {
        claimPose()
        defeatedRef.current = false
        const node = wrapRef.current
        setRun()
        if (!node) {
          resolve()
          return
        }
        // Run from the travel edge toward the wide-frame hold near the foe.
        node.style.opacity = '1'
        const startX = edgeXRef.current ?? computeEdgeX()
        edgeXRef.current = null
        const runMs = runInDuration(startX, toPx)
        playRunSound(runMs)
        const dash = node.animate(
          [{ transform: `translateX(${startX}px)` }, { transform: `translateX(${toPx}px)` }],
          { duration: runMs, easing: 'linear', fill: 'forwards' },
        )
        finishElementAnimation(dash, runMs)
          .then(() => {
            node.style.transform = `translateX(${toPx}px)`
            dash.cancel()
          })
          .catch(() => {})
          .finally(() => {
            // Monster engaged: Blue settles into idle for the duel.
            rest()
            resolve()
          })
      }),

    slideTo: (toPx, ms = 820) =>
      new Promise<void>((resolve) => {
        const node = wrapRef.current
        if (!node) {
          resolve()
          return
        }
        const fromPx = readElementTranslateX(node)
        if (fromPx === toPx) {
          resolve()
          return
        }
        // The camera lock drags Blue a readable distance - stride through it.
        const strides = Math.abs(toPx - fromPx) > 24
        if (strides) {
          claimPose()
          playRunSound(ms)
          setRun()
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
            if (strides) rest()
            resolve()
          })
      }),

    reset: (visible = true) => {
      claimPose()
      defeatedRef.current = false
      edgeXRef.current = null
      const node = wrapRef.current
      if (node) {
        node.style.transform = 'translateX(0)'
        node.style.opacity = visible ? '1' : '0'
      }
      rest()
    },

    element: () => wrapRef.current,
  }))

  return (
    <div
      ref={wrapRef}
      className={className ? `battle-player-actor ${className}` : 'battle-player-actor'}
    >
      <SpriteAnimator
        ref={spriteRef}
        animation={companion.sprites.idle}
        scale={effectiveScale}
        anchorToPixelBounds
        layoutAnimation={companion.sprites.idle}
        pixelAnchorAnimation={companion.sprites.idle}
        pixelAnchorFallback={{ bottomOffset: companion.metrics.footOffset }}
        aria-label={`${label}, your combat companion`}
      />
    </div>
  )
},
)
