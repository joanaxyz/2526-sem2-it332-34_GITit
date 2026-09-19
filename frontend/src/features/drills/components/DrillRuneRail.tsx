import { useCallback, useEffect, useRef, useState } from 'react'

import type { DrillRailSegment } from '@/features/drills/hooks/useDrillSession'

/**
 * The rail: one rune per command form the level teaches.
 *
 * A single progress bar would answer "how much is left" and nothing else.
 * A rune is three stacked bars - one per rung on that card's ladder - so
 * the rail carries breadth and depth at once: how many commands remain,
 * and how well each one is actually known. That makes it the honest
 * answer to "what am I still shaky on" during the session, not only after
 * it, and it keeps the state visible rather than narrated.
 *
 * A light travels to the active rune instead of each rune animating on its
 * own, so attention moves with the session rather than flickering across
 * the whole rail.
 */
export function DrillRuneRail({
  segments,
  size = 'md',
}: {
  segments: DrillRailSegment[]
  /** 'lg' is the end-of-drill state: bigger marks, no running count. */
  size?: 'md' | 'lg'
}) {
  const listRef = useRef<HTMLOListElement | null>(null)
  const [travel, setTravel] = useState<{ x: number; width: number } | null>(null)
  const activeIndex = segments.findIndex((segment) => segment.active)

  const measure = useCallback(() => {
    const list = listRef.current
    if (!list || activeIndex < 0) {
      setTravel(null)
      return
    }
    const item = list.children[activeIndex]
    if (!(item instanceof HTMLElement)) return
    setTravel({ x: item.offsetLeft, width: item.offsetWidth })
  }, [activeIndex])

  useEffect(() => {
    measure()
    if (typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(measure)
    if (listRef.current) observer.observe(listRef.current)
    return () => observer.disconnect()
  }, [measure])

  const retired = segments.filter((segment) => segment.retired).length

  const finished = size === 'lg'

  return (
    <div className="drill-rail" data-size={size}>
      <ol className="drill-rail-runes" ref={listRef} aria-label="Commands in this drill">
        {segments.map((segment) => (
          <li
            key={segment.key}
            className="drill-rune"
            data-state={segment.retired ? 'done' : segment.active ? 'active' : 'pending'}
            data-missed={segment.retired && segment.missed ? '' : undefined}
            // A card can also leave the queue by exhausting its attempts.
            // Marking that apart keeps the finished rail honest instead of
            // showing a blank rune beside three lit ones.
            data-unfinished={segment.retired && !segment.mastered ? '' : undefined}
          >
            <span className="sr-only">
              {`${segment.command}: ${segment.cleared} of ${segment.total} rungs cleared`}
              {segment.retired && !segment.mastered
                ? ', still shaky'
                : segment.retired && segment.missed
                  ? ', needed another look'
                  : ''}
            </span>
            <span className="drill-rune-marks" aria-hidden="true">
              {Array.from({ length: segment.total }, (_, index) => (
                <i
                  key={index}
                  className="drill-rune-mark"
                  data-lit={index < segment.cleared ? '' : undefined}
                />
              ))}
            </span>
          </li>
        ))}
        {travel ? (
          <span
            className="drill-rail-light"
            aria-hidden="true"
            style={{ '--light-x': `${travel.x}px`, '--light-w': `${travel.width}px` } as never}
          />
        ) : null}
      </ol>
      {/* The numerator stays quiet until a command actually retires: the
          runes already show partial progress, and a bright 0 sitting next
          to three lit marks reads as "you have got nowhere". At the end
          every rune is lit, so the count would only restate them. */}
      {finished ? null : (
        <p className="drill-rail-count" data-started={retired > 0 ? '' : undefined}>
          <strong>{retired}</strong>
          <span>/{segments.length} commands</span>
        </p>
      )}
    </div>
  )
}
