import type { DrillCard, DrillChoice, DrillRung } from '@/features/drills/types'

/**
 * The option pool for a pick-one rung, answer included, unshuffled.
 *
 * Shared so the question and the verdict bar cannot disagree about how
 * many numbered rows exist: the bar advertises the `1`-`n` shortcut and
 * the board renders the badges, and an off-by-one between them would
 * teach the wrong shortcut.
 */
export function choicePoolFor(card: DrillCard | null, rung: DrillRung | null): DrillChoice[] {
  if (!card || !rung) return []
  if (rung === 'recognise') {
    return [{ value: card.command, gloss: card.intent }, ...card.command_choices]
  }
  if (rung === 'read') {
    return [{ value: card.intent, gloss: card.command }, ...card.intent_choices]
  }
  if (rung === 'complete' && card.blank) {
    return [{ value: card.blank.answer, gloss: card.intent }, ...card.blank.options]
  }
  return []
}
