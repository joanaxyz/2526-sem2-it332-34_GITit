import { type CSSProperties, useEffect, useMemo, useRef, useState } from 'react'
import { BookOpen } from 'lucide-react'

import heroShowcasePedestalImage from '@/assets/images/hero_showcase_pedestal.png'
import { HomeAttackTarget } from '@/features/home/components/home-hub/HomeAttackTarget'
import { HomeCombatCompanionStatus } from '@/features/home/components/home-hub/HomeCompanionStatus'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import type { LearnedSkill } from '@/features/skills/types'
import { effectForSkill, effectPlacementForSkill } from '@/shared/battle/effects/effectRegistry'
import { isMotionReduced } from '@/shared/battle/hooks/battleMotion'
import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { GitCommandIcon, gitCommandFamily } from '@/shared/git/commandCatalog/commandIcons'
import { animationDuration } from '@/shared/sprites/animationTiming'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimatorHandle } from '@/shared/sprites/types'
import { useImagePixelBounds } from '@/shared/sprites/usePixelBounds'

type HomeCombatShowcaseProps = {
  companion: CompanionPresentation
  skills: LearnedSkill[] | undefined
  skillsLoading: boolean
}

function cssLengthToPx(value: string, context: Element): number | null {
  const trimmed = value.trim()
  const amount = Number.parseFloat(trimmed)
  if (!Number.isFinite(amount)) return null
  if (trimmed.endsWith('rem')) {
    const rootFontSize = Number.parseFloat(window.getComputedStyle(document.documentElement).fontSize)
    return amount * rootFontSize
  }
  if (trimmed.endsWith('em')) {
    const fontSize = Number.parseFloat(window.getComputedStyle(context).fontSize)
    return amount * fontSize
  }
  return amount
}

function homeGroundPoint(layer: HTMLElement, bodyImpact: { x: number; y: number }) {
  const layerBox = layer.getBoundingClientRect()
  const groundBottom = cssLengthToPx(
    window.getComputedStyle(layer).getPropertyValue('--home-sprite-ground-bottom'),
    layer,
  )
  const groundY = groundBottom == null ? layerBox.height * 0.82 : layerBox.height - groundBottom
  return { x: bodyImpact.x, y: Math.max(bodyImpact.y, groundY) }
}

