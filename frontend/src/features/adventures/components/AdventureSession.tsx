import { useEffect, useRef, useState } from 'react'
import type { CSSProperties } from 'react'
import { useBlocker, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { AdventureExitConfirmModal } from '@/features/adventures/components/AdventureExitConfirmModal'
import { AdventureLevelLibraryModal } from '@/features/adventures/components/AdventureLevelLibraryModal'
import { AdventureOutcomeModal } from '@/features/adventures/components/AdventureOutcomeModal'
import { AdventureStartOverConfirmModal } from '@/features/adventures/components/AdventureStartOverConfirmModal'
import { AdventureStatusHeader } from '@/features/adventures/components/AdventureStatusHeader'
import { AdventureWorkspaceMain } from '@/features/adventures/components/AdventureWorkspaceMain'
import { adventuresApi } from '@/features/adventures/api/adventuresApi'
import { useAdventureCommandSubmission } from '@/features/adventures/hooks/useAdventureCommandSubmission'
import { createAdventureWorkspaceCommandHandler } from '@/features/adventures/utils/adventureWorkspaceCommand'
import { useAdventureRun, useStartAdventureRun } from '@/features/adventures/hooks/useAdventureRun'
import { useAdventureSessionMutations } from '@/features/adventures/hooks/useAdventureSessionMutations'
import { invalidateAdventureProgressQueries } from '@/features/adventures/utils/adventureRunCache'
import type { AdventureRun } from '@/features/adventures/types'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { useAuthStore } from '@/shared/auth/useAuth'
import type { TerminalLine } from '@/shared/level/types'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePersistentState } from '@/shared/utils/persistentState'
import { WORKSPACE_BATTLE_STAGE_ROW } from '@/shared/level/workspaceLayout'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

type AdventureWorkspaceSnapshot = {
  run: AdventureRun
  lines: TerminalLine[]
}

