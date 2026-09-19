import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { drillsApi } from '@/features/drills/api/drillsApi'
import { queryKeys } from '@/shared/api/queryKeys'
import type { DrillAnswer, DrillPlan, DrillVerdict } from '@/features/drills/types'
import type { DrillQueueState } from '@/features/drills/utils/drillQueue'
import { gradeCard, gradeSequence } from '@/features/drills/utils/drillGrading'
import {
  accuracy,
  allMastered,
  answerCurrent,
  createQueue,
  currentAsk,
  isFinished,
  restoreQueue,
  shakyKeys,
} from '@/features/drills/utils/drillQueue'

export type DrillRailSegment = {
  /** The closing ordering question is part of the session, but it is not a
      command with a ladder, so anything counting commands has to skip it. */
  kind: 'command' | 'finale'
  key: string
  command: string
  intent: string
  cleared: number
  /** The furthest this card ever reached. A miss claws a rung back, and
      the progress track shows the ground already won behind the live
      edge rather than pretending it was never won. */
  best: number
  total: number
  retired: boolean
  /** Retired by clearing every rung, rather than by hitting the ask cap. */
  mastered: boolean
  missed: boolean
  active: boolean
}

/** The furthest each card has ever reached; monotonic by construction. */
function highWater(
  current: Record<string, number>,
  queue: DrillQueueState,
): Record<string, number> {
  let next = current
  for (const [key, card] of Object.entries(queue.cards)) {
    if ((next[key] ?? 0) >= card.cleared) continue
    if (next === current) next = { ...current }
    next[key] = card.cleared
  }
  return next
}

/**
 * One drill session: the queue, the answer in hand, and the verdict.
 *
 * Two deliberate shapes here. The verdict is separate state rather than
 * derived, because the loop is answer -> check -> read the outcome ->
 * continue, and collapsing check and continue into one press removes the
 * only moment a miss is actually taught. And `round` increments once per
 * ask so option shuffles are stable through re-renders (a resize must not
 * reorder the answers someone is reading) while still varying the next
 * time the same card comes round.
 */