export function HomeCombatShowcase({
  companion,
  skills,
  skillsLoading,
}: HomeCombatShowcaseProps) {
  const companionDef = companion.status === 'ready' ? companion.definition : null
  const companionSlug = companion.status === 'ready' ? companion.slug : null
  const companionRuntime = useMemo(
    () => (companionDef ? companionFromDef(companionDef) : null),
    [companionDef],
  )
  const companionBattle = useMemo(
    () => (companionDef ? companionBattleFromDef(companionDef) : null),
    [companionDef],
  )
  const companionPortrait = companionDef
    ? companionDef.sprites.portrait?.src ?? companionDef.sprites.idle?.src ?? ''
    : ''
  const companionAvatar = companionDef?.sprites.idle?.src ?? companionPortrait
  const hasSkills = (skills?.length ?? 0) > 0
  const [pickedId, setPickedId] = useState<number | null>(null)
  const selectedId = pickedId ?? skills?.[0]?.id ?? null
  const [activeMove, setActiveMove] = useState('Idle')
  const spriteRef = useRef<SpriteAnimatorHandle | null>(null)
  const fxRef = useRef<HTMLDivElement | null>(null)
  const attackerRef = useRef<HTMLDivElement | null>(null)
  const attackTargetRef = useRef<HTMLDivElement | null>(null)
  const targetBodyRef = useRef<HTMLDivElement | null>(null)
  const playTokenRef = useRef(0)
  const settleTimerRef = useRef<number | null>(null)
  const effectTimerRef = useRef<number | null>(null)
  const pedestalBounds = useImagePixelBounds(heroShowcasePedestalImage)
  const pedestalStyle = pedestalBounds
    ? ({
        '--pedestal-anchor-x': `${(pedestalBounds.centerOffsetX / pedestalBounds.naturalWidth) * 100}%`,
        '--pedestal-anchor-y': `${((pedestalBounds.naturalHeight - pedestalBounds.centerY) / pedestalBounds.naturalHeight) * 100}%`,
      } as CSSProperties)
    : undefined

  function clearScheduledWork() {
    if (settleTimerRef.current !== null) window.clearTimeout(settleTimerRef.current)
    if (effectTimerRef.current !== null) window.clearTimeout(effectTimerRef.current)
    settleTimerRef.current = null
    effectTimerRef.current = null
  }

  useEffect(() => () => {
    playTokenRef.current += 1
    clearScheduledWork()
  }, [])

  function playAttack() {
    const sprite = spriteRef.current
    if (!sprite || !companionRuntime || !companionBattle) return
    clearScheduledWork()
    playTokenRef.current += 1
    const token = playTokenRef.current
    setActiveMove('Attack')
    let settled = false
    const settle = () => {
      if (settled || playTokenRef.current !== token) return
      settled = true
      if (settleTimerRef.current !== null) window.clearTimeout(settleTimerRef.current)
      settleTimerRef.current = null
      sprite.setAnimation(companionRuntime.sprites.idle)
      setActiveMove('Idle')
    }
    sprite.setAnimation(companionBattle.attack, { onComplete: settle })
    settleTimerRef.current = window.setTimeout(settle, animationDuration(companionBattle.attack, 1600))
  }

  function flinchTarget() {
    const body = targetBodyRef.current
    if (!body || typeof body.animate !== 'function') return
    const flash = ['brightness(1)', 'brightness(2.1)', 'brightness(1.45)', 'brightness(1.1)', 'brightness(1)']
    const shake = isMotionReduced()
      ? ['none', 'none', 'none', 'none', 'none']
      : ['none', 'translateX(6px) scale(0.93)', 'translateX(-4px) scale(1.03)', 'translateX(2px)', 'none']
    body.animate(
      flash.map((filter, index) => ({ filter, transform: shake[index] })),
      { duration: 440, easing: 'ease-out' },
    )
  }

  function anchor(node: Element | null, xFrac = 0.5, yFrac = 0.5) {
    const layer = fxRef.current
    if (!layer || !node) return { x: 0, y: 0 }
    const layerBox = layer.getBoundingClientRect()
    const box = node.getBoundingClientRect()
    return { x: box.left + box.width * xFrac - layerBox.left, y: box.top + box.height * yFrac - layerBox.top }
  }

  function attackWithSkill(skill: LearnedSkill) {
    if (!companionSlug) return
    setPickedId(skill.id)
    playAttack()
    const layer = fxRef.current
    if (!layer) return

    const skillFamily = gitCommandFamily(skill.base_command)
    const { playback, anchor: impactAnchor } = effectPlacementForSkill(skillFamily, companionSlug)
    // Ground runs leave from the feet, everything else from the casting hand.
    const from = playback === 'ground' ? anchor(attackerRef.current, 0.82, 0.99) : anchor(attackerRef.current, 0.7, 0.42)
    const bodyImpact = anchor(attackTargetRef.current)
    const groundImpact = homeGroundPoint(layer, bodyImpact)
    const feetPlanted = playback === 'ground' || impactAnchor === 'feet'
    const to = playback === 'projectile' ? bodyImpact : feetPlanted ? groundImpact : bodyImpact
    const impactTo = playback === 'projectile' && impactAnchor === 'feet' ? groundImpact : undefined
    // The crystal floats, so a spell planted on the floor beneath it must rise
    // past its top. A scale-1 riser stands ~125px; aim ~20% past the crystal.
    const crystalTop = anchor(targetBodyRef.current, 0.5, 0).y
    const reach = groundImpact.y - crystalTop
    const sizeScale = reach > 0 ? Math.min(2.2, Math.max(1.2, reach / 105)) : 1.6
    effectTimerRef.current = window.setTimeout(() => {
      effectTimerRef.current = null
      void effectForSkill(skillFamily, companionSlug)({ layer, from, to, impactTo, sizeScale, onImpact: flinchTarget })
    }, 120)
  }

  if (companion.status !== 'ready') return <HomeCombatCompanionStatus companion={companion} />

  return (
    <>
      <section className="home-sprite-panel">
        <header className="ref-panel-head">Sprite Showcase</header>
        <div className="home-sprite-stage">
          <div className="home-sprite-rune" aria-hidden="true" />
          <img className="home-sprite-pedestal" src={heroShowcasePedestalImage} alt="" style={pedestalStyle} />
          <div className="home-sprite-avatar" ref={attackerRef}>
            {companionRuntime ? (
              <SpriteAnimator
                ref={spriteRef}
                animation={companionRuntime.sprites.idle}
                scale={companionRuntime.metrics.scale}
                anchorToPixelBounds
                layoutAnimation={companionRuntime.sprites.idle}
                pixelAnchorAnimation={companionRuntime.sprites.idle}
                pixelAnchorFallback={{ bottomOffset: companionRuntime.metrics.footOffset }}
                pixelated
                aria-label={`${companion.definition.label} ${activeMove.toLowerCase()} animation`}
              />
            ) : (
              <img src={companionAvatar} alt="" />
            )}
          </div>
          <HomeAttackTarget bodyRef={targetBodyRef} anchorRef={attackTargetRef} />
          <div className="home-sprite-fx" ref={fxRef} aria-hidden="true" />
        </div>
      </section>

      <section className="home-spellbook-panel" data-onboarding="profile-spellbook">
        <header className="ref-panel-head">
          <BookOpen aria-hidden="true" />
          Spellbook
          {!skillsLoading && hasSkills ? <em>{skills!.length} learned · click to attack</em> : null}
        </header>
        {skillsLoading ? (
          <div className="home-spellbook-grid" aria-hidden="true">
            {Array.from({ length: 8 }, (_, index) => (
              <span className="home-spellbook-skeleton" key={index} />
            ))}
          </div>
        ) : !hasSkills ? (
          <p className="home-spellbook-empty">
            Solve an Adventure with a command to inscribe your first spell.
          </p>
        ) : (
          <div className="home-spellbook-grid app-scrollbar">
            {skills!.map((skill) => (
              <button
                type="button"
                className={skill.id === selectedId ? 'is-selected' : ''}
                key={skill.id}
                title={skill.summary}
                aria-label={`Attack with ${skill.title} — ${skill.base_command}`}
                onClick={() => attackWithSkill(skill)}
              >
                <span className="home-command-icon">
                  <GitCommandIcon command={skill.base_command} />
                </span>
                <strong>{skill.base_command}</strong>
                <small>Chapter {skill.chapter_number}</small>
              </button>
            ))}
          </div>
        )}
      </section>
    </>
  )
}
