import { Check } from 'lucide-react'

import type { TierRun } from './tierWorkspaceTypes'
import { difficultyLabel } from './tierOutcome'

/** Saved scenario clears for the current difficulty, including failed runs and replays. */
export function TierScenarioStepper({ run }: { run: TierRun }) {
  const { completed, total, cleared } = run.progress
  if (total < 1) return null

  const difficulty = difficultyLabel(run)
  const remaining = Math.max(0, total - completed)
  const nextDifficulty = run.difficulty === 'easy' ? 'Medium' : run.difficulty === 'medium' ? 'Hard' : null
  const milestone = cleared
    ? nextDifficulty ? `${nextDifficulty} unlocked` : `${difficulty} tier complete`
    : `${remaining} more to ${nextDifficulty ? `unlock ${nextDifficulty}` : `finish ${difficulty}`}`

  return <section className="tier-scenario-stepper" aria-label={`${difficulty} scenario progress`}>
    <h4>{difficulty} scenarios</h4>
    <ol className="tier-scenario-stepper__steps" aria-label={`${completed} of ${total} ${difficulty} scenarios cleared`}>
      {Array.from({ length: total }, (_, index) => {
        const done = index < completed
        return <li key={index} className={done ? 'is-cleared' : undefined} aria-label={`Scenario ${index + 1} ${done ? 'cleared' : 'remaining'}`}>
          <span className="tier-scenario-stepper__node" aria-hidden="true">
            {done ? <Check /> : index + 1}
          </span>
        </li>
      })}
    </ol>
    <p>{completed} of {total} cleared · {milestone}</p>
  </section>
}
