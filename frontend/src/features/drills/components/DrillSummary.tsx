import { Link } from 'react-router-dom'
import { RotateCcw } from 'lucide-react'

import { DrillProgressTrack } from '@/features/drills/components/DrillProgressTrack'
import type { DrillCard, DrillPlan } from '@/features/drills/types'
import type { DrillRailSegment } from '@/features/drills/hooks/useDrillSession'
import { drillExitPath } from '@/features/drills/utils/drillRoutes'

/**
 * The payoff.
 *
 * It pays no currency on purpose - a four-minute drill that minted coins
 * would cheapen the chapter chests that are meant to feel earned. What it
 * pays instead is information: the forms that took more than one look,
 * named, so the learner walks into the level knowing where they are thin.
 *
 * The finished track is the reward image rather than a row of figures. It
 * is the thing they watched fill for the whole session, so hiding it at
 * the moment it completes throws away the payoff - and it already carries
 * per-command truth (amber where a command needed a second look) that a
 * "commands drilled" tally cannot. One number survives, the one that says
 * something about them rather than about the session's length.
 */
export function DrillSummary({
  plan,
  rail,
  accuracy,
  answered,
  shaky,
  saveFailed,
  onRestart,
}: {
  plan: DrillPlan
  rail: DrillRailSegment[]
  accuracy: number
  answered: number
  shaky: string[]
  saveFailed: boolean
  onRestart: () => void
}) {
  const byKey = new Map<string, DrillCard>(plan.cards.map((card) => [card.key, card]))
  const shakyCards = shaky.map((key) => byKey.get(key)).filter((card): card is DrillCard => !!card)
  // A card can leave the queue without ever topping its ladder, so
  // "cleared" is not the same as "got through it". Saying every command
  // was cleared when some were given up on is the one thing this screen
  // must not do - the learner would walk into the level trusting a
  // reassurance the session never earned.
  const unfinished = rail.filter(
    (segment) => segment.kind === 'command' && !segment.mastered,
  ).length
  const tone = unfinished > 0 ? 'unfinished' : shakyCards.length ? 'wobbled' : 'clean'
  const lede = {
    clean: 'Every command first time. These are ready to use in the level.',
    wobbled: 'Every command cleared. A few needed a second look — they are listed below.',
    unfinished:
      'Session over. Some commands never quite landed — they are listed below, and the level will lean on them.',
  }[tone]

  return (
    <section className="drill-summary" aria-labelledby="drill-summary-title">
      <p className="drill-summary-eyebrow" data-tone={tone}>
        {tone === 'unfinished' ? 'Drill over' : 'Drill cleared'}
      </p>
      <h2 id="drill-summary-title">{plan.level.title}</h2>
      <p className="drill-summary-lede">{lede}</p>

      <div className="drill-summary-tally">
        <DrillProgressTrack segments={rail} mode="record" />
        <dl className="drill-summary-figures">
          <div>
            <dt>First-pass accuracy</dt>
            <dd>{accuracy}%</dd>
          </div>
          <div>
            <dt>Answers given</dt>
            <dd>{answered}</dd>
          </div>
        </dl>
      </div>

      {shakyCards.length ? (
        <section className="drill-summary-shaky" aria-labelledby="drill-shaky-title">
          <h3 id="drill-shaky-title">Worth another look</h3>
          <ul>
            {shakyCards.map((card) => (
              <li key={card.key}>
                <code>{card.command}</code>
                <span>{card.intent}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {saveFailed ? (
        <p className="drill-summary-warning" role="status">
          Your drill is finished, but the result could not be saved. The level map may still show
          it as undrilled.
        </p>
      ) : null}

      <div className="drill-summary-actions">
        <Link className="ui-button ui-button--default" to={drillExitPath(plan)}>
          Back to the level map
        </Link>
        <button type="button" className="ui-button ui-button--ghost" onClick={onRestart}>
          <RotateCcw aria-hidden="true" />
          Drill again
        </button>
      </div>
    </section>
  )
}
