import { useMemo } from 'react'
import type { CSSProperties, ReactNode } from 'react'

import { BattleBackdrop } from '@/shared/battle/components/BattleBackdrop'
import { HealthBar } from '@/shared/battle/components/HealthBar'
import { MonsterActor } from '@/shared/battle/components/MonsterActor'
import { PlayerActor } from '@/shared/battle/components/PlayerActor'
import { SpritePortrait } from '@/shared/battle/components/SpritePortrait'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { labelForMonster } from '@/shared/battle/monsterDescriptors'
import type { BattleMonster, BattleStage as BattleStageConfig, StageLanding } from '@/shared/battle/types'
import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import type { SpriteDef } from '@/shared/cosmetics/types'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { getStoryWorld, monsterSkin } from '@/shared/story-worlds/registry'
import type { StoryWorldDef } from '@/shared/story-worlds/types'
import { storyWorldStyle } from '@/shared/story-worlds/theme'
import { cn } from '@/shared/utils/cn'

const DEFAULT_RAIL_Y = 88

type BattleStageVariant = 'adventure' | 'challenge'

const BATTLE_MODE_CONFIG: Record<
  BattleStageVariant,
  {
    stageClass: string
    arenaClass: string
    railClass: string
    scrollBackdrop: boolean
    monsterBaseLeft: number
    monsterSpread: number
  }
> = {
  adventure: {
    stageClass: 'battle-stage--adventure',
    arenaClass: 'battle-arena--pack',
    railClass: 'battle-landing-rail--pack',
    scrollBackdrop: true,
    monsterBaseLeft: 85,
    monsterSpread: 8,
  },
  challenge: {
    stageClass: 'battle-stage--challenge',
    arenaClass: 'battle-arena--challenge',
    railClass: 'battle-landing-rail--challenge',
    // Pan the backdrop too: the challenge entrance runs Blue in while the camera
    // follows, so a frozen background made him look like he was running on a
    // treadmill. Scroll only fires on the explicit run-in/center beats.
    scrollBackdrop: true,
    monsterBaseLeft: 85,
    monsterSpread: 0,
  },
}

export function BattleStage({
  director,
  variant,
  stage,
  groundFooter,
  centerOverlay,
  topRight,
  className,
  storyWorldSlug,
}: {
  director: BattleDirector
  variant: BattleStageVariant
  stage?: BattleStageConfig | null
  groundFooter?: ReactNode
  centerOverlay?: ReactNode
  topRight?: ReactNode
  className?: string
  storyWorldSlug?: string | null
}) {
  const { companion, companionSlug } = usePlayerLoadout()
  const mode = BATTLE_MODE_CONFIG[variant]
  const storyWorld = getStoryWorld(storyWorldSlug)
  // Memoize on the (stable) companion so the sprite objects keep a stable
  // identity across resolve-driven re-renders. Rebuilding them every render
  // churned the SpriteAnimator's `animation` prop, whose prop-sync effect then
  // reset Blue to idle frame 0 — clobbering an in-flight cast animation.
  const player = useMemo(() => companionFromDef(companion), [companion])
  const playerBattle = useMemo(() => companionBattleFromDef(companion), [companion])
  const railY = railPercent(stage?.landing)
  const parallaxUrl = resolveParallaxUrl(storyWorld, stage)
  const playerMeter =
    typeof director.playerHp === 'number' && typeof director.playerMaxHp === 'number'
      ? { current: director.playerHp, max: director.playerMaxHp }
      : null

  return (
    <section
      data-testid="battle-stage"
      className={cn('battle-stage bg-background', mode.stageClass, className)}
      style={{ ...storyWorldStyle(storyWorld), '--battle-rail-y': `${railY}%` } as CSSProperties}
      aria-label="Battle stage"
    >
      <BattleBackdrop
        ref={director.bindBackdrop}
        parallaxUrl={parallaxUrl}
        scrollEnabled={mode.scrollBackdrop}
      />
      <BattleLand landing={stage?.landing ?? null} />

      <div className={cn('battle-arena', mode.arenaClass)}>
        <div ref={director.bindBackEffectLayer} className="battle-effect-layer battle-effect-layer--back" aria-hidden />
        <div ref={director.bindCamera} className="battle-camera">
          <div className={cn('battle-landing-rail', mode.railClass)} style={{ top: `${railY}%` }}>
            {player && playerBattle ? (
              <div className="battle-player-slot">
                <PlayerActor
                  ref={director.bindPlayer}
                  companion={player}
                  battle={playerBattle}
                  label={companion.label || companionSlug}
                  companionSlug={companionSlug}
                />
              </div>
            ) : null}

            {director.roster.map((monster, index) => (
              <MonsterSlot
                key={`${director.rosterEpoch}:${monster.id}`}
                monster={monster}
                index={index}
                total={director.roster.length}
                baseLeft={mode.monsterBaseLeft}
                spreadStep={mode.monsterSpread}
                stagedHidden={director.stagedMonsterIds.has(monster.id)}
                active={director.activeMonsterId === monster.id}
                bindMonster={director.bindMonster}
                storyWorld={storyWorld}
              />
            ))}
          </div>
        </div>
        <div ref={director.bindEffectLayer} className="battle-effect-layer battle-effect-layer--front" aria-hidden />
      </div>

      <div className={cn('battle-combatants-hud', groundFooter && 'has-ground-footer')}>
        <UnitHud
          kind="player"
          name={companion.label || 'Companion'}
          current={playerMeter?.current ?? null}
          max={playerMeter?.max ?? null}
          portrait={companion.sprites.portrait ?? companion.sprites.idle}
          defeated={director.defeated}
        />
        <div className="battle-combatants-hud__enemies">
          {director.roster.map((monster) => {
            const skin = monsterSkin(storyWorld, monster.species)
            return (
              <UnitHud
                key={monster.id}
                kind="enemy"
                name={skin?.label ?? labelForMonster(monster) ?? 'Enemy'}
                current={monster.hp}
                max={monster.max_hp}
                portrait={skin?.sprites.portrait ?? skin?.sprites.idle}
                defeated={!monster.alive}
                active={director.activeMonsterId === monster.id}
              />
            )
          })}
        </div>
      </div>

      {groundFooter ? <div className="battle-ground-footer">{groundFooter}</div> : null}
      {topRight ? <div className="battle-corner-overlay">{topRight}</div> : null}
      {centerOverlay ? (
        <>
          <div className="battle-center-overlay-backdrop" aria-hidden />
          <div className="battle-center-overlay">{centerOverlay}</div>
        </>
      ) : null}
      {director.defeated ? <div className="battle-defeated-veil" aria-hidden /> : null}
    </section>
  )
}

