import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, ArrowRight, BookOpen, ListTree, Play, SquareTerminal } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { PreviewContentPage } from '@/features/scenarios/components/PreviewContentPage'
import { PreviewDemoPanel } from '@/features/scenarios/components/PreviewDemoPanel'
import { PreviewNavigator } from '@/features/scenarios/components/PreviewNavigator'
import {
  buildPreviewCommands,
  demoBootLines,
  emptyDemoSnapshot,
  isRepositorySnapshot,
  navigationGroupsFromCommands,
  nextReadingLocation,
  normalize,
  previousReadingLocation,
} from '@/features/scenarios/components/previewPayloadUtils'
import type {
  DifficultyAccess,
  DifficultyActionIntent,
  ScenarioSkillFocus,
} from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'

export function SkillFocusPreviewModal({
  scenario,
  difficulty,
  action,
  isProceeding,
  onClose,
  onProceed,
}: {
  scenario: ScenarioSkillFocus
  difficulty?: DifficultyAccess
  action?: DifficultyActionIntent
  isProceeding?: boolean
  onClose: () => void
  onProceed?: () => void
}) {
  const detailQuery = useQuery({
    queryKey: queryKeys.skillFocus(scenario.slug),
    queryFn: () => scenariosApi.getSkillFocus(scenario.slug),
    staleTime: 5 * 60 * 1000,
  })

  if (detailQuery.isLoading) {
    return (
      <Modal open title="Command preview" onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <div className="py-8 text-center text-sm text-muted-foreground">Loading preview...</div>
      </Modal>
    )
  }

  if (detailQuery.isError || !detailQuery.data) {
    return (
      <Modal open title="Command preview" onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {detailQuery.error?.message ?? 'Could not load the command preview.'}
        </div>
      </Modal>
    )
  }

  return (
    <SkillFocusPreviewContent
      scenario={detailQuery.data}
      difficulty={difficulty}
      action={action}
      isProceeding={Boolean(isProceeding)}
      onClose={onClose}
      onProceed={onProceed}
    />
  )
}

