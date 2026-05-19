import { useQuery } from '@tanstack/react-query'
import { useCallback, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'

import { practiceApi } from '@/features/practice/api/practiceApi'
import type { ScenarioSession, TerminalLine } from '@/features/practice/types'

const bootLines: TerminalLine[] = []

export function useScenarioSession(sessionId: number) {
  const [sessionOverride, setSessionOverride] = useState<ScenarioSession | null>(null)
  const [feedbackOverride, setFeedbackOverride] = useState<{ sessionId: number; feedback: string } | null>(null)
  const [lineOverride, setLineOverride] = useState<{ sessionId: number; lines: TerminalLine[] } | null>(null)
  const query = useQuery({
    queryKey: ['scenario-session', sessionId],
    queryFn: () => practiceApi.getSession(sessionId),
    enabled: Number.isFinite(sessionId),
  })
  const baseLines = bootLines
  const setLines: Dispatch<SetStateAction<TerminalLine[]>> = useCallback(
    (value) => {
      setLineOverride((current) => {
        const currentLines = current?.sessionId === sessionId ? current.lines : baseLines
        const lines = typeof value === 'function' ? value(currentLines) : value
        return { sessionId, lines }
      })
    },
    [baseLines, sessionId],
  )
  const setFeedback = useCallback(
    (feedback: string) => setFeedbackOverride({ sessionId, feedback }),
    [sessionId],
  )

  const session = sessionOverride?.id === sessionId ? sessionOverride : (query.data ?? null)
  const lines = lineOverride?.sessionId === sessionId ? lineOverride.lines : baseLines
  const feedback =
    feedbackOverride?.sessionId === sessionId
      ? feedbackOverride.feedback
      : (query.data?.steps.at(-1)?.contextual_feedback ?? '')

  return { query, session, setSession: setSessionOverride, lines, setLines, feedback, setFeedback }
}
