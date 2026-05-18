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
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

export function PracticeWorkspace({ reviewMode = false }: { reviewMode?: boolean }) {
  const params = useParams()
  const sessionId = Number(params.sessionId)
  const { query, session, setSession, lines, setLines, feedback, setFeedback } = useScenarioSession(sessionId)
  const mutation = useCommandSubmission(sessionId, reviewMode)

  if (query.isLoading) return <LoadingState label="Loading scenario workspace" />
  if (query.isError) return <ErrorState title="Could not load scenario workspace" description={query.error.message} />
  if (!session) return <ErrorState title="Could not load scenario workspace" description="The API returned no session data." />

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
      <main className="grid min-h-0 flex-1 grid-cols-[18rem_minmax(0,1fr)] gap-2 p-2 max-2xl:grid-cols-[17rem_minmax(0,1fr)] max-xl:grid-cols-[16rem_minmax(0,1fr)] max-lg:grid-cols-1 max-lg:overflow-auto">
        <aside className="flex min-h-0 flex-col gap-2">
          <ScenarioContextPanel session={session} />
          <CommandCounter session={session} />
          <SessionOutcomeBanner session={session} />
        </aside>
        <section className="grid min-h-0 grid-rows-[minmax(0,1fr)_minmax(10rem,0.36fr)] gap-2 max-lg:min-h-[56rem]">
          <div className="grid min-h-0 grid-cols-[minmax(0,1.04fr)_minmax(0,0.96fr)] gap-2 max-xl:grid-cols-1">
            <LiveDagPanel
              snapshot={session.repository_state}
              className="flex min-h-0 flex-col"
              contentClassName="h-full min-h-0 flex-1"
            />
            <ExpectedStatePanel session={session} />
          </div>
          <div
            className={cn(
              'grid min-h-0 gap-2',
              session.scaffolding.contextual_feedback
                ? 'grid-cols-[minmax(0,1.55fr)_minmax(20rem,0.65fr)] max-xl:grid-cols-1'
                : 'grid-cols-1',
            )}
          >
            <TerminalPanel lines={lines} disabled={session.status !== 'started' || mutation.isPending} onCommand={submit} />
            <ContextualFeedbackPanel session={session} feedback={feedback} />
          </div>
        </section>
      </main>
    </div>
  )
}
