import { describe, expect, it } from 'vitest'

import { displayLessonTitle, normalizeBuilderCommand } from './types'

describe('orientation types', () => {
  it('strips legacy lesson numbering from titles', () => {
    expect(displayLessonTitle('Lesson 0.1 — What Is Git and Why Does It Matter?')).toBe(
      'What Is Git and Why Does It Matter?',
    )
    expect(displayLessonTitle('What Is Git and Why Does It Matter?')).toBe('What Is Git and Why Does It Matter?')
  })

  it('normalizes builder commands for comparison', () => {
    expect(normalizeBuilderCommand('git  commit   -m  "message"')).toBe('git commit -m "message"')
  })
})
