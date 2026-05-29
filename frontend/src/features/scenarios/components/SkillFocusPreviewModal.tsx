import { useQuery } from '@tanstack/react-query'
import { BookOpen, ChevronLeft, ChevronRight, ListTree, Play, SquareTerminal } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'

import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { PreviewCommandContent } from '@/features/scenarios/components/PreviewCommandContent'
import { PreviewDemoPanel } from '@/features/scenarios/components/PreviewDemoPanel'
import { PreviewNavigator } from '@/features/scenarios/components/PreviewNavigator'
import {
  buildPreviewCommands,
  demoBootLines,
  emptyDemoSnapshot,
  isRepositorySnapshot,
  navigationGroupsFromCommands,
  normalize,
  previewAnchorDomId,
} from '@/features/scenarios/components/previewPayloadUtils'
import type { PreviewCommand } from '@/features/scenarios/components/previewPayloadUtils'
import type {
  DifficultyAccess,
  DifficultyActionIntent,
  ScenarioSkillFocus,
} from '@/features/scenarios/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { LoadingState } from '@/shared/components/LoadingState'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

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
        <LoadingState
          description="Loading command guidance and the safe demo."
          label="Loading preview"
          variant="inline"
        />
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
  const [view, setView] = useState<'content' | 'demo'>('content')
  const [isNavigatorOpen, setIsNavigatorOpen] = useState(false)
  const selectedCommand = commands[commandIndex] ?? commands[0]
  const selectedDemoStep = selectedCommand.demo_steps[0] ?? selectedCommand.pages.find((page) => page.demo_steps[0])?.demo_steps[0] ?? null
  const [snapshot, setSnapshot] = useState<RepositorySnapshot>(() => selectedDemoStep?.repository_state ?? initialSnapshot)
  const [terminalLines, setTerminalLines] = useState<TerminalLine[]>(demoBootLines)
  const [isRunningDemo, setIsRunningDemo] = useState(false)
  const contentRef = useRef<HTMLElement | null>(null)
  const [pendingScroll, setPendingScroll] = useState<{ commandIndex: number; anchorId: string; nonce: number } | null>(null)
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
  const isDemoView = view === 'demo'
  const modalTitle = preview?.command_title || scenario.title || preview?.title || 'Command preview'
  const commandLabel = selectedCommand.command || selectedCommand.title

  useEffect(() => {
    if (!pendingScroll || pendingScroll.commandIndex !== commandIndex || view !== 'content') return
    const container = contentRef.current
    if (!container) return

    if (pendingScroll.anchorId === 'top') {
      if (typeof container.scrollTo === 'function') {
        container.scrollTo({ top: 0, behavior: 'smooth' })
      } else {
        container.scrollTop = 0
      }
      return
    }

    const target = document.getElementById(previewAnchorDomId(selectedCommand.id, pendingScroll.anchorId))
    if (target && typeof target.scrollIntoView === 'function') {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [commandIndex, pendingScroll, selectedCommand.id, view])

  function selectCommand(nextCommandIndex: number, anchorId = 'top') {
    const nextCommand = commands[nextCommandIndex]
    if (!nextCommand) return
    setCommandIndex(nextCommandIndex)
    setView('content')
    setIsNavigatorOpen(false)
    setPendingScroll({ commandIndex: nextCommandIndex, anchorId, nonce: Date.now() })
    setSnapshot(nextCommand.pages[0]?.demo_steps[0]?.repository_state ?? nextCommand.demo_steps[0]?.repository_state ?? initialSnapshot)
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
      setView('demo')
    }
  }

  return (
    <Modal
      open
      title={modalTitle}
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
            onClose={() => setIsNavigatorOpen(false)}
            onSelect={selectCommand}
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
                  {difficultyLabel ? (
                    <div className="mb-2">
                      <Badge variant="blue">{difficultyLabel}</Badge>
                    </div>
                  ) : null}
                  <h3 className={cn('mt-1 text-xl font-extrabold leading-tight', !isDemoView && 'font-mono')}>
                    {isDemoView ? 'Safe command demo' : commandLabel}
                  </h3>
                </div>
              </div>
              <Button
                aria-label="Open contents"
                title="Contents"
                type="button"
                size="icon"
                variant="outline"
                onClick={() => setIsNavigatorOpen(true)}
              >
                <ListTree className="size-5" />
              </Button>
            </div>
          </header>

          <section className="min-h-0 min-w-0 overflow-auto p-5 app-scrollbar" ref={contentRef}>
            {isDemoView ? (
              <PreviewDemoPanel
                commands={supportedDemoCommands}
                disabled={isRunningDemo || supportedDemoCommands.length === 0}
                lines={terminalLines}
                snapshot={snapshot}
                onCommand={runDemoCommand}
              />
            ) : (
              <PreviewCommandContent command={selectedCommand} />
            )}
          </section>
        </main>

        <footer className="grid shrink-0 grid-cols-[1fr_auto_1fr] items-center gap-3 border-t border-border bg-card/70 px-5 py-4 max-md:grid-cols-1">
          <div className="flex gap-2">
            {isDemoView ? (
              <Button
                aria-label="Back to command guide"
                title="Back to command guide"
                type="button"
                size="icon"
                variant="outline"
                onClick={() => selectCommand(commandIndex)}
              >
                <BookOpen className="size-5" />
              </Button>
            ) : (
              <Button
                aria-label="Open demo"
                title="Open demo"
                type="button"
                size="icon"
                variant="outline"
                onClick={() => setView('demo')}
              >
                <SquareTerminal className="size-5" />
              </Button>
            )}
          </div>
          <CommandPagination commands={commands} activeCommandIndex={commandIndex} onSelect={selectCommand} />
          {onProceed ? (
            <Button className="justify-self-end max-md:justify-self-start" type="button" disabled={isProceeding} onClick={onProceed}>
              <Play data-icon="inline-start" />
              {isProceeding ? 'Opening...' : startLabel}
            </Button>
          ) : (
            <div />
          )}
        </footer>
      </div>
    </Modal>
  )
}

