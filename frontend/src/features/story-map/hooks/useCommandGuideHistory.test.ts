import { describe, expect, it } from 'vitest'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { loadCommandGuideHistory, rememberCommandGuide } from './useCommandGuideHistory'

const guide = (teachingKey: string, title: string) => ({
  teaching_key: teachingKey,
  title,
  completion_token: 'single-use-token',
  command_form: { usage_form: teachingKey.replace('form:', '') },
}) as CommandIntroduction

describe('command guide history', () => {
  it('keeps guides in encounter order and removes completion tokens', () => {
    const first = guide('form:git init', 'Initialize')
    const second = guide('form:git add <path>', 'Stage a file')
    const history = rememberCommandGuide(rememberCommandGuide([], first), second)

    expect(history.map((item) => item.teaching_key)).toEqual([
      'form:git init',
      'form:git add <path>',
    ])
    expect(history.every((item) => item.completion_token === null)).toBe(true)
  })

  it('does not duplicate a command guide seen again later in the run', () => {
    const first = guide('form:git init', 'Initialize')
    expect(rememberCommandGuide([first], { ...first, title: 'Updated' })).toEqual([first])
  })

  it('ignores malformed session history', () => {
    sessionStorage.setItem('git-it-command-guides:81', JSON.stringify([{ title: 'Missing key' }]))
    expect(loadCommandGuideHistory(81)).toEqual([])
  })
})
