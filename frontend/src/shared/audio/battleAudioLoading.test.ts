import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { loadAudio, tryPlay } = vi.hoisted(() => ({
  loadAudio: vi.fn(() => ({ loop: false, volume: 1, currentTime: 0, paused: true, pause: vi.fn() })),
  tryPlay: vi.fn(),
}))

vi.mock('@/shared/audio/battleAudioDom', () => ({
  audioClockNow: () => 0,
  canUseAudio: () => true,
  fadeOut: vi.fn(),
  loadAudio,
  tryPlay,
}))

describe('audio request admission', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    window.localStorage.setItem('gitit:battle-sound-effects-enabled', 'off')
    window.localStorage.setItem('gitit:battle-music-enabled', 'off')
  })
  afterEach(() => window.localStorage.clear())

  it('creates no media requests for muted home and battle screens', async () => {
    const audio = await import('./battleAudio')
    audio.startBackgroundMusic('outside')
    audio.startBackgroundMusic('inside')
    audio.playSkillSound('flame', 'impact')
    audio.preloadStarRewardSounds(3)
    expect(loadAudio).not.toHaveBeenCalled()
    expect(tryPlay).not.toHaveBeenCalled()
  })

  it('starts only the latest screen loop when music is enabled', async () => {
    const audio = await import('./battleAudio')
    audio.startBackgroundMusic('outside')
    audio.startBackgroundMusic('inside')
    audio.setBattleMusicEnabled(true)
    expect(loadAudio).toHaveBeenCalledExactlyOnceWith('/audio/battle/background/inside-battle-loop.wav')
    expect(tryPlay).toHaveBeenCalledOnce()
    expect(audio.isBattleSoundEnabled()).toBe(false)
    audio.setBattleMusicEnabled(false)
    expect(loadAudio.mock.results[0].value.pause).toHaveBeenCalledOnce()
  })

  it('does not resume a screen that was stopped while muted', async () => {
    const audio = await import('./battleAudio')
    audio.startBackgroundMusic('inside')
    audio.stopBackgroundMusic('inside')
    audio.setBattleMusicEnabled(true)
    expect(loadAudio).not.toHaveBeenCalled()
    expect(tryPlay).not.toHaveBeenCalled()
  })

  it('keeps all effects warm when enabled without downloading muted music', async () => {
    const audio = await import('./battleAudio')
    audio.startBackgroundMusic('inside')
    audio.setBattleSoundEnabled(true)
    expect(loadAudio).toHaveBeenCalledTimes(40)
    expect(loadAudio).toHaveBeenCalledWith('/audio/battle/skills/ice/impact.wav')
    expect(loadAudio).toHaveBeenCalledWith('/audio/battle/rewards/star-3-soft.wav')
    expect(tryPlay).not.toHaveBeenCalled()
  })
})
