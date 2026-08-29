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

export const SKILL_ELEMENTS: BattleSkillElement[] = ['flame', 'ice', 'lightning']
export const SKILL_PHASES: BattleSkillSoundPhase[] = [
  'charge',
  'projectile',
  'target-center',
  'target-ground',
  'ground-run',
  'impact',
]
export const BUTTON_SOUNDS: ButtonSound[] = [
  'button-click',
  'button-click-soft',
  'button-click-bright',
  'button-toggle',
  'button-confirm',
  'button-dismiss',
  'button-danger',
]
export const BUTTON_SOUND_SET = new Set<string>(BUTTON_SOUNDS)
export const BUTTON_CLICK_VARIANTS: ButtonSound[] = ['button-click', 'button-click-soft', 'button-click-bright']
export const BUTTON_SOUND_VOLUMES: Record<ButtonSound, number> = {
  'button-click': 0.2,
  'button-click-soft': 0.18,
  'button-click-bright': 0.18,
  'button-toggle': 0.2,
  'button-confirm': 0.24,
  'button-dismiss': 0.18,
  'button-danger': 0.2,
}
export const COMPANION_SOUND_SLUGS = ['blue', 'white', 'black'] as const
export const COMPANION_SOUNDS: CompanionSound[] = ['hurt', 'death']
export const SYSTEM_SOUNDS: SystemSound[] = ['victory', 'game-over', 'wave-transition', 'run']
export const COMPANION_ELEMENTS: Record<string, BattleSkillElement> = {
  blue: 'flame',
  white: 'ice',
  black: 'lightning',
}

export const SKILL_VOLUMES: Record<BattleSkillSoundPhase, number> = {
  charge: 0.34,
  projectile: 0.32,
  'target-center': 0.38,
  'target-ground': 0.48,
  'ground-run': 0.36,
  impact: 0.46,
}

export const BACKGROUND_VOLUMES: Record<BattleBackgroundKind, number> = {
  outside: 0.32,
  inside: 0.68,
}

export function skillSrc(element: BattleSkillElement, phase: BattleSkillSoundPhase): string {
  return `${AUDIO_ROOT}/skills/${element}/${phase}.wav`
}

export function buttonSrc(sound: ButtonSound): string {
  return `${AUDIO_ROOT}/ui/${sound}.wav`
}

export function backgroundSrc(kind: BattleBackgroundKind): string {
  const fileName = kind === 'outside' ? 'outside-battle-loop' : 'inside-battle-loop'
  return `${AUDIO_ROOT}/background/${fileName}.wav`
}

export function companionSrc(companionSlug: (typeof COMPANION_SOUND_SLUGS)[number], sound: CompanionSound): string {
  return `${AUDIO_ROOT}/companions/${companionSlug}/${sound}.wav`
}

export function monsterHurtSrc(): string {
  return `${AUDIO_ROOT}/monsters/hurt.wav`
}

export function systemSrc(sound: SystemSound): string {
  return `${AUDIO_ROOT}/system/${sound}.wav`
}

export function companionSoundSlug(companionSlug?: string | null): (typeof COMPANION_SOUND_SLUGS)[number] {
  const slug = companionSlug?.trim().toLowerCase()
  if (slug === 'white' || slug === 'black') return slug
  return 'blue'
}
