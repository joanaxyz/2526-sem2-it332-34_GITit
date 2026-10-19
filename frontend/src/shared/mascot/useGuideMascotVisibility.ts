import { useSyncExternalStore } from 'react'

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
