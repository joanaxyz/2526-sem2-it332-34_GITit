import { describe, expect, it } from 'vitest'
import { getScaffoldMessage } from './messages'

const TRIGGERS = ['T1', 'T2', 'T3'] as const
const DIFFICULTIES = ['easy', 'medium', 'hard'] as const

const FORBIDDEN_PATTERNS: Array<{ label: string; test: (s: string) => boolean }> = [
  {
    label: 'markdown hyperlink [...]()',
    test: (s) => /\[.*?\]\(.*?\)/.test(s),
  },
  {
    label: 'anchor tag <a',
    test: (s) => /<a[\s>]/i.test(s),
  },
  {
    label: 'word "remaining"',
    test: (s) => /\bremaining\b/i.test(s),
  },
  {
    label: 'phrase "try git"',
    test: (s) => /try git/i.test(s),
  },
  {
    label: 'phrase "you should"',
    test: (s) => /you should/i.test(s),
  },
  {
    label: 'word "navigate"',
    test: (s) => /\bnavigate\b/i.test(s),
  },
  {
    label: 'word "click"',
    test: (s) => /\bclick\b/i.test(s),
  },
  {
    label: 'phrase "go to"',
    test: (s) => /go to/i.test(s),
  },
]

describe('getScaffoldMessage — No-Answer Policy compliance', () => {
  for (const trigger of TRIGGERS) {
    for (const difficulty of DIFFICULTIES) {
      const msg = getScaffoldMessage(trigger, difficulty)

      it(`${trigger}/${difficulty} returns a non-empty string`, () => {
        expect(typeof msg).toBe('string')
        expect(msg.length).toBeGreaterThan(0)
      })

      for (const pattern of FORBIDDEN_PATTERNS) {
        it(`${trigger}/${difficulty} does not contain ${pattern.label}`, () => {
          expect(pattern.test(msg)).toBe(false)
        })
      }
    }
  }
})

describe('getScaffoldMessage — message identity', () => {
  it('T1 easy matches the specified string exactly', () => {
    expect(getScaffoldMessage('T1', 'easy')).toBe(
      "💡 You've used a portion of your available commands without reaching the target state. Before your next command, compare the live DAG against the Expected-State Diagram — check where your current branch pointer is relative to where it needs to be. Diagnostic commands are free to use.",
    )
  })

  it('T3 hard matches the specified string exactly', () => {
    expect(getScaffoldMessage('T3', 'hard')).toBe(
      '🔴 Your repository state remains unresolved despite substantial command usage. Use git log or git reflog to assess your current state carefully before your next action command.',
    )
  })

  it('T2 medium matches the specified string exactly', () => {
    expect(getScaffoldMessage('T2', 'medium')).toBe(
      "⚠️ Your current command path significantly exceeds the expected transition. Inspect the live DAG carefully and use diagnostic commands to reassess your repository state before continuing.\n\nThe concepts covered in this module's Lesson Overview apply to this scenario.",
    )
  })
})
