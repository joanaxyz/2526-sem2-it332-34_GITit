import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, GitBranch } from 'lucide-react'

import { AdventureBattlePanel } from '@/features/command-adventures/components/AdventureBattlePanel'
import { AdventureContextPanel } from '@/features/command-adventures/components/AdventureContextPanel'
import { AdventureHintPanel, type RevealedHint } from '@/features/command-adventures/components/AdventureHintPanel'
import { AdventureMasteryPanel } from '@/features/command-adventures/components/AdventureMasteryPanel'
import { AdventureOutcomeModal } from '@/features/command-adventures/components/AdventureOutcomeModal'
import { useAdventureCommandSubmission } from '@/features/command-adventures/hooks/useAdventureCommandSubmission'
import { useAdventureRun } from '@/features/command-adventures/hooks/useAdventureRun'
import type { AdventureRun } from '@/features/command-adventures/types'
import { commandSkill, countSatisfied, deriveBattleEvents } from '@/shared/battle/deriveBattleEvents'
import { useBattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { ProjectStructurePanel } from '@/shared/level/components/ProjectStructurePanel'
import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
import { PROJECT_FILES_OPEN_KEY } from '@/shared/level/workspaceKeys'
import { Button } from '@/shared/components/Button'
import { LoadingState } from '@/shared/components/LoadingState'
import { usePersistentState } from '@/shared/utils/persistentState'

export function AdventureSession({
  runId,
  onRestart,
}: {
  runId: number
  onRestart?: () => void
}) {
  const { query, lines, useHint, createFile, writeFile } = useAdventureRun(runId)
  const submitCommand = useAdventureCommandSubmission(runId)
  const director = useBattleDirector()
  const navigate = useNavigate()
  const [hint, setHint] = useState<RevealedHint | null>(null)
  const [projectFilesOpen, setProjectFilesOpen] = usePersistentState(PROJECT_FILES_OPEN_KEY, true)
  const [workspaceEditorPath, setWorkspaceEditorPath] = useState<string | null>(null)
  const attemptId = query.data?.current_attempt?.id ?? null
  const lastAttemptId = useRef(attemptId)

  // The terminal now resets itself when the attempt advances (its lines derive
  // from the new attempt's empty step history); only the revealed hint and the
  // open file editor are local state that still needs clearing per level.
  useEffect(() => {
    if (lastAttemptId.current !== attemptId) {
      lastAttemptId.current = attemptId
      setHint(null)
      setWorkspaceEditorPath(null)
    }
  }, [attemptId])

  if (query.isLoading) {
    return (
      <LoadingState
        description="Preparing the repository, terminal, and command challenge."
        label="Loading adventure"
        variant="screen"
      />
    )
  }
  if (query.isError || !query.data)
    return <p className="p-8 text-sm text-destructive">Could not load this adventure run.</p>

  const run: AdventureRun = query.data
  const restart =
    onRestart ?? (() => window.location.assign(`/command-adventures/${run.command_adventure.slug}`))
  const backToTower = () => navigate(`/tower?storey=${run.storey_id}`)

  if (run.status !== 'started') {
    return (
      <AdventureOutcomeModal
        open
        run={run}
        onRestart={restart}
        onBackToTower={backToTower}
        onClose={backToTower}
      />
    )
  }

  const attempt = run.current_attempt
  if (!attempt) {
    return <LoadingState description="Setting up the next repository." label="Preparing next level" variant="screen" />
  }

  function revealHint() {
    useHint.mutate(undefined, {
      onSuccess: (response) => setHint({ number: response.hint_number, text: response.hint }),
    })
  }

  function handleCommand(command: string) {
    const checksBefore = countSatisfied(attempt?.objective_checks)
    director.onCastStart()
    submitCommand.mutate(command, {
      onSuccess: (response) => {
        // Authoritative battle outcome once the backend block ships; until
        // then, synthesize the same events from the signals already present.
        if (response.battle) {
          director.onResolve(response.battle)
          return
        }
        const isTransition = !('partial' in response.run)
        const patchChecks =
          'partial' in response.run ? response.run.current_attempt?.objective_checks : null
        director.onResolve(
          deriveBattleEvents({
            solved: response.solved,
            counted: response.command_classification === 'counted',
            progressed: response.solved || countSatisfied(patchChecks) > checksBefore,
            skill: commandSkill(command),
            // A transition without a solve is the budget running dry.
            defeated: isTransition && !response.solved,
            monsters: director.currentMonsters(),
          }),
        )
      },
      onError: () => director.onError(),
    })
  }

  return (
    <div className="workspace-bg flex h-screen flex-col overflow-hidden">
      <header
        className="shrink-0 border-b border-primary/20 bg-background/80 px-3 py-2.5 backdrop-blur-sm"
        style={{ boxShadow: '0 1px 8px rgba(0,245,212,0.10), 0 1px 0 rgba(0,245,212,0.14)' }}
      >
        <div className="flex items-center gap-3">
          <Button type="button" variant="ghost" size="sm" onClick={() => navigate(-1)}>
            <ArrowLeft className="size-4" />
            Back
          </Button>
          <span className="grid shrink-0 size-8 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary shadow-[0_0_10px_rgba(0,245,212,0.18)]">
            <GitBranch className="size-4" />
          </span>
          <span className="min-w-0 truncate text-sm font-semibold text-foreground">
            {run.command_adventure.title}
          </span>
        </div>
      </header>

      <main className="relative grid min-h-0 flex-1 grid-cols-[24rem_minmax(0,1fr)] gap-2 p-2 max-xl:grid-cols-[21rem_minmax(0,1fr)] max-lg:grid-cols-1 max-lg:overflow-auto">
        <aside
          className="grid min-h-0 gap-2 overflow-hidden max-lg:min-h-[44rem]"
          style={{
            gridTemplateRows: projectFilesOpen
              ? 'minmax(10rem, 1fr) auto minmax(12rem, 0.75fr)'
              : 'minmax(10rem, 1fr) auto auto',
          }}
        >
          <div className="min-h-0 overflow-y-auto app-scrollbar">
            <AdventureContextPanel run={run} attempt={attempt} />
          </div>
          <AdventureMasteryPanel run={run} className="shrink-0" />
          <div className="min-h-0 overflow-hidden">
            <ProjectStructurePanel
              snapshot={attempt.repository_state}
              className="h-full"
              selectedPath={workspaceEditorPath}
              createDisabled={createFile.isPending}
              isOpen={projectFilesOpen}
              onToggle={() => setProjectFilesOpen((v) => !v)}
              onCreateFile={async (input) => {
                const updatedRun = await createFile.mutateAsync(input)
                setWorkspaceEditorPath(input.path)
                return updatedRun
              }}
              onOpenFile={setWorkspaceEditorPath}
            />
          </div>
        </aside>

        <section className="flex min-h-0 flex-col gap-2 max-lg:min-h-[36rem]">
          <AdventureBattlePanel
            run={run}
            attempt={attempt}
            director={director}
            className="h-44 shrink-0 max-lg:h-36"
          />
          <div className="min-h-0 flex-1">
            <TerminalPanel
              lines={lines}
              processing={submitCommand.isPending}
              runDisabled={submitCommand.isPending}
              className="h-full"
              onCommand={handleCommand}
            />
          </div>

          {attempt.scaffolding.hints ? (
            <AdventureHintPanel
              className="shrink-0"
              hint={hint}
              hintCount={attempt.counts.hint_count}
              isRevealing={useHint.isPending}
              onReveal={revealHint}
            />
          ) : null}
        </section>
        <WorkspaceEditorOverlay
          snapshot={attempt.repository_state}
          filePath={workspaceEditorPath}
          open={Boolean(workspaceEditorPath)}
          writeDisabled={writeFile.isPending}
          onClose={() => setWorkspaceEditorPath(null)}
          onWriteFile={(input) => writeFile.mutateAsync(input)}
        />
      </main>
    </div>
  )
}