function CommandPagination({
  commands,
  activeCommandIndex,
  onSelect,
}: {
  commands: PreviewCommand[]
  activeCommandIndex: number
  onSelect: (commandIndex: number) => void
}) {
  const canGoPrevious = activeCommandIndex > 0
  const canGoNext = activeCommandIndex < commands.length - 1

  return (
    <div className="flex items-center justify-center gap-2" aria-label="Commands">
      <Button
        aria-label="Previous command"
        title="Previous command"
        className="size-8 rounded-sm"
        disabled={!canGoPrevious}
        type="button"
        size="icon"
        variant="ghost"
        onClick={() => onSelect(activeCommandIndex - 1)}
      >
        <ChevronLeft className="size-4" />
      </Button>
      <div className="flex min-w-0 items-center gap-1.5">
        {commands.map((command, index) => {
          const selected = index === activeCommandIndex
          const label = command.command || command.title
          return (
            <button
              aria-current={selected ? 'page' : undefined}
              aria-label={`Switch to ${label}`}
              title={label}
              className={cn(
                'grid size-5 place-items-center rounded-full transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
                selected ? 'text-primary' : 'text-muted-foreground hover:text-foreground',
              )}
              key={command.id}
              type="button"
              onClick={() => onSelect(index)}
            >
              <span className={cn('block rounded-full', selected ? 'size-2.5 bg-primary' : 'size-2 bg-muted-foreground/45')} />
            </button>
          )
        })}
      </div>
      <Button
        aria-label="Next command"
        title="Next command"
        className="size-8 rounded-sm"
        disabled={!canGoNext}
        type="button"
        size="icon"
        variant="ghost"
        onClick={() => onSelect(activeCommandIndex + 1)}
      >
        <ChevronRight className="size-4" />
      </Button>
    </div>
  )
}
