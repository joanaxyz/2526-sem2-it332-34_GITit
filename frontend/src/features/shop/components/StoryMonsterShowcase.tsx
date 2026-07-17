import { ChevronDown, HeartCrack, PersonStanding, Skull, Sparkles, Swords } from 'lucide-react'
import { type ComponentType, useEffect, useMemo, useRef, useState } from 'react'

import { EmptyState } from '@/shared/components/EmptyState'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { listStoryWorldMonsters, type StoryWorldMonsterEntry } from '@/shared/story-worlds/registry'
import type { MonsterEffectLayer } from '@/shared/story-worlds/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { useSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'

const MONSTER_STAGE_HEIGHT = 260
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
  const selected = monsters.find((monster) => monster.slug === selectedSlug) ?? monsters[0]
  // Measured visible pixels of the idle sheet (async, cached per sheet). Stage fitting
  // must not use the raw frame box: frame padding varies per sheet (512px lancer frames
  // vs 256px peers) and would shrink exactly the monsters with roomy frames.
  const idleSprite = selected?.skin.sprites.idle
  const idleAnimation = selected && idleSprite ? spriteAnimation(idleSprite, `${selected.slug}.idle`, true) : null
  const idleAnchor = useSpritePixelAnchor(idleAnimation)

  if (!selected) {
    return (
      <div className="shop-contents-block shop-monster-showcase shop-monster-showcase--empty">
        <EmptyState title="No monsters registered" description="This story world has no monster registry yet." />
      </div>
    )
  }

  const activeMove = canPreviewMove(selected, move) ? move : 'idle'
  const sprite = selected.skin.sprites[activeMove === 'skill' ? 'idle' : activeMove] ?? selected.skin.sprites.idle
  const animation = spriteAnimation(sprite, `${selected.slug}.${activeMove}`, activeMove === 'idle')
  // Battle-native size (visible px × displayScale × species scale), shrunk only if the
  // monster itself would overflow the stage — keeps roster sizes relatively honest.
  const visibleHeight = (idleAnchor?.bounds.height ?? animation.frameHeight) * (idleAnimation?.displayScale ?? 1)
  const scale = Math.min(1.35, MONSTER_STAGE_HEIGHT / (visibleHeight * selected.skin.scale)) * selected.skin.scale
  const effectLayers = activeMove === 'skill' ? selected.skin.attack.effect?.layers ?? [] : []
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
        ) : null}
        {effectLayers.map((layer, index) => (
          <div
            key={`${selected.slug}-fx-${playKey}-${index}`}
            className="shop-monster-effect-layer"
            style={{
              opacity: layer.opacity ?? 1,
              transform: `translate(calc(-50% + ${layer.offset_x ?? 0}px), calc(-50% + ${layer.offset_y ?? 0}px))`,
              zIndex: layer.layer === 'back' ? 0 : 3,
            }}
          >
            <SpriteAnimator
              animation={effectAnimation(layer, `${selected.slug}.effect.${index}`)}
              scale={(layer.scale ?? selected.skin.attack.effect?.scale ?? 0.7) * 1.2}
              pixelated
              aria-label={`${selected.label} skill effect`}
            />
          </div>
        ))}

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

// Roster picker as a compact themed dropdown. The sprite-rail geometry fought the
// wildly different frame paddings per sheet; a name list is legible and honest.
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
