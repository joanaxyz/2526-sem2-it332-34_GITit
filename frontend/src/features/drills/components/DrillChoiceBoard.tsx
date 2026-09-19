import { Check, X } from 'lucide-react'

import type { DrillChoice, DrillVerdict } from '@/features/drills/types'

/**
 * The answer set for every pick-one rung.
 *
 * Two layouts, one vocabulary. Whole commands and intent prose get
 * hairline-split rows - the same pattern the level callout uses, so the
 * drill reads as part of the map it hangs off. Single tokens (`-m`, `-A`)
 * get chips, because a two-character answer stretched across a full-width
 * row looks like a mistake.
 *
 * Graded state never rests on colour: the right answer and the wrong pick
 * both carry an icon and, for screen readers, a spoken label.
 */
export function DrillChoiceBoard({
  options,
  layout,
  voice,
  selected,
  correctValue,
  verdict,
  onSelect,
}: {
  options: DrillChoice[]
  layout: 'rows' | 'chips'
  /** Commands render in the mono machine voice; intents are interface prose. */
  voice: 'machine' | 'prose'
  selected: string | null
  correctValue: string
  verdict: DrillVerdict | null
  onSelect: (value: string) => void
}) {
  return (
    <ul className="drill-choices" data-layout={layout} data-voice={voice} role="list">
      {options.map((option, index) => {
        const isSelected = selected === option.value
        const isAnswer = option.value === correctValue
        const state = !verdict
          ? isSelected
            ? 'selected'
            : 'idle'
          : isAnswer
            ? 'answer'
            : isSelected
              ? 'wrong'
              : 'muted'

        return (
          <li key={option.value}>
            <button
              type="button"
              className="drill-choice"
              data-state={state}
              disabled={Boolean(verdict)}
              aria-pressed={isSelected}
              onClick={() => onSelect(option.value)}
            >
              <span className="drill-choice-key" aria-hidden="true">
                {index + 1}
              </span>
              <span className="drill-choice-value">{option.value}</span>
              {state === 'answer' ? (
                <span className="drill-choice-mark" data-tone="right">
                  <Check aria-hidden="true" />
                  <span className="sr-only">Correct answer</span>
                </span>
              ) : null}
              {state === 'wrong' ? (
                <span className="drill-choice-mark" data-tone="wrong">
                  <X aria-hidden="true" />
                  <span className="sr-only">Your answer, incorrect</span>
                </span>
              ) : null}
            </button>
          </li>
        )
      })}
    </ul>
  )
}
