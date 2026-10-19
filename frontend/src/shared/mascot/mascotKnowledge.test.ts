import { describe, expect, it } from 'vitest'
import { mascotSpeechPosition } from './mascotKnowledge'

describe('mascot speech placement', () => {
  it('sits above the character when there is room', () => {
    const position = mascotSpeechPosition(500, 600, 296, 180, 1024, 768)
    expect(position).toEqual({ left: 352, top: 308, below: false, tail: 148 })
  })

  it('stays inside a narrow viewport at either horizontal edge', () => {
    for (const x of [35, 285]) {
      const { left, top, tail } = mascotSpeechPosition(x, 500, 296, 180, 320, 640)
      expect(left).toBeGreaterThanOrEqual(12)
      expect(left + 296).toBeLessThanOrEqual(308)
      expect(top).toBeGreaterThanOrEqual(12)
      expect(tail).toBeGreaterThanOrEqual(20)
      expect(tail).toBeLessThanOrEqual(276)
    }
  })

  it('uses space below a high ledge and clamps to the bottom in short viewports', () => {
    expect(mascotSpeechPosition(200, 110, 296, 180, 400, 640)).toMatchObject({ top: 122, below: true })
    const position = mascotSpeechPosition(200, 110, 296, 180, 400, 220)
    expect(position.top + 180).toBeLessThanOrEqual(208)
  })
})