function MonsterSlot({
  monster,
  index,
  total,
  baseLeft,
  spreadStep,
  stagedHidden,
  active,
  bindMonster,
  storyWorld,
}: {
  monster: BattleMonster
  index: number
  total: number
  baseLeft: number
  spreadStep: number
  stagedHidden: boolean
  active: boolean
  bindMonster: BattleDirector['bindMonster']
  storyWorld: StoryWorldDef
}) {
  const spread = total <= 1 ? 0 : index - (total - 1) / 2
  const left = baseLeft + spread * spreadStep
  return (
    <div
      className="battle-monster-slot"
      style={{ left: `${left}%` }}
    >
      <span className="battle-range-shadow" aria-hidden />
      <MonsterActor
        ref={(handle) => bindMonster(monster.id, handle)}
        monster={monster}
        stagedHidden={stagedHidden}
        className={active ? 'is-active' : undefined}
        storyWorld={storyWorld}
      />
    </div>
  )
}

function UnitHud({
  kind,
  name,
  current,
  max,
  portrait,
  defeated,
  active,
}: {
  kind: 'player' | 'enemy'
  name: string
  current: number | null
  max: number | null
  portrait?: SpriteDef
  defeated?: boolean
  active?: boolean
}) {
  if (current === null || max === null) return null
  return (
    <div
      className={cn(
        'battle-unit-hud',
        kind === 'enemy' ? 'battle-unit-hud--enemy' : 'battle-unit-hud--player',
        defeated && 'is-defeated',
        active && 'is-active',
      )}
    >
      <SpritePortrait
        sprite={portrait}
        label={name}
        className="battle-unit-hud__portrait"
        fallback={<span className="battle-unit-hud__portrait battle-unit-hud__portrait--fallback">?</span>}
      />
      <span className="battle-unit-hud__vitals">
        <span className="battle-unit-hud__name">{name}</span>
        <span className="battle-unit-hud__value">{Math.max(0, current)} / {max}</span>
        <HealthBar
          value={Math.max(0, current)}
          max={max}
          variant={kind === 'enemy' ? 'enemy' : 'hp'}
          className="battle-unit-hud__meter"
          aria-label={`${name} health`}
        />
      </span>
    </div>
  )
}

function BattleLand({ landing }: { landing: StageLanding | null }) {
  if (!landing) return null
  return (
    <div
      className="battle-land"
      style={{
        left: `${landing.x * 100}%`,
        top: `${landing.y * 100}%`,
        width: `${landing.width * 100}%`,
        height: `${landing.height * 100}%`,
      }}
      aria-hidden
    />
  )
}

function railPercent(landing?: StageLanding | null) {
  if (!landing) return DEFAULT_RAIL_Y
  return Math.max(48, Math.min(88, (landing.y + landing.height) * 100))
}

function resolveParallaxUrl(
  storyWorld: StoryWorldDef,
  stage?: BattleStageConfig | null,
): string | null {
  const slug = stage?.parallax?.slug
  if (slug) return storyWorld.battle.parallax?.[slug]?.src ?? storyWorld.battle.backdrop.src
  return storyWorld.battle.backdrop.src
}
