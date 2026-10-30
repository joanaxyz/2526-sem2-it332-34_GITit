import { useEffect, useEffectEvent, useMemo, useRef, useState } from 'react'

import { ENCOUNTER_SPELLS } from '@/features/landing/utils/landingContent'
import { effectForSkill, effectPlacementForSkill } from '@/shared/battle/effects/effectRegistry'
import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { DEFAULT_COMPANION_SLUG, getCompanion } from '@/shared/cosmetics/companions/registry'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'
import { animationDuration } from '@/shared/sprites/animationTiming'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation, SpriteAnimatorHandle } from '@/shared/sprites/types'
import { DEFAULT_STORY_WORLD_SLUG, getStoryWorld, monsterSkin } from '@/shared/story-worlds/registry'
import { cn } from '@/shared/utils/cn'
import { useMediaQuery } from '@/shared/utils/useMediaQuery'

const FOE_SPECIES = 'lich-king'
const AUTO_CAST_DELAY_MS = 900
const AUTO_CAST_INTERVAL_MS = 3400
const EFFECT_LEAD_MS = 120
const COMPACT_SCALE = 0.62

function sheet(sprite: SpriteDef, name: string, loop: boolean): SpriteAnimation {
  return {
    name,
    src: sprite.src,
    frameWidth: sprite.frameWidth,
    frameHeight: sprite.frameHeight,
    columns: sprite.columns,
    rows: sprite.rows,
    frameCount: sprite.frameCount,
    fps: sprite.fps,
    loop,
    displayScale: sprite.displayScale,
  }
}

// The resolved motion setting (shared/preferences) already folds in the OS
// preference, so the encounter also honours the in-app Motion switch.
function motionReduced() {
  return typeof document !== 'undefined' && document.documentElement.dataset.motion === 'reduced'
}

/**
 * Blue against a Spire monster, driven by the same sheets and spell effects as
 * a real battle. It casts on its own while on screen until the visitor picks a
 * spell, then waits for them.
 */
