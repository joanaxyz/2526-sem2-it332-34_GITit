import { useEffect, useRef, useState } from 'react'
import { useBlocker, useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'

import { tierRunsApi } from '@/features/story-map/api/tierRunsApi'
import { TierStatusHeader } from '@/features/story-map/components/TierStatusHeader'
import { TierOutcomeModal } from '@/features/story-map/components/TierOutcomeModal'
import { tierOutcomeNextStep } from '@/features/story-map/components/tierOutcome'
import { CommandIntroductionPanel } from '@/features/story-map/components/CommandIntroductionPanel'
import { WorkspaceTips } from '@/features/story-map/components/WorkspaceTips'
import { useTierCommandSubmission } from '@/features/story-map/hooks/useTierCommandSubmission'
import { useDismissTip } from '@/features/story-map/hooks/useDismissTip'
import { useTierWorkspaceMutations } from '@/features/story-map/hooks/useTierWorkspaceMutations'
import { createTierWorkspaceCommandHandler } from '@/features/story-map/utils/tierWorkspaceCommand'
import { readableGuides } from '@/features/story-map/utils/commandGuides'
import { useLeaveAbandonedRun } from '@/features/story-map/hooks/useLeaveAbandonedRun'
import { useTierRun } from '@/features/story-map/hooks/useTierRun'
import { useTierRunAssets } from '@/features/story-map/hooks/useTierRunAssets'
import { invalidateTierProgressQueries } from '@/features/story-map/utils/tierRunCache'
import { mapUrlForRun, tierScene } from '@/features/story-map/components/tierWorkspaceLayout'
import { useTierScaffolding } from '@/features/story-map/scaffolding/useTierScaffolding'
import { useAuthStore } from '@/shared/auth/useAuth'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { useOutcomeAnimationGate } from '@/shared/level-runtime/outcomeAnimation'
import { OutcomeNextStepMascot } from '@/shared/level/components/game-outcome/OutcomeNextStepMascot'
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
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { queryKeys } from '@/shared/api/queryKeys'
import { usePersistentState } from '@/shared/utils/persistentState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { SkillLearnedOverlay } from '@/shared/skill-learning/SkillLearnedOverlay'
import { useSkillLearnedQueue } from '@/shared/skill-learning/useSkillLearnedQueue'

/** The adventure-tier run lifecycle around the shared gameplay workspace
 * (shared/level/workspace): command guides, tips, learned skills and scenario flow.
 * ChallengeWorkspace wraps the same workspace for Challenge Gate trials. */
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
  const dagAnimation = useDagAnimation()
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
  // A hidden "taught elsewhere" note stays hidden for its command.
  const [hiddenElsewhereKey, setHiddenElsewhereKey] = useState<string | null>(null)
  const dismissTip = useDismissTip(runId)
  const user = useAuthStore((state) => state.user)
  const autoOpen = useWorkspaceAutoOpen({
    userId: user?.id,
    storyLevelKey: run?.tier.adventure_level_id,
    difficulty: run?.tier.difficulty,
    tourMode: 'tier',
    started: run?.status === 'started',
  })
  const repoDrawer = useRepoGraphDrawer(run?.repository_state)
  const [exitNavigationRunId, setExitNavigationRunId] = useState<number | null>(null)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const latestRunRef = useRef<TierRun | null>(null)
  const bypassNavigationRunId = useRef<number | null>(null)
  const exitNavigationPending = exitNavigationRunId === runId
  const learnedSkills = useSkillLearnedQueue({
    runId,
    blocked: mutation.isPending || dagAnimation.animating || battleDirector.animating || exitNavigationPending,
  })
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
    startNextLevel,
    continueTier,
    retry,
    replay,
    playAgain,
    createFileMutation,
    writeFileMutation,
    renameFileMutation,
    deleteFileMutation,
  } = useTierWorkspaceMutations({
    run,
    runId,
    navigate,
    queryClient,
    latestRunRef,
    bypassNavigationRunId,
    setExitNavigationRunId,
    setExitConfirmOpen,
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
  const scene = tierScene(run)
  const story = workspaceStoryContent(run, scene.title)
  const commandGuides = readableGuides(run)
  const elsewhere = run.guide_elsewhere?.guide.teaching_key !== hiddenElsewhereKey ? run.guide_elsewhere : null
  const guideHidden = run.tutor?.phase === 'introduction' && run.tutor.teaching_key === hiddenGuideKey
  const introductionOpen = Boolean(run.tutor && guideAllowed
    && !learnedSkills.pending
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
    onSkillsLearned: learnedSkills.enqueue,
  })

  const outcomeModalOpen =
    !learnedSkills.pending &&
    !storyOpen && !introductionOpen && !replayGuide &&
    !exitNavigationPending &&
    (run.status === 'completed' || run.status === 'failed') &&
    !mutation.isPending &&
    dismissedCompletionRunId !== run.id &&
    completionAnimationReady(run.id)
  // Once the result is dismissed, the mascot carries the run's next step.
  const nextStep = dismissedCompletionRunId === run.id && !exitNavigationPending
    ? tierOutcomeNextStep({
      run,
      onBackToMap: () => navigate(mapUrlForRun(run)),
      onRetry: playAgain,
      onContinue: continueTier,
      onNextLevel: run.next_difficulty ? () => startNextLevel(run.next_difficulty!.id) : undefined,
    })
    : null

  return (
    <div className="workspace-bg gameplay-workspace-screen tier-workspace-screen">
      <TierStatusHeader
        run={run}
        isExiting={exitMutation.isPending || exitNavigationPending}
        onExit={() => run.status === 'started' ? setExitConfirmOpen(true) : exitMutation.mutate()}
        onRetry={retry}
        onStartOver={() => setStartOverConfirmOpen(true)}
        onReplay={replay}
        commandGuides={run.status === 'started' && guideAllowed ? commandGuides : []}
        currentCommandGuideKey={run.tutor?.teaching_key}
        commandGuideOpen={introductionOpen || Boolean(replayGuide)}
        onSelectCommandGuide={openCommandGuide}
        repoGraph={repoDrawer.drawerMode ? {
          open: repoDrawer.open,
          hasUpdate: repoDrawer.hasUpdate,
          controls: REPO_GRAPH_ID,
          buttonRef: repoDrawer.buttonRef,
          onOpen: repoDrawer.openDrawer,
        } : undefined}
      />
      <GameplayWorkspaceMain
        teachingActive={introductionOpen}
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
      {run.status === 'started' && guideAllowed && !learnedSkills.pending ? (
        <WorkspaceTips
          tips={run.tips}
          elsewhere={elsewhere}
          onDismissTip={dismissTip}
          onReadGuide={openCommandGuide}
          onHideElsewhere={() => setHiddenElsewhereKey(run.guide_elsewhere?.guide.teaching_key ?? null)}
        />
      ) : null}
      {introductionOpen && run.tutor ? (
        <CommandIntroductionPanel key={`${run.id}:${run.tutor.context_id}`} run={run} tutor={run.tutor}
          onDismiss={() => setHiddenGuideKey(run.tutor?.teaching_key ?? null)} />
      ) : null}
      {!learnedSkills.pending && !introductionOpen && replayGuide ? (
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
      />
      {nextStep ? <OutcomeNextStepMascot key={run.id} step={nextStep} /> : null}
      <WorkspaceStoryModal
        open={storyOpen && !learnedSkills.pending}
        title={story.title}
        intro={story.intro}
        startingPoint={story.startingPoint}
        realWorldContext={story.realWorldContext}
        task={story.task}
        expectedResult={story.expectedResult}
        onClose={autoOpen.closeStory}
      />
      {tourOpen && !learnedSkills.pending ? (
        <WorkspaceTour
          key={`${user?.id ?? 'guest'}:tier:${run.id}`}
          runId={run.id}
          onClose={autoOpen.closeTour}
          repoGraphInDrawer={repoDrawer.drawerMode}
        />
      ) : null}
      <ExitConfirmModal
        open={exitConfirmOpen}
        title="Exit adventure?"
        isExiting={exitMutation.isPending || exitNavigationPending}
        onClose={() => setExitConfirmOpen(false)}
        onRetry={retry}
        onExit={() => exitMutation.mutate()}
      />
      <StartOverConfirmModal
        open={startOverConfirmOpen}
        onClose={() => setStartOverConfirmOpen(false)}
        onStartFresh={retry}
      />
      <SkillLearnedOverlay skill={learnedSkills.skill} companionSlug={companionSlug} onClose={learnedSkills.dismiss} />
    </div>
  )
}
