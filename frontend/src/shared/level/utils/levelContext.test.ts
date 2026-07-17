import { describe, expect, it } from 'vitest'

import { normalizeLevelContext } from '@/shared/level/utils/levelContext'

describe('normalizeLevelContext', () => {
  it('keeps a copyable value when its field label is intentionally hidden', () => {
    expect(
      normalizeLevelContext({
        story: 'Use the required commit message shown below.',
        details: [{ label: '', value: 'Save staged work' }],
      }).details,
    ).toEqual([{ label: '', value: 'Save staged work' }])
  })
})
