import { buttonSoundForEventTarget } from '@/shared/audio/battleButtonSounds'
import { audioClockNow, canUseAudio, fadeOut, loadAudio, tryPlay } from '@/shared/audio/battleAudioDom'
import {
  BACKGROUND_VOLUMES,
  BUTTON_CLICK_VARIANTS,
  BUTTON_SOUND_VOLUMES,
  BUTTON_SOUNDS,
  COMPANION_ELEMENTS,
  COMPANION_SOUND_SLUGS,
  COMPANION_SOUNDS,
  SKILL_ELEMENTS,
  SKILL_PHASES,
  SKILL_VOLUMES,
  SYSTEM_SOUNDS,
  backgroundSrc,
  buttonSrc,
  companionSoundSlug,
  companionSrc,
  monsterHurtSrc,
  skillSrc,
  systemSrc,
} from '@/shared/audio/battleAudioCatalog'
import type {
  BattleBackgroundKind,
  BattleSkillElement,
  BattleSkillSoundPhase,
  ButtonSound,
} from '@/shared/audio/battleAudioCatalog'

export { buttonSoundForElement } from '@/shared/audio/battleButtonSounds'
export type {
  BattleBackgroundKind,
  BattleSkillElement,
  BattleSkillSoundPhase,
} from '@/shared/audio/battleAudioCatalog'

const LEGACY_AUDIO_ENABLED_STORAGE_KEY = 'gitit:battle-audio-enabled'
const SOUND_EFFECTS_ENABLED_STORAGE_KEY = 'gitit:battle-sound-effects-enabled'
const MUSIC_ENABLED_STORAGE_KEY = 'gitit:battle-music-enabled'

type AudioPreferenceListener = (enabled: boolean) => void

const activeOneShots = new Set<HTMLAudioElement>()
const soundEffectsEnabledListeners = new Set<AudioPreferenceListener>()
const musicEnabledListeners = new Set<AudioPreferenceListener>()
let battleSoundEffectsEnabled = readAudioChannelPreference(SOUND_EFFECTS_ENABLED_STORAGE_KEY)
let battleMusicEnabled = readAudioChannelPreference(MUSIC_ENABLED_STORAGE_KEY)
let activeBackground: { kind: BattleBackgroundKind; audio: HTMLAudioElement } | null = null
let clearPendingBackgroundUnlock: (() => void) | null = null
let activeRunSound: HTMLAudioElement | null = null
let clearPendingRunStop: (() => void) | null = null
let buttonClickVariantIndex = 0
let lastButtonSoundAt = 0

export function skillElementForCompanion(companionSlug?: string | null): BattleSkillElement {
  const slug = companionSlug?.trim().toLowerCase() ?? ''
  return COMPANION_ELEMENTS[slug] ?? 'flame'
}

function preloadBattleAudio(): void {
  if (!canUseAudio()) return
  for (const element of SKILL_ELEMENTS) {
    for (const phase of SKILL_PHASES) {
      loadAudio(skillSrc(element, phase))
    }
  }
  for (const sound of BUTTON_SOUNDS) {
    loadAudio(buttonSrc(sound))
  }
  loadAudio(backgroundSrc('outside'))
  loadAudio(backgroundSrc('inside'))
  for (const slug of COMPANION_SOUND_SLUGS) {
    for (const sound of COMPANION_SOUNDS) {
      loadAudio(companionSrc(slug, sound))
    }
  }
  loadAudio(monsterHurtSrc())
  for (const sound of SYSTEM_SOUNDS) {
    loadAudio(systemSrc(sound))
  }
}

export function isBattleSoundEnabled(): boolean {
  return battleSoundEffectsEnabled
}

export function setBattleSoundEnabled(enabled: boolean): void {
  if (battleSoundEffectsEnabled === enabled) return
  battleSoundEffectsEnabled = enabled
  persistAudioChannelPreference(SOUND_EFFECTS_ENABLED_STORAGE_KEY, enabled)
  if (!enabled) suspendSoundEffects()
  for (const listener of soundEffectsEnabledListeners) {
    listener(enabled)
  }
}

export function subscribeBattleSoundEnabled(listener: AudioPreferenceListener): () => void {
  soundEffectsEnabledListeners.add(listener)
  return () => {
    soundEffectsEnabledListeners.delete(listener)
  }
}

