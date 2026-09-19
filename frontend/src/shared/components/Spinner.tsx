import { cn } from '@/shared/utils/cn'

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg'

/**
 * The basic spinner: the whole loading vocabulary for anything smaller than a
 * screen. A panel, a modal body, a section of a page that is still filling in
 * keeps its surroundings on screen and spins here, so only the full-screen
 * `LoadingScreen` ever runs the companion.
 *
 * Decorative on its own - the surrounding `LoadingState` (or the caller's own
 * control) owns the accessible name.
 */
export function Spinner({ size = 'md', className }: { size?: SpinnerSize; className?: string }) {
  return <span aria-hidden="true" className={cn('git-it-spinner', `git-it-spinner--${size}`, className)} />
}
