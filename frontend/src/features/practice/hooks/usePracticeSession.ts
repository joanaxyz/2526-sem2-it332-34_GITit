import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo } from 'react'

import { practiceApi } from '@/features/practice/api/practiceApi'
import { isEphemeralStep } from '@/features/practice/hooks/useCommandSubmission'
import type { PracticeSession, TerminalLine } from '@/features/practice/types'
import { clearSessionBootstrap, readSessionBootstrap } from '@/features/scenarios/utils/sessionBootstrap'
import { queryKeys } from '@/shared/api/queryKeys'

const bootLines: TerminalLine[] = []

function terminalLinesFromSession(session: PracticeSession): TerminalLine[] {
  const lines = [...bootLines]
  for (const step of session.steps ?? []) {
    lines.push(
      { id: `input-${step.id}`, kind: 'input', text: step.command_text },
      {
        id: `output-${step.id}`,
        kind:
          step.result_category === 'TargetMatched'
            ? 'success'
            : step.result_category === 'Error'
              ? 'warning'
              : 'output',
        text:
          step.result_category === 'Pending'
            ? '…'
            : step.terminal_output,
      },
    )
  }
  return lines
}

export function usePracticeSession(sessionId: number) {
  const queryClient = useQueryClient()
  const bootstrapSession = Number.isFinite(sessionId) ? readSessionBootstrap(sessionId) : undefined
  const cachedSession = Number.isFinite(sessionId)
    ? queryClient.getQueryData<PracticeSession>(queryKeys.practiceSession(sessionId))
    : undefined
  const initialSession = cachedSession ?? bootstrapSession

  const query = useQuery({
    queryKey: queryKeys.practiceSession(sessionId),
    queryFn: async () => {
      const session = await practiceApi.getSession(sessionId)
      clearSessionBootstrap(sessionId)
      return session
    },
    enabled: Number.isFinite(sessionId),
    initialData: initialSession,
    staleTime: 30_000,
  })

  const session = query.data ?? null
  const lines = useMemo(() => (session ? terminalLinesFromSession(session) : bootLines), [session])
  const feedback = session?.steps?.filter((step) => !isEphemeralStep(step)).at(-1)?.contextual_feedback ?? ''

  return {
    query,
    session,
    lines,
    feedback,
  }
}
