import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { useBlocker, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { TierExitConfirmModal } from '@/features/story-map/components/TierExitConfirmModal'
import { TierStatusHeader } from '@/features/story-map/components/TierStatusHeader'
import { TierOutcomeModal } from '@/features/story-map/components/TierOutcomeModal'
import { TierStartOverConfirmModal } from '@/features/story-map/components/TierStartOverConfirmModal'
import { TierWorkspaceMain } from '@/features/story-map/components/TierWorkspaceMain'
import { TierWorkspaceTour } from '@/features/story-map/components/TierWorkspaceTour'
import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import { useTierWorkspaceMutations } from '@/features/story-map/hooks/useTierWorkspaceMutations'
import { createTierWorkspaceCommandHandler } from '@/features/story-map/utils/tierWorkspaceCommand'
import { useTierRun } from '@/features/story-map/hooks/useTierRun'
import { invalidateTierProgressQueries } from '@/features/story-map/utils/tierRunCache'
import {
  DEFAULT_TERMINAL_PANE_RATIO,
  TERMINAL_PANE_RATIO_KEY,
  clamp,
  constrainedTerminalPaneRatio,
  mapUrlForRun,
  ratioSanitizer,
} from '@/features/story-map/components/tierWorkspaceLayout'
import { useTierScaffolding } from '@/features/story-map/scaffolding/useTierScaffolding'
import { useAuthStore } from '@/shared/auth/useAuth'
import { useDragResize } from '@/shared/level/hooks/useDragResize'
import { hasSeenLevelTour, markLevelTourSeen } from '@/shared/level/utils/levelTour'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { useTierDagAnimation } from '@/features/story-map/hooks/useTierDagAnimation'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePersistentState } from '@/shared/utils/persistentState'

/** Mirrors ChallengeWorkspace.tsx for the adventure-tier run lifecycle - new
 * and parallel, ChallengeWorkspace itself is untouched. Its first-run tour is
 * TierWorkspaceTour, not ChallengeWorkspaceTour: this screen is where every
 * difficulty-tiered adventure level is played, and the Challenge Gate copy
 * does not describe it. */
