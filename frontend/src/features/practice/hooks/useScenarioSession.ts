import { useQuery } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'

import { practiceApi } from '@/features/practice/api/practiceApi'
import type { ScenarioSession, TerminalLine } from '@/features/practice/types'
import { queryKeys } from '@/shared/api/queryKeys'

const bootLines: TerminalLine[] = []

function terminalLinesFromSession(session: ScenarioSession): TerminalLine[] {
  const lines = [...bootLines]
  for (const step of session.steps) {
    lines.push(
      { id: `input-${step.id}`, kind: 'input', text: step.command_text },
      {
        id: `output-${step.id}`,
        kind: step.result_category === 'TargetMatched' ? 'success' : 'output',
        text: step.terminal_output,
      },
    )
  }
  return lines
}

export function useScenarioSession(sessionId: number) {
  const [lineOverride, setLineOverride] = useState<{ sessionId: number; lines: TerminalLine[] } | null>(null)
  const query = useQuery({
    queryKey: queryKeys.scenarioSession(sessionId),
    queryFn: () => practiceApi.getSession(sessionId),
    enabled: Number.isFinite(sessionId),
  })
  const baseLines = useMemo(() => (query.data ? terminalLinesFromSession(query.data) : bootLines), [query.data])
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
  const resetLocalSessionState = useCallback(() => {
    setLineOverride(null)
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(resetLocalSessionState, 0)
    return () => window.clearTimeout(timeoutId)
  }, [resetLocalSessionState, sessionId])

  const session = query.data ?? null
  const lines = lineOverride?.sessionId === sessionId ? lineOverride.lines : baseLines
  const feedback = query.data?.steps.at(-1)?.contextual_feedback ?? ''

  return {
    query,
    session,
    lines,
    setLines,
    feedback,
    resetLocalSessionState,
  }
}
