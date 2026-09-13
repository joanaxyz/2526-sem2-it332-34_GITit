/**
 * The app's resolved motion setting (`data-motion`, written by
 * `shared/preferences` before React mounts). Recharts animates in JavaScript, so
 * the CSS reduced-motion rules cannot reach it — chart components ask here.
 *
 * Anything other than a resolved "full" draws instantly: that covers the
 * reduced-motion setting and any render where preferences have not been applied
 * at all, which is the honest default for a chart that must be readable the
 * moment it appears.
 */
export function chartAnimationDuration(duration = 520): number {
  if (typeof document === 'undefined') return 0
  return document.documentElement.dataset.motion === 'full' ? duration : 0
}
