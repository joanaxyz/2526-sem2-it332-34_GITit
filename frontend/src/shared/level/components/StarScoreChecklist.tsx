import { Check, Circle, Minus } from 'lucide-react'

import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import { cn } from '@/shared/utils/cn'

import './star-score-checklist.css'

export type StarBreakdown = ApiSchemas['StarBreakdownResponse']

const LABELS = {
  clear: 'Reach the target state',
  command_target: 'Stay within the command target',
  retry_allowance: 'Stay within target with at most one retry',
  generous_target: 'Finish within the generous target',
  efficient_target: 'Finish within the efficient target',
} as const

/** Displays server-owned eligibility; never calculates a grade in the browser. */
export function StarScoreChecklist({ breakdown, active = false, tier = false, multiScenario = false, savedStars, variant = 'full' }: {
  breakdown: StarBreakdown
  variant?: 'full' | 'compact' | 'result'
  active?: boolean
  tier?: boolean
  multiScenario?: boolean
  savedStars?: number
}) {
  if (variant === 'result') return <section className="star-checklist" aria-label="Star checklist">
    {(breakdown.scoring_policy_version ?? 1) < 2 ? <p>Earlier scoring rules</p> : null}
    <ul>{breakdown.criteria.map(criterion => {
      const Icon = criterion.state === 'earned' ? Check : Minus
      const target = criterion.key === 'efficient_target' || criterion.key === 'command_target' ? breakdown.command_target : breakdown.generous_target
      return <li key={criterion.key} className={`star-checklist__row is-${criterion.state}`}><Icon className="star-checklist__icon" aria-hidden="true" /><div><p className="star-checklist__label">{LABELS[criterion.key]}</p>{criterion.key !== 'clear' ? <p className="star-checklist__detail">{criterion.key === 'retry_allowance' ? `${breakdown.retry_count} retries / 1 allowed.` : `${breakdown.counted_commands} / ${target} counted commands.`}</p> : null}</div><span className="star-checklist__state">{criterion.state === 'earned' ? '+1' : 'Not earned'}</span></li>
    })}</ul>
  </section>
  if (variant === 'compact') return <CompactStarChecklist breakdown={breakdown} />
  if ((breakdown.scoring_policy_version ?? 1) >= 2) {
    return <CurrentStarChecklist breakdown={breakdown} active={active} multiScenario={multiScenario} savedStars={savedStars} />
  }
  const overTarget = Math.max(0, breakdown.counted_commands - breakdown.command_target)
  const notCleared = breakdown.criteria.some((criterion) => criterion.reason === 'not_cleared')
  const summary = breakdown.graded_under_previous_rules
    ? 'This run was graded under earlier scoring rules. Replay to earn stars under the current rules.'
    : notCleared
    ? 'The target state was not reached. No stars earned.'
    : overTarget > 0
      ? `Command target exceeded by ${overTarget}. Both bonus stars ${active ? 'are unavailable' : 'were not earned'}.`
      : breakdown.retry_count > 1
        ? 'The retry allowance was exceeded. The third star requires at most one retry.'
        : active ? 'All three stars are still available. Clear the scenario to earn them.' : 'All three star conditions met.'

  return (
    <section className="star-checklist" aria-label="Star checklist">
      <div className="star-checklist__heading">
        <h4>Star checklist</h4>
        <span>{active ? 'Available on clear' : 'Earned this run'} <strong>{active ? breakdown.available_stars : breakdown.stars} / 3</strong></span>
      </div>
      <p className={cn('star-checklist__summary', (overTarget > 0 || breakdown.retry_count > 1 || notCleared) && 'is-reduced')}>
        {summary}
      </p>
      <ul>
        {breakdown.criteria.map((criterion) => {
          const Icon = criterion.state === 'earned' ? Check : criterion.state === 'missed' ? Minus : Circle
          const detail = criterion.reason === 'previous_scoring_rules'
            ? 'Recorded under earlier scoring rules.'
            : criterion.key === 'clear'
            ? criterion.state === 'earned' ? 'Scenario cleared.' : 'Clear the scenario to unlock its stars.'
            : criterion.key === 'command_target'
              ? `${breakdown.counted_commands} / ${breakdown.command_target} counted commands.`
              : criterion.reason === 'command_target_exceeded'
                ? `${breakdown.retry_count} retries / 1 allowed. This bonus also requires staying within the command target.`
                : `${breakdown.retry_count} ${breakdown.retry_count === 1 ? 'retry' : 'retries'} / 1 allowed.`
          return (
            <li key={criterion.key} className={`star-checklist__row is-${criterion.state}`}>
              <Icon className="star-checklist__icon" aria-hidden="true" />
              <div>
                <p className="star-checklist__label">{LABELS[criterion.key]}</p>
                <p className="star-checklist__detail">{detail}</p>
              </div>
              <span className="star-checklist__state">
                {criterion.state === 'earned' ? '+1 earned' : criterion.state === 'pending' ? '+1 on clear' : active ? 'Unavailable' : 'Not earned'}
              </span>
            </li>
          )
        })}
      </ul>
      <details className="star-checklist__rules" onClick={(event) => event.stopPropagation()} onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') event.stopPropagation()
      }}>
        <summary tabIndex={0}>What counts toward the score?</summary>
        <p className="star-checklist__footnote">
          Git commands that change state and invalid commands count. Valid inspections, file edits and opening the command guide are free.
        </p>
        <p className="star-checklist__footnote">Failed attempts and starting over after submitting commands use a retry. Empty starts are free.</p>
        {tier ? <p className="star-checklist__footnote">Before your first clear, retries carry across scenarios in this difficulty tier.</p> : null}
        <p className="star-checklist__footnote">A fresh replay starts a new retry allowance. Retry and Start over continue the current one.</p>
        {multiScenario ? <p className="star-checklist__footnote">Each scenario has its own command target. Your lowest scenario best becomes your saved level score.</p> : null}
      </details>
      {savedStars !== undefined ? (
        <p className="star-checklist__saved">Saved best{multiScenario ? ' for this level' : ''}: <strong>{savedStars} / 3</strong>. Replays can improve it; lower scores never replace it.</p>
      ) : null}
    </section>
  )
}


