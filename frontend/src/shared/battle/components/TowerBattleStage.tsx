import { type CSSProperties, type ReactNode, useMemo } from 'react'

import { HealthBar } from '@/shared/battle/components/HealthBar'
import { MonsterActor } from '@/shared/battle/components/MonsterActor'
import { PlayerActor } from '@/shared/battle/components/PlayerActor'
import { TowerBackdrop } from '@/shared/battle/components/TowerBackdrop'
import { TowerCrystal } from '@/shared/battle/components/TowerCrystal'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { computeSky } from '@/features/storeys/sky/skyPhases'
import { cn } from '@/shared/utils/cn'

/** Height of the stone ledge (the tower floor) as a % of the stage. */
const LEDGE_PCT = 26

/**
 * One floor of the tower as a defense arena: Blue guards the crystal on a stone
 * ledge while monsters march in from the right. The sky echoes the /tower page
 * (computeSky at the current time of day). Clearing the floor flies Blue up to
 * the next — the director drives every actor imperatively, so this component
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

      {/* The stone ledge — this floor of the tower, echoing the page separators. */}
      <div className="battle-ledge absolute inset-x-0 bottom-0" style={{ height: `${LEDGE_PCT}%` }} aria-hidden>
        <span className="battle-ledge-crenels" />
      </div>

      {/* The crystal Blue defends, planted on the ledge at the left. */}
      <div className="absolute left-[9%] z-10" style={{ bottom: `${LEDGE_PCT}%` }}>
        <TowerCrystal ref={bindCrystal} scale={isBossStage ? 1.05 : 1.2} />
      </div>

      {/* Blue, standing guard between the crystal and the monsters. */}
      <div className="absolute left-[27%] z-10" style={{ bottom: `calc(${LEDGE_PCT}% - 6px)` }}>
        <PlayerActor ref={bindPlayer} scale={playerScale} />
      </div>

      {/* The encounter, anchored right, marching order right-to-left. */}
      <div
        className="absolute right-[5%] z-10 flex flex-row-reverse items-end gap-3"
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

      {/* Effects overlay — throwaway WAAPI nodes only. */}
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
