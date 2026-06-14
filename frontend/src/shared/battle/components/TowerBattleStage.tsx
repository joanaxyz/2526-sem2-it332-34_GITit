import { useQuery } from '@tanstack/react-query'
import { type CSSProperties, type ReactNode, useMemo } from 'react'

import { HealthBar } from '@/shared/battle/components/HealthBar'
import { MonsterActor } from '@/shared/battle/components/MonsterActor'
import { PlayerActor } from '@/shared/battle/components/PlayerActor'
import { TowerBackdrop } from '@/shared/battle/components/TowerBackdrop'
import { TowerCrystal } from '@/shared/battle/components/TowerCrystal'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { computeSky } from '@/features/tower-map/sky/skyPhases'
import { queryKeys } from '@/shared/api/queryKeys'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { BattleArtifactAssetDescriptor, CharacterAssetDescriptor } from '@/shared/assets/types'
import { characterBattleFromDescriptor, characterFromDescriptor } from '@/shared/sprites/characters'
import { crystalFromDescriptor } from '@/shared/sprites/crystal'
import { cn } from '@/shared/utils/cn'

/** Height of the stone ledge (the tower floor) as a % of the stage. */
const LEDGE_PCT = 26

/**
 * One floor of the tower as a defense arena: Blue holds the left of a stone
 * ledge and blasts the monsters besieging the crystal on the right. The sky
 * echoes the /tower page
 * (computeSky at the current time of day). Clearing the floor flies Blue up to
 * the next - the director drives every actor imperatively, so this component
 * re-renders only on roster/HP snapshots.
 */
export function TowerBattleStage({
  director,
  variant,
  mana,
  timeOfDay,
  groundFooter,
  className,
}: {
  director: BattleDirector
  variant: 'adventure' | 'challenge'
  /** Blue's mana = the command budget. Null hides the plaque (e.g. replay). */
  mana: { current: number; max: number } | null
  /** 0..24 hour; defaults to now so the battle sky matches the live tower sky. */
  timeOfDay?: number
  groundFooter?: ReactNode
  className?: string
}) {
  const isBossStage = variant === 'challenge'
  const playerScale = isBossStage ? 0.42 : 0.5
  const { roster, defeated, bindPlayer, bindBackdrop, bindCrystal, bindEffectLayer, bindMonster } = director

  // Blue and the crystal render from their seeded backend descriptors (like
  // monsters). Both maps are tiny and cached; the actors mount once ready —
  // no choreography runs before the player submits, so the late ref-bind is safe.
  const characterQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('character'),
    queryFn: () => assetsApi.getDescriptors('character'),
    staleTime: 5 * 60 * 1000,
  })
  const artifactQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('battle_artifact'),
    queryFn: () => assetsApi.getDescriptors('battle_artifact'),
    staleTime: 5 * 60 * 1000,
  })

  const player = useMemo(() => {
    const descriptor = characterQuery.data?.results?.blue
    if (descriptor?.kind !== 'character') return null
    const blue = descriptor as CharacterAssetDescriptor
    const character = characterFromDescriptor(blue)
    const battle = characterBattleFromDescriptor(blue)
    return character && battle ? { character, battle } : null
  }, [characterQuery.data])

  const crystal = useMemo(() => {
    const descriptor = artifactQuery.data?.results?.crystal
    if (descriptor?.kind !== 'battle_artifact') return null
    return crystalFromDescriptor(descriptor as BattleArtifactAssetDescriptor)
  }, [artifactQuery.data])

  const skyVars = useMemo(() => {
    const hour = timeOfDay ?? (() => {
      const now = new Date()
      return now.getHours() + now.getMinutes() / 60
    })()
    return computeSky(hour).vars as CSSProperties
  }, [timeOfDay])

  return (
    <div
      className={cn(
        'relative isolate overflow-hidden rounded-lg border border-primary/20',
        'shadow-[0_0_18px_rgba(0,245,212,0.08)]',
        className,
      )}
      style={{ ...skyVars, contain: 'layout paint style' }}
      data-testid="battle-stage"
    >
      <TowerBackdrop ref={bindBackdrop} />

      {/* The stone ledge - this floor of the tower, echoing the page separators. */}
      <div className="battle-ledge absolute inset-x-0 bottom-0" style={{ height: `${LEDGE_PCT}%` }} aria-hidden>
        <span className="battle-ledge-crenels" />
      </div>

      {/* Centered, width-capped arena: the sky and ledge stay full-bleed, but
          Blue, the monsters, and the crystal stay clustered near the tower so a
          wide panel never strands the companion far from the fight. */}
      <div className="battle-arena absolute inset-y-0 left-1/2 w-full max-w-[34rem] -translate-x-1/2">
        {/* The crystal Blue defends, planted on the right of the ledge. */}
        {crystal ? (
          <div className="absolute right-[10%] z-[6]" style={{ bottom: `${LEDGE_PCT}%` }}>
            <TowerCrystal ref={bindCrystal} crystal={crystal} scale={isBossStage ? 1.05 : 1.2} />
          </div>
        ) : null}

        {/* Blue holds the left flank, blasting monsters off the crystal. */}
        {player ? (
          <div className="absolute left-[8%] z-10" style={{ bottom: `calc(${LEDGE_PCT}% - 6px)` }}>
            <PlayerActor ref={bindPlayer} character={player.character} battle={player.battle} scale={playerScale} />
          </div>
        ) : null}

        {/* The encounter besieges the crystal from the right; Blue strikes from
            the left. Anchored just left of the crystal, packed toward it. */}
        <div
          className="absolute right-[28%] z-10 flex flex-row-reverse items-end gap-3"
          style={{ bottom: `${LEDGE_PCT}%` }}
        >
          {roster.map((monster) => (
            <MonsterActor
              key={monster.id}
              ref={(handle) => bindMonster(monster.id, handle)}
              monster={monster}
              scale={isBossStage ? 1.2 : 1.45}
            />
          ))}
        </div>
      </div>

      {/* Mana plaque: the command budget styled as Blue's casting reserve. */}
      {mana ? (
        <div className="absolute left-2 top-2 z-20 flex items-center gap-2 rounded-md border border-primary/25 bg-background/70 px-2 py-1 backdrop-blur-sm">
          <span className="text-[10px] font-semibold uppercase tracking-widest text-primary">Mana</span>
          <HealthBar value={mana.current} max={mana.max} variant="mana" className="w-24" aria-label="Mana" />
          <span className="font-mono text-[10px] text-foreground/80">
            {mana.current}/{mana.max}
          </span>
        </div>
      ) : null}

      {/* Effects overlay - throwaway WAAPI nodes only. */}
      <div
        ref={bindEffectLayer}
        className="pointer-events-none absolute inset-0 z-20"
        style={{ contain: 'strict' }}
        aria-hidden
      />

      {/* Defeat: the stage dims until the outcome modal takes over. */}
      {defeated ? (
        <div className="absolute inset-0 z-30 bg-black/55 backdrop-blur-[1px] transition-opacity" aria-hidden />
      ) : null}

      {groundFooter ? <div className="absolute inset-x-2 bottom-1 z-20">{groundFooter}</div> : null}
    </div>
  )
}
