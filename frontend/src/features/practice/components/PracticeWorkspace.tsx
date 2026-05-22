import { useRef, useState } from 'react'
import type { CSSProperties, PointerEvent as ReactPointerEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { GripHorizontal, GripVertical } from 'lucide-react'

import { CommandCounter } from '@/features/scenarios/components/CommandCounter'
import { ScenarioContextPanel } from '@/features/scenarios/components/ScenarioContextPanel'
import { ScenarioStatusHeader } from '@/features/scenarios/components/ScenarioStatusHeader'
import { CompletionCelebrationModal } from '@/features/practice/components/CompletionCelebrationModal'
import { ContextualFeedbackPanel } from '@/features/practice/components/ContextualFeedbackPanel'
import { ExpectedStatePanel } from '@/features/practice/components/ExpectedStatePanel'
import { InspectionAnswerPanel } from '@/features/practice/components/InspectionAnswerPanel'
import { LiveDagPanel } from '@/features/practice/components/LiveDagPanel'
import { ProjectStructurePanel } from '@/features/practice/components/ProjectStructurePanel'
import { ScenarioWorkspaceTour } from '@/features/practice/components/ScenarioWorkspaceTour'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { practiceApi } from '@/features/practice/api/practiceApi'
import { hasSeenScenarioTour, markScenarioTourSeen } from '@/features/practice/utils/scenarioTour'
import { useCommandSubmission } from '@/features/practice/hooks/useCommandSubmission'
import { useScenarioSession } from '@/features/practice/hooks/useScenarioSession'
import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { ErrorState } from '@/shared/components/ErrorState'
import { PracticeWorkspaceSkeleton } from '@/shared/components/Skeleton'
import { cn } from '@/shared/utils/cn'

const DEFAULT_TERMINAL_RATIO = 0.28
const DEFAULT_DIAGRAM_RATIO = 0.52
const DEFAULT_TERMINAL_PANE_RATIO = 0.76

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

function ResizeHandle({
  label,
  orientation,
  className,
  onPointerDown,
}: {
  label: string
  orientation: 'horizontal' | 'vertical'
  className?: string
  onPointerDown: (event: ReactPointerEvent<HTMLDivElement>) => void
}) {
  const isVertical = orientation === 'vertical'
  const Icon = isVertical ? GripVertical : GripHorizontal

  return (
    <div
      aria-label={label}
      aria-orientation={orientation}
      className={cn(
        'group relative z-10 flex shrink-0 items-center justify-center',
        isVertical ? 'h-full cursor-col-resize px-1' : 'w-full cursor-row-resize py-1',
        className,
      )}
      role="separator"
      onPointerDown={onPointerDown}
    >
      <span
        className={cn(
          'rounded-full bg-border/70 transition-colors group-hover:bg-primary/70 group-active:bg-primary',
          isVertical ? 'h-full w-px' : 'h-px w-full',
        )}
      />
      <span className="absolute grid size-5 place-items-center rounded-full border border-border bg-background/95 text-muted-foreground shadow-sm transition-colors group-hover:border-primary/60 group-hover:text-primary group-active:text-primary">
        <Icon className="size-3" />
      </span>
    </div>
  )
}

export function PracticeWorkspace({ reviewMode = false }: { reviewMode?: boolean }) {
  const params = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const sessionId = Number(params.sessionId)
  const { query, session, setSession, lines, setLines, feedback, setFeedback } = useScenarioSession(sessionId)
  const mutation = useCommandSubmission(sessionId, reviewMode)
  const inspectionAnswerMutation = useMutation({
    mutationFn: (answer: Record<string, unknown>) => {
      if (!session) throw new Error('No session is available.')
      return practiceApi.submitInspectionAnswer(session.id, answer)
    },
    onSuccess: (response) => {
      setSession(response.session)
      syncScenarioSessionInCache(queryClient, response.session)
      void queryClient.invalidateQueries({ queryKey: ['units'] })
      setLines((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          kind: response.session.status === 'completed' ? 'success' : 'warning',
          text: response.summary,
        },
      ])
    },
    onError: (error) => {
      setLines((items) => [...items, { id: crypto.randomUUID(), kind: 'warning', text: error.message }])
    },
  })
  const [dismissedCompletionSessionId, setDismissedCompletionSessionId] = useState<number | null>(null)
  const [terminalRatio, setTerminalRatio] = useState(DEFAULT_TERMINAL_RATIO)
  const [diagramRatio, setDiagramRatio] = useState(DEFAULT_DIAGRAM_RATIO)
  const [terminalPaneRatio, setTerminalPaneRatio] = useState(DEFAULT_TERMINAL_PANE_RATIO)
  const [tourOpen, setTourOpen] = useState(false)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const user = useAuthStore((state) => state.user)
  const workspaceGridRef = useRef<HTMLElement>(null)
  const diagramGridRef = useRef<HTMLDivElement>(null)
  const terminalGridRef = useRef<HTMLDivElement>(null)
  const exitMutation = useMutation({
    mutationFn: () => {
      if (!session) throw new Error('No session is available to exit.')
      if (session.status === 'started') return scenariosApi.abandonSession(session.id)
      return Promise.resolve(session)
    },
    onSuccess: (updatedSession) => {
      syncScenarioSessionInCache(queryClient, updatedSession)
      void queryClient.invalidateQueries({ queryKey: ['units'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      navigate(`/units?unit=${updatedSession.unit.id}`)
    },
  })
  const nextLevelMutation = useMutation({
    mutationFn: () =>
      scenariosApi.startSession({
        difficulty_instance_id: session?.next_difficulty?.id ?? 0,
        source_entry_point: 'unit_card',
      }),
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      void queryClient.invalidateQueries({ queryKey: ['units'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      if (session?.status === 'completed') setDismissedCompletionSessionId(session.id)
      navigate(`/practice/${next.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (difficultyInstanceId: number) => reviewApi.startReviewSession(difficultyInstanceId),
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      void queryClient.invalidateQueries({ queryKey: ['units'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      if (session?.status === 'completed') setDismissedCompletionSessionId(session.id)
      navigate(`/review/${next.id}`)
    },
  })
  const retryMutation = useMutation({
    mutationFn: () => {
      if (!session) throw new Error('No session is available to retry.')
      return scenariosApi.retrySession(session.id)
    },
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      void queryClient.invalidateQueries({ queryKey: ['units'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      setDismissedCompletionSessionId(null)
      navigate(`/practice/${next.id}`)
    },
  })
  const unitScenariosQuery = useQuery({
    queryKey: ['unit-scenarios', session?.unit.id],
    queryFn: () => scenariosApi.listForUnit(session!.unit.id),
    enabled: !!session?.unit.id,
    staleTime: 5 * 60 * 1000,
  })
  const currentScenario = unitScenariosQuery.data?.find((s) => s.id === session?.scenario.id)
  const reviewableDifficulties = currentScenario?.difficulties.filter(
    (d) => d.review_available && d.difficulty !== session?.difficulty
  ) ?? []

  if (query.isLoading) return <PracticeWorkspaceSkeleton />
  if (query.isError) return <ErrorState title="Could not load scenario workspace" description={query.error.message} />
  if (!session) return <ErrorState title="Could not load scenario workspace" description="The API returned no session data." />

  const tourKey = `${user?.id ?? 'guest'}:${session.scenario.id}`
  const shouldAutoOpenTour = dismissedTourKey !== tourKey && !hasSeenScenarioTour(user?.id)
  const isTourOpen = tourOpen || shouldAutoOpenTour

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

  function beginTerminalResize(event: ReactPointerEvent<HTMLDivElement>) {
    const bounds = workspaceGridRef.current?.getBoundingClientRect()
    if (!bounds) return
    const resizeBounds = bounds
    event.preventDefault()

    function update(clientY: number) {
      const bottomHeight = resizeBounds.bottom - clientY
      setTerminalRatio(clamp(bottomHeight / resizeBounds.height, 0.22, 0.58))
    }

    function handlePointerMove(moveEvent: PointerEvent) {
      update(moveEvent.clientY)
    }

    function handlePointerUp() {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.body.style.cursor = 'row-resize'
    document.body.style.userSelect = 'none'
    update(event.clientY)
    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', handlePointerUp, { once: true })
  }

  function beginDiagramResize(event: ReactPointerEvent<HTMLDivElement>) {
    const bounds = diagramGridRef.current?.getBoundingClientRect()
    if (!bounds) return
    const resizeBounds = bounds
    event.preventDefault()

    function update(clientX: number) {
      setDiagramRatio(clamp((clientX - resizeBounds.left) / resizeBounds.width, 0.34, 0.66))
    }

    function handlePointerMove(moveEvent: PointerEvent) {
      update(moveEvent.clientX)
    }

    function handlePointerUp() {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    update(event.clientX)
    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', handlePointerUp, { once: true })
  }

  function beginTerminalPaneResize(event: ReactPointerEvent<HTMLDivElement>) {
    const bounds = terminalGridRef.current?.getBoundingClientRect()
    if (!bounds) return
    const resizeBounds = bounds
    event.preventDefault()

    function update(clientX: number) {
      setTerminalPaneRatio(clamp((clientX - resizeBounds.left) / resizeBounds.width, 0.52, 0.86))
    }

    function handlePointerMove(moveEvent: PointerEvent) {
      update(moveEvent.clientX)
    }

    function handlePointerUp() {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', handlePointerUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    update(event.clientX)
    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', handlePointerUp, { once: true })
  }

  const workspaceGridStyle = {
    gridTemplateRows: `minmax(14rem, ${1 - terminalRatio}fr) 0.375rem minmax(10rem, ${terminalRatio}fr)`,
  }
  const diagramGridStyle = {
    '--live-dag-size': `${diagramRatio}fr`,
    '--expected-dag-size': `${1 - diagramRatio}fr`,
  } as CSSProperties
  const terminalGridStyle = {
    '--terminal-pane-size': `${terminalPaneRatio}fr`,
    '--feedback-pane-size': `${1 - terminalPaneRatio}fr`,
  } as CSSProperties

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      <ScenarioStatusHeader
        session={session}
        isExiting={exitMutation.isPending}
        isRetrying={retryMutation.isPending}
        onExit={() => exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onOpenTour={() => setTourOpen(true)}
        onContinue={() => retryMutation.mutate()}
      />
      <main className="grid min-h-0 flex-1 grid-cols-[18rem_minmax(0,1fr)] gap-2 p-2 max-2xl:grid-cols-[17rem_minmax(0,1fr)] max-xl:grid-cols-[16rem_minmax(0,1fr)] max-lg:grid-cols-1 max-lg:overflow-auto">
        <aside className="flex min-h-0 flex-col gap-2" data-tour-target="scenario-brief">
          <ScenarioContextPanel session={session} />
          {!reviewMode ? <CommandCounter session={session} /> : null}
          {!reviewMode && session.completion_type === 'inspection' ? (
            <InspectionAnswerPanel
              disabled={session.status !== 'started'}
              isSubmitting={inspectionAnswerMutation.isPending}
              session={session}
              onSubmit={(answer) => inspectionAnswerMutation.mutate(answer)}
            />
          ) : null}
          <ProjectStructurePanel snapshot={session.repository_state} />
        </aside>
        <section
          ref={workspaceGridRef}
          className="grid min-h-0 gap-0 max-lg:min-h-[56rem]"
          style={workspaceGridStyle}
        >
          <div
            ref={diagramGridRef}
            className="grid min-h-0 grid-cols-1 gap-2 xl:grid-cols-[minmax(0,var(--live-dag-size))_0.375rem_minmax(0,var(--expected-dag-size))] xl:gap-0"
            style={diagramGridStyle}
          >
            <div className="h-full min-h-0" data-tour-target="live-dag">
              <LiveDagPanel
                snapshot={session.repository_state}
                className="flex h-full min-h-0 flex-col"
                contentClassName="h-full min-h-0 flex-1"
              />
            </div>
            <ResizeHandle
              label="Resize diagrams"
              orientation="vertical"
              className="hidden xl:flex"
              onPointerDown={beginDiagramResize}
            />
            <div className="h-full min-h-0" data-tour-target="expected-state">
              <ExpectedStatePanel session={session} />
            </div>
          </div>
          <ResizeHandle
            label="Resize terminal height"
            orientation="horizontal"
            onPointerDown={beginTerminalResize}
          />
          <div
            ref={terminalGridRef}
            className={cn(
              'grid min-h-0',
              session.scaffolding.contextual_feedback
                ? 'grid-cols-1 gap-2 xl:grid-cols-[minmax(0,var(--terminal-pane-size))_0.375rem_minmax(18rem,var(--feedback-pane-size))] xl:gap-0'
                : 'grid-cols-1',
            )}
            style={terminalGridStyle}
          >
            <div className="h-full min-h-0" data-tour-target="terminal">
              <TerminalPanel
                lines={lines}
                disabled={session.status !== 'started' || mutation.isPending}
                className="h-full"
                onCommand={submit}
              />
            </div>
            {session.scaffolding.contextual_feedback ? (
              <ResizeHandle
                label="Resize terminal and feedback"
                orientation="vertical"
                className="hidden xl:flex"
                onPointerDown={beginTerminalPaneResize}
              />
            ) : null}
            {session.scaffolding.contextual_feedback ? (
              <div className="h-full min-h-0" data-tour-target="feedback">
                <ContextualFeedbackPanel session={session} feedback={feedback} />
              </div>
            ) : (
              <ContextualFeedbackPanel session={session} feedback={feedback} />
            )}
          </div>
        </section>
      </main>
      <CompletionCelebrationModal
        open={(session.status === 'completed' || session.status === 'failed') && dismissedCompletionSessionId !== session.id}
        session={session}
        onClose={() => {
          setDismissedCompletionSessionId(session.id)
        }}
        onBackToUnits={() => navigate(`/units?unit=${session.unit.id}`)}
        onRetry={() => retryMutation.mutate()}
        onContinue={() => retryMutation.mutate()}
        onReviewDifficulty={(difficulty) => reviewMutation.mutate(difficulty.id)}
        previousDifficulties={reviewableDifficulties}
        isReviewing={reviewMutation.isPending}
        isRetrying={retryMutation.isPending}
        isContinuing={retryMutation.isPending}
        onNextLevel={session.next_difficulty ? () => nextLevelMutation.mutate() : undefined}
        isStartingNextLevel={nextLevelMutation.isPending}
        nextDifficultyLabel={
          session.next_difficulty
            ? session.next_difficulty.difficulty.charAt(0).toUpperCase() + session.next_difficulty.difficulty.slice(1)
            : null
        }
      />
      {isTourOpen ? (
        <ScenarioWorkspaceTour
          key={tourKey}
          session={session}
          onClose={() => {
            markScenarioTourSeen(user?.id)
            setDismissedTourKey(tourKey)
            setTourOpen(false)
          }}
        />
      ) : null}
    </div>
  )
}
