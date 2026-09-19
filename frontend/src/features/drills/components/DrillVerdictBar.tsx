import { ArrowRight, Check, X } from 'lucide-react'

import type { DrillCard, DrillRung, DrillSequence, DrillVerdict } from '@/features/drills/types'

/**
 * The single forward control, and where both outcomes are taught.
 *
 * A wrong answer is answered with authored truth rather than a red cross:
 * every distractor is a real command form, so the panel can say what the
 * learner actually reached for and what it really does, next to what they
 * wanted. That comparison is the whole reason the drill exists - it is the
 * confusion that stalls people in the terminal.
 *
 * A right answer is confirmed, not just scored. "Correct" on its own
 * teaches nothing; restating the pairing the learner just proved is the
 * other half of a recall loop, and it costs them one line instead of the
 * miss panel's three - a nod against an explanation, so the rhythm of a
 * clean run stays quick.
 *
 * Nothing here scolds and nothing ends: a missed card simply returns.
 */
export function DrillVerdictBar({
  verdict,
  canCheck,
  card,
  rung,
  sequence,
  optionCount,
  onCheck,
  onAdvance,
}: {
  verdict: DrillVerdict | null
  canCheck: boolean
  card: DrillCard | null
  rung: DrillRung | null
  sequence: DrillSequence | null
  /** How many numbered choices the current question offers, if any. */
  optionCount: number
  onCheck: () => void
  onAdvance: () => void
}) {
  const tone = !verdict ? 'idle' : verdict.correct ? 'right' : 'wrong'
  const answerText = !card
    ? (sequence?.steps.join('  →  ') ?? '')
    : rung === 'read'
      ? card.intent
      : rung === 'complete'
        ? (card.blank?.answer ?? '')
        : card.command
  const answerGloss = !card ? (sequence?.label ?? '') : rung === 'read' ? card.command : card.intent
  // Only the pick-one rungs have numbered rows to shortcut to.
  const picksByNumber = optionCount && optionCount > 1 ? optionCount : null

  return (
    <div className="drill-verdict" data-tone={tone}>
      {/* Always mounted: the bar opens by animating its first grid row, and
          a row that does not exist cannot transition. */}
      <div className="drill-teach-slot">
        {verdict?.correct ? (
          <p className="drill-confirm" role="status">
            <code>{answerText}</code>
            {answerGloss ? <em>{answerGloss}</em> : null}
          </p>
        ) : null}
        {verdict && !verdict.correct ? (
          <div className="drill-teach" role="status">
            {verdict.picked ? (
              <p className="drill-teach-row" data-role="picked">
                <span className="drill-teach-label">You picked</span>
                <code>{verdict.picked}</code>
                {verdict.pickedGloss ? <em>{verdict.pickedGloss}</em> : null}
              </p>
            ) : null}
            <p className="drill-teach-row" data-role="answer">
              <span className="drill-teach-label">The answer</span>
              <code>{answerText}</code>
              {answerGloss ? <em>{answerGloss}</em> : null}
            </p>
            <p className="drill-teach-note">This one comes back before the drill ends.</p>
          </div>
        ) : null}
      </div>

      <div className="drill-verdict-bar">
        <p className="drill-verdict-state" role="status">
          {tone === 'right' ? (
            <>
              <Check aria-hidden="true" />
              <span>Correct</span>
            </>
          ) : null}
          {tone === 'wrong' ? (
            <>
              <X aria-hidden="true" />
              <span>Not this one</span>
            </>
          ) : null}
          {tone === 'idle' ? (
            <span className="drill-verdict-hint">
              {/* The numbered badges on each row imply the shortcut; naming
                  it is what makes a keyboard-first loop discoverable. */}
              {picksByNumber ? (
                <>
                  <kbd>1</kbd>&ndash;<kbd>{picksByNumber}</kbd> to pick
                  <span aria-hidden="true"> · </span>
                </>
              ) : null}
              <kbd>Enter</kbd> to check
            </span>
          ) : null}
        </p>

        {verdict ? (
          <button type="button" className="ui-button ui-button--default" onClick={onAdvance}>
            Continue
            <ArrowRight aria-hidden="true" />
          </button>
        ) : (
          <button
            type="button"
            className="ui-button ui-button--default"
            disabled={!canCheck}
            onClick={onCheck}
          >
            Check
          </button>
        )}
      </div>
    </div>
  )
}
