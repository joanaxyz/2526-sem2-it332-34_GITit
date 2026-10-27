import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { playStarRewardSound, preloadStarRewardSounds, setBattleMusicEnabled, setBattleSoundEnabled } from './battleAudio'

const { audio, loadAudio, tryPlay } = vi.hoisted(() => {
  const audio = { volume: 1, currentTime: 0, loop: false, addEventListener: vi.fn(), pause: vi.fn(), remove: vi.fn() }
  return { audio, loadAudio: vi.fn((src: string) => ({ src, cloneNode: () => audio })), tryPlay: vi.fn() }
})

vi.mock('@/shared/audio/battleAudioDom', () => ({
  audioClockNow: () => 0,
  canUseAudio: () => true,
  fadeOut: vi.fn(),
  loadAudio,
  tryPlay,
}))

beforeEach(() => {
  setBattleSoundEnabled(true)
  setBattleMusicEnabled(false)
  vi.clearAllMocks()
})
afterEach(() => setBattleSoundEnabled(false))

describe('generated star reward sounds', () => {
  it.each([0, 1, 2, 3])('plays the %s-star file independently of the music setting', (grade) => {
    const stop = playStarRewardSound(grade)
    expect(loadAudio).toHaveBeenCalledWith(`/audio/battle/rewards/star-${grade}-soft.wav`)
    expect(tryPlay).toHaveBeenCalledWith(audio, expect.any(Function))
    expect(audio.loop).toBe(false)
    stop()
    expect(audio.pause).toHaveBeenCalledOnce()
  })

  it('warms only the cues needed for a two-star result', () => {
    preloadStarRewardSounds(2)
    expect(loadAudio.mock.calls.map(([src]) => src)).toEqual([
      '/audio/battle/rewards/star-1-soft.wav', '/audio/battle/rewards/star-2-soft.wav',
    ])
  })

  it('honors mute immediately, including a cue already playing', () => {
    playStarRewardSound(1)
    setBattleSoundEnabled(false)
    expect(audio.pause).toHaveBeenCalledOnce()
    expect(audio.currentTime).toBe(0)
    vi.clearAllMocks()
    playStarRewardSound(2)
    expect(loadAudio).not.toHaveBeenCalled()
    expect(tryPlay).not.toHaveBeenCalled()
  })

  it.each([-1, 4, NaN, 1.5])('ignores invalid star grades (%s)', (grade) => {
    playStarRewardSound(grade)
    expect(loadAudio).not.toHaveBeenCalled()
  })
})
