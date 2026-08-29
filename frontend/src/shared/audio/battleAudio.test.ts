import { beforeEach, describe, expect, it, vi } from 'vitest'

import { buttonSoundForElement } from './battleAudio'

function button(markup: string): HTMLButtonElement {
  const wrapper = document.createElement('div')
  wrapper.innerHTML = markup.trim()
  const element = wrapper.firstElementChild
  if (!(element instanceof HTMLButtonElement)) throw new Error('Expected a button fixture')
  return element
}

describe('buttonSoundForElement', () => {
  it('uses explicit button sound overrides', () => {
    expect(buttonSoundForElement(button('<button data-button-sound="button-toggle">Flip</button>'))).toBe('button-toggle')
    expect(buttonSoundForElement(button('<button data-button-sound="none">Quiet</button>'))).toBeNull()
  })

  it('keeps disabled buttons silent', () => {
    expect(buttonSoundForElement(button('<button disabled>Save</button>'))).toBeNull()
    expect(buttonSoundForElement(button('<button aria-disabled="true">Save</button>'))).toBeNull()
  })

  it('classifies common product actions into distinct button sounds', () => {
    expect(buttonSoundForElement(button('<button aria-pressed="false">Overview</button>'))).toBe('button-toggle')
    expect(buttonSoundForElement(button('<button class="ui-button ui-button--destructive">Delete run</button>'))).toBe(
      'button-danger',
    )
    expect(buttonSoundForElement(button('<button type="submit">Save changes</button>'))).toBe('button-confirm')
    expect(buttonSoundForElement(button('<button aria-label="Back to Map"><span /></button>'))).toBe('button-dismiss')
    expect(buttonSoundForElement(button('<button>Inspect</button>'))).toBe('button-click')
  })
})

describe('battle audio preferences', () => {
  beforeEach(() => {
    window.localStorage.clear()
    vi.resetModules()
  })

  it('persists sound effects and music independently', async () => {
    const audio = await import('./battleAudio')

    audio.setBattleSoundEnabled(false)
    audio.setBattleMusicEnabled(false)

    expect(window.localStorage.getItem('gitit:battle-sound-effects-enabled')).toBe('off')
    expect(window.localStorage.getItem('gitit:battle-music-enabled')).toBe('off')

    audio.setBattleSoundEnabled(true)

    expect(window.localStorage.getItem('gitit:battle-sound-effects-enabled')).toBe('on')
    expect(window.localStorage.getItem('gitit:battle-music-enabled')).toBe('off')
  })

  it('restores separate audio channel settings from localStorage', async () => {
    window.localStorage.setItem('gitit:battle-sound-effects-enabled', 'off')
    window.localStorage.setItem('gitit:battle-music-enabled', 'on')

    const audio = await import('./battleAudio')

    expect(audio.isBattleSoundEnabled()).toBe(false)
    expect(audio.isBattleMusicEnabled()).toBe(true)
  })

  it('uses the legacy all-audio setting as a first-run fallback', async () => {
    window.localStorage.setItem('gitit:battle-audio-enabled', 'off')

    const audio = await import('./battleAudio')

    expect(audio.isBattleSoundEnabled()).toBe(false)
    expect(audio.isBattleMusicEnabled()).toBe(false)
  })
})

describe('battle movement audio visibility', () => {
  it('stops an active run loop and refuses to restart it while the page is hidden', async () => {
    window.localStorage.clear()
    const originalHidden = Object.getOwnPropertyDescriptor(document, 'hidden')
    const runAudio = {
      currentTime: 0,
      loop: false,
      paused: true,
      play: vi.fn().mockImplementation(function (this: { paused: boolean }) {
        this.paused = false
        return Promise.resolve()
      }),
      pause: vi.fn().mockImplementation(function (this: { paused: boolean }) {
        this.paused = true
      }),
      remove: vi.fn(),
      volume: 1,
    }
    const baseAudio = {
      cloneNode: vi.fn(() => runAudio),
    }
    const fadeOut = vi.fn((audio: typeof runAudio) => {
      audio.pause()
      audio.currentTime = 0
    })

    vi.resetModules()
    vi.doMock('@/shared/audio/battleAudioDom', () => ({
      audioClockNow: () => 0,
      canUseAudio: () => true,
      fadeOut,
      loadAudio: () => baseAudio,
      tryPlay: (audio: typeof runAudio) => {
        void audio.play()
      },
    }))

    try {
      Object.defineProperty(document, 'hidden', { configurable: true, value: false })
      const audio = await import('./battleAudio')
      const unbind = audio.bindBattleAudioVisibility()

      audio.playRunSound(10_000)
      expect(runAudio.play).toHaveBeenCalledTimes(1)

      Object.defineProperty(document, 'hidden', { configurable: true, value: true })
      document.dispatchEvent(new Event('visibilitychange'))

      expect(fadeOut).toHaveBeenCalledWith(runAudio, 0)
      expect(runAudio.pause).toHaveBeenCalledTimes(1)

      audio.playRunSound(10_000)
      expect(runAudio.play).toHaveBeenCalledTimes(1)

      unbind()
    } finally {
      vi.doUnmock('@/shared/audio/battleAudioDom')
      vi.resetModules()
      if (originalHidden) {
        Object.defineProperty(document, 'hidden', originalHidden)
      } else {
        Reflect.deleteProperty(document, 'hidden')
      }
    }
  })
})
