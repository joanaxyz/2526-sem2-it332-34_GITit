const LEGACY_AUDIO_ENABLED_STORAGE_KEY = 'gitit:battle-audio-enabled'
export const SOUND_EFFECTS_ENABLED_STORAGE_KEY = 'gitit:battle-sound-effects-enabled'
export const MUSIC_ENABLED_STORAGE_KEY = 'gitit:battle-music-enabled'

export function readAudioChannelPreference(storageKey: string): boolean {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return true
    const saved = window.localStorage.getItem(storageKey)
    if (saved) return saved !== 'off'
    return window.localStorage.getItem(LEGACY_AUDIO_ENABLED_STORAGE_KEY) !== 'off'
  } catch {
    return true
  }
}

export function persistAudioChannelPreference(storageKey: string, enabled: boolean): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return
    window.localStorage.setItem(storageKey, enabled ? 'on' : 'off')
  } catch {
    // Storage can be unavailable in private or embedded contexts; audio still works.
  }
}
