import { useRef, type KeyboardEvent, type PointerEvent } from 'react'
import { Moon, Pause, Play, Sun } from 'lucide-react'

type SkyClockProps = {
  /** Current tower time, 0..24 hours. */
  timeOfDay: number
  /** Fired when the user drags the hand or nudges with the keyboard. */
  onScrub: (hour: number) => void
  /** Whether the day-night cycle is auto-advancing. */
  running: boolean
  onToggleRunning: () => void
  phaseLabel: string
}

const wrap24 = (hour: number) => ((hour % 24) + 24) % 24

function formatClock(timeOfDay: number) {
  const h = wrap24(timeOfDay)
  let hours = Math.floor(h)
  let minutes = Math.round((h - hours) * 60)
  if (minutes === 60) {
    minutes = 0
    hours = (hours + 1) % 24
  }
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

// Noon sits at the top of the dial, midnight at the bottom (a sundial). 0° points
// up; the angle grows clockwise so morning is on the left, evening on the right.
function hourToAngle(hour: number) {
  return (wrap24(hour) - 12) * 15
}

// A 24-hour astronomical clock face: noon sits at the top, midnight at the base.
const TICKS = Array.from({ length: 24 }, (_, i) => i)
const NUMERALS = [
  { hour: 12, label: 'XII' },
  { hour: 18, label: 'XVIII' },
  { hour: 0, label: 'XXIV' },
  { hour: 6, label: 'VI' },
]

export function SkyClock({ timeOfDay, onScrub, running, onToggleRunning, phaseLabel }: SkyClockProps) {
  const dialRef = useRef<HTMLDivElement | null>(null)
  const draggingRef = useRef(false)

  const isDay = timeOfDay >= 6 && timeOfDay < 18
  const angle = hourToAngle(timeOfDay)
  const rad = (angle * Math.PI) / 180
  const handLength = 30
  const tipX = 50 + handLength * Math.sin(rad)
  const tipY = 50 - handLength * Math.cos(rad)

  function pointerToHour(event: PointerEvent<HTMLDivElement>) {
    const el = dialRef.current
    if (!el) return null
    const rect = el.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const dx = event.clientX - cx
    const dy = event.clientY - cy
    // atan2(dx, -dy): up = 0°, right = +90°, matching hourToAngle.
    const deg = (Math.atan2(dx, -dy) * 180) / Math.PI
    return wrap24(12 + deg / 15)
  }

  function handlePointerDown(event: PointerEvent<HTMLDivElement>) {
    draggingRef.current = true
    event.currentTarget.setPointerCapture(event.pointerId)
    const hour = pointerToHour(event)
    if (hour !== null) onScrub(hour)
  }

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    if (!draggingRef.current) return
    const hour = pointerToHour(event)
    if (hour !== null) onScrub(hour)
  }

  function handlePointerUp(event: PointerEvent<HTMLDivElement>) {
    draggingRef.current = false
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    const step = event.shiftKey ? 1 : 0.5
    if (event.key === 'ArrowUp' || event.key === 'ArrowRight') {
      event.preventDefault()
      onScrub(wrap24(timeOfDay + step))
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowLeft') {
      event.preventDefault()
      onScrub(wrap24(timeOfDay - step))
    } else if (event.key === 'Home') {
      event.preventDefault()
      onScrub(0)
    } else if (event.key === 'End') {
      event.preventDefault()
      onScrub(12)
    }
  }

  return (
    <div className="sky-clock">
      <div
        ref={dialRef}
        className="sky-clock-dial"
        role="slider"
        tabIndex={0}
        aria-label="Set tower time of day"
        aria-valuemin={0}
        aria-valuemax={24}
        aria-valuenow={Number(timeOfDay.toFixed(1))}
        aria-valuetext={`${formatClock(timeOfDay)}, ${phaseLabel}`}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onKeyDown={handleKeyDown}
      >
        <svg viewBox="0 0 100 100" aria-hidden="true">
          <defs>
            <radialGradient id="sky-clock-face" cx="50%" cy="38%" r="70%">
              <stop offset="0%" stopColor="rgba(22, 48, 76, 0.94)" />
              <stop offset="54%" stopColor="rgba(7, 20, 44, 0.96)" />
              <stop offset="100%" stopColor="rgba(2, 8, 22, 0.98)" />
            </radialGradient>
          </defs>
          <path
            className="sky-clock-silhouette"
            d="M50 2 L56 11 L67 8 L70 19 L81 20 L80 31 L91 38 L84 48 L92 57 L82 64 L84 75 L72 76 L68 87 L58 84 L50 98 L42 84 L32 87 L28 76 L16 75 L18 64 L8 57 L16 48 L9 38 L20 31 L19 20 L30 19 L33 8 L44 11 Z"
          />
          <circle className="sky-clock-rim sky-clock-rim--outer" cx="50" cy="50" r="47" />
          <circle className="sky-clock-rim sky-clock-rim--face" cx="50" cy="50" r="43" fill="url(#sky-clock-face)" />
          <circle className="sky-clock-rim sky-clock-rim--inner" cx="50" cy="50" r="32" />
          <path className="sky-clock-ornament" d="M50 8 C54 16 58 19 67 19 C61 25 60 30 64 38 C56 35 51 36 45 42 C45 33 42 28 34 24 C43 22 47 17 50 8Z" />
          <path className="sky-clock-ornament sky-clock-ornament--lower" d="M50 92 C46 84 42 81 33 81 C39 75 40 70 36 62 C44 65 49 64 55 58 C55 67 58 72 66 76 C57 78 53 83 50 92Z" />
          <line className="sky-clock-cross" x1="14" y1="50" x2="86" y2="50" />
          <line className="sky-clock-cross" x1="50" y1="14" x2="50" y2="86" />
          {TICKS.map((hour) => {
            const a = (hourToAngle(hour) * Math.PI) / 180
            const major = hour % 3 === 0
            const inner = major ? 36.5 : 39.5
            const outer = 43.5
            return (
              <line
                key={hour}
                className={major ? 'sky-clock-tick sky-clock-tick--major' : 'sky-clock-tick'}
                x1={50 + inner * Math.sin(a)}
                y1={50 - inner * Math.cos(a)}
                x2={50 + outer * Math.sin(a)}
                y2={50 - outer * Math.cos(a)}
              />
            )
          })}
          {TICKS.map((hour) => {
            const a = (hourToAngle(hour) * Math.PI) / 180
            return (
              <circle
                key={hour}
                className="sky-clock-gem"
                cx={50 + 31 * Math.sin(a)}
                cy={50 - 31 * Math.cos(a)}
                r="1.5"
              />
            )
          })}
          {NUMERALS.map(({ hour, label }) => {
            const a = (hourToAngle(hour) * Math.PI) / 180
            return (
              <text
                key={`${hour}-${label}`}
                className="sky-clock-roman"
                x={50 + 24 * Math.sin(a)}
                y={50 - 24 * Math.cos(a)}
              >
                {label}
              </text>
            )
          })}
          {/* The travelling body: sun by day, moon by night, riding the hand tip. */}
          <line className="sky-clock-hand sky-clock-hand--shadow" x1="50" y1="50" x2={tipX} y2={tipY} />
          <path className="sky-clock-hand-tail" d={`M50 50 L${50 - 11 * Math.sin(rad)} ${50 + 11 * Math.cos(rad)}`} />
          <line className="sky-clock-hand" x1="50" y1="50" x2={tipX} y2={tipY} />
          <circle className={isDay ? 'sky-clock-sun' : 'sky-clock-moon'} cx={tipX} cy={tipY} r="6" />
          <circle className="sky-clock-hub" cx="50" cy="50" r="3.4" />
        </svg>
      </div>

      <div className="sky-clock-readout">
        <span className="sky-clock-time">
          {isDay ? <Sun className="size-3.5" /> : <Moon className="size-3.5" />}
          {formatClock(timeOfDay)}
        </span>
        <span className="sky-clock-phase">{phaseLabel}</span>
      </div>

      <button
        type="button"
        className="sky-clock-toggle"
        onClick={onToggleRunning}
        aria-pressed={running}
        aria-label={running ? 'Pause day-night cycle' : 'Resume day-night cycle'}
        title={running ? 'Pause day-night cycle' : 'Resume day-night cycle'}
      >
        {running ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
      </button>
    </div>
  )
}