function SkillFocusPreviewContent({
  scenario,
  difficulty,
  action,
  isProceeding,
  onClose,
  onProceed,
}: {
  scenario: ScenarioSkillFocus
  difficulty?: DifficultyAccess
  action?: DifficultyActionIntent
  isProceeding: boolean
  onClose: () => void
  onProceed?: () => void
}) {
  const preview = scenario.command_preview
  const initialSnapshot = useMemo(
    () =>
      isRepositorySnapshot(preview?.demo_repository_state)
        ? preview.demo_repository_state
        : isRepositorySnapshot(scenario.demo_repository_state)
          ? scenario.demo_repository_state
          : emptyDemoSnapshot,
    [preview?.demo_repository_state, scenario.demo_repository_state],
  )
  const supportedDemoCommands = useMemo(
    () => preview?.supported_demo_commands ?? scenario.safe_demo_commands ?? [],
    [preview?.supported_demo_commands, scenario.safe_demo_commands],
  )
  const commands = useMemo(() => buildPreviewCommands(scenario, initialSnapshot), [initialSnapshot, scenario])
  const navGroups = useMemo(() => navigationGroupsFromCommands(commands), [commands])
  const [commandIndex, setCommandIndex] = useState(0)
  const [pageIndex, setPageIndex] = useState(0)
  const [view, setView] = useState<'content' | 'demo'>('content')
  const [isNavigatorOpen, setIsNavigatorOpen] = useState(false)
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({})
  const selectedCommand = commands[commandIndex] ?? commands[0]
  const selectedPage = selectedCommand.pages[pageIndex] ?? selectedCommand.pages[0]
  const selectedDemoStep = selectedCommand.demo_steps[0] ?? selectedPage.demo_steps[0] ?? null
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(() => selectedDemoStep?.repository_state ?? initialSnapshot)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>(demoBootLines)
  const [isRunningDemo, setIsRunningDemo] = useState(false)
  const difficultyLabel = difficulty
    ? difficulty.difficulty.charAt(0).toUpperCase() + difficulty.difficulty.slice(1)
    : null
  const startLabel =
    action === 'review'
      ? 'Open review'
      : action === 'continue' || action === 'resume'
        ? 'Continue'
        : action === 'retry'
          ? 'Retry scenario'
          : 'Start scenario'
  const previousLocation = previousReadingLocation(commands, commandIndex, pageIndex)
  const nextLocation = nextReadingLocation(commands, commandIndex, pageIndex)
  const canGoPrevious = Boolean(previousLocation)
  const canGoNext = Boolean(nextLocation)
  const isDemoView = view === 'demo'
  const previewLabel = preview?.diagnostic ? 'Diagnostic command preview' : 'Command preview'

  function selectPage(nextCommandIndex: number, nextPageIndex: number) {
    const nextCommand = commands[nextCommandIndex]
    if (!nextCommand) return
    const nextPage = nextCommand.pages[nextPageIndex] ?? nextCommand.pages[0]
    if (!nextPage) return
    setCommandIndex(nextCommandIndex)
    setPageIndex(nextCommand.pages[nextPageIndex] ? nextPageIndex : 0)
    setView('content')
    setIsNavigatorOpen(false)
    setSnapshot(nextPage.demo_steps[0]?.repository_state ?? nextCommand.demo_steps[0]?.repository_state ?? initialSnapshot)
  }

  function toggleGroup(groupId: string) {
    setCollapsedGroups((groups) => ({ ...groups, [groupId]: !groups[groupId] }))
  }

  async function runDemoCommand(command: string) {
    setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'input', text: command }])
    setIsRunningDemo(true)
    const normalizedCommand = normalize(command)
    const nextCommandIndex = commands.findIndex((item) =>
      item.demo_steps.some((step) => normalize(step.command) === normalizedCommand),
    )

    try {
      const response = await scenariosApi.submitDemoCommand(scenario.slug, { command, repository_state: snapshot })
      if (isRepositorySnapshot(response.repository_state)) {
        setSnapshot(response.repository_state)
      }
      setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'output', text: response.terminal_output }])
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Could not run demo command.'
      setTerminalLines((items) => [...items, { id: crypto.randomUUID(), kind: 'warning', text: message }])
    } finally {
      setIsRunningDemo(false)
    }

    if (nextCommandIndex >= 0) {
      setCommandIndex(nextCommandIndex)
      setPageIndex(0)
      setView('demo')
    }
  }

  return (
    <Modal
      open
      title={preview?.title ?? 'Command preview'}
      onClose={onClose}
      className="max-h-[94vh] w-full max-w-6xl overflow-hidden"
      contentClassName="h-[calc(94vh-4.5rem)] overflow-hidden p-0"
    >
      <div className="relative flex h-full min-h-0 flex-col overflow-hidden">
        {isNavigatorOpen ? (
          <PreviewNavigator
            groups={navGroups}
            commands={commands}
            activeCommandIndex={commandIndex}
            activePageIndex={pageIndex}
            collapsedGroups={collapsedGroups}
            onClose={() => setIsNavigatorOpen(false)}
            onSelect={selectPage}
            onToggleGroup={toggleGroup}
          />
        ) : null}

        <main className="grid min-h-0 min-w-0 flex-1 grid-rows-[auto_minmax(0,1fr)] overflow-hidden">
          <header className="border-b border-border bg-card/60 p-5">
            <div className="flex min-w-0 flex-wrap items-start justify-between gap-4">
              <div className="flex min-w-0 items-start gap-3">
                <div className="grid size-10 shrink-0 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
                  {isDemoView ? <SquareTerminal className="size-5" /> : <BookOpen className="size-5" />}
                </div>
                <div className="min-w-0">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    {difficultyLabel ? <Badge variant="blue">{difficultyLabel}</Badge> : null}
                    <Badge variant="outline">{preview?.focus_label ?? scenario.focus}</Badge>
                  </div>
                  <p className="text-xs font-semibold uppercase text-primary">{previewLabel}</p>
                  <h3 className="mt-1 text-base font-extrabold leading-tight">{scenario.title}</h3>
                  {isDemoView ? (
                    <p className="mt-3 text-xs font-semibold uppercase text-muted-foreground">Demo</p>
                  ) : selectedCommand.command || selectedPage.eyebrow ? (
                    <p className="mt-3 truncate text-xs font-semibold uppercase text-muted-foreground">
                      {selectedCommand.command ?? selectedPage.eyebrow}
                    </p>
                  ) : null}
                  <h4 className="mt-1 text-xl font-extrabold leading-tight">
                    {isDemoView ? 'Try commands in a safe preview repository' : selectedPage.heading ?? selectedPage.title}
                  </h4>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {isDemoView ? 'Shared demo for this command preview' : `Page ${pageIndex + 1} of ${selectedCommand.pages.length}`}
                  </p>
                </div>
              </div>
              <Button type="button" size="sm" variant="outline" onClick={() => setIsNavigatorOpen(true)}>
                <ListTree data-icon="inline-start" />
                Contents
              </Button>
            </div>
          </header>

          <section className="min-h-0 min-w-0 overflow-auto p-5 app-scrollbar">
            {isDemoView ? (
              <PreviewDemoPanel
                commands={supportedDemoCommands}
                disabled={isRunningDemo || supportedDemoCommands.length === 0}
                lines={terminalLines}
                snapshot={snapshot}
                onCommand={runDemoCommand}
              />
            ) : (
              <PreviewContentPage page={selectedPage} />
            )}
          </section>
        </main>

        <footer className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-t border-border bg-card/70 px-5 py-4">
          <div className="flex flex-wrap gap-2">
            {isDemoView ? (
              <Button type="button" size="sm" variant="outline" onClick={() => setView('content')}>
                <ArrowLeft data-icon="inline-start" />
                Back to pages
              </Button>
            ) : (
              <>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!canGoPrevious}
                  onClick={() => previousLocation && selectPage(previousLocation.commandIndex, previousLocation.pageIndex)}
                >
                  <ArrowLeft data-icon="inline-start" />
                  Previous
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!canGoNext}
                  onClick={() => nextLocation && selectPage(nextLocation.commandIndex, nextLocation.pageIndex)}
                >
                  Next
                  <ArrowRight data-icon="inline-start" />
                </Button>
                <Button type="button" size="sm" variant="outline" onClick={() => setView('demo')}>
                  <SquareTerminal data-icon="inline-start" />
                  Open demo
                </Button>
              </>
            )}
          </div>
          {onProceed ? (
            <Button type="button" disabled={isProceeding} onClick={onProceed}>
              <Play data-icon="inline-start" />
              {isProceeding ? 'Opening...' : startLabel}
            </Button>
          ) : (
            <Button type="button" variant="outline" onClick={onClose}>
              Close preview
            </Button>
          )}
        </footer>
      </div>
    </Modal>
  )
}
