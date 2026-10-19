const STORAGE_KEY = 'git-it-guide-appearance'

export function readGuideMascotVisibility(): boolean {
  if (typeof window === 'undefined') return true
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    if (value === 'false' || value === 'hidden') return false
    return true
  } catch {
    return true
  }
}

export function applyGuideMascotVisibility(visible: boolean) {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.guideMascotVisible = String(visible)
  if (typeof window !== 'undefined') window.dispatchEvent(new Event('guide-mascot-visibility-change'))
}

export function initializeGuideMascotVisibility() {
  applyGuideMascotVisibility(readGuideMascotVisibility())
}

export function setGuideMascotVisibility(visible: boolean): boolean {
  applyGuideMascotVisibility(visible)
  if (typeof window === 'undefined') return false
  try {
    window.localStorage.setItem(STORAGE_KEY, String(visible))
    return true
  } catch {
    return false
  }
}
