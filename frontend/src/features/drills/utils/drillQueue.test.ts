import { describe, expect, it } from 'vitest'

import type { DrillCard } from '@/features/drills/types'
import {
  MAX_ASKS_PER_CARD,
  accuracy,
  allMastered,
  answerCurrent,
  createQueue,
  currentAsk,
  isFinished,
  ladderFor,
  restoreQueue,
  shakyKeys,
} from '@/features/drills/utils/drillQueue'

function card(key: string, overrides: Partial<DrillCard> = {}): DrillCard {
  return {
    key,
    command: `git ${key}`,
    intent: `Do ${key}`,
    base_command: 'git',
    summary: '',
    tokens: ['git', key],
    command_choices: [
      { value: 'git other', gloss: 'Other' },
      { value: 'git another', gloss: 'Another' },
    ],
    intent_choices: [
      { value: 'Do other', gloss: 'git other' },
      { value: 'Do another', gloss: 'git another' },
    ],
    blank: {
      index: 1,
      answer: key,
      options: [
        { value: 'other', gloss: 'Other' },
        { value: 'another', gloss: 'Another' },
      ],
    },
    bank: ['git', key, 'other'],
    ...overrides,
  }
}

function play(cards: DrillCard[], hasSequence: boolean, answers: boolean[]) {
  let state = createQueue(cards, hasSequence)
  for (const correct of answers) {
    state = answerCurrent(state, correct)
  }
  return state
}

describe('the drill ladder', () => {
  it('climbs recognise then complete then forge when the card supports all three', () => {
    expect(ladderFor(card('add'))).toEqual(['recognise', 'complete', 'forge'])
  })

  it('alternates the opening rung so recall runs both directions', () => {
    expect(ladderFor(card('add'), 1)).toEqual(['read', 'complete', 'forge'])
    expect(ladderFor(card('add'), 2)).toEqual(['recognise', 'complete', 'forge'])
  })

  it('substitutes rather than dropping a rung when a card has no blank', () => {
    const ladder = ladderFor(card('status', { blank: null }))
    expect(ladder).toEqual(['recognise', 'read', 'forge'])
  })

  it('never asks the same rung twice in one ladder', () => {
    const noBlank = ladderFor(card('status', { blank: null }), 1)
    expect(noBlank).toEqual([...new Set(noBlank)])
    expect(noBlank).toEqual(['read', 'forge'])
  })

  it('collapses to assembly for a card with no alternatives at all', () => {
    const bare = card('init', { blank: null, command_choices: [], intent_choices: [] })
    expect(ladderFor(bare)).toEqual(['forge'])
  })
})

describe('retiring a card', () => {
  it('takes one clear per rung, not one clear overall', () => {
    const cards = [card('add')]
    const afterOne = play(cards, false, [true])
    expect(isFinished(afterOne)).toBe(false)
    expect(currentAsk(afterOne)).toEqual({ kind: 'card', cardKey: 'add', rung: 'complete' })

    const afterAll = play(cards, false, [true, true, true])
    expect(isFinished(afterAll)).toBe(true)
  })

  it('cycles the whole set before repeating a card', () => {
    const state = play([card('add'), card('commit')], false, [true])
    // The second card opens on the reading rung - see ladderFor.
    expect(currentAsk(state)).toEqual({ kind: 'card', cardKey: 'commit', rung: 'read' })
  })
})

describe('a miss', () => {
  it('steps the card back a rung and gives up the clear it had banked', () => {
    const state = play([card('add')], false, [true, false])
    expect(currentAsk(state)).toEqual({ kind: 'card', cardKey: 'add', rung: 'recognise' })
    expect(state.cards.add.cleared).toBe(0)
  })

  it('brings the card back within a couple of asks rather than at the end', () => {
    const cards = [card('a'), card('b'), card('c'), card('d')]
    const state = answerCurrent(createQueue(cards, false), false)
    expect(state.queue.indexOf('a')).toBe(2)
  })

  it('marks the card shaky for the session even once it is cleared', () => {
    const state = play([card('add')], false, [false, true, true, true])
    expect(shakyKeys(state)).toEqual(['add'])
  })
})

