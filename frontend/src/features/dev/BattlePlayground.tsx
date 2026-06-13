import { useEffect, useRef, useState } from 'react'

import { TowerBattleStage } from '@/shared/battle/components/TowerBattleStage'
import { clientAdventureRoster, clientChallengeRoster, deriveBattleEvents } from '@/shared/battle/deriveBattleEvents'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'

/**
 * ⚠ Dev-only battle sandbox (/dev/battle): every actor, cast phase, effect and
 * choreography beat, driven by buttons and a fake-latency slider — no run, no
 * backend. Compiled away in production builds (DEV-gated route).
 */
export function BattlePlayground() {
  const director = useBattleDirector()
  const [variant, setVariant] = useState<'adventure' | 'challenge'>('adventure')
  const [latency, setLatency] = useState(450)
  const [skill, setSkill] = useState('commit')
  const [mana, setMana] = useState(8)
  const [levelIndex, setLevelIndex] = useState(0)
  const encounterRef = useRef(0)

  const maxMana = 8

  useEffect(() => {
    director.setEncounter(
      variant === 'adventure' ? clientAdventureRoster(0, 6) : clientChallengeRoster(0, 8),
    )
    // Run once on mount / variant flip only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [variant])

  function submit(kind: 'hit' | 'miss' | 'solve' | 'diagnostic') {
    director.onCastStart()
    const spends = kind !== 'diagnostic'
    const nextMana = spends ? Math.max(0, mana - 1) : mana
    setMana(nextMana)
    window.setTimeout(() => {
      const block = deriveBattleEvents({
        solved: kind === 'solve',
        counted: kind !== 'diagnostic',
        progressed: kind === 'hit',
        skill,
        // Defeat = the mana ran dry on a non-solving counted command.
        defeated: spends && kind !== 'solve' && nextMana <= 0,
        monsters: director.currentMonsters(),
      })
      director.onResolve(block)
      if (kind === 'solve') {
        const nextIndex = levelIndex + 1
        setLevelIndex(nextIndex)
        encounterRef.current = nextIndex
        director.setEncounter(
          variant === 'adventure'
            ? clientAdventureRoster(nextIndex, 6)
            : clientChallengeRoster(nextIndex, 8),
          { travel: variant === 'adventure' },
        )
      }
    }, latency)
  }

  return (
    <div className="workspace-bg min-h-screen p-6 text-foreground">
      <h1 className="mb-3 text-lg font-semibold">Battle playground</h1>
      <TowerBattleStage
        director={director}
        variant={variant}
        mana={{ current: mana, max: maxMana }}
        className="h-64 w-full max-w-4xl"
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
        <button className="rounded border border-amber-400/40 px-3 py-1" onClick={() => submit('miss')}>
          Miss
        </button>
        <button className="rounded border border-emerald-400/40 px-3 py-1" onClick={() => submit('solve')}>
          Solve level
        </button>
        <button className="rounded border border-border px-3 py-1" onClick={() => submit('diagnostic')}>
          Diagnostic (free)
        </button>
        <button
          className="rounded border border-border px-3 py-1"
          onClick={() => {
            setMana(maxMana)
            setLevelIndex(0)
            director.setEncounter(
              variant === 'adventure' ? clientAdventureRoster(0, 6) : clientChallengeRoster(0, 8),
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
          <option value="challenge">challenge (boss)</option>
        </select>
      </div>
    </div>
  )
}

export const Component = BattlePlayground
