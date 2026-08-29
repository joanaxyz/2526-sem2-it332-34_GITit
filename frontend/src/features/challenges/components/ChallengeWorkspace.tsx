import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { useBlocker, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { ChallengeExitConfirmModal } from '@/features/challenges/components/ChallengeExitConfirmModal'
import { ChallengeStatusHeader } from '@/features/challenges/components/ChallengeStatusHeader'
import { ChallengeOutcomeModal } from '@/features/challenges/components/ChallengeOutcomeModal'
import { ChallengeStartOverConfirmModal } from '@/features/challenges/components/ChallengeStartOverConfirmModal'
import { ChallengeWorkspaceMain } from '@/features/challenges/components/ChallengeWorkspaceMain'
import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import { useChallengeWorkspaceMutations } from '@/features/challenges/hooks/useChallengeWorkspaceMutations'
import { createChallengeWorkspaceCommandHandler } from '@/features/challenges/utils/challengeWorkspaceCommand'
import { useChallengeRun } from '@/features/challenges/hooks/useChallengeRun'
import { invalidateLevelProgressQueries } from '@/features/challenges/utils/challengeRunCache'
import { ChallengeWorkspaceTour } from '@/features/challenges/components/ChallengeWorkspaceTour'
import {
  BATTLE_OPEN_KEY,
  BATTLE_STAGE_COLLAPSED_ROW,
  BATTLE_STAGE_OPEN_ROW,
  DEFAULT_TARGET_DIAGRAM_RATIO,
  DEFAULT_TERMINAL_PANE_RATIO,
  DEFAULT_TERMINAL_RATIO,
  TARGET_DIAGRAM_RATIO_KEY,
  TERMINAL_PANE_RATIO_KEY,
  TERMINAL_RATIO_KEY,
  clamp,
  constrainedTerminalPaneRatio,
  mapUrlForRun,
  ratioSanitizer,
} from '@/features/challenges/components/challengeWorkspaceLayout'
import { useScaffolding } from '@/features/challenges/scaffolding/useScaffolding'
import { useDragResize } from '@/shared/level/hooks/useDragResize'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { hasSeenLevelTour, markLevelTourSeen } from '@/shared/level/utils/levelTour'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { ChallengeRun } from '@/features/challenges/types'
import { useAuthStore } from '@/shared/auth/useAuth'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePersistentState } from '@/shared/utils/persistentState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