export function EncounterStage() {
  const companionDef = getCompanion(DEFAULT_COMPANION_SLUG)
  const companion = useMemo(() => companionFromDef(companionDef), [companionDef])
  const companionBattle = useMemo(() => companionBattleFromDef(companionDef), [companionDef])
  const foeSkin = monsterSkin(getStoryWorld(DEFAULT_STORY_WORLD_SLUG), FOE_SPECIES)
  const foe = useMemo(
    () =>
      foeSkin
        ? {
            idle: sheet(foeSkin.sprites.idle, `${FOE_SPECIES}.idle`, true),
            hurt: sheet(foeSkin.sprites.hurt ?? foeSkin.sprites.idle, `${FOE_SPECIES}.hurt`, false),
          }
        : null,
    [foeSkin],
  )

  const stageRef = useRef<HTMLDivElement>(null)
  const fxRef = useRef<HTMLDivElement>(null)
  const casterRef = useRef<HTMLDivElement>(null)
  const foeBodyRef = useRef<HTMLDivElement>(null)
  const casterSpriteRef = useRef<SpriteAnimatorHandle>(null)
  const foeSpriteRef = useRef<SpriteAnimatorHandle>(null)
  const timersRef = useRef<number[]>([])

  const [reduced] = useState(motionReduced)
  const actorScale = useMediaQuery('(max-width: 720px)') ? COMPACT_SCALE : 1
  const [inView, setInView] = useState(false)
  const [visitorTookOver, setVisitorTookOver] = useState(false)
  const [activeSpell, setActiveSpell] = useState<string | null>(null)
  const [autoIndex, setAutoIndex] = useState(0)

  function later(fn: () => void, ms: number) {
    timersRef.current.push(window.setTimeout(fn, ms))
  }

  useEffect(
    () => () => {
      for (const timer of timersRef.current) window.clearTimeout(timer)
    },
    [],
  )

  useEffect(() => {
    const node = stageRef.current
    if (!node || typeof IntersectionObserver === 'undefined') return
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0.35 })
    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  function point(node: Element | null, xFrac: number, yFrac: number) {
    const layer = fxRef.current
    if (!layer || !node) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    const box = node.getBoundingClientRect()
    return { x: box.left + box.width * xFrac - layerBox.left, y: box.top + box.height * yFrac - layerBox.top }
  }

  function flinchFoe() {
    if (foe) {
      const restFoe = () => foeSpriteRef.current?.setAnimation(foe.idle)
      foeSpriteRef.current?.setAnimation(foe.hurt, { onComplete: restFoe })
      later(restFoe, animationDuration(foe.hurt, 1200))
    }
    const body = foeBodyRef.current
    if (!body || typeof body.animate !== 'function') return
    const flash = ['brightness(1)', 'brightness(2)', 'brightness(1.4)', 'brightness(1)']
    const shake = reduced ? ['none', 'none', 'none', 'none'] : ['none', 'translateX(8px)', 'translateX(-4px)', 'none']
    body.animate(
      flash.map((filter, index) => ({ filter, transform: shake[index] })),
      { duration: 420, easing: 'ease-out' },
    )
  }

  function cast(family: string) {
    const caster = casterSpriteRef.current
    const layer = fxRef.current
    if (!caster || !layer || !companion || !companionBattle || activeSpell) return

    setActiveSpell(family)
    const restCaster = () => caster.setAnimation(companion.sprites.idle)
    caster.setAnimation(companionBattle.attack, { onComplete: restCaster })
    const attackMs = animationDuration(companionBattle.attack, 1600)
    later(restCaster, attackMs)
    later(() => setActiveSpell(null), attackMs + 500)

    const { playback, anchor } = effectPlacementForSkill(family, DEFAULT_COMPANION_SLUG)
    const from = playback === 'ground' ? point(casterRef.current, 0.8, 0.98) : point(casterRef.current, 0.7, 0.42)
    const body = point(foeBodyRef.current, 0.5, 0.55)
    const ground = point(foeBodyRef.current, 0.5, 0.97)
    const planted = playback === 'ground' || anchor === 'feet'
    const to = playback === 'projectile' ? body : planted ? ground : body
    const impactTo = playback === 'projectile' && anchor === 'feet' ? ground : undefined
    later(() => {
      void effectForSkill(family, DEFAULT_COMPANION_SLUG)({ layer, from, to, impactTo, sizeScale: 1.4 * actorScale, onImpact: flinchFoe })
    }, EFFECT_LEAD_MS)
  }

  const autoCast = useEffectEvent(() => {
    cast(ENCOUNTER_SPELLS[autoIndex].family)
    setAutoIndex((index) => (index + 1) % ENCOUNTER_SPELLS.length)
  })

  useEffect(() => {
    if (reduced || !inView || visitorTookOver || activeSpell) return
    const timer = window.setTimeout(autoCast, autoIndex === 0 ? AUTO_CAST_DELAY_MS : AUTO_CAST_INTERVAL_MS)
    return () => window.clearTimeout(timer)
  }, [reduced, inView, visitorTookOver, activeSpell, autoIndex])

  if (!companion || !foe || !foeSkin) return null

  return (
    <div className="landing-arena">
      <div ref={stageRef} className="landing-stage">
        <span className="landing-stage__ground" aria-hidden="true" />
        <div ref={casterRef} className="landing-stage__caster">
          <SpriteAnimator
            ref={casterSpriteRef}
            animation={companion.sprites.idle}
            scale={companion.metrics.scale * actorScale}
            anchorToPixelBounds
            layoutAnimation={companion.sprites.idle}
            pixelAnchorAnimation={companion.sprites.idle}
            pixelAnchorFallback={{ bottomOffset: companion.metrics.footOffset }}
            pixelated
            aria-label={`${companionDef.label}, your companion`}
          />
        </div>
        <div className="landing-stage__foe">
          <div ref={foeBodyRef} className="landing-stage__foe-body">
            <SpriteAnimator
              ref={foeSpriteRef}
              animation={foe.idle}
              scale={foeSkin.scale * actorScale}
              anchorToPixelBounds
              layoutAnimation={foe.idle}
              pixelAnchorAnimation={foe.idle}
              pixelAnchorFallback={{ bottomOffset: foeSkin.metrics.foot_offset }}
              flipX
              pixelated
              aria-label={foeSkin.label}
            />
          </div>
          <p className="landing-stage__nameplate">{foeSkin.label}</p>
        </div>
        <div ref={fxRef} className="landing-stage__fx" aria-hidden="true" />
      </div>

      <div className="landing-spells" role="group" aria-label="Cast a Git command">
        {ENCOUNTER_SPELLS.map((spell) => (
          <button
            key={spell.family}
            type="button"
            className={cn('landing-spells__spell', activeSpell === spell.family && 'is-active')}
            disabled={activeSpell !== null}
            onClick={() => {
              setVisitorTookOver(true)
              cast(spell.family)
            }}
          >
            <GitCommandIcon command={spell.command} className="landing-spells__icon" />
            {spell.command}
          </button>
        ))}
      </div>
    </div>
  )
}
