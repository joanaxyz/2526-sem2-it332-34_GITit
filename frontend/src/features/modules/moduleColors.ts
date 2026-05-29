export type ModuleAccent = {
  /** Primary accent hex — used for text, icons, progress bar, and CSS variable cascade */
  color: string
  /** Darker end of the progress bar gradient */
  gradientTo: string
  /** Pre-built rgba — card left border at rest (also used as icon border) */
  borderRgba: string
  /** Pre-built rgba — left border on hover (also used as lesson-row inset shadow) */
  borderHoverRgba: string
  /** Pre-built rgba — box-shadow glow on hover (cascades to child cards) */
  glowRgba: string
}

// Single source of truth for all per-module color accents.
// Change any value here to retune a module's full palette.
export const MODULE_ACCENTS: Record<number, ModuleAccent> = {
  0: {
    // Module 0 — Orientation: teal-green (original brand color)
    color: '#00D4AA',
    gradientTo: '#00A896',
    borderRgba: 'rgba(0, 212, 170, 0.35)',
    borderHoverRgba: 'rgba(0, 212, 170, 0.7)',
    glowRgba: 'rgba(0, 212, 170, 0.3)',
  },
  1: {
    // Module 1 — Local Repository Foundations: bright blue
    color: '#3B82F6',
    gradientTo: '#1D4ED8',
    borderRgba: 'rgba(59, 130, 246, 0.35)',
    borderHoverRgba: 'rgba(59, 130, 246, 0.7)',
    glowRgba: 'rgba(59, 130, 246, 0.3)',
  },
  2: {
    // Module 2 — Branching and Collaboration: violet/indigo
    color: '#C4B5FD',
    gradientTo: '#8B5CF6',
    borderRgba: 'rgba(196, 181, 253, 0.35)',
    borderHoverRgba: 'rgba(196, 181, 253, 0.7)',
    glowRgba: 'rgba(196, 181, 253, 0.3)',
  },
  3: {
    // Module 3 — Conflict Resolution: sky blue
    color: '#38BDF8',
    gradientTo: '#0284C7',
    borderRgba: 'rgba(56, 189, 248, 0.35)',
    borderHoverRgba: 'rgba(56, 189, 248, 0.7)',
    glowRgba: 'rgba(56, 189, 248, 0.3)',
  },
  4: {
    // Module 4 — Advanced Recovery and History: purple
    color: '#A78BFA',
    gradientTo: '#7C3AED',
    borderRgba: 'rgba(167, 139, 250, 0.35)',
    borderHoverRgba: 'rgba(167, 139, 250, 0.7)',
    glowRgba: 'rgba(167, 139, 250, 0.3)',
  },
}

const FALLBACK_ACCENT = MODULE_ACCENTS[0]

export function getModuleAccent(moduleNumber: number): ModuleAccent {
  return MODULE_ACCENTS[moduleNumber] ?? FALLBACK_ACCENT
}