export function isBattleMusicEnabled(): boolean {
  return battleMusicEnabled
}

export function setBattleMusicEnabled(enabled: boolean): void {
  if (battleMusicEnabled === enabled) return
  battleMusicEnabled = enabled
  persistAudioChannelPreference(MUSIC_ENABLED_STORAGE_KEY, enabled)
  if (enabled) {
    resumeActiveBackground()
  } else {
    suspendBackgroundMusic()
  }
  for (const listener of musicEnabledListeners) {
    listener(enabled)
  }
}

export function subscribeBattleMusicEnabled(listener: AudioPreferenceListener): () => void {
  musicEnabledListeners.add(listener)
  return () => {
    musicEnabledListeners.delete(listener)
  }
}

export function playSkillSound(element: BattleSkillElement | undefined, phase: BattleSkillSoundPhase): void {
  if (!element) return
  playOneShot(skillSrc(element, phase), SKILL_VOLUMES[phase])
}

export function bindButtonSoundEffects(target: Document | HTMLElement = document): () => void {
  if (!canUseAudio()) return () => undefined

  const handleClick = (event: Event) => {
    if (event.defaultPrevented) return
    const sound = buttonSoundForEventTarget(event.target)
    if (!sound) return
    playButtonSound(sound)
  }

  target.addEventListener('click', handleClick)
  return () => target.removeEventListener('click', handleClick)
}

function playButtonSound(sound: ButtonSound = 'button-click'): void {
  const now = audioClockNow()
  if (now - lastButtonSoundAt < 36) return
  lastButtonSoundAt = now

  const selectedSound = sound === 'button-click' ? nextButtonClickVariant() : sound
  playOneShot(buttonSrc(selectedSound), BUTTON_SOUND_VOLUMES[selectedSound])
}

export function playCompanionHurtSound(companionSlug?: string | null): void {
  playOneShot(companionSrc(companionSoundSlug(companionSlug), 'hurt'), 0.42)
}

export function playCompanionDeathSound(companionSlug?: string | null): void {
  playOneShot(companionSrc(companionSoundSlug(companionSlug), 'death'), 0.46)
}

export function playMonsterHurtSound(): void {
  playOneShot(monsterHurtSrc(), 0.36)
}

export function playVictorySound(): void {
  stopBattleBackground({ fadeMs: 0 })
  playOneShot(systemSrc('victory'), 0.5)
}

export function playGameOverSound(): void {
  stopBattleBackground({ fadeMs: 0 })
  playOneShot(systemSrc('game-over'), 0.5)
}

export function playWaveTransitionSound(): void {
  playOneShot(systemSrc('wave-transition'), 0.44)
}

export function playRunSound(durationMs = 0): void {
  if (!durationMs) {
    playOneShot(systemSrc('run'), 0.28)
    return
  }
  playLoopFor(systemSrc('run'), 0.26, durationMs)
}

export function startBackgroundMusic(kind: BattleBackgroundKind): void {
  if (!canUseAudio()) return
  preloadBattleAudio()
  if (activeBackground?.kind === kind) {
    activeBackground.audio.loop = true
    activeBackground.audio.volume = BACKGROUND_VOLUMES[kind]
    if (battleMusicEnabled && activeBackground.audio.paused) {
      playBackground(activeBackground.audio)
    }
    return
  }
  clearBackgroundUnlock()
  if (activeBackground) {
    fadeOut(activeBackground.audio, 260)
  }

  const audio = loadAudio(backgroundSrc(kind))
  audio.loop = true
  audio.volume = BACKGROUND_VOLUMES[kind]
  audio.currentTime = 0
  activeBackground = { kind, audio }
  if (!battleMusicEnabled) return
  playBackground(audio)
}

export function stopBackgroundMusic(kind?: BattleBackgroundKind, options: { fadeMs?: number } = {}): void {
  if (kind && activeBackground?.kind !== kind) return
  clearBackgroundUnlock()
  const audio = activeBackground?.audio ?? null
  activeBackground = null
  if (!audio) return
  const fadeMs = options.fadeMs ?? 300
  if (fadeMs <= 0) {
    audio.pause()
    audio.currentTime = 0
    return
  }
  fadeOut(audio, fadeMs)
}

