import { describe, expect, it } from 'vitest'

import type { CommandIntroduction, GuideElsewhere } from '@/features/story-map/api/commandIntroductionsApi'
import { readableGuides } from './commandGuides'

const guide = (teachingKey: string) => ({ teaching_key: teachingKey }) as CommandIntroduction

describe('readable command guides', () => {
  it("lists the scenario's finished guides, the guide taught elsewhere, then the open one", () => {
    const run = {
      command_guides: [guide('git-init/current-directory')],
      guide_elsewhere: { guide: guide('form:git rebase <upstream>') } as GuideElsewhere,
      tutor: guide('form:git add <path>...'),
    }

    expect(readableGuides(run).map((item) => item.teaching_key)).toEqual([
      'git-init/current-directory',
      'form:git rebase <upstream>',
      'form:git add <path>...',
    ])
  })

  it('lists a guide once even when it is also the open one', () => {
    const finished = guide('git-init/current-directory')
    const run = { command_guides: [finished], guide_elsewhere: null, tutor: { ...finished } }
    expect(readableGuides(run)).toEqual([finished])
  })

  it('has nothing to read when the run teaches nothing', () => {
    expect(readableGuides({ command_guides: [], guide_elsewhere: null, tutor: null })).toEqual([])
  })
})
