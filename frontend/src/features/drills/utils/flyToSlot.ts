/**
 * FLIP for the chip that just moved.
 *
 * Tapping a token sends it from the bank to the forge line. Without the
 * flight the chip teleports and the two rows read as unrelated lists;
 * with it, the assembly line is visibly built out of the bank. The chip
 * has already been re-parented by React when this runs, so the animation
 * plays on the destination element, backwards from where the source sat.
 */

const FLIGHT_MS = 240
const EASE_OUT_EXPO = 'cubic-bezier(0.16, 1, 0.3, 1)'

export function prefersReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

export function flyFrom(from: DOMRect | null, to: HTMLElement | null): void {
  if (!from || !to) return
  if (prefersReducedMotion() || typeof to.animate !== 'function') return
  const target = to.getBoundingClientRect()
  const dx = from.left - target.left
  const dy = from.top - target.top
  if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return
  const scale = target.width > 0 ? Math.min(from.width / target.width, 1.4) : 1
  to.animate(
    [
      { transform: `translate(${dx}px, ${dy}px) scale(${scale})`, opacity: 0.65 },
      { transform: 'translate(0, 0) scale(1)', opacity: 1 },
    ],
    { duration: FLIGHT_MS, easing: EASE_OUT_EXPO, fill: 'none' },
  )
}
