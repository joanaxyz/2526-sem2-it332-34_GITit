import { useEffect } from 'react'
import type { RefObject } from 'react'

const FOCUSABLE_SELECTOR =
  'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

/**
 * Shared focus-trap behavior for dialogs, menus, and other keyboard-modal
 * overlays: moves focus into `containerRef` while `active`, cycles Tab/
 * Shift+Tab between its focusable descendants, and restores focus to
 * whatever had it beforehand once `active` goes false (or the component
 * unmounts). Does not handle Escape-to-close or scroll locking — those stay
 * caller-specific since not every consumer wants them.
 */
export function useFocusTrap(containerRef: RefObject<HTMLElement | null>, active: boolean) {
  useEffect(() => {
    if (!active) return
    const container = containerRef.current
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null

    const focusable = () => Array.from(container?.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR) ?? [])
    window.requestAnimationFrame(() => (focusable()[0] ?? container)?.focus())

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Tab') return
      const items = focusable()
      if (!items.length) {
        event.preventDefault()
        container?.focus()
        return
      }
      const first = items[0]
      const last = items[items.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      previousFocus?.focus()
    }
  }, [active, containerRef])
}
