export type ModuleAccent = {
  color: string
  gradientTo: string
  borderRgba: string
  borderHoverRgba: string
  glowRgba: string
}

export const MODULE_ACCENTS: Record<number, ModuleAccent> = {
  1: {
    color: '#3B82F6',
    gradientTo: '#1D4ED8',
    borderRgba: 'rgba(59, 130, 246, 0.35)',
    borderHoverRgba: 'rgba(59, 130, 246, 0.7)',
    glowRgba: 'rgba(59, 130, 246, 0.3)',
  },
  2: {
    color: '#00D4AA',
    gradientTo: '#00A896',
    borderRgba: 'rgba(0, 212, 170, 0.35)',
    borderHoverRgba: 'rgba(0, 212, 170, 0.7)',
    glowRgba: 'rgba(0, 212, 170, 0.3)',
  },
  3: {
    color: '#38BDF8',
    gradientTo: '#0284C7',
    borderRgba: 'rgba(56, 189, 248, 0.35)',
    borderHoverRgba: 'rgba(56, 189, 248, 0.7)',
    glowRgba: 'rgba(56, 189, 248, 0.3)',
  },
  4: {
    color: '#A78BFA',
    gradientTo: '#7C3AED',
    borderRgba: 'rgba(167, 139, 250, 0.35)',
    borderHoverRgba: 'rgba(167, 139, 250, 0.7)',
    glowRgba: 'rgba(167, 139, 250, 0.3)',
  },
  5: {
    color: '#FBBF24',
    gradientTo: '#D97706',
    borderRgba: 'rgba(251, 191, 36, 0.35)',
    borderHoverRgba: 'rgba(251, 191, 36, 0.7)',
    glowRgba: 'rgba(251, 191, 36, 0.22)',
  },
}

const FALLBACK_ACCENT = MODULE_ACCENTS[1]

export function getModuleAccent(moduleNumber: number): ModuleAccent {
  return MODULE_ACCENTS[moduleNumber] ?? FALLBACK_ACCENT
}
