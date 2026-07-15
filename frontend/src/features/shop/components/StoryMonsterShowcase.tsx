import { ChevronLeft, ChevronRight, HeartCrack, PersonStanding, Skull, Sparkles, Swords } from 'lucide-react'
import { type CSSProperties, type ComponentType, useMemo, useState } from 'react'

import { EmptyState } from '@/shared/components/EmptyState'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { listStoryWorldMonsters, type StoryWorldMonsterEntry } from '@/shared/story-worlds/registry'
import type { MonsterEffectLayer } from '@/shared/story-worlds/types'
import { SpriteAnimator } from '@/shared/sprites/SpriteAnimator'
import type { SpriteAnimation } from '@/shared/sprites/types'
import { useSpritePixelAnchor } from '@/shared/sprites/usePixelBounds'

const MONSTER_STAGE_HEIGHT = 210
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
  battleStageSrc,
  storyLabel,
  worldSlug,
}: {
  battleStageSrc?: string
  storyLabel: string
  worldSlug: string
}) {
  const monsters = useMemo(() => listStoryWorldMonsters(worldSlug), [worldSlug])
  const [selectedSlug, setSelectedSlug] = useState(() => monsters[0]?.slug ?? '')
  const [move, setMove] = useState<MonsterPreviewMove>('idle')
  const [playKey, setPlayKey] = useState(0)
  const [monsterPage, setMonsterPage] = useState(0)
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
  const scale = Math.min(1, MONSTER_STAGE_HEIGHT / (visibleHeight * selected.skin.scale)) * selected.skin.scale
  const effectLayers = activeMove === 'skill' ? selected.skin.attack.effect?.layers ?? [] : []
  const isSkillFx = activeMove === 'skill'
  const monstersPerPage = 7
  const monsterPageCount = Math.max(1, Math.ceil(monsters.length / monstersPerPage))
  const clampedMonsterPage = Math.min(monsterPage, monsterPageCount - 1)
  const visibleMonsters = monsters.slice(clampedMonsterPage * monstersPerPage, (clampedMonsterPage + 1) * monstersPerPage)

  function goMonsterPage(nextPage: number) {
    setMonsterPage(Math.max(0, Math.min(monsterPageCount - 1, nextPage)))
  }

  function selectMonster(monster: StoryWorldMonsterEntry) {
    const nextIndex = monsters.findIndex((entry) => entry.slug === monster.slug)
    if (nextIndex >= 0) setMonsterPage(Math.floor(nextIndex / monstersPerPage))
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
    <div className="shop-contents-block shop-monster-showcase">
      <header className="shop-block-head">
        <span>Monster Registry</span>
        <small>{monsters.length} foes from {storyLabel}</small>
      </header>

      <div
        className="shop-monster-stage"
        aria-label={
          isSkillFx
            ? `${selected.label} skill effect preview`
            : `${selected.label} ${MONSTER_MOVE_LABELS[activeMove]} preview`
        }
        style={battleStageSrc ? { '--monster-stage-bg': `url(${battleStageSrc})` } as CSSProperties : undefined}
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
            <small>{selected.tier}</small>
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

      <div className="shop-monster-carousel" aria-label="All story monsters">
        {monsterPageCount > 1 ? (
          <button
            type="button"
            className="shop-preview-pager shop-preview-pager--left"
            aria-label="Previous monsters"
            disabled={clampedMonsterPage === 0}
            onClick={() => goMonsterPage(clampedMonsterPage - 1)}
          >
            <ChevronLeft aria-hidden="true" />
          </button>
        ) : null}
        <div className="shop-monster-carousel-track" role="list">
          {visibleMonsters.map((monster) => (
            <MonsterPickerButton
              key={monster.slug}
              monster={monster}
              active={monster.slug === selected.slug}
              onSelect={() => selectMonster(monster)}
            />
          ))}
        </div>
        {monsterPageCount > 1 ? (
          <button
            type="button"
            className="shop-preview-pager shop-preview-pager--right"
            aria-label="Next monsters"
            disabled={clampedMonsterPage === monsterPageCount - 1}
            onClick={() => goMonsterPage(clampedMonsterPage + 1)}
          >
            <ChevronRight aria-hidden="true" />
          </button>
        ) : null}
        {monsterPageCount > 1 ? (
          <div className="shop-preview-pager-dots" role="tablist" aria-label="Monster pages">
            {Array.from({ length: monsterPageCount }, (_, i) => (
              <button
                key={i}
                type="button"
                role="tab"
                aria-selected={i === clampedMonsterPage}
                aria-label={`Monster page ${i + 1} of ${monsterPageCount}`}
                data-active={i === clampedMonsterPage}
                onClick={() => goMonsterPage(i)}
              />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  )
}

function canPreviewMove(monster: StoryWorldMonsterEntry, move: MonsterPreviewMove): boolean {
  if (move === 'skill') return Boolean(monster.skin.attack.effect?.layers?.length)
  return Boolean(monster.skin.sprites[move])
}

const MONSTER_PICK_STAGE_HEIGHT = 56

// Foot-accurate roster picker: no card chrome, just the sprite standing on a
// ground line. Scale + vertical anchor both derive from measured alpha pixels
// (frame padding differs per sheet) so every monster's feet land on the same
// line regardless of how much transparent margin its sheet carries.
function MonsterPickerButton({
  monster,
  active,
  onSelect,
}: {
  monster: StoryWorldMonsterEntry
  active: boolean
  onSelect: () => void
}) {
  const portrait = monster.portrait ?? monster.skin.sprites.idle
  const animation = spriteAnimation(portrait, `${monster.slug}.pick`, false)
  const anchor = useSpritePixelAnchor(animation)
  const displayScale = animation.displayScale ?? 1
  const visibleHeight = (anchor?.bounds.height ?? animation.frameHeight) * displayScale
  const scale = Math.min(1, MONSTER_PICK_STAGE_HEIGHT / (visibleHeight * monster.skin.scale)) * monster.skin.scale
  const anchorScale = displayScale * scale
  const bottomOffset = (anchor?.bottomOffset ?? monster.skin.metrics.foot_offset ?? 0) * anchorScale
  const centerOffsetX = (anchor?.centerOffsetX ?? 0) * anchorScale

  return (
    <button
      type="button"
      role="listitem"
      className="shop-monster-pick"
      data-active={active}
      onClick={onSelect}
      aria-label={monster.label}
      title={monster.label}
    >
      <span className="shop-monster-pick-stage">
        <span className="shop-monster-pick-ground" aria-hidden="true" />
        <span
          className="shop-monster-pick-sprite"
          style={{
            width: animation.frameWidth * scale,
            height: animation.frameHeight * scale,
            backgroundImage: `url(${animation.src})`,
            backgroundSize: `${animation.columns * 100}% ${animation.rows * 100}%`,
            backgroundPosition: '0% 0%',
            transform: `translate(${centerOffsetX}px, ${bottomOffset}px)`,
          }}
        />
      </span>
    </button>
  )
}
