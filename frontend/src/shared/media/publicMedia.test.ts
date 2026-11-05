import { statSync } from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'
import optimizedMedia from './optimizedPublicMedia.json'
import { publicMediaUrl } from './publicMedia'

describe('optimized delivery media', () => {
  it('keeps an existing URL when no smaller delivery copy is registered', () => {
    expect(publicMediaUrl('/favicon.png')).toBe('/favicon.png')
    expect(publicMediaUrl('/unknown-image.png')).toBe('/unknown-image.png')
  })

  it('ships a smaller file for every registered replacement', () => {
    for (const [source, target] of Object.entries(optimizedMedia)) {
      const original = statSync(path.join(process.cwd(), 'public', source))
      const optimized = statSync(path.join(process.cwd(), 'public', target))
      expect(optimized.size, target).toBeLessThan(original.size)
      expect(publicMediaUrl(source)).toBe(target)
    }
  })
})