function CurrentStarChecklist({ breakdown, active, multiScenario, savedStars }: {
  breakdown: StarBreakdown; active: boolean; multiScenario: boolean; savedStars?: number
}) {
  return <section className="star-checklist" aria-label="Star checklist">
    <div className="star-checklist__heading"><h4>Star checklist</h4>
      <span>{active ? 'Available on clear' : 'Earned this run'} <strong>{active ? breakdown.available_stars : breakdown.stars} / 3</strong></span>
    </div>
    <p className="star-checklist__summary">
      {active ? 'Complete the scenario to earn stars for this attempt.' : breakdown.stars ? 'Scenario completed!' : 'The target state was not reached. No stars earned.'}
    </p>
    <ul>{breakdown.criteria.map((criterion) => {
      const Icon = criterion.state === 'earned' ? Check : criterion.state === 'missed' ? Minus : Circle
      const target = criterion.key === 'efficient_target' ? breakdown.command_target : breakdown.generous_target
      return <li key={criterion.key} className={`star-checklist__row is-${criterion.state}`}>
        <Icon className="star-checklist__icon" aria-hidden="true" />
        <div><p className="star-checklist__label">{LABELS[criterion.key]}</p>
          <p className="star-checklist__detail">{criterion.key === 'clear' ? 'Reach the required outcome before the maximum allowance.'
            : `${breakdown.counted_commands} / ${target} counted commands.`}</p></div>
        <span className="star-checklist__state">{criterion.state === 'earned' ? '+1 earned' : criterion.state === 'pending' ? '+1 on clear' : active ? 'Unavailable' : 'Not earned'}</span>
      </li>
    })}</ul>
    <p className="star-checklist__footnote">3 stars: ≤ {breakdown.command_target}; 2 stars: ≤ {breakdown.generous_target}; 1 star: complete within {breakdown.maximum_commands} counted commands.</p>
    <p className="star-checklist__footnote">Typos, failed commands, recovery and repeated actions count. Valid inspections, file edits and opening the command guide are free.</p>
    <p className="star-checklist__footnote">Retries and restarts never reduce stars. Each attempt is scored separately.</p>
    {multiScenario ? <p className="star-checklist__footnote">Your lowest scenario best becomes your saved level score.</p> : null}
    {savedStars !== undefined ? <p className="star-checklist__saved">Saved best{multiScenario ? ' for this level' : ''}: <strong>{savedStars} / 3</strong>. Lower scores never replace it.</p> : null}
  </section>
}


function CompactStarChecklist({ breakdown }: { breakdown: StarBreakdown }) {
  const legacy = (breakdown.scoring_policy_version ?? 1) < 2
  return <section className="star-checklist star-checklist--compact" aria-label="Star checklist">
    {legacy ? <p className="star-checklist__legacy">Earlier scoring rules</p> : null}
    <ul>{breakdown.criteria.map((criterion) => {
      const Icon = criterion.state === 'earned' ? Check : criterion.state === 'missed' ? Minus : Circle
      const target = criterion.key === 'generous_target' ? breakdown.generous_target : breakdown.command_target
      const label = criterion.key === 'clear'
        ? criterion.state === 'earned' ? 'Scenario completed' : 'Scenario not completed'
        : criterion.key === 'retry_allowance'
          ? 'Within target; at most one retry'
          : target !== undefined ? `Within ${target}-command target` : LABELS[criterion.key]
      const grade = criterion.key === 'clear' ? null
        : criterion.key === 'efficient_target' || criterion.key === 'retry_allowance' ? '3 stars' : '2 stars'
      return <li key={criterion.key} className={`star-checklist__row is-${criterion.state}`}>
        <Icon className="star-checklist__icon" aria-hidden="true" />
        <span className="star-checklist__label">{label}</span>
        {grade ? <span className="star-checklist__state">{grade}</span> : null}
        <span className="sr-only">{criterion.state === 'earned' ? 'Met' : criterion.state === 'pending' ? 'Pending' : 'Not met'}</span>
      </li>
    })}</ul>
  </section>
}
