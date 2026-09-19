import type { DrillAnswer, DrillCard, DrillRung, DrillVerdict } from '@/features/drills/types'

/**
 * Grading runs in the browser so feedback lands inside the ~80ms window
 * where it still reads as a reaction rather than a response. The backend
 * owns nothing here on purpose: the drill pays no currency and unlocks
 * nothing, so there is no reward to forge.
 */

/**
 * Two commands match when they say the same thing to Git.
 *
 * Spacing is collapsed because assembled tokens and typed text should not
 * disagree over a double space, and a message argument is compared loosely
 * because the catalog writes `<message>` where a learner reasonably types
 * `"message"` - insisting on the placeholder spelling would test typing,
 * not Git.
 */
export function normalizeCommand(value: string): string {
  return value
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/["'`]/g, '')
    .replace(/<([^>]+)>/g, '$1')
    .toLowerCase()
}

export function commandsMatch(a: string, b: string): boolean {
  return normalizeCommand(a) === normalizeCommand(b)
}

function expectedFor(card: DrillCard, rung: DrillRung): string {
  if (rung === 'read') return card.intent
  if (rung === 'complete') return card.blank?.answer ?? ''
  return card.command
}

function glossFor(card: DrillCard, rung: DrillRung, picked: string): string | null {
  const pool =
    rung === 'read'
      ? card.intent_choices
      : rung === 'complete'
        ? (card.blank?.options ?? [])
        : card.command_choices
  return pool.find((choice) => choice.value === picked)?.gloss ?? null
}

export function gradeCard(
  card: DrillCard,
  rung: DrillRung,
  answer: DrillAnswer | null,
): DrillVerdict {
  if (!answer) return { correct: false, picked: null, pickedGloss: null }
  if (answer.kind === 'choice') {
    const expected = expectedFor(card, rung)
    // Intent text is authored prose, so it is compared verbatim; command
    // text goes through the Git-equivalence rules above.
    const correct =
      rung === 'read' ? answer.value === expected : commandsMatch(answer.value, expected)
    return {
      correct,
      picked: answer.value,
      pickedGloss: correct ? null : glossFor(card, rung, answer.value),
    }
  }
  const assembled = answer.values.join(' ')
  return {
    correct: commandsMatch(assembled, card.command),
    picked: assembled || null,
    pickedGloss: null,
  }
}

export function gradeSequence(steps: string[], answer: DrillAnswer | null): DrillVerdict {
  const placed = answer?.kind === 'tokens' ? answer.values : []
  const correct =
    placed.length === steps.length && placed.every((step, index) => step === steps[index])
  return { correct, picked: placed.join(' → ') || null, pickedGloss: null }
}