describe('session safety', () => {
  it('cannot be trapped by a card nobody can answer', () => {
    let state = createQueue([card('add')], false)
    for (let index = 0; index < MAX_ASKS_PER_CARD + 3; index += 1) {
      if (isFinished(state)) break
      state = answerCurrent(state, false)
    }
    expect(isFinished(state)).toBe(true)
    expect(state.cards.add.asks).toBeLessThanOrEqual(MAX_ASKS_PER_CARD)
  })

  it('running out of attempts ends the session but is not a clear', () => {
    let state = createQueue([card('add')], false)
    while (!isFinished(state)) state = answerCurrent(state, false)

    expect(isFinished(state)).toBe(true)
    // Brute-forcing to the end must not earn the level a "Drilled" mark.
    expect(allMastered(state)).toBe(false)
  })

  it('topping every ladder is a clear', () => {
    const state = play([card('add'), card('commit')], false, Array(6).fill(true))
    expect(isFinished(state)).toBe(true)
    expect(allMastered(state)).toBe(true)
  })

  it('never advances past a question that was not answered', () => {
    const empty = createQueue([], false)
    expect(answerCurrent(empty, true)).toBe(empty)
  })
})

describe('the ordering finale', () => {
  it('waits until every card has retired', () => {
    const state = play([card('add')], true, [true, true, true])
    expect(isFinished(state)).toBe(false)
    expect(currentAsk(state)).toEqual({ kind: 'sequence' })
    expect(isFinished(answerCurrent(state, true))).toBe(true)
  })

  it('is skipped entirely when the level has no multi-step solution', () => {
    const state = play([card('add')], false, [true, true, true])
    expect(currentAsk(state)).toBeNull()
  })
})

describe('the end-of-session readout', () => {
  it('reports whole-percent accuracy over every ask, misses included', () => {
    const state = play([card('add')], false, [false, true, true, true])
    expect(state.answered).toBe(4)
    expect(accuracy(state)).toBe(75)
  })

  it('reports zero rather than dividing by nothing before the first answer', () => {
    expect(accuracy(createQueue([card('add')], false))).toBe(0)
  })
})


describe('resuming a saved queue', () => {
  const cards = [card('add'), card('commit')]

  it('comes back on the same rung with the same progress', () => {
    const saved = play(cards, false, [true, true])
    const restored = restoreQueue(cards, false, saved)

    expect(restored).not.toBeNull()
    expect(currentAsk(restored!)).toEqual(currentAsk(saved))
    expect(restored!.answered).toBe(saved.answered)
    expect(restored!.correct).toBe(saved.correct)
    expect(restored!.cards.add.cleared).toBe(saved.cards.add.cleared)
  })

  it('keeps a card that was already retired retired', () => {
    const saved = play([card('add')], false, [true, true, true])
    const restored = restoreQueue([card('add')], false, saved)

    expect(restored!.cards.add.retired).toBe(true)
    expect(restored!.queue).toEqual([])
  })

  it('refuses a save that does not cover the current cards', () => {
    // A reseed added a command the saved run never knew about.
    const saved = play([card('add')], false, [true])
    expect(restoreQueue([card('add'), card('commit')], false, saved)).toBeNull()
  })

  it('refuses junk instead of resuming into a broken queue', () => {
    expect(restoreQueue(cards, false, null)).toBeNull()
    expect(restoreQueue(cards, false, {})).toBeNull()
    expect(restoreQueue(cards, false, { cards: 'nope' })).toBeNull()
  })

  it('clamps a tampered ladder position back into range', () => {
    const saved = play(cards, false, [true])
    const tampered = {
      ...saved,
      cards: { ...saved.cards, add: { ...saved.cards.add, rung: 99, cleared: 99, asks: 999 } },
    }
    const restored = restoreQueue(cards, false, tampered)!

    const ladder = restored.cards.add.ladder.length
    expect(restored.cards.add.rung).toBe(ladder - 1)
    expect(restored.cards.add.cleared).toBe(ladder)
    expect(restored.cards.add.asks).toBeLessThanOrEqual(MAX_ASKS_PER_CARD)
  })

  it('re-queues an unretired card the saved order lost', () => {
    const saved = play(cards, false, [true])
    const restored = restoreQueue(cards, false, { ...saved, queue: [] })!

    expect(restored.queue.sort()).toEqual(['add', 'commit'])
  })

  it('never reports more correct than answered', () => {
    const saved = play(cards, false, [true])
    const restored = restoreQueue(cards, false, { ...saved, answered: 1, correct: 50 })!

    expect(restored.correct).toBeLessThanOrEqual(restored.answered)
  })
})
