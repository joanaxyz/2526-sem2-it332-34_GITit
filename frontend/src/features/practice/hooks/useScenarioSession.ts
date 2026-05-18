import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'

import { practiceApi } from '@/features/practice/api/practiceApi'
import type { ScenarioSession, TerminalLine } from '@/features/practice/types'

export function useScenarioSession(sessionId: number) {
  const [session, setSession] = useState<ScenarioSession | null>(null)
  const [feedback, setFeedback] = useState('')
  const [lines, setLines] = useState<TerminalLine[]>([
    { id: 'boot-1', kind: 'system', text: 'Repository state loaded. Command-count policy active.' },
    { id: 'boot-2', kind: 'output', text: 'Inspect the DAG and scenario context before changing state.' },
  ])
  const query = useQuery({
    queryKey: ['scenario-session', sessionId],
    queryFn: () => practiceApi.getSession(sessionId),
    enabled: Number.isFinite(sessionId),
  })

  useEffect(() => {
    if (query.data) setSession(query.data)
  }, [query.data])

  return { query, session: session ?? query.data ?? null, setSession, lines, setLines, feedback, setFeedback }
}
