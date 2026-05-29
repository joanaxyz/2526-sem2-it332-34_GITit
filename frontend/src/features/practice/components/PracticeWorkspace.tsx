import { useRef, useState } from 'react'
import type { CSSProperties, PointerEvent as ReactPointerEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { GripHorizontal, GripVertical } from 'lucide-react'

import { ScenarioContextPanel } from '@/features/scenarios/components/ScenarioContextPanel'
import { ScenarioStatusHeader } from '@/features/scenarios/components/ScenarioStatusHeader'
import { CompletionCelebrationModal } from '@/features/practice/components/CompletionCelebrationModal'
import { ContextualFeedbackPanel } from '@/features/practice/components/ContextualFeedbackPanel'
import { ExpectedStatePanel } from '@/features/practice/components/ExpectedStatePanel'
import { LiveDagPanel } from '@/features/practice/components/LiveDagPanel'
import { ProjectStructurePanel } from '@/features/practice/components/ProjectStructurePanel'
import { ScenarioWorkspaceTour } from '@/features/practice/components/ScenarioWorkspaceTour'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { WorkspaceEditorOverlay } from '@/features/practice/components/WorkspaceEditorOverlay'
import { practiceApi } from '@/features/practice/api/practiceApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { hasSeenScenarioTour, markScenarioTourSeen } from '@/features/practice/utils/scenarioTour'
import { useCommandSubmission } from '@/features/practice/hooks/useCommandSubmission'
import { useScenarioSession } from '@/features/practice/hooks/useScenarioSession'
import { reviewApi } from '@/features/review/api/reviewApi'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { invalidateScenarioProgressQueries, syncScenarioSessionInCache, updateScenarioSessionCache } from '@/features/scenarios/utils/scenarioCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { PracticeWorkspaceSkeleton } from '@/shared/components/Skeleton'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

const DEFAULT_TERMINAL_RATIO = 0.28
const DEFAULT_DIAGRAM_RATIO = 0.52
const DEFAULT_TERMINAL_PANE_RATIO = 0.60
const MIN_TERMINAL_PANE_WIDTH = 544
const MIN_FEEDBACK_PANE_WIDTH = 288
const MAX_FEEDBACK_PANE_WIDTH = 480
const RESIZE_HANDLE_WIDTH = 6

function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

function constrainedTerminalPaneRatio(clientX: number, bounds: DOMRect) {
  const usableWidth = Math.max(bounds.width - RESIZE_HANDLE_WIDTH, 1)
  const rawRatio = (clientX - bounds.left) / bounds.width
  const minRatio = Math.max(
    MIN_TERMINAL_PANE_WIDTH / usableWidth,
    1 - MAX_FEEDBACK_PANE_WIDTH / usableWidth,
  )
  const maxRatio = 1 - MIN_FEEDBACK_PANE_WIDTH / usableWidth

  if (minRatio > maxRatio) {
    return clamp(rawRatio, 0.58, 0.86)
  }

  return clamp(rawRatio, minRatio, maxRatio)
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
  const { query, session, lines, feedback } = useScenarioSession(sessionId)
  const mutation = useCommandSubmission(sessionId, reviewMode)
  const [dismissedCompletionSessionId, setDismissedCompletionSessionId] = useState<number | null>(null)
  const [terminalRatio, setTerminalRatio] = useState(DEFAULT_TERMINAL_RATIO)
  const [diagramRatio, setDiagramRatio] = useState(DEFAULT_DIAGRAM_RATIO)
  const [terminalPaneRatio, setTerminalPaneRatio] = useState(DEFAULT_TERMINAL_PANE_RATIO)
  const [projectFilesOpen, setProjectFilesOpen] = useState(true)
  const [tourOpen, setTourOpen] = useState(false)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const [startOverConfirmOpen, setStartOverConfirmOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
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
      invalidateScenarioProgressQueries(queryClient)
      navigate(`/modules?module=${updatedSession.module.id}`)
    },
  })
  const nextLevelMutation = useMutation({
    mutationFn: () =>
      scenariosApi.startSession({
        difficulty_instance_id: session?.next_difficulty?.id ?? 0,
        source_entry_point: 'module_card',
      }),
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      invalidateScenarioProgressQueries(queryClient)
      if (session?.status === 'completed') setDismissedCompletionSessionId(session.id)
      navigate(`/practice/${next.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (difficultyInstanceId: number) => reviewApi.startReviewSession(difficultyInstanceId),
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      invalidateScenarioProgressQueries(queryClient)
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
      invalidateScenarioProgressQueries(queryClient)
      setDismissedCompletionSessionId(null)
      setStartOverConfirmOpen(false)
      navigate(`/practice/${next.id}`)
    },
  })
  const createFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!session) throw new Error('No session is available to update.')
      return practiceApi.createFile(session.id, input)
    },
    onSuccess: (updatedSession) => {
      updateScenarioSessionCache(queryClient, updatedSession)
    },
  })
  const writeFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!session) throw new Error('No session is available to update.')
      return practiceApi.writeFile(session.id, input)
    },
    onSuccess: (updatedSession) => {
      updateScenarioSessionCache(queryClient, updatedSession)
    },
  })
  const reviewableDifficulties = session?.reviewable_difficulties ?? []

  if (query.isLoading) return <PracticeWorkspaceSkeleton />
  if (query.isError) return <ErrorState title="Could not load scenario workspace" description={query.error.message} />
  if (!session) return <ErrorState title="Could not load scenario workspace" description="The API returned no session data." />

  // #region agent log
  fetch('http://127.0.0.1:7681/ingest/62fc7eb8-c151-4a74-bb87-4f3717466167',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'4d73ce'},body:JSON.stringify({sessionId:'4d73ce',location:'PracticeWorkspace.tsx:session-ready',message:'session loaded, rendering workspace',data:{hypothesisId:'B',sessionId:session.id,status:session.status,commitsCount:session.repository_state?.commits?.length??0},timestamp:Date.now(),runId:'post-fix'})}).catch(()=>{});
  // #endregion

  const tourKey = `${user?.id ?? 'guest'}:${session.scenario.id}`
  const shouldAutoOpenTour = dismissedTourKey !== tourKey && !hasSeenScenarioTour(user?.id)
  const isTourOpen = tourOpen || shouldAutoOpenTour

  function submit(command: string) {
    if (command.trim().toLowerCase() === 'exit') {
      setExitConfirmOpen(true)
      return
    }
    mutation.mutate(command, {
      onSuccess: (response) => {
        if (response.command_family === 'mergetool') {
          const snapshot = response.session.repository_state
          const requestedPaths = stringList(snapshot.operation_metadata?.last_mergetool_paths)
          const conflictPaths = snapshot.conflicts ?? []
          const nextPath = requestedPaths.find((path) => conflictPaths.includes(path)) ?? conflictPaths[0]
          if (nextPath) setWorkspaceEditorPath(nextPath)
        }
      },
    })
  }

  function startFreshAttempt() {
    retryMutation.mutate()
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
      setTerminalPaneRatio(constrainedTerminalPaneRatio(clientX, resizeBounds))
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
        onExit={() => session.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onOpenTour={() => setTourOpen(true)}
        onContinue={() => retryMutation.mutate()}
      />
      <main className="relative grid min-h-0 flex-1 grid-cols-[27rem_minmax(0,1fr)] gap-2 p-2 max-2xl:grid-cols-[26rem_minmax(0,1fr)] max-xl:grid-cols-[23rem_minmax(0,1fr)] max-lg:grid-cols-1 max-lg:overflow-auto">
        <aside
          className="grid min-h-0 gap-2 overflow-hidden max-lg:min-h-[44rem]"
          style={{
            gridTemplateRows: projectFilesOpen
              ? 'minmax(13rem, 0.72fr) minmax(18rem, 0.58fr)'
              : 'minmax(13rem, 1fr) auto',
          }}
          data-testid="workspace-sidebar"
          data-tour-target="scenario-brief"
        >
          <div className="min-h-0 overflow-y-auto app-scrollbar" data-testid="scenario-context-scroll">
            <ScenarioContextPanel session={session} />
          </div>

          <div className={cn('overflow-hidden', projectFilesOpen ? 'min-h-[14rem]' : '')} data-testid="project-structure-region">
            <ProjectStructurePanel
              snapshot={session.repository_state}
              className="h-full"
              selectedPath={workspaceEditorPath}
              createDisabled={session.status !== 'started' || createFileMutation.isPending}
              isOpen={projectFilesOpen}
              onToggle={() => setProjectFilesOpen((v) => !v)}
              onCreateFile={async (input) => {
                const updatedSession = await createFileMutation.mutateAsync(input)
                setWorkspaceEditorPath(input.path)
                return updatedSession
              }}
              onOpenFile={setWorkspaceEditorPath}
            />
          </div>
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
            data-testid="terminal-feedback-grid"
            className={cn(
              'grid min-h-0 min-w-0',
              session.scaffolding.contextual_feedback
                ? 'grid-cols-1 gap-2 xl:grid-cols-[minmax(34rem,var(--terminal-pane-size))_0.375rem_minmax(18rem,var(--feedback-pane-size))] xl:gap-0'
                : 'grid-cols-1',
            )}
            style={terminalGridStyle}
          >
            <div className="h-full min-h-0" data-tour-target="terminal">
              <TerminalPanel
                lines={lines}
                disabled={session.status !== 'started'}
                runDisabled={mutation.isPending}
                processing={mutation.isPending}
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
              <div className="h-full min-h-0 w-full min-w-0" data-tour-target="feedback">
                <ContextualFeedbackPanel session={session} feedback={feedback} />
              </div>
            ) : (
              <ContextualFeedbackPanel session={session} feedback={feedback} />
            )}
          </div>
        </section>
        <WorkspaceEditorOverlay
          snapshot={session.repository_state}
          filePath={workspaceEditorPath}
          open={Boolean(workspaceEditorPath)}
          writeDisabled={session.status !== 'started' || writeFileMutation.isPending}
          onClose={() => setWorkspaceEditorPath(null)}
          onWriteFile={(input) => writeFileMutation.mutateAsync(input)}
        />
      </main>
      <CompletionCelebrationModal
        open={(session.status === 'completed' || session.status === 'failed') && dismissedCompletionSessionId !== session.id}
        session={session}
        onClose={() => {
          setDismissedCompletionSessionId(session.id)
        }}
        onBackToModules={() => navigate(`/modules?module=${session.module.id}`)}
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
      <Modal
        open={exitConfirmOpen}
        title="Exit lesson?"
        className="w-full max-w-md"
        onClose={() => setExitConfirmOpen(false)}
      >
        <div className="space-y-5">
          <p className="text-sm leading-6 text-muted-foreground">
            Are you sure you want to exit? You cannot go back. Your progress will be discarded and this session will be marked as abandoned.
          </p>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" disabled={exitMutation.isPending} onClick={() => setExitConfirmOpen(false)}>
              Cancel
            </Button>
            <Button type="button" variant="destructive" disabled={exitMutation.isPending} onClick={() => exitMutation.mutate()}>
              {exitMutation.isPending ? 'Exiting…' : 'Exit Anyway'}
            </Button>
          </div>
        </div>
      </Modal>
      <Modal
        open={startOverConfirmOpen}
        title="Start fresh attempt?"
        className="w-full max-w-md"
        onClose={() => setStartOverConfirmOpen(false)}
      >
        <div className="space-y-5">
          <p className="text-sm leading-6 text-muted-foreground">
            This starts a fresh attempt and variant. Your current workspace state resets, and the terminal history from this attempt will not carry over.
          </p>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>Completed progress is not deleted.</li>
            <li>This action cannot be undone.</li>
          </ul>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" disabled={retryMutation.isPending} onClick={() => setStartOverConfirmOpen(false)}>
              Cancel
            </Button>
            <Button type="button" disabled={retryMutation.isPending} onClick={startFreshAttempt}>
              {retryMutation.isPending ? 'Starting' : 'Start fresh attempt'}
            </Button>
          </div>
        </div>
      </Modal>
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
