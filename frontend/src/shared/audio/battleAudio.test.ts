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
