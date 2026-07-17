import { useEffect, useRef, useState } from 'react'

import { BattleStage } from '@/shared/battle/components/BattleStage'
import { clientAdventureRoster, clientChallengeRoster, deriveBattleEventsFromCommandOutcome } from '@/shared/battle/deriveBattleEvents'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'

/**
 * Dev-only battle sandbox (/dev/battle): every actor, attack phase, effect and
 * choreography beat, driven by buttons and a fake-latency slider - no run, no
 * backend. Monster + backdrop visuals come from the selected StoryWorld, while
 * player visuals come from the companion registry. Compiled away in production builds (DEV-gated route).
 */
function BattlePlayground() {
  const director = useBattleDirector()
  const [variant, setVariant] = useState<'adventure' | 'challenge'>('adventure')
  const [latency, setLatency] = useState(450)
  const [skill, setSkill] = useState('commit')
  const [playerHp, setPlayerHp] = useState(8)
  const [levelIndex, setLevelIndex] = useState(0)
  const encounterRef = useRef(0)

  const maxHp = 8

  useEffect(() => {
    director.setEncounter(
      variant === 'adventure' ? clientAdventureRoster(0, 6) : clientChallengeRoster(0, 8),
      { entry: 'run', playerHp, playerMaxHp: maxHp },
    )
    // Restage on variant flip. The director object is intentionally excluded
    // because it is an imperative facade.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [variant])

  function submit(kind: 'hit' | 'miss' | 'solve' | 'diagnostic') {
    director.onAttackStart()
    const hpBefore = director.playerHp ?? playerHp
    window.setTimeout(() => {
      const block = deriveBattleEventsFromCommandOutcome({
        outcome: {
          processed: true,
          counted: kind !== 'diagnostic',
          solved: kind === 'solve',
          failed: kind !== 'solve' && kind !== 'diagnostic' && hpBefore <= 1,
          command_family: skill,
          previous_rules_passing: 0,
          rules_passing: kind === 'hit' || kind === 'solve' ? 1 : 0,
          rules_delta: kind === 'hit' || kind === 'solve' ? 1 : 0,
          total_rules: Math.max(1, director.currentMonsters()[0]?.max_hp ?? 1),
          max_counted_commands: maxHp,
          counted_command_count: kind !== 'diagnostic' ? maxHp - hpBefore + 1 : maxHp - hpBefore,
          remaining_counted_commands: kind !== 'diagnostic' ? Math.max(0, hpBefore - 1) : hpBefore,
        },
        skill,
        monsters: director.currentMonsters(),
      })
      setPlayerHp(block.player_hp ?? hpBefore)
      director.onResolve(block)
      if (kind === 'solve') {
        const nextIndex = levelIndex + 1
        setLevelIndex(nextIndex)
        encounterRef.current = nextIndex
        setPlayerHp(maxHp)
        director.setEncounter(
          variant === 'adventure' ? clientAdventureRoster(nextIndex, 6) : clientChallengeRoster(nextIndex, 8),
          { travel: variant === 'adventure', entry: variant === 'adventure' ? 'run' : 'none', playerHp: maxHp, playerMaxHp: maxHp },
        )
      }
    }, latency)
  }

  return (
    <div className="workspace-bg min-h-screen p-6 text-foreground">
      <h1 className="mb-3 text-lg font-semibold">Battle playground</h1>
      <BattleStage
        director={director}
        variant={variant}
        className="battle-playground-stage"
        stage={null}
        groundFooter={
          variant === 'adventure' ? (
            <div className="h-1.5 rounded-full bg-primary/20">
              <div className="h-full w-1/3 rounded-full bg-primary/70" />
            </div>
          ) : undefined
        }
      />

      <div className="mt-4 flex max-w-4xl flex-wrap items-center gap-2 text-sm">
        <button className="rounded border border-primary/40 px-3 py-1" onClick={() => submit('hit')}>
          Hit ({skill})
        </button>
        <button className="rounded border border-warning/40 px-3 py-1" onClick={() => submit('miss')}>
          Miss
        </button>
        <button className="rounded border border-primary/40 px-3 py-1" onClick={() => submit('solve')}>
          Solve level
        </button>
        <button className="rounded border border-border px-3 py-1" onClick={() => submit('diagnostic')}>
          Diagnostic (free)
        </button>
        <button
          className="rounded border border-border px-3 py-1"
          onClick={() => {
            setPlayerHp(maxHp)
            setLevelIndex(0)
            director.setEncounter(
              variant === 'adventure' ? clientAdventureRoster(0, 6) : clientChallengeRoster(0, 8),
              { entry: 'run', playerHp: maxHp, playerMaxHp: maxHp },
            )
          }}
        >
          Reset
        </button>

        <label className="ml-4 flex items-center gap-2">
          latency {latency}ms
          <input
            type="range"
            min={100}
            max={2500}
            step={50}
            value={latency}
            onChange={(e) => setLatency(Number(e.target.value))}
          />
        </label>

        <select
          className="rounded border border-border bg-background px-2 py-1"
          value={skill}
          onChange={(e) => setSkill(e.target.value)}
        >
          {['commit', 'add', 'merge', 'push', 'pull', 'branch', 'rebase', 'reset', 'stash'].map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>

        <select
          className="rounded border border-border bg-background px-2 py-1"
          value={variant}
          onChange={(e) => setVariant(e.target.value as 'adventure' | 'challenge')}
        >
          <option value="adventure">adventure</option>
          <option value="challenge">challenge</option>
        </select>

        <span className="rounded border border-border/70 px-3 py-1 text-muted-foreground">
          HP {playerHp}/{maxHp}
        </span>
      </div>
    </div>
  )
}

export const Component = BattlePlayground