export function AdventureSession({
  runId,
  onRestart,
}: {
  runId: number
  onRestart?: () => void
}) {
  const { query, lines, createFile, writeFile, renameFile, deleteFile } = useAdventureRun(runId)
  const user = useAuthStore((state) => state.user)
  const submitCommand = useAdventureCommandSubmission(runId)
  const director = useBattleDirector()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { companionSlug } = usePlayerLoadout()
  const retryRun = useStartAdventureRun()
  const startNextLevel = useStartAdventureRun()
  const [projectFilesOpen, setProjectFilesOpen] = usePersistentState(PROJECT_FILES_OPEN_KEY, true)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const [levelLibraryOpen, setLevelLibraryOpen] = useState(false)
  const [startOverConfirmOpen, setStartOverConfirmOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [exitNavigationRunId, setExitNavigationRunId] = useState<number | null>(null)
  const [lastWorkspace, setLastWorkspace] = useState<AdventureWorkspaceSnapshot | null>(null)
  const queriedRun = query.data
  const queriedRunId = queriedRun?.id ?? null
  const queriedRunStatus = queriedRun?.status ?? null
  const { completionAnimationReady, queueOutcomeAnimation } = useOutcomeAnimationGate({
    runId: queriedRunId,
    status: queriedRunStatus,
    animating: director.animating,
  })
  const attemptId = queriedRun?.current_attempt?.id ?? null
  const lastAttemptId = useRef(attemptId)
  const latestRunRef = useRef<AdventureRun | null>(null)
  const bypassNavigationRunId = useRef<number | null>(null)
  const exitNavigationPending = exitNavigationRunId === runId
  const activeRunId = queriedRun?.status === 'started' ? queriedRun.id : null
  const navigationBlocker = useBlocker(({ currentLocation, nextLocation }) => {
    if (!activeRunId || bypassNavigationRunId.current === activeRunId) return false
    return currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search
  })

  useEffect(() => {
    latestRunRef.current = queriedRun ?? null
  }, [queriedRun])

  useEffect(() => {
    if (navigationBlocker.state !== 'blocked' || !activeRunId) return

    void adventuresApi
      .discardRun(activeRunId)
      .catch(() => undefined)
      .finally(() => {
        queryClient.removeQueries({ queryKey: queryKeys.adventureRun(activeRunId) })
        invalidateAdventureProgressQueries(queryClient)
        navigationBlocker.proceed()
      })
  }, [activeRunId, navigationBlocker, queryClient])

  // The terminal resets itself when the attempt advances (its lines derive from
  // the new attempt's empty step history); only the open file editor needs clearing.
  useEffect(() => {
    if (lastAttemptId.current !== attemptId) {
      lastAttemptId.current = attemptId
      setWorkspaceEditorPath(null)
      setLevelLibraryOpen(false)
    }
  }, [attemptId])

  const {
    exitMutation,
    restart,
    backToMap,
    openNextLevel,
    isRestarting,
    isOpeningNextLevel,
  } = useAdventureSessionMutations({
    runId,
    run: queriedRun,
    onRestart,
    navigate,
    queryClient,
    retryRun,
    startNextLevel,
    latestRunRef,
    bypassNavigationRunId,
    setExitNavigationRunId,
    setExitConfirmOpen,
    setStartOverConfirmOpen,
  })
  if (query.isLoading) {
    return (
      <LoadingState
        companionSlug={companionSlug}
        description="Preparing the repository, terminal, and command challenge."
        label="Loading adventure"
        variant="screen"
      />
    )
  }
  if (query.isError || !query.data)
    return <p className="p-8 text-sm text-destructive">Could not load this adventure run.</p>

  const run: AdventureRun = query.data
  const workspaceRun = run.current_attempt ? run : lastWorkspace?.run ?? run
  const attempt = run.current_attempt ?? workspaceRun.current_attempt
  const outcomeModalOpen =
    !exitNavigationPending &&
    (run.status === 'completed' || run.status === 'failed') &&
    !submitCommand.isPending &&
    (!attempt || completionAnimationReady(run.id))
  const workspaceLines = run.status === 'started' ? lines : lastWorkspace?.lines ?? lines
  const repoSlug = workspaceRun.selected_level?.slug ?? run.selected_level?.slug
  const workspaceGridStyle = {
    gridTemplateRows: `${WORKSPACE_BATTLE_STAGE_ROW} minmax(13rem, 1fr)`,
  } as CSSProperties

  if (!attempt && run.status === 'started') {
    return (
      <LoadingState
        companionSlug={companionSlug}
        description="Setting up the next repository."
        label="Preparing next level"
        variant="screen"
      />
    )
  }

  if (!attempt) {
    return (
      <div className="workspace-bg gameplay-workspace-screen">
        <AdventureOutcomeModal
          open={outcomeModalOpen}
          run={run}
          onRestart={restart}
          onNextLevel={openNextLevel}
          onBackToMap={backToMap}
          onClose={backToMap}
          isOpeningNextLevel={isOpeningNextLevel}
          isRestarting={isRestarting}
        />
      </div>
    )
  }

  const handleCommand = createAdventureWorkspaceCommandHandler({
    attempt,
    run,
    lines,
    submitCommand,
    director,
    setExitConfirmOpen,
    setLastWorkspace,
    queueOutcomeAnimation,
  })

  return (
    <div className="workspace-bg gameplay-workspace-screen">
      <AdventureStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isRestarting}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={restart}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onOpenLibrary={() => setLevelLibraryOpen(true)}
      />

      <AdventureWorkspaceMain
        run={run}
        workspaceRun={workspaceRun}
        attempt={attempt}
        director={director}
        username={user?.username}
        repoSlug={repoSlug}
        workspaceLines={workspaceLines}
        workspaceGridStyle={workspaceGridStyle}
        projectFilesOpen={projectFilesOpen}
        workspaceEditorPath={workspaceEditorPath}
        createDisabled={
          run.status !== 'started' ||
          createFile.isPending ||
          renameFile.isPending ||
          deleteFile.isPending
        }
        writeDisabled={run.status !== 'started' || writeFile.isPending}
        commandPending={submitCommand.isPending}
        onToggleProjectFiles={() => setProjectFilesOpen((v) => !v)}
        onCreateFile={async (input) => {
          const updatedRun = await createFile.mutateAsync(input)
          return updatedRun
        }}
        onRenameFile={async (input) => {
          const updatedRun = await renameFile.mutateAsync(input)
          if (workspaceEditorPath === input.path) setWorkspaceEditorPath(null)
          return updatedRun
        }}
        onDeleteFile={async (path) => {
          const updatedRun = await deleteFile.mutateAsync(path)
          if (workspaceEditorPath === path || workspaceEditorPath?.startsWith(`${path}/`)) {
            setWorkspaceEditorPath(null)
          }
          return updatedRun
        }}
        onOpenFile={setWorkspaceEditorPath}
        onCommand={handleCommand}
        onCloseEditor={() => setWorkspaceEditorPath(null)}
        onWriteFile={(input) => writeFile.mutateAsync(input)}
      />
      {levelLibraryOpen ? (
        <AdventureLevelLibraryModal run={run} onClose={() => setLevelLibraryOpen(false)} />
      ) : null}
      <AdventureOutcomeModal
        open={outcomeModalOpen}
        run={run}
        onRestart={restart}
        onNextLevel={openNextLevel}
        onBackToMap={backToMap}
        onClose={backToMap}
        isOpeningNextLevel={isOpeningNextLevel}
        isRestarting={isRestarting}
      />
      <AdventureExitConfirmModal
        open={exitConfirmOpen}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isRestarting}
        onClose={() => setExitConfirmOpen(false)}
        onRetry={restart}
        onExit={() => exitMutation.mutate()}
      />
      <AdventureStartOverConfirmModal
        open={startOverConfirmOpen}
        isRestarting={isRestarting}
        onClose={() => setStartOverConfirmOpen(false)}
        onRestart={restart}
      />
    </div>
  )
}
