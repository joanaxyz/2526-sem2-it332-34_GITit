import { describe, expect, it } from 'vitest'

import type { DrillCard } from '@/features/drills/types'
import { commandsMatch, gradeCard, gradeSequence } from '@/features/drills/utils/drillGrading'

const commitCard: DrillCard = {
  key: 'git-commit/message',
  command: 'git commit -m <message>',
  intent: 'Commit with a message',
  base_command: 'git commit',
  summary: 'Create or replace a commit from the staged snapshot.',
  tokens: ['git', 'commit', '-m', '<message>'],
  command_choices: [{ value: 'git commit --amend', gloss: 'Rewrite the last commit' }],
  intent_choices: [{ value: 'Rewrite the last commit', gloss: 'git commit --amend' }],
  blank: {
    index: 2,
    answer: '-m',
    options: [{ value: '--amend', gloss: 'Rewrite the last commit' }],
  },
  bank: ['git', 'commit', '-m', '<message>', '--amend'],
}

describe('command equivalence', () => {
  it('ignores spacing that Git does not care about', () => {
    expect(commandsMatch('git   commit  -m <message>', 'git commit -m <message>')).toBe(true)
  })

  it('accepts a quoted message where the catalog writes a placeholder', () => {
    expect(commandsMatch('git commit -m "message"', 'git commit -m <message>')).toBe(true)
  })

  it('still rejects a different flag', () => {
    expect(commandsMatch('git commit -a', 'git commit -m <message>')).toBe(false)
  })
})

describe('grading a pick', () => {
  it('explains a wrong pick with the authored line for what they chose', () => {
    const verdict = gradeCard(commitCard, 'recognise', {
      kind: 'choice',
      value: 'git commit --amend',
    })
    expect(verdict.correct).toBe(false)
    expect(verdict.pickedGloss).toBe('Rewrite the last commit')
  })

  it('compares intent prose verbatim, not loosely', () => {
    expect(
      gradeCard(commitCard, 'read', { kind: 'choice', value: 'Commit with a message' }).correct,
    ).toBe(true)
    expect(
      gradeCard(commitCard, 'read', { kind: 'choice', value: 'commit with a message' }).correct,
    ).toBe(false)
  })

  it('grades the blank against the hidden token', () => {
    expect(gradeCard(commitCard, 'complete', { kind: 'choice', value: '-m' }).correct).toBe(true)
    expect(gradeCard(commitCard, 'complete', { kind: 'choice', value: '--amend' }).correct).toBe(
      false,
    )
  })

  it('treats no answer as wrong without throwing', () => {
    expect(gradeCard(commitCard, 'forge', null)).toEqual({
      correct: false,
      picked: null,
      pickedGloss: null,
    })
  })
})

describe('grading an assembly', () => {
  it('accepts the tokens in order', () => {
    const verdict = gradeCard(commitCard, 'forge', {
      kind: 'tokens',
      values: ['git', 'commit', '-m', '<message>'],
    })
    expect(verdict.correct).toBe(true)
  })

  it('rejects the right tokens in the wrong order', () => {
    const verdict = gradeCard(commitCard, 'forge', {
      kind: 'tokens',
      values: ['git', '-m', 'commit', '<message>'],
    })
    expect(verdict.correct).toBe(false)
  })
})

describe('grading the ordering finale', () => {
  const steps = ['git init', 'git add .', "git commit -m 'Initial commit'"]

  it('needs every step in the authored order', () => {
    expect(gradeSequence(steps, { kind: 'tokens', values: steps }).correct).toBe(true)
  })

  it('rejects a partial run', () => {
    expect(gradeSequence(steps, { kind: 'tokens', values: steps.slice(0, 2) }).correct).toBe(false)
  })

  it('rejects a swapped pair', () => {
    const swapped = [steps[0], steps[2], steps[1]]
    expect(gradeSequence(steps, { kind: 'tokens', values: swapped }).correct).toBe(false)
  })
})
