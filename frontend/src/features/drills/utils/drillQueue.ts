import type { DrillCard, DrillRung } from '@/features/drills/types'

/**
 * The drill's repetition engine.
 *
 * A card is not "done" when it is answered right once - recognising a
 * command in a list is not the same skill as writing it. Each card carries
 * a short ladder (recognise -> complete -> forge) and only retires once it
 * has been cleared at every rung it supports, so the same command is met
 * three times, three ways, inside one short session.
 *
 * A miss is not a penalty, it is a re-teach: the card steps back one rung
 * and returns a couple of asks later, which is close enough to feel like
 * the same breath and far enough that the answer is recalled rather than
 * copied. Nothing here ends a session early; there is no fail state,
 * because this is the rung people come to when they are already stuck.
 */

/** Ask gap after a miss: near enough to still be warm, far enough to recall. */
export const MISS_REINSERT_GAP = 2
/** A ceiling so a card nobody can get right cannot trap the session. */
export const MAX_ASKS_PER_CARD = 7

export type DrillCardState = {
  key: string
  ladder: DrillRung[]
  /** Index into `ladder`: the rung this card is asked at next. */
  rung: number
  /** How many distinct rungs have been cleared, lowest first. */
  cleared: number
  asks: number
  missed: boolean
  retired: boolean
}

export type DrillQueueState = {
  cards: Record<string, DrillCardState>
  /** Card keys in ask order; the head is the current question. */
  queue: string[]
  /** Appended once, after every card retires. */
  sequencePending: boolean
  answered: number
  correct: number
}

/**
 * The rungs this particular card can actually be asked at.
 *
 * The opening rung alternates by position: odd-numbered cards are asked
 * intent-to-command (Recognise) and even-numbered ones command-to-intent
 * (Read). Recall has to run both directions - writing a command and
 * understanding one you are handed are different skills, and a learner who
 * only ever drills one way can still be lost reading a teammate's script -
 * and alternating buys that without making the session longer or turning
 * every card into the same three questions.
 *
 * Substitution rather than omission keeps the ladder honest: a card with no
 * distinguishable token to hide borrows the reading question for its middle
 * rung instead of dropping straight to assembly.
 */
export function ladderFor(card: DrillCard, position = 0): DrillRung[] {
  const canRecognise = card.command_choices.length >= 2
  const canRead = card.intent_choices.length >= 2
  const opensReading = position % 2 === 1
  const first: DrillRung = opensReading
    ? canRead
      ? 'read'
      : canRecognise
        ? 'recognise'
        : 'forge'
    : canRecognise
      ? 'recognise'
      : canRead
        ? 'read'
        : 'forge'
  const rungs: DrillRung[] = [
    first,
    card.blank ? 'complete' : canRead && first !== 'read' ? 'read' : 'forge',
    'forge',
  ]
  return rungs.filter((rung, index) => rungs.indexOf(rung) === index)
}

export function createQueue(cards: DrillCard[], hasSequence: boolean): DrillQueueState {
  const state: DrillQueueState = {
    cards: {},
    queue: [],
    sequencePending: hasSequence,
    answered: 0,
    correct: 0,
  }
  cards.forEach((card, position) => {
    state.cards[card.key] = {
      key: card.key,
      ladder: ladderFor(card, position),
      rung: 0,
      cleared: 0,
      asks: 0,
      missed: false,
      retired: false,
    }
    state.queue.push(card.key)
  })
  return state
}

/**
 * Rebuild a saved queue onto today's cards, or refuse it.
 *
 * Drill content is seeded, so it can change under a half-finished run: a
 * reseed can add a command, drop one, or shorten a ladder. Rather than
 * trusting the stored shape, every card is rehydrated onto the ladder the
 * client just loaded and every counter is clamped to it. If the saved
 * state does not cover the current cards at all it is discarded, because
 * resuming into a drill that no longer matches the level is worse than
 * starting again.
 */