export function TierWorkspace() {
  const params = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const runId = Number(params.runId)
  const { query, run, lines } = useTierRun(runId)
  const observedRunId = run?.id ?? null
  const observedRunStatus = run?.status ?? null
  const mutation = useTierCommandSubmission(runId)
  const { clearToast, evaluateAndNotify } = useTierScaffolding(runId)
  const [dismissedCompletionRunId, setDismissedCompletionRunId] = useState<number | null>(null)
  const [terminalPaneRatio, setTerminalPaneRatio] = usePersistentState(
    TERMINAL_PANE_RATIO_KEY,
    DEFAULT_TERMINAL_PANE_RATIO,
    ratioSanitizer(0.4, 0.92, DEFAULT_TERMINAL_PANE_RATIO),
  )
  const [projectFilesOpen, setProjectFilesOpen] = usePersistentState(PROJECT_FILES_OPEN_KEY, true)
  const dagAnimation = useTierDagAnimation()
  const battleDirector = useBattleDirector()
  const { completionAnimationReady, queueOutcomeAnimation } = useOutcomeAnimationGate({
    runId: observedRunId,
    status: observedRunStatus,
    animating: dagAnimation.animating || battleDirector.animating,
  })
  const [startOverConfirmOpen, setStartOverConfirmOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const user = useAuthStore((state) => state.user)
  const [exitNavigationRunId, setExitNavigationRunId] = useState<number | null>(null)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const latestRunRef = useRef<TierRun | null>(null)
  const bypassNavigationRunId = useRef<number | null>(null)
  const exitNavigationPending = exitNavigationRunId === runId
  const activeRunId = run?.status === 'started' ? run.id : null
  const navigationBlocker = useBlocker(({ currentLocation, nextLocation }) => {
    if (!activeRunId || bypassNavigationRunId.current === activeRunId) return false
    return currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search
  })
  const terminalGridRef = useRef<HTMLDivElement>(null)
  const beginTerminalPaneResize = useDragResize(terminalGridRef, 'col-resize', (event, bounds) => {
    setTerminalPaneRatio(constrainedTerminalPaneRatio(event.clientX, bounds))
  })

  const resizeStep = 0.03
  const keyboardResizeTerminalPane = (delta: number) => {
    setTerminalPaneRatio((value) => clamp(value + delta * resizeStep, 0.4, 0.92))
  }

  useEffect(() => {
    latestRunRef.current = run
  }, [run])

  useEffect(() => {
    if (navigationBlocker.state !== 'blocked' || !activeRunId) return

    void tierRunsApi
      .discardRun(activeRunId)
      .catch(() => undefined)
      .finally(() => {
        queryClient.removeQueries({ queryKey: queryKeys.adventureTierRun(activeRunId) })
        invalidateTierProgressQueries(queryClient)
        navigationBlocker.proceed()
      })
  }, [activeRunId, navigationBlocker, queryClient])

  const {
    exitMutation,
    startLevelMutation,
    continueMutation,
    replayMutation,
    retryMutation,
    createFileMutation,
    writeFileMutation,
    renameFileMutation,
    deleteFileMutation,
    startFreshAttempt,
    playAgain,
  } = useTierWorkspaceMutations({
    run,
    runId,
    navigate,
    queryClient,
    latestRunRef,
    bypassNavigationRunId,
    setExitNavigationRunId,
    setExitConfirmOpen,
    setStartOverConfirmOpen,
    setDismissedCompletionRunId,
  })
  if (query.isLoading) {
    return (
      <LoadingState
        description="Preparing the repository, terminal, and adventure workspace."
        label="Loading adventure"
        showCompanion={false}
        variant="screen"
      />
    )
  }
  if (query.isError) return <ErrorState title="Could not load adventure workspace" description={query.error.message} />
  if (!run) return <ErrorState title="Could not load adventure workspace" description="The API returned no run data." />

  const shellPrompt = terminalPrompt({ username: undefined, repo: run.tier.adventure_level_slug })
  const tourKey = `${user?.id ?? 'guest'}:tier`
  const tourOpen =
    run.status === 'started' && dismissedTourKey !== tourKey && !hasSeenLevelTour(user?.id, 'tier')

  const submit = createTierWorkspaceCommandHandler({
    runId,
    mutation,
    dagAnimation,
    battleDirector,
    queryClient,
    clearToast,
    evaluateAndNotify,
    setExitConfirmOpen,
    setWorkspaceEditorPath,
    queueOutcomeAnimation,
  })

  const isReplaying = retryMutation.isPending || replayMutation.isPending
  const outcomeModalOpen =
    !exitNavigationPending &&
    (run.status === 'completed' || run.status === 'failed') &&
    !mutation.isPending &&
    dismissedCompletionRunId !== run.id &&
    completionAnimationReady(run.id)

  const terminalGridStyle = {
    '--terminal-pane-size': `${terminalPaneRatio}fr`,
    '--feedback-pane-size': `${1 - terminalPaneRatio}fr`,
  } as CSSProperties

  return (
    <div className="workspace-bg gameplay-workspace-screen">
      <TierStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isReplaying}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onReplay={() => replayMutation.mutate(run.tier.id)}
      />
      <TierWorkspaceMain
        run={run}
        lines={lines}
        shellPrompt={shellPrompt}
        projectFilesOpen={projectFilesOpen}
        workspaceEditorPath={workspaceEditorPath}
        createDisabled={
          run.status !== 'started' ||
          createFileMutation.isPending ||
          renameFileMutation.isPending ||
          deleteFileMutation.isPending
        }
        writeDisabled={run.status !== 'started' || writeFileMutation.isPending}
        dagAnimation={dagAnimation}
        battleDirector={battleDirector}
        terminalGridRef={terminalGridRef}
        terminalGridStyle={terminalGridStyle}
        mutationPending={mutation.isPending}
        onToggleProjectFiles={() => setProjectFilesOpen((value) => !value)}
        onCreateFile={async (input) => {
          const updatedRun = await createFileMutation.mutateAsync(input)
          return updatedRun
        }}
        onRenameFile={async (input) => {
          const updatedRun = await renameFileMutation.mutateAsync(input)
          if (workspaceEditorPath === input.path) setWorkspaceEditorPath(null)
          return updatedRun
        }}
        onDeleteFile={async (path) => {
          const updatedRun = await deleteFileMutation.mutateAsync(path)
          if (workspaceEditorPath === path || workspaceEditorPath?.startsWith(`${path}/`)) {
            setWorkspaceEditorPath(null)
          }
          return updatedRun
        }}
        onOpenFile={setWorkspaceEditorPath}
        onBeginTerminalPaneResize={beginTerminalPaneResize}
        onKeyboardTerminalPaneResize={keyboardResizeTerminalPane}
        onResetTerminalPaneResize={() => setTerminalPaneRatio(DEFAULT_TERMINAL_PANE_RATIO)}
        onCommand={submit}
        onCloseEditor={() => setWorkspaceEditorPath(null)}
        onWriteFile={(input) => writeFileMutation.mutateAsync(input)}
      />
      <TierOutcomeModal
        open={outcomeModalOpen}
        run={run}
        onClose={() => {
          setDismissedCompletionRunId(run.id)
        }}
        onBackToMap={() => navigate(mapUrlForRun(run))}
        onRetry={playAgain}
        isRetrying={isReplaying}
        onContinue={() => continueMutation.mutate()}
        isContinuing={continueMutation.isPending}
        onNextLevel={run.next_difficulty ? () => startLevelMutation.mutate(run.next_difficulty!.id) : undefined}
        isStartingNextLevel={
          startLevelMutation.isPending && startLevelMutation.variables === run.next_difficulty?.id
        }
        nextDifficultyLabel={
          run.next_difficulty
            ? run.next_difficulty.difficulty.charAt(0).toUpperCase() + run.next_difficulty.difficulty.slice(1)
            : null
        }
      />
      {tourOpen ? (
        <TierWorkspaceTour
          key={`${tourKey}:${run.id}`}
          runId={run.id}
          onClose={() => {
            markLevelTourSeen(user?.id, 'tier')
            setDismissedTourKey(tourKey)
          }}
        />
      ) : null}
      <TierExitConfirmModal
        open={exitConfirmOpen}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={retryMutation.isPending}
        onClose={() => setExitConfirmOpen(false)}
        onRetry={startFreshAttempt}
        onExit={() => exitMutation.mutate()}
      />
      <TierStartOverConfirmModal
        open={startOverConfirmOpen}
        isStarting={retryMutation.isPending}
        onClose={() => setStartOverConfirmOpen(false)}
        onStartFresh={startFreshAttempt}
      />
    </div>
  )
}
