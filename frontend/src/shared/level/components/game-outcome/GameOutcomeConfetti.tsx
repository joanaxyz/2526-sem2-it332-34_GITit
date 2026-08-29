import { PartyPopper } from 'lucide-react'
import type { CSSProperties } from 'react'

const confettiColors = ['hsl(var(--primary))', 'hsl(var(--accent))', 'rgb(var(--theme-rail-rgb))', 'rgb(var(--theme-challenge-rgb))', 'hsl(var(--warning))', 'rgb(var(--theme-spark-rgb))']

const confettiPieces = Array.from({ length: 52 }, (_, index) => {
  const side = index % 2 === 0 ? -1 : 1
  const lane = Math.floor(index / 2)
  const x = side * (38 + ((lane * 18) % 220))
  const y = 80 + ((index * 29) % 200)
  return {
    color: confettiColors[index % confettiColors.length],
    delay: `${(index % 10) * 42}ms`,
    duration: `${1700 + (index % 7) * 120}ms`,
    height: `${7 + (index % 4) * 2}px`,
    rotate: `${side * (210 + (index % 8) * 32)}deg`,
    width: `${4 + (index % 4)}px`,
    x: `${x}px`,
    y: `${y}px`,
  }
})

/**
 * Party poppers plus a falling neon burst for successful game outcomes.
 */
export function GameOutcomeConfetti() {
  return (
    <>
      <div className="game-outcome-party-popper game-outcome-party-popper-left" aria-hidden="true">
        <PartyPopper className="size-10 text-accent" />
      </div>
      <div className="game-outcome-party-popper game-outcome-party-popper-right" aria-hidden="true">
        <PartyPopper className="size-10 -scale-x-100 text-primary" />
      </div>
      <div className="game-outcome-confetti-layer pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
        {confettiPieces.map((piece, index) => (
          <span
            className="game-outcome-confetti"
            key={`${piece.x}-${piece.y}-${index}`}
            style={
              {
                '--confetti-color': piece.color,
                '--confetti-delay': piece.delay,
                '--confetti-duration': piece.duration,
                '--confetti-height': piece.height,
                '--confetti-rotate': piece.rotate,
                '--confetti-width': piece.width,
                '--confetti-x': piece.x,
                '--confetti-y': piece.y,
              } as CSSProperties
            }
          />
        ))}
      </div>
    </>
  )
}