export function restoreQueue(
  cards: DrillCard[],
  hasSequence: boolean,
  saved: unknown,
): DrillQueueState | null {
  if (!saved || typeof saved !== 'object') return null
  const state = saved as Partial<DrillQueueState>
  const savedCards = state.cards
  if (!savedCards || typeof savedCards !== 'object') return null

  const fresh = createQueue(cards, hasSequence)
  const keys = Object.keys(fresh.cards)
  if (!keys.length || !keys.every((key) => savedCards[key])) return null

  const restored: Record<string, DrillCardState> = {}
  for (const key of keys) {
    const base = fresh.cards[key]
    const held = savedCards[key]
    const cleared = Math.min(Math.max(Number(held.cleared) || 0, 0), base.ladder.length)
    restored[key] = {
      ...base,
      cleared,
      rung: Math.min(Math.max(Number(held.rung) || 0, 0), base.ladder.length - 1),
      asks: Math.min(Math.max(Number(held.asks) || 0, 0), MAX_ASKS_PER_CARD),
      missed: Boolean(held.missed),
      retired: Boolean(held.retired) || cleared >= base.ladder.length,
    }
  }

  const queue = (Array.isArray(state.queue) ? state.queue : []).filter(
    (key) => restored[key] && !restored[key].retired,
  )
  // Any unretired card the saved order lost still has to be asked.
  for (const key of keys) {
    if (!restored[key].retired && !queue.includes(key)) queue.push(key)
  }

  const answered = Math.max(Number(state.answered) || 0, 0)
  return {
    cards: restored,
    queue,
    sequencePending: hasSequence && state.sequencePending !== false,
    answered,
    correct: Math.min(Math.max(Number(state.correct) || 0, 0), answered),
  }
}

export function currentAsk(
  state: DrillQueueState,
): { kind: 'card'; cardKey: string; rung: DrillRung } | { kind: 'sequence' } | null {
  const key = state.queue[0]
  if (key) {
    const card = state.cards[key]
    return { kind: 'card', cardKey: key, rung: card.ladder[card.rung] }
  }
  return state.sequencePending ? { kind: 'sequence' } : null
}

function reinsert(queue: string[], key: string, gap: number): string[] {
  const rest = queue.slice(1)
  const at = Math.min(gap, rest.length)
  return [...rest.slice(0, at), key, ...rest.slice(at)]
}

/** Advance past the current question. Pure: returns the next state. */
export function answerCurrent(state: DrillQueueState, correct: boolean): DrillQueueState {
  const key = state.queue[0]
  if (!key) {
    return state.sequencePending
      ? {
          ...state,
          sequencePending: false,
          answered: state.answered + 1,
          correct: state.correct + (correct ? 1 : 0),
        }
      : state
  }

  const card = state.cards[key]
  const asks = card.asks + 1
  const exhausted = asks >= MAX_ASKS_PER_CARD
  const next: DrillCardState = correct
    ? {
        ...card,
        asks,
        cleared: card.cleared + 1,
        rung: Math.min(card.rung + 1, card.ladder.length - 1),
        retired: card.cleared + 1 >= card.ladder.length || exhausted,
      }
    : {
        ...card,
        asks,
        missed: true,
        // Step back a rung, and give up the clear that rung had banked: the
        // card has to earn its way up again, which is the repetition.
        cleared: Math.max(card.cleared - 1, 0),
        rung: Math.max(card.rung - 1, 0),
        retired: exhausted,
      }

  return {
    ...state,
    cards: { ...state.cards, [key]: next },
    queue: next.retired
      ? state.queue.slice(1)
      : reinsert(state.queue, key, correct ? state.queue.length : MISS_REINSERT_GAP),
    answered: state.answered + 1,
    correct: state.correct + (correct ? 1 : 0),
  }
}

export function isFinished(state: DrillQueueState): boolean {
  return state.queue.length === 0 && !state.sequencePending
}

/** Whole percent of asks answered right, for the end-of-session readout. */
export function accuracy(state: DrillQueueState): number {
  if (state.answered === 0) return 0
  return Math.round((state.correct / state.answered) * 100)
}

/**
 * True only when every card topped its ladder.
 *
 * The queue also empties when cards exhaust their attempts, which is not
 * the same achievement - reporting that as a clear would put a "Drilled"
 * mark on a level the learner brute-forced.
 */
export function allMastered(state: DrillQueueState): boolean {
  return Object.values(state.cards).every((card) => card.cleared >= card.ladder.length)
}

/** Cards missed at least once - the only thing worth telling them to revisit. */
export function shakyKeys(state: DrillQueueState): string[] {
  return Object.values(state.cards)
    .filter((card) => card.missed)
    .map((card) => card.key)
}
