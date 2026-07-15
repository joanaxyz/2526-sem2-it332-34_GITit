export type BattleSkillElement = 'flame' | 'ice' | 'lightning'
export type BattleSkillSoundPhase =
  | 'charge'
  | 'projectile'
  | 'target-center'
  | 'target-ground'
  | 'ground-run'
  | 'impact'
export type ButtonSound =
  | 'button-click'
  | 'button-click-soft'
  | 'button-click-bright'
  | 'button-toggle'
  | 'button-confirm'
  | 'button-dismiss'
  | 'button-danger'
export type BattleBackgroundKind = 'outside' | 'inside'
export type CompanionSound = 'hurt' | 'death'
export type SystemSound = 'victory' | 'game-over' | 'wave-transition' | 'run'

const AUDIO_ROOT = '/audio/battle'
const SKILL_ELEMENTS: BattleSkillElement[] = ['flame', 'ice', 'lightning']
const SKILL_PHASES: BattleSkillSoundPhase[] = [
  'charge',
  'projectile',
  'target-center',
  'target-ground',
  'ground-run',
  'impact',
]
const BUTTON_SOUNDS: ButtonSound[] = [
  'button-click',
  'button-click-soft',
  'button-click-bright',
  'button-toggle',
  'button-confirm',
  'button-dismiss',
  'button-danger',
]
const BUTTON_SOUND_SET = new Set<string>(BUTTON_SOUNDS)
const BUTTON_CLICK_VARIANTS: ButtonSound[] = ['button-click', 'button-click-soft', 'button-click-bright']
const BUTTON_SOUND_VOLUMES: Record<ButtonSound, number> = {
  'button-click': 0.2,
  'button-click-soft': 0.18,
  'button-click-bright': 0.18,
  'button-toggle': 0.2,
  'button-confirm': 0.24,
  'button-dismiss': 0.18,
  'button-danger': 0.2,
}
const COMPANION_SOUND_SLUGS = ['blue', 'white', 'black'] as const
const COMPANION_SOUNDS: CompanionSound[] = ['hurt', 'death']
const SYSTEM_SOUNDS: SystemSound[] = ['victory', 'game-over', 'wave-transition', 'run']
const COMPANION_ELEMENTS: Record<string, BattleSkillElement> = {
  blue: 'flame',
  white: 'ice',
  black: 'lightning',
}

const SKILL_VOLUMES: Record<BattleSkillSoundPhase, number> = {
  charge: 0.34,
  projectile: 0.32,
  'target-center': 0.38,
  'target-ground': 0.48,
  'ground-run': 0.36,
  impact: 0.46,
}

const BACKGROUND_VOLUMES: Record<BattleBackgroundKind, number> = {
  outside: 0.32,
  inside: 0.68,
}

const LEGACY_AUDIO_ENABLED_STORAGE_KEY = 'gitit:battle-audio-enabled'
const SOUND_EFFECTS_ENABLED_STORAGE_KEY = 'gitit:battle-sound-effects-enabled'
const MUSIC_ENABLED_STORAGE_KEY = 'gitit:battle-music-enabled'

type AudioPreferenceListener = (enabled: boolean) => void

const audioCache = new Map<string, HTMLAudioElement>()
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

