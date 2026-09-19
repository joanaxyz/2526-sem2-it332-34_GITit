import { useId, useLayoutEffect, useRef, useState } from 'react'
import { Keyboard, Undo2 } from 'lucide-react'

import type { DrillVerdict } from '@/features/drills/types'
import { flyFrom } from '@/features/drills/utils/flyToSlot'

type Piece = { id: string; value: string }

function toPieces(values: string[], prefix: string): Piece[] {
  return values.map((value, index) => ({ id: `${prefix}:${index}:${value}`, value }))
}

/**
 * Build-the-answer, for both production rungs.
 *
 * Assembling a command from loose tokens is the closest thing to typing it
 * that still fits in a few seconds, and it rehearses the part beginners
 * actually get wrong - which flag, in which order - without punishing
 * them for a typo. The same mechanic orders the level's authored solution
 * in the finale, so there is one interaction to learn, not two.
 *
 * Tokens fly from the bank to the line rather than teleporting, because
 * the two rows have to read as one object being built, not two lists.
 */
export function DrillAssembleBoard({
  values,
  placedIds,
  onChange,
  variant,
  verdict,
  expected,
  allowTyping = false,
  typed,
  onTyped,
}: {
  values: string[]
  placedIds: string[]
  onChange: (next: string[]) => void
  variant: 'tokens' | 'steps'
  verdict: DrillVerdict | null
  expected: string[]
  allowTyping?: boolean
  typed?: string
  onTyped?: (value: string) => void
}) {
  const pieces = toPieces(values, variant)
  const byId = new Map(pieces.map((piece) => [piece.id, piece]))
  const placed = placedIds.map((id) => byId.get(id)).filter((piece): piece is Piece => !!piece)
  const remaining = pieces.filter((piece) => !placedIds.includes(piece.id))
  const [typing, setTyping] = useState(false)
  const inputId = useId()

  const flightRef = useRef<{ id: string; rect: DOMRect } | null>(null)
  const slotRefs = useRef(new Map<string, HTMLElement>())

  useLayoutEffect(() => {
    const flight = flightRef.current
    if (!flight) return
    flightRef.current = null
    flyFrom(flight.rect, slotRefs.current.get(flight.id) ?? null)
  })

  function place(piece: Piece, source: HTMLElement | null) {
    if (verdict) return
    flightRef.current = source ? { id: piece.id, rect: source.getBoundingClientRect() } : null
    onChange([...placedIds, piece.id])
  }

  function lift(piece: Piece) {
    if (verdict) return
    onChange(placedIds.filter((id) => id !== piece.id))
  }

  if (typing && allowTyping) {
    return (
      <div className="drill-assemble" data-variant="typed">
        <label className="drill-typed-label" htmlFor={inputId}>
          Type the command
        </label>
        <input
          id={inputId}
          className="drill-typed-input"
          value={typed ?? ''}
          spellCheck={false}
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          disabled={Boolean(verdict)}
          placeholder="git …"
          onChange={(event) => onTyped?.(event.target.value)}
        />
        <button
          type="button"
          className="drill-mode-toggle"
          onClick={() => {
            setTyping(false)
            onTyped?.('')
          }}
        >
          <Undo2 aria-hidden="true" />
          Use the token bank
        </button>
      </div>
    )
  }

  return (
    <div className="drill-assemble" data-variant={variant}>
      <ol className="drill-line" data-empty={placed.length === 0 ? '' : undefined}>
        {placed.map((piece, index) => {
          const state = !verdict ? 'idle' : piece.value === expected[index] ? 'right' : 'wrong'
          return (
            <li key={piece.id}>
              <button
                type="button"
                ref={(node) => {
                  if (node) slotRefs.current.set(piece.id, node)
                  else slotRefs.current.delete(piece.id)
                }}
                className="drill-piece"
                data-placed=""
                data-state={state}
                disabled={Boolean(verdict)}
                aria-label={`Remove ${piece.value} from position ${index + 1}`}
                onClick={() => lift(piece)}
              >
                {variant === 'steps' ? (
                  <span className="drill-piece-index" aria-hidden="true">
                    {index + 1}
                  </span>
                ) : null}
                <span className="drill-piece-value">{piece.value}</span>
              </button>
            </li>
          )
        })}
        {/* Ordering shows its empty slots numbered: the shape of the answer
            is part of the question, and an empty dashed line above a bank
            of chips reads as a caption rather than a target. Assembly needs
            no slots - a command has no fixed length. */}
        {variant === 'steps'
          ? expected.slice(placed.length).map((_, offset) => (
              <li key={`slot-${placed.length + offset}`}>
                <span className="drill-slot" aria-hidden="true">
                  <span className="drill-piece-index">{placed.length + offset + 1}</span>
                </span>
              </li>
            ))
          : null}
        {variant === 'tokens' && placed.length === 0 ? (
          <li className="drill-line-hint" aria-hidden="true">
            Build the command
          </li>
        ) : null}
      </ol>

      <ul className="drill-bank" aria-label="Available pieces">
        {remaining.map((piece) => (
          <li key={piece.id}>
            <button
              type="button"
              className="drill-piece"
              disabled={Boolean(verdict)}
              onClick={(event) => place(piece, event.currentTarget)}
            >
              <span className="drill-piece-value">{piece.value}</span>
            </button>
          </li>
        ))}
        {remaining.length === 0 ? (
          <li className="drill-bank-empty" aria-hidden="true">
            Everything is placed
          </li>
        ) : null}
      </ul>

      {allowTyping && !verdict ? (
        <button type="button" className="drill-mode-toggle" onClick={() => setTyping(true)}>
          <Keyboard aria-hidden="true" />
          Type it instead
        </button>
      ) : null}
    </div>
  )
}
