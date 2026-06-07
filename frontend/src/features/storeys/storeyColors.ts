export type ModuleAccent = {
  color: string
  gradientTo: string
  borderRgba: string
  borderHoverRgba: string
  glowRgba: string
}

const BLUE: ModuleAccent = {
  color: '#00B4D8',
  gradientTo: '#0077B6',
  borderRgba: 'rgba(0, 180, 216, 0.32)',
  borderHoverRgba: 'rgba(0, 180, 216, 0.68)',
  glowRgba: 'rgba(0, 180, 216, 0.22)',
}

const TEAL: ModuleAccent = {
  color: '#00F5D4',
  gradientTo: '#00A896',
  borderRgba: 'rgba(0, 245, 212, 0.32)',
  borderHoverRgba: 'rgba(0, 245, 212, 0.68)',
  glowRgba: 'rgba(0, 245, 212, 0.22)',
}

export const MODULE_ACCENTS: Record<number, ModuleAccent> = {
  1: BLUE,
  2: TEAL,
  3: BLUE,
  4: TEAL,
  5: BLUE,
}

const FALLBACK_ACCENT = BLUE

export function getModuleAccent(moduleNumber: number): ModuleAccent {
  return MODULE_ACCENTS[moduleNumber] ?? FALLBACK_ACCENT
}
