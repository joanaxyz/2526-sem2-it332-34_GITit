import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'

import type { DrillRailSegment } from '@/features/drills/hooks/useDrillSession'

type TrackVars = CSSProperties & Record<string, string | number>

function clamp(value: number): string {
  return `${Math.max(0, Math.min(1, value)) * 100}%`
}

/**
 * The drill's one progress statement.
 *
 * It replaces a row of per-command runes that asked the eye to read a bar
 * chart before it could answer "how far in am I". That is one question and
 * it deserves one shape: a single front, moving left to right, gaining on
 * every rung banked.
 *
 * The bar is notched into one length per command, weighted by that
 * command's ladder, so it still carries the session's scale - six commands
 * and a finale, not an unmarked stripe - but the fill runs straight
 * through the notches rather than per command. A drill cycles between its
 * cards rather than finishing them in turn, so per-command fills scattered
 * lit dashes along the rail and the eye had to add them up. That was the
 * rune rail's failure in a new shape.
 *
 * Two fills, not one. A miss claws back the rung it banked, so a literal
 * bar slides backwards and reads as punishment. The dim reach mark stays
 * at the furthest the session ever got, so a miss shows as ground to win
 * back rather than ground destroyed - the same contract the verdict bar
 * keeps when it says the card will come round again.
 *
 * At the end the same bar switches to `record`: each notch now fills from
 * its own command's result, because the question has changed from "how far
 * am I" to "how did that go", and amber is the honest answer for a command
 * that needed a second look.
 */
export function DrillProgressTrack({
  segments,
  mode = 'progress',
}: {
  segments: DrillRailSegment[]
  /** 'record' is the end-of-drill state: per-command truth, read not watched. */
  mode?: 'progress' | 'record'
}) {
  const total = segments.reduce((sum, segment) => sum + segment.total, 0)
  const cleared = segments.reduce((sum, segment) => sum + segment.cleared, 0)
  const reached = segments.reduce(
    (sum, segment) => sum + Math.max(segment.best, segment.cleared),
    0,
  )

  // A sweep of light runs the length already earned each time a rung is
  // banked. It is keyed so it remounts and replays: a width transition
  // moves the edge, but nothing about it says "that one counted".
  const [gain, setGain] = useState(0)
  const previous = useRef(cleared)
  useEffect(() => {
    if (cleared > previous.current) setGain((value) => value + 1)
    previous.current = cleared
  }, [cleared])

  let offset = 0
  const lengths = segments.map((segment) => {
    const start = offset
    offset += segment.total
    return { segment, start, end: offset }
  })
  // The notch the front is standing in. Everything before it is behind you.
  const front = mode === 'progress' ? lengths.findIndex((row) => row.end > cleared) : -1

  return (
    <div className="drill-track" data-mode={mode}>
      <div
        className="drill-track-bar"
        role="progressbar"
        aria-label="Drill progress"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={cleared}
        aria-valuetext={`${cleared} of ${total} steps cleared`}
      >
        {lengths.map(({ segment, start, end }, index) => {
          const span = Math.max(end - start, 1)
          const fill =
            mode === 'record' ? segment.cleared / span : (cleared - start) / span
          const reach =
            mode === 'record'
              ? Math.max(segment.best, segment.cleared) / span
              : (reached - start) / span
          const state =
            mode === 'record'
              ? segment.retired
                ? 'done'
                : 'pending'
              : index === front
                ? 'active'
                : index < front || front < 0
                  ? 'done'
                  : 'pending'

          return (
            <span
              key={segment.key}
              className="drill-track-seg"
              aria-hidden="true"
              data-state={state}
              data-missed={mode === 'record' && segment.missed ? '' : undefined}
              // A card can also leave the queue by exhausting its attempts.
              // Marking that apart keeps the record honest instead of
              // showing a gap that looks like a rendering fault.
              data-unfinished={
                mode === 'record' && segment.retired && !segment.mastered ? '' : undefined
              }
              style={{ flexGrow: span, flexShrink: 1, flexBasis: 0 }}
            >
              <i className="drill-track-reach" style={{ '--reach': clamp(reach) } as TrackVars} />
              <i className="drill-track-fill" style={{ '--fill': clamp(fill) } as TrackVars} />
            </span>
          )
        })}
        {gain > 0 && mode === 'progress' ? (
          <i
            key={gain}
            className="drill-track-sweep"
            aria-hidden="true"
            style={{ '--swept': clamp(cleared / Math.max(total, 1)) } as TrackVars}
          />
        ) : null}
      </div>

      {/* The notches are decoration to a screen reader - the bar above
          already reports the number. This is the per-command breadth a
          sighted learner reads off the record at the end. */}
      {mode === 'record' ? (
        <ul className="sr-only">
          {segments.map((segment) => (
            <li key={segment.key}>
              {`${segment.command}: ${segment.cleared} of ${segment.total} steps cleared`}
              {segment.retired && !segment.mastered
                ? ', never landed'
                : segment.missed
                  ? ', needed another look'
                  : ''}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