export function preloadBattleAudio(): void {
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

export function buttonSoundForElement(element: Element): ButtonSound | null {
  if (isDisabledButtonLike(element)) return null

  const explicit = element.getAttribute('data-button-sound')?.trim()
  if (explicit === 'none') return null
  if (explicit && BUTTON_SOUND_SET.has(explicit)) return explicit as ButtonSound

  const classText = element.getAttribute('class')?.toLowerCase() ?? ''
  const labelText = [
    element.getAttribute('aria-label'),
    element.getAttribute('title'),
    element.textContent,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()

  if (/\b(danger|destructive|is-danger)\b/.test(classText)) return 'button-danger'
  if (/\b(delete|remove|revoke|sign out|unpublish|destroy|discard|reset|deduct)\b/.test(labelText)) {
    return 'button-danger'
  }
  if (/\b(close|cancel|back|exit|dismiss|previous)\b/.test(labelText) || /\b(close|dismiss)\b/.test(classText)) {
    return 'button-dismiss'
  }
  if (
    element.getAttribute('aria-pressed') !== null ||
    element.getAttribute('aria-selected') !== null ||
    element.getAttribute('role') === 'tab' ||
    element.getAttribute('role') === 'switch' ||
    /\b(tab|toggle|filter|selector|carousel|pager|switch)\b/.test(classText)
  ) {
    return 'button-toggle'
  }
  if (
    element.getAttribute('type') === 'submit' ||
    /\b(primary|submit|action|cta)\b/.test(classText) ||
    /\b(start|play|try again|retry|continue|next|buy|purchase|unlock|save|update|apply|create|publish|add|copy|submit|confirm|open|search)\b/.test(
      labelText,
    )
  ) {
    return 'button-confirm'
  }

  return 'button-click'
}

export function playButtonSound(sound: ButtonSound = 'button-click'): void {
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

export function startBattleBackground(): void {
  startBackgroundMusic('inside')
}

export function stopBattleBackground(options: { fadeMs?: number } = {}): void {
  stopBackgroundMusic('inside', options)
}

function skillSrc(element: BattleSkillElement, phase: BattleSkillSoundPhase): string {
  return `${AUDIO_ROOT}/skills/${element}/${phase}.wav`
}

function buttonSrc(sound: ButtonSound): string {
  return `${AUDIO_ROOT}/ui/${sound}.wav`
}

function buttonSoundForEventTarget(target: EventTarget | null): ButtonSound | null {
  if (!(target instanceof Element)) return null
  const element = target.closest('button, [role="button"], [role="tab"], [role="switch"], .ui-button')
  if (!element) return null
  return buttonSoundForElement(element)
}

function isDisabledButtonLike(element: Element): boolean {
  if (element.closest('[aria-disabled="true"]')) return true
  if (element.closest('[disabled]')) return true
  if (element instanceof HTMLButtonElement || element instanceof HTMLInputElement) return element.disabled
  return false
}

function nextButtonClickVariant(): ButtonSound {
  const sound = BUTTON_CLICK_VARIANTS[buttonClickVariantIndex % BUTTON_CLICK_VARIANTS.length]
  buttonClickVariantIndex += 1
  return sound
}

function audioClockNow(): number {
  if (typeof window !== 'undefined' && window.performance) return window.performance.now()
  return Date.now()
}

function backgroundSrc(kind: BattleBackgroundKind): string {
  const fileName = kind === 'outside' ? 'outside-battle-loop' : 'inside-battle-loop'
  return `${AUDIO_ROOT}/background/${fileName}.wav`
}

function companionSrc(companionSlug: (typeof COMPANION_SOUND_SLUGS)[number], sound: CompanionSound): string {
  return `${AUDIO_ROOT}/companions/${companionSlug}/${sound}.wav`
}

function monsterHurtSrc(): string {
  return `${AUDIO_ROOT}/monsters/hurt.wav`
}

function systemSrc(sound: SystemSound): string {
  return `${AUDIO_ROOT}/system/${sound}.wav`
}

function canUseAudio(): boolean {
  return import.meta.env.MODE !== 'test' && typeof window !== 'undefined' && typeof Audio !== 'undefined'
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

function loadAudio(src: string): HTMLAudioElement {
  const cached = audioCache.get(src)
  if (cached) return cached
  const audio = new Audio(src)
  audio.preload = 'auto'
  audioCache.set(src, audio)
  return audio
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

function tryPlay(audio: HTMLAudioElement, onReject?: () => void): void {
  try {
    const result = audio.play()
    void result.catch(() => {
      onReject?.()
    })
  } catch {
    onReject?.()
  }
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

function companionSoundSlug(companionSlug?: string | null): (typeof COMPANION_SOUND_SLUGS)[number] {
  const slug = companionSlug?.trim().toLowerCase()
  if (slug === 'white' || slug === 'black') return slug
  return 'blue'
}

function fadeOut(audio: HTMLAudioElement, durationMs: number): void {
  if (durationMs <= 0 || typeof window.requestAnimationFrame !== 'function') {
    audio.pause()
    audio.currentTime = 0
    return
  }

  const started = window.performance.now()
  const startVolume = audio.volume
  const step = (now: number) => {
    const progress = Math.min(1, (now - started) / durationMs)
    audio.volume = startVolume * (1 - progress)
    if (progress < 1) {
      window.requestAnimationFrame(step)
      return
    }
    audio.pause()
    audio.currentTime = 0
    audio.volume = startVolume
  }
  window.requestAnimationFrame(step)
}
