import { useEffect, useId, useMemo, useRef, useState } from 'react'

import { DrillAssembleBoard } from '@/features/drills/components/DrillAssembleBoard'
import { DrillChoiceBoard } from '@/features/drills/components/DrillChoiceBoard'
import type {
  DrillAnswer,
  DrillCard,
  DrillChoice,
  DrillRung,
  DrillSequence,
  DrillVerdict,
} from '@/features/drills/types'
import { choicePoolFor } from '@/features/drills/utils/drillChoices'
import { prefersReducedMotion } from '@/features/drills/utils/flyToSlot'
import { seededShuffle, shuffleAway } from '@/features/drills/utils/drillShuffle'

const RUNG_LABEL: Record<DrillRung, string> = {
  recognise: 'Recognise',
  read: 'Read',
  complete: 'Complete',
  forge: 'Forge',
}

const RUNG_QUESTION: Record<DrillRung, string> = {
  recognise: 'Which command does this?',
  read: 'What does this command do?',
  complete: 'Fill the missing piece.',
  forge: 'Build the command.',
}

/**
 * One question. The rung decides what is shown and what is asked for; the
 * subject line is always the thing the learner is reasoning *from*, and the
 * answer area is always the thing they are reasoning *to*.
 *
 * The parent remounts this per ask, so draft answers are local state - a
 * half-placed token line must never survive into the next question.
 */
export function DrillQuestion({
  card,
  rung,
  sequence,
  round,
  verdict,
  onAnswer,
}: {
  card: DrillCard | null
  rung: DrillRung | null
  sequence: DrillSequence | null
  round: number
  verdict: DrillVerdict | null
  onAnswer: (answer: DrillAnswer | null) => void
}) {
  const [selected, setSelected] = useState<string | null>(null)
  const [placedIds, setPlacedIds] = useState<string[]>([])
  const [typed, setTyped] = useState('')
  const sectionRef = useRef<HTMLElement | null>(null)
  const askId = useId()

  // Each question is a fresh mount, so without this the Continue button
  // unmounts and focus falls to the document: a keyboard user would tab
  // from the top of the page for every question, and a screen reader
  // would never be told the question changed. Focusing the labelled
  // section announces it once and puts Tab one step from the first answer.
  useEffect(() => {
    sectionRef.current?.focus({ preventScroll: true })
  }, [])

  // Grading opens the teach panel, which on a short viewport pushes the
  // answer the learner just gave below the fold - exactly the thing they
  // need to see marked. Bring the graded row back into view.
  useEffect(() => {
    if (!verdict) return
    // The wrong pick first, deliberately. A combined selector returns
    // whichever comes first in the DOM, which is usually the right answer
    // sitting above the learner's own - and the one thing they came to see
    // marked is the one they chose.
    const marked =
      sectionRef.current?.querySelector('[data-state="wrong"]') ??
      sectionRef.current?.querySelector('[data-state="answer"]')
    marked?.scrollIntoView({
      block: 'nearest',
      behavior: prefersReducedMotion() ? 'auto' : 'smooth',
    })
  }, [verdict])

  const isSequence = !card || !rung

  const options: DrillChoice[] = useMemo(() => {
    const pool = choicePoolFor(card, rung)
    if (!pool.length) return []
    return seededShuffle(pool, `${card?.key}:${rung}:${round}`)
  }, [card, round, rung])

  const bank = useMemo(() => {
    if (isSequence) return shuffleAway(sequence?.steps ?? [], `sequence:${round}`)
    if (rung === 'forge' && card) return shuffleAway(card.bank, `${card.key}:forge:${round}`)
    return []
  }, [card, isSequence, round, rung, sequence])

  function pick(value: string) {
    setSelected(value)
    onAnswer({ kind: 'choice', value })
  }

  function placeAll(next: string[], pieces: string[]) {
    setPlacedIds(next)
    const values = next.map((id) => pieces[Number(id.split(':')[1])])
    onAnswer(values.length ? { kind: 'tokens', values } : null)
  }

  if (isSequence) {
    if (!sequence) return null
    return (
      <section
        className="drill-question"
        ref={sectionRef}
        tabIndex={-1}
        aria-labelledby={askId}
      >
        <p className="drill-rung">Order the moves</p>
        <h2 className="drill-ask" id={askId}>
          Put this run in the order it happens.
        </h2>
        <p className="drill-subject-note">{sequence.task || sequence.label}</p>
        <DrillAssembleBoard
          values={bank}
          placedIds={placedIds}
          onChange={(next) => placeAll(next, bank)}
          variant="steps"
          verdict={verdict}
          expected={sequence.steps}
        />
      </section>
    )
  }

  if (!card || !rung) return null

  const blankIndex = card.blank?.index ?? -1

  return (
    <section className="drill-question" ref={sectionRef} tabIndex={-1} aria-labelledby={askId}>
      <p className="drill-rung">
        {RUNG_LABEL[rung]}
        {/* Only Read may name the command, because Read already shows it in
            full. Every other rung hides some part of it - the whole line on
            Recognise and Forge, one token on Complete - and printing the
            base command here would hand that part straight back. */}
        {rung !== 'read' ? null : (
          <>
            <span aria-hidden="true"> · </span>
            <span className="drill-rung-command">{card.base_command}</span>
          </>
        )}
      </p>
      <h2 className="drill-ask" id={askId}>
        {RUNG_QUESTION[rung]}
      </h2>

      {rung === 'recognise' ? <p className="drill-subject">{card.intent}</p> : null}
      {rung === 'read' ? <p className="drill-subject" data-voice="machine">{card.command}</p> : null}
      {rung === 'complete' ? (
        <>
          <p className="drill-subject-note">{card.intent}</p>
          <p className="drill-subject" data-voice="machine">
            {card.tokens.map((token, index) =>
              index === blankIndex ? (
                <span
                  key={`slot-${index}`}
                  className="drill-gap"
                  data-filled={selected ? '' : undefined}
                >
                  {selected ?? '   '}
                </span>
              ) : (
                <span key={`${token}-${index}`}>{token}</span>
              ),
            )}
          </p>
        </>
      ) : null}
      {rung === 'forge' ? <p className="drill-subject">{card.intent}</p> : null}

      {rung === 'forge' ? (
        <DrillAssembleBoard
          values={bank}
          placedIds={placedIds}
          onChange={(next) => placeAll(next, bank)}
          variant="tokens"
          verdict={verdict}
          expected={card.tokens}
          allowTyping
          typed={typed}
          onTyped={(value) => {
            setTyped(value)
            const values = value.trim().split(/\s+/).filter(Boolean)
            onAnswer(values.length ? { kind: 'tokens', values } : null)
          }}
        />
      ) : (
        <DrillChoiceBoard
          options={options}
          layout={rung === 'complete' ? 'chips' : 'rows'}
          voice={rung === 'read' ? 'prose' : 'machine'}
          selected={selected}
          correctValue={
            rung === 'read'
              ? card.intent
              : rung === 'complete'
                ? (card.blank?.answer ?? '')
                : card.command
          }
          verdict={verdict}
          onSelect={pick}
        />
      )}
    </section>
  )
}
