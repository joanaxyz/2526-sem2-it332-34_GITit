import { useEffect, useSyncExternalStore } from 'react'

function subscribe(onChange: () => void) {
  if (typeof window === 'undefined') return () => undefined
  window.addEventListener('guide-mascot-visibility-change', onChange)
  return () => window.removeEventListener('guide-mascot-visibility-change', onChange)
}

function getSnapshot() {
  return typeof document === 'undefined'
    ? true
    : document.documentElement.dataset.guideMascotVisible !== 'false'
}

export function useGuideMascotVisibility() {
  return useSyncExternalStore(subscribe, getSnapshot, () => true)
}

let worldMascotHolds = 0

/** Hides the page mascot while a full-screen reader is open, without changing the saved preference. */
export function useHideWorldMascot() {
  useEffect(() => {
    const root = document.documentElement
    worldMascotHolds += 1
    root.dataset.worldMascotHidden = 'true'
    return () => {
      worldMascotHolds -= 1
      if (!worldMascotHolds) delete root.dataset.worldMascotHidden
    }
  }, [])
}