export function useDrillSession(plan: DrillPlan) {
  const queryClient = useQueryClient()
  // A drill runs for several minutes and re-asks what you missed, so a
  // refresh used to cost the whole ladder. The server hands back the
  // queue it last checkpointed; `restoreQueue` refuses it if the seeded
  // content has moved on underneath it.
  const [queue, setQueue] = useState(
    () =>
      restoreQueue(plan.cards, Boolean(plan.sequence), plan.resume?.queue_state) ??
      createQueue(plan.cards, Boolean(plan.sequence)),
  )
  const [resumed] = useState(() => Boolean(plan.resume?.queue_state))
  const [best, setBest] = useState<Record<string, number>>(() => highWater({}, queue))
  const [finaleMissed, setFinaleMissed] = useState(false)
  const [answer, setAnswer] = useState<DrillAnswer | null>(null)
  const [verdict, setVerdict] = useState<DrillVerdict | null>(null)
  const [round, setRound] = useState(0)
  const reportedRef = useRef(false)

  const cardsByKey = useMemo(
    () => Object.fromEntries(plan.cards.map((card) => [card.key, card])),
    [plan.cards],
  )
  const ask = currentAsk(queue)
  const card = ask?.kind === 'card' ? (cardsByKey[ask.cardKey] ?? null) : null
  const finished = isFinished(queue)

  // Derived rather than written inside `advance`, so the map survives a
  // restored checkpoint and a StrictMode double-render alike: it only ever
  // climbs, and re-running it on the same queue is a no-op.
  useEffect(() => {
    setBest((current) => highWater(current, queue))
  }, [queue])

  const saveRun = useMutation({
    mutationFn: (body: Parameters<typeof drillsApi.saveRun>[1]) =>
      drillsApi.saveRun(plan.level.id, body),
  })

  const report = useMutation({
    mutationFn: (body: Parameters<typeof drillsApi.reportSession>[1]) =>
      drillsApi.reportSession(plan.level.id, body),
    onSuccess: () => {
      // The level map paints a "Drilled" mark from the chapter overview, so
      // it has to be refetched or the map still says undrilled on return.
      if (plan.level.chapter_id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.chapterOverview(plan.level.chapter_id),
        })
      }
    },
  })

  useEffect(() => {
    if (!finished || reportedRef.current) return
    reportedRef.current = true
    report.mutate({
      answers_total: queue.answered,
      answers_correct: queue.correct,
      // Only a session where every card topped its ladder counts as a
      // clear; running out of attempts still records the attempt and the
      // weak spots, but must not mark the level drilled.
      completed: allMastered(queue),
      shaky_form_keys: shakyKeys(queue),
    })
  }, [finished, queue, report])

  // Checkpoint after every answer rather than on a timer: the queue only
  // moves when a question is answered, and a save that lands one question
  // behind would resume into a question the learner already cleared.
  // Fire-and-forget - a failed checkpoint must never interrupt the drill.
  const checkpoint = useCallback(
    (next: DrillQueueState) => {
      if (isFinished(next)) return
      saveRun.mutate({
        cards: next.cards as unknown as Record<string, Record<string, never>>,
        queue: next.queue,
        sequence_pending: next.sequencePending,
        answered: next.answered,
        correct: next.correct,
      })
    },
    [saveRun],
  )

  const check = useCallback(() => {
    if (!ask || verdict) return
    setVerdict(
      ask.kind === 'sequence'
        ? gradeSequence(plan.sequence?.steps ?? [], answer)
        : gradeCard(cardsByKey[ask.cardKey], ask.rung, answer),
    )
  }, [answer, ask, cardsByKey, plan.sequence, verdict])

  const advance = useCallback(() => {
    if (!verdict) return
    if (ask?.kind === 'sequence' && !verdict.correct) setFinaleMissed(true)
    setQueue((current) => {
      const next = answerCurrent(current, verdict.correct)
      checkpoint(next)
      return next
    })
    setAnswer(null)
    setVerdict(null)
    setRound((value) => value + 1)
  }, [ask, checkpoint, verdict])

  const restart = useCallback(() => {
    reportedRef.current = false
    // Drop the server-side checkpoint too, or leaving mid-way through the
    // second run would offer to resume the first one.
    drillsApi.discardRun(plan.level.id).catch(() => undefined)
    setQueue(createQueue(plan.cards, Boolean(plan.sequence)))
    setBest({})
    setFinaleMissed(false)
    setAnswer(null)
    setVerdict(null)
    setRound(0)
  }, [plan.cards, plan.level.id, plan.sequence])

  const rail: DrillRailSegment[] = useMemo(() => {
    const segments: DrillRailSegment[] = plan.cards.map((planCard) => {
      const state = queue.cards[planCard.key]
      const total = state?.ladder.length ?? 1
      const cleared = state?.cleared ?? 0
      return {
        kind: 'command',
        key: planCard.key,
        command: planCard.command,
        intent: planCard.intent,
        cleared,
        best: Math.max(best[planCard.key] ?? 0, cleared),
        total,
        retired: state?.retired ?? false,
        mastered: cleared >= total,
        missed: state?.missed ?? false,
        active: ask?.kind === 'card' && ask.cardKey === planCard.key,
      }
    })
    // Without this the track would sit at a full bar while the closing
    // ordering question is still on screen - the one moment a progress
    // statement must not lie.
    if (plan.sequence) {
      const done = !queue.sequencePending
      segments.push({
        kind: 'finale',
        key: '__finale__',
        command: plan.sequence.label || 'The full run',
        intent: plan.sequence.task || '',
        cleared: done ? 1 : 0,
        best: done ? 1 : 0,
        total: 1,
        retired: done,
        mastered: done,
        missed: finaleMissed,
        active: ask?.kind === 'sequence',
      })
    }
    return segments
  }, [ask, best, finaleMissed, plan.cards, plan.sequence, queue.cards, queue.sequencePending])

  return {
    ask,
    card,
    sequence: plan.sequence,
    answer,
    setAnswer,
    verdict,
    check,
    advance,
    restart,
    finished,
    rail,
    round,
    accuracy: accuracy(queue),
    answered: queue.answered,
    shaky: shakyKeys(queue),
    savedProgress: report.data?.progress ?? null,
    saveFailed: report.isError,
    resumed,
  }
}

export type DrillSession = ReturnType<typeof useDrillSession>