export function ChallengeWorkspace() {
  const params = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const runId = Number(params.runId)
  const { query, run, lines } = useChallengeRun(runId)
  const { companionSlug } = usePlayerLoadout()
  const observedRunId = run?.id ?? null
  const observedRunStatus = run?.status ?? null
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
  const [battleOpen, setBattleOpen] = usePersistentState(BATTLE_OPEN_KEY, true)
  const director = useBattleDirector()
  const { completionAnimationReady, queueOutcomeAnimation } = useOutcomeAnimationGate({
    runId: observedRunId,
    status: observedRunStatus,
    animating: director.animating,
  })
  const [tourOpen, setTourOpen] = useState(false)
  const [dismissedTourKey, setDismissedTourKey] = useState<string | null>(null)
  const [startOverConfirmOpen, setStartOverConfirmOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [exitNavigationRunId, setExitNavigationRunId] = useState<number | null>(null)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const user = useAuthStore((state) => state.user)
  const latestRunRef = useRef<ChallengeRun | null>(null)
  const bypassNavigationRunId = useRef<number | null>(null)
  const exitNavigationPending = exitNavigationRunId === runId
  const activeRunId = run?.status === 'started' ? run.id : null
  const navigationBlocker = useBlocker(({ currentLocation, nextLocation }) => {
    if (!activeRunId || bypassNavigationRunId.current === activeRunId) return false
    return currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search
  })
  const workspaceGridRef = useRef<HTMLElement>(null)
  const diagramGridRef = useRef<HTMLDivElement>(null)
  const terminalGridRef = useRef<HTMLDivElement>(null)
  const beginTerminalResize = useDragResize(workspaceGridRef, 'row-resize', (event, bounds) => {
    setTerminalRatio(clamp((bounds.bottom - event.clientY) / bounds.height, 0.22, 0.58))
  })
  const beginDiagramResize = useDragResize(diagramGridRef, 'col-resize', (event, bounds) => {
    setTargetDiagramRatio(clamp((event.clientX - bounds.left) / bounds.width, 0.34, 0.66))
  })
  const beginTerminalPaneResize = useDragResize(terminalGridRef, 'col-resize', (event, bounds) => {
    setTerminalPaneRatio(constrainedTerminalPaneRatio(event.clientX, bounds))
  })

  const resizeStep = 0.03
  const keyboardResizeDiagram = (delta: number) => {
    setTargetDiagramRatio((value) => clamp(value + delta * resizeStep, 0.34, 0.66))
  }
  const keyboardResizeTerminal = (delta: number) => {
    setTerminalRatio((value) => clamp(value + delta * resizeStep, 0.22, 0.58))
  }
  const keyboardResizeTerminalPane = (delta: number) => {
    setTerminalPaneRatio((value) => clamp(value + delta * resizeStep, 0.4, 0.92))
  }

  useEffect(() => {
    latestRunRef.current = run
  }, [run])

  useEffect(() => {
    if (navigationBlocker.state !== 'blocked' || !activeRunId) return

    void challengesApi
      .discardChallengeRun(activeRunId)
      .catch(() => undefined)
      .finally(() => {
        queryClient.removeQueries({ queryKey: queryKeys.challengeRun(activeRunId) })
        invalidateLevelProgressQueries(queryClient)
        navigationBlocker.proceed()
      })
  }, [activeRunId, navigationBlocker, queryClient])

  const {
    exitMutation,
    startLevelMutation,
    replayMutation,
    retryMutation,
    createFileMutation,
    writeFileMutation,
    renameFileMutation,
    deleteFileMutation,
    startFreshAttempt,
    playAgain,
  } = useChallengeWorkspaceMutations({
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
        companionSlug={companionSlug}
        description="Preparing the repository, terminal, and challenge workspace."
        label="Loading challenge"
        variant="screen"
      />
    )
  }
  if (query.isError) return <ErrorState title="Could not load challenge workspace" description={query.error.message} />
  if (!run) return <ErrorState title="Could not load challenge workspace" description="The API returned no run data." />

  const shellPrompt = terminalPrompt({ username: user?.username, repo: run.challenge.slug })
  const tourKey = `${user?.id ?? 'guest'}:challenge:${run.challenge.level_id}`
  const shouldAutoOpenTour = dismissedTourKey !== tourKey && !hasSeenLevelTour(user?.id)
  const isTourOpen = tourOpen || shouldAutoOpenTour

  const submit = createChallengeWorkspaceCommandHandler({
    run,
    runId,
    mutation,
    director,
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

  const workspaceGridStyle = {
    // Leading row = the challenge battle strip, uppermost in this column;
    // collapses to a slim HP bar. The DAG/terminal rows keep their resize.
    // Plain fr stories (min-heights live on the pane classes): minmax(len, fr)
    // stops distributing free space once a min binds and leaves a dead band.
    gridTemplateRows: `${battleOpen ? BATTLE_STAGE_OPEN_ROW : BATTLE_STAGE_COLLAPSED_ROW} minmax(0, ${1 - terminalRatio}fr) 0.375rem minmax(0, ${terminalRatio}fr)`,
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
    <div className="workspace-bg gameplay-workspace-screen">
      <ChallengeStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isReplaying}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onReplay={() => replayMutation.mutate(run.challenge.level_id)}
      />
      <ChallengeWorkspaceMain
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
        workspaceGridRef={workspaceGridRef}
        workspaceGridStyle={workspaceGridStyle}
        director={director}
        battleOpen={battleOpen}
        hasTargetDiagram={hasTargetDiagram}
        diagramGridRef={diagramGridRef}
        diagramGridStyle={diagramGridStyle}
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
        onToggleBattle={() => setBattleOpen((value) => !value)}
        onBeginDiagramResize={beginDiagramResize}
        onBeginTerminalResize={beginTerminalResize}
        onBeginTerminalPaneResize={beginTerminalPaneResize}
        onKeyboardDiagramResize={keyboardResizeDiagram}
        onKeyboardTerminalResize={keyboardResizeTerminal}
        onKeyboardTerminalPaneResize={keyboardResizeTerminalPane}
        onResetDiagramResize={() => setTargetDiagramRatio(DEFAULT_TARGET_DIAGRAM_RATIO)}
        onResetTerminalResize={() => setTerminalRatio(DEFAULT_TERMINAL_RATIO)}
        onResetTerminalPaneResize={() => setTerminalPaneRatio(DEFAULT_TERMINAL_PANE_RATIO)}
        onCommand={submit}
        onCloseEditor={() => setWorkspaceEditorPath(null)}
        onWriteFile={(input) => writeFileMutation.mutateAsync(input)}
      />
      <ChallengeOutcomeModal
        open={outcomeModalOpen}
        run={run}
        onClose={() => {
          setDismissedCompletionRunId(run.id)
        }}
        onBackToMap={() => navigate(mapUrlForRun(run))}
        onRetry={playAgain}
        isRetrying={isReplaying}
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
      <ChallengeExitConfirmModal
        open={exitConfirmOpen}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={retryMutation.isPending}
        onClose={() => setExitConfirmOpen(false)}
        onRetry={startFreshAttempt}
        onExit={() => exitMutation.mutate()}
      />
      <ChallengeStartOverConfirmModal
        open={startOverConfirmOpen}
        isStarting={retryMutation.isPending}
        onClose={() => setStartOverConfirmOpen(false)}
        onStartFresh={startFreshAttempt}
      />
      {isTourOpen ? (
        <ChallengeWorkspaceTour
          key={tourKey}
          run={run}
          onClose={() => {
            markLevelTourSeen(user?.id)
            setDismissedTourKey(tourKey)
            setTourOpen(false)
          }}
        />
      ) : null}
    </div>
  )
}
