import { useParams } from 'react-router-dom'

import { CommandCounter } from '@/features/scenarios/components/CommandCounter'
import { ScenarioContextPanel } from '@/features/scenarios/components/ScenarioContextPanel'
import { ScenarioStatusHeader } from '@/features/scenarios/components/ScenarioStatusHeader'
import { ContextualFeedbackPanel } from '@/features/practice/components/ContextualFeedbackPanel'
import { ExpectedStatePanel } from '@/features/practice/components/ExpectedStatePanel'
import { LiveDagPanel } from '@/features/practice/components/LiveDagPanel'
import { SessionOutcomeBanner } from '@/features/practice/components/SessionOutcomeBanner'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { useCommandSubmission } from '@/features/practice/hooks/useCommandSubmission'
import { useScenarioSession } from '@/features/practice/hooks/useScenarioSession'
import { LoadingState } from '@/shared/components/LoadingState'

export function PracticeWorkspace({ reviewMode = false }: { reviewMode?: boolean }) {
  const params = useParams()
  const sessionId = Number(params.sessionId)
  const { query, session, setSession, lines, setLines, feedback, setFeedback } = useScenarioSession(sessionId)
  const mutation = useCommandSubmission(sessionId, reviewMode)

  if (query.isLoading || !session) return <LoadingState label="Loading scenario workspace" />

  function submit(command: string) {
    setLines((items) => [...items, { id: crypto.randomUUID(), kind: 'input', text: command }])
    mutation.mutate(command, {
      onSuccess: (response) => {
        setSession(response.session)
        setFeedback(response.step.contextual_feedback)
        setLines((items) => [
          ...items,
          {
            id: crypto.randomUUID(),
            kind: response.session.status === 'completed' ? 'success' : 'output',
            text: response.step.terminal_output,
          },
        ])
      },
      onError: (error) => {
        setLines((items) => [...items, { id: crypto.randomUUID(), kind: 'warning', text: error.message }])
      },
    })
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <ScenarioStatusHeader session={session} />
      <main className="grid min-h-0 flex-1 grid-cols-[20rem_minmax(0,1fr)_22rem] gap-3 p-3 max-xl:grid-cols-[18rem_minmax(0,1fr)] max-lg:grid-cols-1 max-lg:overflow-auto">
        <aside className="flex min-h-0 flex-col gap-3">
          <ScenarioContextPanel session={session} />
          <CommandCounter session={session} />
          <SessionOutcomeBanner session={session} />
        </aside>
        <section className="grid min-h-0 grid-rows-[minmax(15rem,0.8fr)_minmax(18rem,1fr)] gap-3">
          <LiveDagPanel snapshot={session.repository_state} />
          <TerminalPanel lines={lines} disabled={session.status !== 'started' || mutation.isPending} onCommand={submit} />
        </section>
        <aside className="flex min-h-0 flex-col gap-3 max-xl:col-span-2 max-lg:col-span-1">
          <ExpectedStatePanel session={session} />
          <ContextualFeedbackPanel session={session} feedback={feedback} />
        </aside>
      </main>
    </div>
  )
}
