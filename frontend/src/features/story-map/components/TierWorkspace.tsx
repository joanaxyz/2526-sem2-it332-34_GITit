import { useEffect, useRef, useState } from 'react'
import { useBlocker, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { TierExitConfirmModal } from '@/features/story-map/components/TierExitConfirmModal'
import { TierStatusHeader } from '@/features/story-map/components/TierStatusHeader'
import { TierStatsBar } from '@/features/story-map/components/tier-workspace/TierStatsBar'
import { TierStoryModal } from '@/features/story-map/components/tier-workspace/TierStoryModal'
import { TierOutcomeModal } from '@/features/story-map/components/TierOutcomeModal'
import { TierStartOverConfirmModal } from '@/features/story-map/components/TierStartOverConfirmModal'
import { TierWorkspaceMain } from '@/features/story-map/components/TierWorkspaceMain'
import { TierWorkspaceTour } from '@/features/story-map/components/TierWorkspaceTour'
import { CommandIntroductionPanel } from '@/features/story-map/components/CommandIntroductionPanel'
import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import { useCommandGuideHistory } from '@/features/story-map/hooks/useCommandGuideHistory'
import { useTierWorkspaceMutations } from '@/features/story-map/hooks/useTierWorkspaceMutations'
import { createTierWorkspaceCommandHandler } from '@/features/story-map/utils/tierWorkspaceCommand'
import { useLeaveAbandonedRun } from '@/features/story-map/hooks/useLeaveAbandonedRun'
import { useTierRun } from '@/features/story-map/hooks/useTierRun'
import { useTierRunAssets } from '@/features/story-map/hooks/useTierRunAssets'
import { invalidateTierProgressQueries } from '@/features/story-map/utils/tierRunCache'
import { mapUrlForRun } from '@/features/story-map/components/tierWorkspaceLayout'
import { useTierScaffolding } from '@/features/story-map/scaffolding/useTierScaffolding'
import { useAuthStore } from '@/shared/auth/useAuth'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { useTierDagAnimation } from '@/features/story-map/hooks/useTierDagAnimation'
import { useTierAutoOpenQueue } from '@/features/story-map/hooks/useTierAutoOpenQueue'
import { useTierRepoDrawer } from '@/features/story-map/hooks/useTierRepoDrawer'
import { TIER_REPO_GRAPH_ID } from '@/features/story-map/components/tier-workspace/TierDiagramStage'
import { tierStoryContent } from '@/features/story-map/utils/tierStory'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePersistentState } from '@/shared/utils/persistentState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'

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
  const { companionSlug, isLoading: loadoutLoading } = usePlayerLoadout()
  const assetsReady = useTierRunAssets({
    run,
    companionSlug,
    enabled: !loadoutLoading,
  })
  const observedRunId = run?.id ?? null
  const observedRunStatus = run?.status ?? null
  const mutation = useTierCommandSubmission(runId)
  const { clearToast, evaluateAndNotify } = useTierScaffolding(runId)
  const [dismissedCompletionRunId, setDismissedCompletionRunId] = useState<number | null>(null)
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
  // A hidden guide stays hidden for its lesson (across commands) until reopened.
  const [hiddenGuideKey, setHiddenGuideKey] = useState<string | null>(null)
  const [selectedGuideKey, setSelectedGuideKey] = useState<string | null>(null)
  const commandGuides = useCommandGuideHistory(runId, run?.tutor)
  const user = useAuthStore((state) => state.user)
  const autoOpen = useTierAutoOpenQueue({
    userId: user?.id,
    adventureLevelId: run?.tier.adventure_level_id,
    difficulty: run?.tier.difficulty,
    started: run?.status === 'started',
  })
  const repoDrawer = useTierRepoDrawer(run?.repository_state)
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

  useEffect(() => {
    latestRunRef.current = run
  }, [run])

  useLeaveAbandonedRun(run, navigate)

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
  if (query.isLoading || (!query.isError && !assetsReady)) {
    return (
      <LoadingScreen
        description="Preparing the repository, terminal, and adventure workspace."
        label="Loading adventure"
      />
    )
  }
  if (query.isError) return <ErrorState title="Could not load adventure workspace" description={query.error.message} />
  if (!run) return <ErrorState title="Could not load adventure workspace" description="The API returned no run data." />

  const shellPrompt = terminalPrompt(user?.username)
  const { storyOpen, tourOpen, guideAllowed } = autoOpen
  const story = tierStoryContent(run)
  const guideHidden = run.tutor?.phase === 'introduction' && run.tutor.teaching_key === hiddenGuideKey
  const introductionOpen = Boolean(run.tutor && guideAllowed
    && !mutation.isPending && !dagAnimation.animating && !battleDirector.animating
    && !guideHidden)
  const replayGuide = selectedGuideKey
    ? commandGuides.find((guide) => guide.teaching_key === selectedGuideKey) ?? null
    : null

  const openCommandGuide = (teachingKey: string) => {
    if (run.tutor?.teaching_key === teachingKey && run.tutor.phase === 'introduction') {
      setSelectedGuideKey(null)
      setHiddenGuideKey(null)
      return
    }
    setSelectedGuideKey(teachingKey)
  }

  const submit = createTierWorkspaceCommandHandler({
    runId,
    mutation,
    dagAnimation,
    battleDirector,
    queryClient,
    clearToast,
    evaluateAndNotify: (updatedRun, classification) => {
      if (!updatedRun.tutor) evaluateAndNotify(updatedRun, classification)
    },
    setExitConfirmOpen,
    setWorkspaceEditorPath,
    queueOutcomeAnimation,
  })

  const isReplaying = retryMutation.isPending || replayMutation.isPending
  const outcomeModalOpen =
    !storyOpen && !introductionOpen && !replayGuide &&
    !exitNavigationPending &&
    (run.status === 'completed' || run.status === 'failed') &&
    !mutation.isPending &&
    dismissedCompletionRunId !== run.id &&
    completionAnimationReady(run.id)

  return (
    <div className="workspace-bg gameplay-workspace-screen tier-workspace-screen">
      <TierStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        isRetrying={isReplaying}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={() => retryMutation.mutate()}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onReplay={() => replayMutation.mutate(run.tier.id)}
        commandGuides={run.status === 'started' && guideAllowed ? commandGuides : []}
        currentCommandGuideKey={run.tutor?.teaching_key}
        commandGuideOpen={introductionOpen || Boolean(replayGuide)}
        onSelectCommandGuide={openCommandGuide}
      />
      <TierStatsBar
        run={run}
        repoGraph={repoDrawer.drawerMode ? {
          open: repoDrawer.open,
          hasUpdate: repoDrawer.hasUpdate,
          controls: TIER_REPO_GRAPH_ID,
          buttonRef: repoDrawer.buttonRef,
          onOpen: repoDrawer.openDrawer,
        } : undefined}
      />
      <TierWorkspaceMain
        teachingActive={introductionOpen}
        repoGraphDrawer={repoDrawer.drawerMode ? {
          open: repoDrawer.open,
          openCount: repoDrawer.openCount,
          onClose: repoDrawer.closeDrawer,
        } : undefined}
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
        onOpenStory={autoOpen.openStory}
        onCommand={submit}
        onCloseEditor={() => setWorkspaceEditorPath(null)}
        onWriteFile={(input) => writeFileMutation.mutateAsync(input)}
      />
      {introductionOpen && run.tutor ? (
        <CommandIntroductionPanel key={`${run.id}:${run.tutor.context_id}`} run={run} tutor={run.tutor}
          onDismiss={() => setHiddenGuideKey(run.tutor?.teaching_key ?? null)} />
      ) : null}
      {!introductionOpen && replayGuide ? (
        <CommandIntroductionPanel
          key={`${run.id}:replay:${replayGuide.teaching_key}`}
          run={run}
          tutor={replayGuide}
          replay
          onDismiss={() => setSelectedGuideKey(null)}
        />
      ) : null}
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
      <TierStoryModal
        open={storyOpen}
        title={story.title}
        intro={story.intro}
        realWorldContext={story.realWorldContext}
        task={story.task}
        onClose={autoOpen.closeStory}
      />
      {tourOpen ? (
        <TierWorkspaceTour
          key={`${user?.id ?? 'guest'}:tier:${run.id}`}
          runId={run.id}
          onClose={autoOpen.closeTour}
          targetInDrawer={repoDrawer.drawerMode && Boolean(run.scaffolding.expected_state && run.expected_state)}
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
