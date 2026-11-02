import { Check, X } from 'lucide-react'
import type { DrillVerdict } from '@/features/drills/types'

/** Brief hit feedback; detailed corrections belong in the end-of-run review. */
export function DrillVerdictBar({ verdict, canCheck, optionCount, onCheck,
  flightChoices = false, outOfLives = false, checkpoint = false, fell = false,
}: {
  verdict: DrillVerdict | null
  canCheck: boolean
  optionCount: number
  onCheck: () => void
  flightChoices?: boolean
  outOfLives?: boolean
  checkpoint?: boolean
  fell?: boolean
}) {
  const tone = !verdict ? 'idle' : verdict.correct ? 'right' : 'wrong'
  if (!verdict && (flightChoices || checkpoint)) return null
  return <div className="drill-verdict" data-tone={tone}>
    <div className="drill-verdict-bar">
      <p className="drill-verdict-state" role="status">
        {verdict ? <>
          <span className="drill-verdict-badge" aria-hidden="true">{verdict.correct ? <Check /> : <X />}</span>
          <span>{verdict.correct ? 'Correct' : fell ? 'Game over' : outOfLives ? 'Out of lives' : verdict.reason === 'passed' ? 'Missed' : 'Life lost'}</span>
        </> : <span className="drill-verdict-hint">
          {optionCount > 1 ? <><kbd>1</kbd>–<kbd>{optionCount}</kbd> to pick<span aria-hidden="true"> · </span></> : null}
          {flightChoices ? 'Fly into an answer' : checkpoint ? 'Build the path before Blue reaches a gap' : <><kbd>Enter</kbd> to check</>}
        </span>}
      </p>
      {!verdict ? <button type="button" className="ui-button ui-button--default" disabled={!canCheck} onClick={onCheck}>Check</button> : null}
    </div>
  </div>
}
