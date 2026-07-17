import { ChevronDown, HeartCrack, PersonStanding, Skull, Sparkles, Swords } from 'lucide-react'
import { type ComponentType, type RefObject, useEffect, useMemo, useRef, useState } from 'react'

import { EmptyState } from '@/shared/components/EmptyState'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { listStoryWorldMonsters, type StoryWorldMonsterEntry } from '@/shared/story-worlds/registry'
import type { MonsterEffectLayer } from '@/shared/story-worlds/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import {
  effectPlacementFromPixelAnchor,
  type EffectPixelPlacement,
} from '@/shared/sprites/effectPixelPlacement'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { useSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'

const MONSTER_GROUND_FRACTION = 0.18
const MONSTER_STAGE_FALLBACK = { width: 320, height: 208 }
const MONSTER_STAGE_PADDING = 12
const MONSTER_MAX_SCALE_BOOST = 1.25
const MONSTER_EFFECT_PREVIEW_BOOST = 1.2
const MONSTER_EFFECT_CENTER_FRACTION = 0.48
const MONSTER_MOVE_LABELS: Record<MonsterPreviewMove, string> = {
  idle: 'Idle',
  attack: 'Attack',
  hurt: 'Hurt',
  death: 'Death',
  skill: 'Skill FX',
}
const MONSTER_MOVE_ICONS: Record<MonsterPreviewMove, ComponentType<{ 'aria-hidden'?: boolean }>> = {
  idle: PersonStanding,
  attack: Swords,
  hurt: HeartCrack,
  death: Skull,
  skill: Sparkles,
}
const MONSTER_MOVE_ORDER: MonsterPreviewMove[] = ['idle', 'attack', 'hurt', 'death', 'skill']

type MonsterPreviewMove = 'idle' | 'attack' | 'hurt' | 'death' | 'skill'

type ElementSize = {
  width: number
  height: number
}

type EffectPoint = {
  x: number
  y: number
}

type EffectBounds = {
  left: number
  top: number
  right: number
  bottom: number
}

function clampFraction(value: number): number {
  return Math.min(1, Math.max(0, value))
}

function normalizedEffectPoint(value: unknown, fallback: EffectPoint): EffectPoint {
  if (!value || typeof value !== 'object') return fallback
  const point = value as { x?: unknown; y?: unknown }
  const x = Number(point.x)
  const y = Number(point.y)
  if (!Number.isFinite(x) || !Number.isFinite(y)) return fallback
  return { x: clampFraction(x), y: clampFraction(y) }
}

function normalizedEffectBounds(value: unknown): EffectBounds {
  if (!value || typeof value !== 'object') return { left: 0, top: 0, right: 1, bottom: 1 }
  const bounds = value as Partial<Record<keyof EffectBounds, unknown>>
  const rawLeft = Number(bounds.left)
  const rawTop = Number(bounds.top)
  const rawRight = Number(bounds.right)
  const rawBottom = Number(bounds.bottom)
  if (![rawLeft, rawTop, rawRight, rawBottom].every(Number.isFinite)) {
    return { left: 0, top: 0, right: 1, bottom: 1 }
  }
  const left = clampFraction(rawLeft)
  const top = clampFraction(rawTop)
  return {
    left,
    top,
    right: clampFraction(Math.max(left, rawRight)),
    bottom: clampFraction(Math.max(top, rawBottom)),
  }
}

function fittedEffectLayer({
  effect,
  layer,
  stage,
  measuredPlacement,
}: {
  effect: NonNullable<StoryWorldMonsterEntry['skin']['attack']['effect']>
  layer: MonsterEffectLayer
  stage: ElementSize
  measuredPlacement?: EffectPixelPlacement | null
}) {
  const fallbackAnchor = effect.anchor === 'feet' ? { x: 0.5, y: 0.86 } : { x: 0.5, y: 0.5 }
  const placeAnchor = normalizedEffectPoint(
    effect.place_anchor ?? effect.placeAnchor ?? measuredPlacement?.anchor,
    fallbackAnchor,
  )
  const placeBounds = normalizedEffectBounds(
    effect.place_bounds ?? effect.placeBounds ?? measuredPlacement?.bounds,
  )
  const target = {
    x: stage.width / 2,
    y:
      effect.anchor === 'feet'
        ? stage.height * (1 - MONSTER_GROUND_FRACTION)
        : stage.height * MONSTER_EFFECT_CENTER_FRACTION,
  }
  const authoredScale = (layer.scale ?? effect.scale ?? 0.7) * MONSTER_EFFECT_PREVIEW_BOOST
  const displayScale = layer.displayScale ?? 1
  const scaledWidth = layer.frameWidth * displayScale * authoredScale
  const scaledHeight = layer.frameHeight * displayScale * authoredScale
  const extents = {
    left: Math.max(1, (placeAnchor.x - placeBounds.left) * scaledWidth),
    right: Math.max(1, (placeBounds.right - placeAnchor.x) * scaledWidth),
    top: Math.max(1, (placeAnchor.y - placeBounds.top) * scaledHeight),
    bottom: Math.max(1, (placeBounds.bottom - placeAnchor.y) * scaledHeight),
  }
  const fitFactor = Math.min(
    1,
    Math.max(1, target.x - MONSTER_STAGE_PADDING) / extents.left,
    Math.max(1, stage.width - target.x - MONSTER_STAGE_PADDING) / extents.right,
    Math.max(1, target.y - MONSTER_STAGE_PADDING) / extents.top,
    Math.max(1, stage.height - target.y - MONSTER_STAGE_PADDING) / extents.bottom,
  )

  return {
    scale: Math.max(0.1, authoredScale * fitFactor),
    placeAnchor,
    target,
  }
}

function useElementSize<T extends HTMLElement>(): [RefObject<T | null>, ElementSize] {
  const ref = useRef<T>(null)
  const [size, setSize] = useState<ElementSize>(MONSTER_STAGE_FALLBACK)

  useEffect(() => {
    const node = ref.current
    if (!node) return undefined
    const element = node

    function updateSize() {
      const box = element.getBoundingClientRect()
      if (box.width > 0 && box.height > 0) {
        setSize({ width: box.width, height: box.height })
      }
    }

    updateSize()
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(updateSize)
    observer?.observe(element)
    window.addEventListener('resize', updateSize)

    return () => {
      observer?.disconnect()
      window.removeEventListener('resize', updateSize)
    }
  }, [])

  return [ref, size]
}

function fittedMonsterScale({
  activeAnchor,
  idleAnchor,
  animation,
  baseScale,
  footOffset,
  stage,
}: {
  activeAnchor: ReturnType<typeof useSpritePixelAnchor>
  idleAnchor: ReturnType<typeof useSpritePixelAnchor>
  animation: SpriteAnimation
  baseScale: number
  footOffset: number
  stage: ElementSize
}) {
  const bounds = activeAnchor?.bounds ?? idleAnchor?.bounds ?? {
    left: 0,
    top: 0,
    right: animation.frameWidth - 1,
    bottom: animation.frameHeight - 1,
  }
  const displayScale = animation.displayScale ?? 1
  const bottomOffset = idleAnchor?.bottomOffset ?? footOffset
  const centerOffsetX = idleAnchor?.centerOffsetX ?? 0

  const leftExtent = Math.max(
    1,
    (animation.frameWidth / 2 - centerOffsetX - bounds.left) * displayScale,
  )
  const rightExtent = Math.max(
    1,
    (bounds.right + 1 - animation.frameWidth / 2 + centerOffsetX) * displayScale,
  )
  const topExtent = Math.max(
    1,
    (animation.frameHeight - bottomOffset - bounds.top) * displayScale,
  )
  const bottomExtent = Math.max(
    0,
    (bounds.bottom + 1 - (animation.frameHeight - bottomOffset)) * displayScale,
  )

  const groundBottom = stage.height * MONSTER_GROUND_FRACTION
  const availableAbove = Math.max(1, stage.height - groundBottom - MONSTER_STAGE_PADDING)
  const availableBelow = Math.max(1, groundBottom - MONSTER_STAGE_PADDING / 2)
  const availableSide = Math.max(1, stage.width / 2 - MONSTER_STAGE_PADDING)
  const fitFactors = [
    MONSTER_MAX_SCALE_BOOST,
    availableAbove / (topExtent * baseScale),
    availableSide / (leftExtent * baseScale),
    availableSide / (rightExtent * baseScale),
  ]
  if (bottomExtent > 0) fitFactors.push(availableBelow / (bottomExtent * baseScale))

  return Math.max(0.1, baseScale * Math.min(...fitFactors))
}

function spriteAnimation(sprite: SpriteDef, name: string, loop?: boolean): SpriteAnimation {
  return {
    name,
    src: sprite.src,
    frameWidth: sprite.frameWidth,
    frameHeight: sprite.frameHeight,
    columns: sprite.columns,
    rows: sprite.rows,
    frameCount: sprite.frameCount,
    fps: sprite.fps,
    loop: loop ?? sprite.loops,
    displayScale: sprite.displayScale,
  }
}

function effectAnimation(layer: MonsterEffectLayer, name: string): SpriteAnimation {
  return spriteAnimation(layer, name, false)
}

export function StoryMonsterShowcase({
  storyLabel,
  worldSlug,
}: {
  storyLabel: string
  worldSlug: string
}) {
  const monsters = useMemo(() => listStoryWorldMonsters(worldSlug), [worldSlug])
  const [selectedSlug, setSelectedSlug] = useState(() => monsters[0]?.slug ?? '')
  const [move, setMove] = useState<MonsterPreviewMove>('idle')
  const [playKey, setPlayKey] = useState(0)
  const [stageRef, stageSize] = useElementSize<HTMLDivElement>()
  const selected = monsters.find((monster) => monster.slug === selectedSlug) ?? monsters[0]
  const idleSprite = selected?.skin.sprites.idle
  const idleAnimation = selected && idleSprite ? spriteAnimation(idleSprite, `${selected.slug}.idle`, true) : null
  const idleAnchor = useSpritePixelAnchor(idleAnimation)
  const requestedMove = selected && canPreviewMove(selected, move) ? move : 'idle'
  const requestedSprite = selected?.skin.sprites[requestedMove === 'skill' ? 'idle' : requestedMove] ?? idleSprite
  const requestedAnimation = selected && requestedSprite
    ? spriteAnimation(requestedSprite, `${selected.slug}.${requestedMove}`, requestedMove === 'idle')
    : null
  const activeAnchor = useSpritePixelAnchor(requestedAnimation)
  const previewEffect = requestedMove === 'skill' ? selected?.skin.attack.effect : undefined
  const previewFrontLayer = previewEffect?.layers.find((layer) => layer.layer !== 'back') ?? previewEffect?.layers[0]
  const previewEffectAnimation = previewFrontLayer
    ? effectAnimation(previewFrontLayer, `${selected?.slug ?? 'monster'}.effect.preview`)
    : null
  const previewEffectPixels = useSpritePixelAnchor(previewEffectAnimation)
  const measuredEffectPlacement = previewEffect && previewEffectAnimation
    ? effectPlacementFromPixelAnchor(
        previewEffectPixels,
        previewEffectAnimation,
        previewEffect.playback,
        previewEffect.anchor ?? 'center',
        previewEffect.impact_start_frame,
      )
    : null

  if (!selected) {
    return (
      <div className="shop-contents-block shop-monster-showcase shop-monster-showcase--empty">
        <EmptyState title="No monsters registered" description="This story world has no monster registry yet." />
      </div>
    )
  }

  const activeMove = requestedMove
  const animation = requestedAnimation ?? spriteAnimation(selected.skin.sprites.idle, `${selected.slug}.idle`, true)
  const scale = fittedMonsterScale({
    activeAnchor,
    idleAnchor,
    animation: idleAnimation ?? animation,
    baseScale: selected.skin.scale,
    footOffset: selected.skin.metrics.foot_offset ?? 0,
    stage: stageSize,
  })
  const attackEffect = activeMove === 'skill' ? previewEffect : undefined
  const effectLayers = attackEffect?.layers ?? []
  const isSkillFx = activeMove === 'skill'

  function selectMonster(monster: StoryWorldMonsterEntry) {
    setSelectedSlug(monster.slug)
    setMove('idle')
    setPlayKey((key) => key + 1)
  }

  function selectMove(nextMove: MonsterPreviewMove) {
    if (!canPreviewMove(selected, nextMove)) return
    setMove(nextMove)
    setPlayKey((key) => key + 1)
  }

  return (
    <div className="shop-contents-block shop-monster-showcase" aria-label={`${storyLabel} monster registry`}>
      <header className="shop-block-head">
        <span>Monster Registry</span>
        <small>{monsters.length} foes</small>
      </header>

      <div
        ref={stageRef}
        className="shop-monster-stage"
        aria-label={
          isSkillFx
            ? `${selected.label} skill effect preview`
            : `${selected.label} ${MONSTER_MOVE_LABELS[activeMove]} preview`
        }
        data-mode={isSkillFx ? 'skill-fx' : 'monster'}
      >
        <div className="shop-monster-stage-glow" aria-hidden="true" />
        {!isSkillFx ? (
          <div className="shop-monster-actor">
            <SpriteAnimator
              key={`${selected.slug}-${activeMove}-${playKey}`}
              animation={animation}
              scale={scale}
              anchorToPixelBounds
              layoutAnimation={idleAnimation ?? undefined}
              pixelAnchorAnimation={idleAnimation ?? undefined}
              pixelAnchorFallback={{ bottomOffset: selected.skin.metrics.foot_offset ?? 0 }}
              pixelated
              aria-label={`${selected.label} ${MONSTER_MOVE_LABELS[activeMove]}`}
            />
          </div>
        ) : null}
        {attackEffect
          ? effectLayers.map((layer, index) => {
              const geometry = fittedEffectLayer({
                effect: attackEffect,
                layer,
                stage: stageSize,
                measuredPlacement: measuredEffectPlacement,
              })
              return (
                <div
                  key={`${selected.slug}-fx-${playKey}-${index}`}
                  className="shop-monster-effect-layer"
                  data-anchor={attackEffect.anchor ?? 'center'}
                  style={{
                    left: geometry.target.x,
                    top: geometry.target.y,
                    opacity: layer.opacity ?? 1,
                    transform: `translate(calc(-${geometry.placeAnchor.x * 100}% + ${layer.offset_x ?? 0}px), calc(-${geometry.placeAnchor.y * 100}% + ${layer.offset_y ?? 0}px))`,
                    zIndex: layer.layer === 'back' ? 0 : 3,
                  }}
                >
                  <SpriteAnimator
                    animation={effectAnimation(layer, `${selected.slug}.effect.${index}`)}
                    scale={geometry.scale}
                    pixelated
                    aria-label={`${selected.label} skill effect`}
                  />
                </div>
              )
            })
          : null}

        <div className="shop-monster-toolbar" aria-label="Monster animation controls">
          <div className="shop-monster-toolbar-id">
            <strong>{selected.label}</strong>
          </div>
          <div className="shop-monster-toolbar-moves" role="tablist" aria-label="Preview pose">
            {MONSTER_MOVE_ORDER.map((option) => {
              const disabled = !canPreviewMove(selected, option)
              const Icon = MONSTER_MOVE_ICONS[option]
              return (
                <button
                  key={option}
                  type="button"
                  role="tab"
                  className="shop-monster-move"
                  data-active={activeMove === option}
                  aria-selected={activeMove === option}
                  disabled={disabled}
                  title={MONSTER_MOVE_LABELS[option]}
                  aria-label={MONSTER_MOVE_LABELS[option]}
                  onClick={() => selectMove(option)}
                >
                  <Icon aria-hidden={true} />
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <MonsterSelect monsters={monsters} selected={selected} onSelect={selectMonster} />
    </div>
  )
}

function MonsterSelect({
  monsters,
  selected,
  onSelect,
}: {
  monsters: StoryWorldMonsterEntry[]
  selected: StoryWorldMonsterEntry
  onSelect: (monster: StoryWorldMonsterEntry) => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return undefined
    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }
    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open])

  return (
    <div className="shop-monster-select" ref={rootRef}>
      <button
        type="button"
        className="shop-monster-select-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="shop-monster-select-value">
          <strong>{selected.label}</strong>
        </span>
        <ChevronDown aria-hidden="true" data-open={open} />
      </button>
      {open ? (
        <ul className="shop-monster-select-menu" role="listbox" aria-label="Story monsters">
          {monsters.map((monster) => (
            <li key={monster.slug} role="option" aria-selected={monster.slug === selected.slug}>
              <button
                type="button"
                className="shop-monster-select-option"
                data-active={monster.slug === selected.slug}
                onClick={() => {
                  onSelect(monster)
                  setOpen(false)
                }}
              >
                <span>{monster.label}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}

function canPreviewMove(monster: StoryWorldMonsterEntry, move: MonsterPreviewMove): boolean {
  if (move === 'skill') return Boolean(monster.skin.attack.effect?.layers?.length)
  return Boolean(monster.skin.sprites[move])
}
