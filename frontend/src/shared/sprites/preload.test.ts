import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { isImageWarm, warmImage, warmImages, warmSprite, withBudget } from './preload'
import type { SpriteAnimation } from './types'

/**
 * jsdom never loads images: it leaves `decode` undefined and fires neither
 * `load` nor `error`. This stand-in restores the one behavior the preloader
 * depends on - a src that settles - and counts how often each one is fetched.
 */
class FakeImage {
  static requests: string[] = []
  decoding = 'auto'
  onload: (() => void) | null = null
  onerror: (() => void) | null = null
  #src = ''

  get src(): string {
    return this.#src
  }

  set src(next: string) {
    this.#src = next
    FakeImage.requests.push(next)
    setTimeout(() => {
      if (next.includes('missing')) this.onerror?.()
      else this.onload?.()
    }, 0)
  }
}

const originalImage = globalThis.Image

function sheet(src: string): SpriteAnimation {
  return { name: 'test', src, frameWidth: 4, frameHeight: 4, columns: 2, rows: 2, frameCount: 4, fps: 8, loop: true }
}

beforeEach(() => {
  FakeImage.requests = []
  Object.defineProperty(globalThis, 'Image', { configurable: true, value: FakeImage })
})

afterEach(() => {
  Object.defineProperty(globalThis, 'Image', { configurable: true, value: originalImage })
})

describe('warmImage', () => {
  it('fetches one src once, however many surfaces ask for it', async () => {
    await Promise.all([warmImage('/a-once.png'), warmImage('/a-once.png')])
    await warmImage('/a-once.png')

    expect(FakeImage.requests).toEqual(['/a-once.png'])
    expect(isImageWarm('/a-once.png')).toBe(true)
  })

  it('reports a src cold until it has actually been decoded', async () => {
    expect(isImageWarm('/b-cold.png')).toBe(false)

    await warmImage('/b-cold.png')

    expect(isImageWarm('/b-cold.png')).toBe(true)
  })

  it('counts a failed image as warm so a gate never waits for it twice', async () => {
    await expect(warmImage('/c-missing.png')).resolves.toBeUndefined()

    expect(isImageWarm('/c-missing.png')).toBe(true)
  })

  it('ignores an empty src', async () => {
    await warmImage('')

    expect(FakeImage.requests).toEqual([])
  })
})

describe('warmSprite', () => {
  it('decodes the sheet behind the animation', async () => {
    await warmSprite(sheet('/d-sheet.png'))

    expect(isImageWarm('/d-sheet.png')).toBe(true)
  })
})

describe('warmImages', () => {
  it('resolves once every source has settled', async () => {
    await warmImages(['/e-one.png', '/e-two.png'])

    expect(isImageWarm('/e-one.png')).toBe(true)
    expect(isImageWarm('/e-two.png')).toBe(true)
  })
})

describe('withBudget', () => {
  it('gives up on work that never settles', async () => {
    await expect(withBudget(new Promise<void>(() => {}), 10)).resolves.toBeUndefined()
  })

  it('waits indefinitely when no budget is set', async () => {
    let done = false
    await withBudget(Promise.resolve().then(() => { done = true }))

    expect(done).toBe(true)
  })
})