function stopBattleBackground(options: { fadeMs?: number } = {}): void {
  stopBackgroundMusic('inside', options)
}

function nextButtonClickVariant(): ButtonSound {
  const sound = BUTTON_CLICK_VARIANTS[buttonClickVariantIndex % BUTTON_CLICK_VARIANTS.length]
  buttonClickVariantIndex += 1
  return sound
}

function readAudioChannelPreference(storageKey: string): boolean {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return true
    const saved = window.localStorage.getItem(storageKey)
    if (saved) return saved !== 'off'
    return window.localStorage.getItem(LEGACY_AUDIO_ENABLED_STORAGE_KEY) !== 'off'
  } catch {
    return true
  }
}

function persistAudioChannelPreference(storageKey: string, enabled: boolean): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return
    window.localStorage.setItem(storageKey, enabled ? 'on' : 'off')
  } catch {
    // Storage can be unavailable in private or embedded contexts; audio still works.
  }
}

function playOneShot(src: string, volume: number): void {
  if (!canUseAudio() || !battleSoundEffectsEnabled) return
  const base = loadAudio(src)
  const audio = base.cloneNode(true) as HTMLAudioElement
  audio.volume = volume
  audio.loop = false
  activeOneShots.add(audio)
  audio.addEventListener(
    'ended',
    () => {
      activeOneShots.delete(audio)
      audio.remove()
    },
    { once: true },
  )
  tryPlay(audio)
  resumeActiveBackground()
}

function playLoopFor(src: string, volume: number, durationMs: number): void {
  if (!canUseAudio() || !battleSoundEffectsEnabled) return
  stopRunLoop(90)
  const base = loadAudio(src)
  const audio = base.cloneNode(true) as HTMLAudioElement
  audio.volume = volume
  audio.loop = true
  activeRunSound = audio
  tryPlay(audio)
  resumeActiveBackground()

  const timeout = window.setTimeout(() => {
    if (activeRunSound === audio) stopRunLoop(140)
  }, Math.max(120, durationMs))
  clearPendingRunStop = () => window.clearTimeout(timeout)
}

function stopRunLoop(fadeMs: number): void {
  clearPendingRunStop?.()
  clearPendingRunStop = null
  const audio = activeRunSound
  activeRunSound = null
  if (!audio) return
  fadeOut(audio, fadeMs)
}

function playBackground(audio: HTMLAudioElement): void {
  if (!battleMusicEnabled) return
  tryPlay(audio, () => scheduleBackgroundUnlock(audio))
}

function resumeActiveBackground(): void {
  if (!battleMusicEnabled) return
  const audio = activeBackground?.audio
  if (!audio || !audio.paused) return
  playBackground(audio)
}

function scheduleBackgroundUnlock(audio: HTMLAudioElement): void {
  if (!canUseAudio() || !battleMusicEnabled || activeBackground?.audio !== audio) return
  clearBackgroundUnlock()
  const retry = () => {
    clearBackgroundUnlock()
    if (activeBackground?.audio === audio) {
      playBackground(audio)
    }
  }
  window.addEventListener('pointerdown', retry, { capture: true, once: true })
  window.addEventListener('click', retry, { capture: true, once: true })
  window.addEventListener('keydown', retry, { capture: true, once: true })
  window.addEventListener('touchstart', retry, { capture: true, once: true })
  clearPendingBackgroundUnlock = () => {
    window.removeEventListener('pointerdown', retry, { capture: true })
    window.removeEventListener('click', retry, { capture: true })
    window.removeEventListener('keydown', retry, { capture: true })
    window.removeEventListener('touchstart', retry, { capture: true })
  }
}

function clearBackgroundUnlock(): void {
  clearPendingBackgroundUnlock?.()
  clearPendingBackgroundUnlock = null
}

function suspendSoundEffects(): void {
  clearPendingRunStop?.()
  clearPendingRunStop = null
  for (const audio of activeOneShots) {
    audio.pause()
    audio.currentTime = 0
    audio.remove()
  }
  activeOneShots.clear()
  if (activeRunSound) {
    activeRunSound.pause()
    activeRunSound.currentTime = 0
    activeRunSound.remove()
    activeRunSound = null
  }
}

function suspendBackgroundMusic(): void {
  clearBackgroundUnlock()
  if (activeBackground?.audio) {
    activeBackground.audio.pause()
  }
}
