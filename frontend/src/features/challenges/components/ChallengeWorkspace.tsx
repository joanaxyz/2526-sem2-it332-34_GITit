import { useEffect, useRef, useState } from 'react'
import { useBlocker, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import { ChallengeStatusHeader } from '@/features/challenges/components/ChallengeStatusHeader'
import { ChallengeOutcomeModal } from '@/features/challenges/components/ChallengeOutcomeModal'
import { challengeOutcomeNextStep } from '@/features/challenges/components/challengeOutcome'
import { challengeScene, mapUrlForRun } from '@/features/challenges/components/challengeWorkspaceLayout'
import { useChallengeCommandSubmission } from '@/features/challenges/hooks/useChallengeCommandSubmission'
import { useChallengeRun } from '@/features/challenges/hooks/useChallengeRun'
import { useChallengeRunAssets } from '@/features/challenges/hooks/useChallengeRunAssets'
import { useChallengeWorkspaceMutations } from '@/features/challenges/hooks/useChallengeWorkspaceMutations'
import { useScaffolding } from '@/features/challenges/scaffolding/useScaffolding'
import type { ChallengeRun } from '@/features/challenges/types'
import { invalidateLevelProgressQueries } from '@/features/challenges/utils/challengeRunCache'
import { createChallengeWorkspaceCommandHandler } from '@/features/challenges/utils/challengeWorkspaceCommand'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { OutcomeNextStepMascot } from '@/shared/level/components/game-outcome/OutcomeNextStepMascot'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { ExitConfirmModal } from '@/shared/level/workspace/ExitConfirmModal'
import { GameplayWorkspaceMain } from '@/shared/level/workspace/GameplayWorkspaceMain'
import { StartOverConfirmModal } from '@/shared/level/workspace/StartOverConfirmModal'
import { useDagAnimation } from '@/shared/level/workspace/useDagAnimation'
import { useRepoGraphDrawer } from '@/shared/level/workspace/useRepoGraphDrawer'
import { useWorkspaceAutoOpen } from '@/shared/level/workspace/useWorkspaceAutoOpen'
import { REPO_GRAPH_ID } from '@/shared/level/workspace/WorkspaceDiagramStage'
import { WorkspaceStoryModal } from '@/shared/level/workspace/WorkspaceStoryModal'
import { workspaceStoryContent } from '@/shared/level/workspace/workspaceStory'
import { WorkspaceTour } from '@/shared/level/workspace/WorkspaceTour'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { usePersistentState } from '@/shared/utils/persistentState'

/** The Challenge Gate trial lifecycle around the shared gameplay workspace:
 * the same battle stage, terminal and diagrams as an adventure tier, with the
 * trial's own scaffolding, outcome and retry flow. */
export function ChallengeWorkspace() {
  const params = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const runId = Number(params.runId)
  const { query, run, lines } = useChallengeRun(runId)
  const { companionSlug, isLoading: loadoutLoading } = usePlayerLoadout()
  const assetsReady = useChallengeRunAssets({ run, companionSlug, enabled: !loadoutLoading })
  const observedRunId = run?.id ?? null
  const observedRunStatus = run?.status ?? null
  const mutation = useChallengeCommandSubmission(runId)
  const { clearToast, evaluateAndNotify } = useScaffolding(runId)
  const [dismissedCompletionRunId, setDismissedCompletionRunId] = useState<number | null>(null)
  const [projectFilesOpen, setProjectFilesOpen] = usePersistentState(PROJECT_FILES_OPEN_KEY, true)
  const dagAnimation = useDagAnimation()
  const battleDirector = useBattleDirector()
  const { completionAnimationReady, queueOutcomeAnimation } = useOutcomeAnimationGate({
    runId: observedRunId,
    status: observedRunStatus,
    animating: dagAnimation.animating || battleDirector.animating,
  })
  const [startOverConfirmOpen, setStartOverConfirmOpen] = useState(false)
  const [exitConfirmOpen, setExitConfirmOpen] = useState(false)
  const [exitNavigationRunId, setExitNavigationRunId] = useState<number | null>(null)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const user = useAuthStore((state) => state.user)
  const autoOpen = useWorkspaceAutoOpen({
    userId: user?.id,
    storyLevelKey: run ? `challenge:${run.challenge.level_id}` : undefined,
    difficulty: run?.difficulty ?? undefined,
    tourMode: 'challenge',
    started: run?.status === 'started',
  })
  const repoDrawer = useRepoGraphDrawer(run?.repository_state)
  const latestRunRef = useRef<ChallengeRun | null>(null)
  const bypassNavigationRunId = useRef<number | null>(null)
  const exitNavigationPending = exitNavigationRunId === runId
  const activeRunId = run?.status === 'started' ? run.id : null
  const navigationBlocker = useBlocker(({ currentLocation, nextLocation }) => {
    if (!activeRunId || bypassNavigationRunId.current === activeRunId) return false
    return currentLocation.pathname !== nextLocation.pathname || currentLocation.search !== nextLocation.search
  })

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
  if (query.isLoading || (!query.isError && !assetsReady)) {
    return (
      <LoadingScreen
        description="Preparing the repository, terminal, and challenge workspace."
        label="Loading challenge"
      />
    )
  }
  if (query.isError) return <ErrorState title="Could not load challenge workspace" description={query.error.message} />
  if (!run) return <ErrorState title="Could not load challenge workspace" description="The API returned no run data." />

  const shellPrompt = terminalPrompt(user?.username)
  const scene = challengeScene(run)
  const story = workspaceStoryContent(run, scene.title)
  const { storyOpen, tourOpen } = autoOpen

  const submit = createChallengeWorkspaceCommandHandler({
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
    !storyOpen &&
    !exitNavigationPending &&
    (run.status === 'completed' || run.status === 'failed') &&
    !mutation.isPending &&
    dismissedCompletionRunId !== run.id &&
    completionAnimationReady(run.id)
  // Once the result is dismissed, the mascot carries the trial's next step.
  const nextStep = dismissedCompletionRunId === run.id && !exitNavigationPending
    ? challengeOutcomeNextStep({
      run,
      onBackToMap: () => navigate(mapUrlForRun(run)),
      onRetry: playAgain,
      isRetrying: isReplaying,
      onNextLevel: run.next_difficulty ? () => startLevelMutation.mutate(run.next_difficulty!.id) : undefined,
      isStartingNextLevel: startLevelMutation.isPending && startLevelMutation.variables === run.next_difficulty?.id,
    })
    : null

  return (
    <div className="workspace-bg gameplay-workspace-screen tier-workspace-screen">
      <ChallengeStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isReplaying}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onReplay={() => replayMutation.mutate(run.challenge.level_id)}
        repoGraph={repoDrawer.drawerMode ? {
          open: repoDrawer.open,
          hasUpdate: repoDrawer.hasUpdate,
          controls: REPO_GRAPH_ID,
          buttonRef: repoDrawer.buttonRef,
          onOpen: repoDrawer.openDrawer,
        } : undefined}
      />
      <GameplayWorkspaceMain
        repoGraphDrawer={repoDrawer.drawerMode ? {
          open: repoDrawer.open,
          openCount: repoDrawer.openCount,
          onClose: repoDrawer.closeDrawer,
        } : undefined}
        run={run}
        scene={scene}
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
        mutationPending={mutation.isPending}
        onToggleProjectFiles={() => setProjectFilesOpen((value) => !value)}
        onCreateFile={(input) => createFileMutation.mutateAsync(input)}
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
        onOpenStory={autoOpen.openStory}
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
      />
      {nextStep ? <OutcomeNextStepMascot key={run.id} step={nextStep} /> : null}
      <WorkspaceStoryModal
        open={storyOpen}
        title={story.title}
        intro={story.intro}
        startingPoint={story.startingPoint}
        realWorldContext={story.realWorldContext}
        task={story.task}
        expectedResult={story.expectedResult}
        onClose={autoOpen.closeStory}
      />
      {tourOpen ? (
        <WorkspaceTour
          key={`${user?.id ?? 'guest'}:challenge:${run.id}`}
          mode="challenge"
          runId={run.id}
          onClose={autoOpen.closeTour}
          repoGraphInDrawer={repoDrawer.drawerMode}
        />
      ) : null}
      <ExitConfirmModal
        open={exitConfirmOpen}
        title="Exit challenge?"
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={retryMutation.isPending}
        onClose={() => setExitConfirmOpen(false)}
        onRetry={startFreshAttempt}
        onExit={() => exitMutation.mutate()}
      />
      <StartOverConfirmModal
        open={startOverConfirmOpen}
        isStarting={retryMutation.isPending}
        onClose={() => setStartOverConfirmOpen(false)}
        onStartFresh={startFreshAttempt}
      />
    </div>
  )
}
