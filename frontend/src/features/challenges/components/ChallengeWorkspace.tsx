import { useRef, useState } from 'react'
import type { CSSProperties, PointerEvent as ReactPointerEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { GripHorizontal, GripVertical } from 'lucide-react'
import { Toaster } from 'sonner'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { challengeRunsApi } from '@/features/challenges/api/challengeRunsApi'
import { ChallengeStatusHeader } from '@/features/challenges/components/ChallengeStatusHeader'
import { ChallengeOutcomeModal } from '@/features/challenges/components/ChallengeOutcomeModal'
import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import { useChallengeRun } from '@/features/challenges/hooks/useChallengeRun'
import {
  invalidatePracticeProgressQueries,
  syncChallengeRunInCache,
  updateChallengeRunCache,
} from '@/features/challenges/utils/challengeRunCache'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { PracticeContextPanel } from '@/shared/practice/components/PracticeContextPanel'
import { ContextualFeedbackPanel } from '@/shared/practice/components/ContextualFeedbackPanel'
import { LiveDagPanel } from '@/shared/practice/components/LiveDagPanel'
import { ProjectStructurePanel } from '@/shared/practice/components/ProjectStructurePanel'
import { ChallengeWorkspaceTour } from '@/shared/practice/components/PracticeWorkspaceTour'
import { TerminalPanel } from '@/shared/practice/components/TerminalPanel'
import { WorkspaceEditorOverlay } from '@/shared/practice/components/WorkspaceEditorOverlay'
import { useScaffolding } from '@/shared/practice/scaffolding/useScaffolding'
import { hasSeenPracticeTour, markPracticeTourSeen } from '@/shared/practice/utils/practiceTour'
import type { ChallengeRun } from '@/shared/practice/types'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'
import { usePersistentState } from '@/shared/utils/persistentState'

const DEFAULT_TERMINAL_RATIO = 0.28
const DEFAULT_TARGET_DIAGRAM_RATIO = 0.5
const DEFAULT_TERMINAL_PANE_RATIO = 0.60
const MIN_TERMINAL_PANE_WIDTH = 544
const MIN_FEEDBACK_PANE_WIDTH = 288
const MAX_FEEDBACK_PANE_WIDTH = 480
const RESIZE_HANDLE_WIDTH = 6

// Persisted workspace layout. One shared zoom key keeps both DAG panels at the
// learner's chosen zoom across commands and sessions (see LiveDagPanel).
const TERMINAL_RATIO_KEY = 'workspace:terminal-ratio'
const TARGET_DIAGRAM_RATIO_KEY = 'workspace:target-diagram-ratio'
const TERMINAL_PANE_RATIO_KEY = 'workspace:terminal-pane-ratio'
const PROJECT_FILES_OPEN_KEY = 'workspace:project-files-open'
const DAG_ZOOM_KEY = 'workspace:dag-zoom'

function ratioSanitizer(min: number, max: number, fallback: number) {
  return (value: number) =>
    typeof value === 'number' && Number.isFinite(value) ? clamp(value, min, max) : fallback
}

function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

function towerUrlForRun(run: Pick<ChallengeRun, 'storey'>) {
  return `/tower?storey=${run.storey.id}`
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

export function ChallengeWorkspace() {
  const params = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const runId = Number(params.runId)
  const { query, run, lines, feedback } = useChallengeRun(runId)
  const mutation = useChallengeCommandSubmission(runId)
  const { clearToast, evaluateAndNotify } = useScaffolding(runId)
  const [dismissedCompletionRunId, setDismissedCompletionRunId] = useState<number | null>(null)
  const [terminalRatio, setTerminalRatio] = usePersistentState(
    TERMINAL_RATIO_KEY,
    DEFAULT_TERMINAL_RATIO,
    ratioSanitizer(0.22, 0.58, DEFAULT_TERMINAL_RATIO),
  )
  const [targetDiagramRatio, setTargetDiagramRatio] = usePersistentState(
    TARGET_DIAGRAM_RATIO_KEY,
    DEFAULT_TARGET_DIAGRAM_RATIO,
    ratioSanitizer(0.34, 0.66, DEFAULT_TARGET_DIAGRAM_RATIO),
  )
  const [terminalPaneRatio, setTerminalPaneRatio] = usePersistentState(
    TERMINAL_PANE_RATIO_KEY,
    DEFAULT_TERMINAL_PANE_RATIO,
    ratioSanitizer(0.4, 0.92, DEFAULT_TERMINAL_PANE_RATIO),
  )
  const [projectFilesOpen, setProjectFilesOpen] = usePersistentState(PROJECT_FILES_OPEN_KEY, true)
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
      if (!run) throw new Error('No challenge run is available to exit.')
      if (run.status === 'started') return challengesApi.finishChallengeRun(run.id)
      return Promise.resolve(run)
    },
    onSuccess: (updatedRun) => {
      syncChallengeRunInCache(queryClient, updatedRun)
      invalidatePracticeProgressQueries(queryClient)
      navigate(towerUrlForRun(updatedRun))
    },
  })
  // Starts a fresh run on any level — the "Next level" CTA and the completion
  // modal's level navigator both route through here, so jumping to a lower level
  // works exactly like advancing to the next one.
  const startLevelMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId),
    onSuccess: (next) => {
      syncChallengeRunInCache(queryClient, next)
      invalidatePracticeProgressQueries(queryClient)
      if (run?.status === 'completed') setDismissedCompletionRunId(run.id)
      navigate(`/challenge-runs/${next.id}`)
    },
  })
  // Replaying a free-play (review) run starts a fresh uncounted run on the same
  // level — never the retry endpoint, which rejects non-primary runs. This keeps
  // "Play again" working for already-completed levels without touching progress.
  const reviewMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId, { review: true }),
    onSuccess: (next) => {
      syncChallengeRunInCache(queryClient, next)
      invalidatePracticeProgressQueries(queryClient)
      setDismissedCompletionRunId(null)
      navigate(`/challenge-runs/${next.id}`)
    },
  })
  const retryMutation = useMutation({
    mutationFn: () => {
      if (!run) throw new Error('No challenge run is available to retry.')
      return challengesApi.retryChallengeRun(run.id)
    },
    onSuccess: (next) => {
      syncChallengeRunInCache(queryClient, next)
      invalidatePracticeProgressQueries(queryClient)
      setDismissedCompletionRunId(null)
      setStartOverConfirmOpen(false)
      navigate(`/challenge-runs/${next.id}`)
    },
  })
  const createFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.createFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })
  const writeFileMutation = useMutation({
    mutationFn: (input: { path: string; content: string }) => {
      if (!run) throw new Error('No challenge run is available to update.')
      return challengeRunsApi.writeFile(run.id, input)
    },
    onSuccess: (updatedRun) => {
      updateChallengeRunCache(queryClient, updatedRun)
    },
  })
  if (query.isLoading) {
    return (
      <LoadingState
        description="Preparing the repository, terminal, and challenge workspace."
        label="Loading challenge"
        variant="screen"
      />
    )
  }
  if (query.isError) return <ErrorState title="Could not load challenge workspace" description={query.error.message} />
  if (!run) return <ErrorState title="Could not load challenge workspace" description="The API returned no run data." />

  const tourKey = `${user?.id ?? 'guest'}:challenge:${run.challenge.level_id}`
  const shouldAutoOpenTour = dismissedTourKey !== tourKey && !hasSeenPracticeTour(user?.id)
  const isTourOpen = tourOpen || shouldAutoOpenTour

  function submit(command: string) {
    if (command.trim().toLowerCase() === 'exit') {
      setExitConfirmOpen(true)
      return
    }

    clearToast()

    mutation.mutate(command, {
      onSuccess: (response) => {
        if (response.command_family === 'mergetool') {
          const snapshot = response.run.repository_state
          const requestedPaths = stringList(snapshot.operation_metadata?.last_mergetool_paths)
          const conflictPaths = snapshot.conflicts ?? []
          const nextPath = requestedPaths.find((path) => conflictPaths.includes(path)) ?? conflictPaths[0]
          if (nextPath) setWorkspaceEditorPath(nextPath)
        }

        if (!response.run.review_mode) {
          const updatedRun = queryClient.getQueryData<ChallengeRun>(queryKeys.challengeRun(runId))
          if (updatedRun) {
            evaluateAndNotify(
              updatedRun,
              response.step.command_classification,
              () => {
                setExitConfirmOpen(true)
              },
            )
          }
        }
      },
    })
  }

  function startFreshAttempt() {
    retryMutation.mutate()
  }

  // "Play again" routes by mode: a free-play (review) run can't use the retry
  // endpoint, so it starts a fresh uncounted run; a primary run keeps the retry
  // flow that carries prior-attempt context.
  function playAgain() {
    if (run?.review_mode) {
      reviewMutation.mutate(run.challenge.level_id)
    } else {
      retryMutation.mutate()
    }
  }

  const isReplaying = retryMutation.isPending || reviewMutation.isPending

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
      setTargetDiagramRatio(clamp((clientX - resizeBounds.left) / resizeBounds.width, 0.34, 0.66))
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
  const hasTargetDiagram = Boolean(run.scaffolding.expected_state && run.expected_state)
  const diagramGridStyle = {
    '--live-dag-size': `${targetDiagramRatio}fr`,
    '--expected-dag-size': `${1 - targetDiagramRatio}fr`,
  } as CSSProperties
  const terminalGridStyle = {
    '--terminal-pane-size': `${terminalPaneRatio}fr`,
    '--feedback-pane-size': `${1 - terminalPaneRatio}fr`,
  } as CSSProperties

  return (
    <div className="workspace-bg flex h-screen flex-col overflow-hidden">
      <Toaster position="bottom-right" expand={false} />
      <ChallengeStatusHeader
        run={run}
        isExiting={exitMutation.isPending}
        isRetrying={isReplaying}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onOpenTour={() => setTourOpen(true)}
        onContinue={() => retryMutation.mutate()}
        onReplay={() => reviewMutation.mutate(run.challenge.level_id)}
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
          data-tour-target="practice-brief"
        >
          <div className="min-h-0 overflow-y-auto app-scrollbar" data-testid="practice-context-scroll">
            <PracticeContextPanel run={run} />
          </div>

          <div className={cn('overflow-hidden', projectFilesOpen ? 'min-h-[14rem]' : '')} data-testid="project-structure-region">
            <ProjectStructurePanel
              snapshot={run.repository_state}
              className="h-full"
              selectedPath={workspaceEditorPath}
              createDisabled={run.status !== 'started' || createFileMutation.isPending}
              isOpen={projectFilesOpen}
              onToggle={() => setProjectFilesOpen((v) => !v)}
              onCreateFile={async (input) => {
                const updatedRun = await createFileMutation.mutateAsync(input)
                setWorkspaceEditorPath(input.path)
                return updatedRun
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
            className={cn(
              'grid min-h-0 grid-cols-1 gap-2',
              hasTargetDiagram
                ? 'xl:grid-cols-[minmax(0,var(--live-dag-size))_0.375rem_minmax(0,var(--expected-dag-size))] xl:gap-0'
                : 'xl:grid-cols-1',
            )}
            style={diagramGridStyle}
          >
            <div className="h-full min-h-0" data-tour-target="live-dag">
              <LiveDagPanel
                title="Current DAG"
                snapshot={run.repository_state}
                className="flex h-full min-h-0 flex-col"
                contentClassName="h-full min-h-0 flex-1"
                zoomStorageKey={DAG_ZOOM_KEY}
              />
            </div>
            {hasTargetDiagram ? (
              <>
                <ResizeHandle
                  label="Resize diagrams"
                  orientation="vertical"
                  className="hidden xl:flex"
                  onPointerDown={beginDiagramResize}
                />
                <div className="h-full min-h-0" data-tour-target="expected-state">
                  <LiveDagPanel
                    title="Target DAG"
                    snapshot={run.expected_state!}
                    className="flex h-full min-h-0 flex-col"
                    contentClassName="h-full min-h-0 flex-1"
                    zoomStorageKey={DAG_ZOOM_KEY}
                  />
                </div>
              </>
            ) : null}
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
              run.scaffolding.contextual_feedback
                ? 'grid-cols-1 gap-2 xl:grid-cols-[minmax(34rem,var(--terminal-pane-size))_0.375rem_minmax(18rem,var(--feedback-pane-size))] xl:gap-0'
                : 'grid-cols-1',
            )}
            style={terminalGridStyle}
          >
            <div className="h-full min-h-0" data-tour-target="terminal">
              <TerminalPanel
                lines={lines}
                disabled={run.status !== 'started'}
                runDisabled={mutation.isPending}
                processing={mutation.isPending}
                className="h-full"
                onCommand={submit}
              />
            </div>
            {run.scaffolding.contextual_feedback ? (
              <ResizeHandle
                label="Resize terminal and feedback"
                orientation="vertical"
                className="hidden xl:flex"
                onPointerDown={beginTerminalPaneResize}
              />
            ) : null}
            {run.scaffolding.contextual_feedback ? (
              <div className="h-full min-h-0 w-full min-w-0" data-tour-target="feedback">
                <ContextualFeedbackPanel run={run} feedback={feedback} />
              </div>
            ) : (
              <ContextualFeedbackPanel run={run} feedback={feedback} />
            )}
          </div>
        </section>
        <WorkspaceEditorOverlay
          snapshot={run.repository_state}
          filePath={workspaceEditorPath}
          open={Boolean(workspaceEditorPath)}
          writeDisabled={run.status !== 'started' || writeFileMutation.isPending}
          onClose={() => setWorkspaceEditorPath(null)}
          onWriteFile={(input) => writeFileMutation.mutateAsync(input)}
        />
      </main>
      <ChallengeOutcomeModal
        open={(run.status === 'completed' || run.status === 'failed') && dismissedCompletionRunId !== run.id}
        run={run}
        onClose={() => {
          setDismissedCompletionRunId(run.id)
        }}
        onBackToTower={() => navigate(towerUrlForRun(run))}
        onRetry={playAgain}
        onContinue={playAgain}
        isRetrying={isReplaying}
        isContinuing={isReplaying}
        onNextLevel={run.next_difficulty ? () => startLevelMutation.mutate(run.next_difficulty!.id) : undefined}
        isStartingNextLevel={
          startLevelMutation.isPending && startLevelMutation.variables === run.next_difficulty?.id
        }
        onSelectLevel={(levelId) => startLevelMutation.mutate(levelId)}
        busyLevelId={startLevelMutation.isPending ? startLevelMutation.variables : null}
        nextDifficultyLabel={
          run.next_difficulty
            ? run.next_difficulty.difficulty.charAt(0).toUpperCase() + run.next_difficulty.difficulty.slice(1)
            : null
        }
      />
      <Modal
        open={exitConfirmOpen}
        title="Exit challenge?"
        className="w-full max-w-md"
        onClose={() => setExitConfirmOpen(false)}
      >
        <div className="space-y-5">
          <p className="text-sm leading-6 text-muted-foreground">
            Are you sure you want to exit? Your current progress will be discarded and this run will be marked as abandoned.
          </p>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" disabled={exitMutation.isPending} onClick={() => setExitConfirmOpen(false)}>
              Cancel
            </Button>
            <Button type="button" variant="destructive" disabled={exitMutation.isPending} onClick={() => exitMutation.mutate()}>
              {exitMutation.isPending ? 'Exiting...' : 'Exit Anyway'}
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
        <ChallengeWorkspaceTour
          key={tourKey}
          run={run}
          onClose={() => {
            markPracticeTourSeen(user?.id)
            setDismissedTourKey(tourKey)
            setTourOpen(false)
          }}
        />
      ) : null}
    </div>
  )
}
