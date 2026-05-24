import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  ChevronDown,
  ChevronRight,
  Code2,
  GitBranch,
  ListTree,
  Play,
  SquareTerminal,
  X,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { DemoLiveDagPanel } from '@/features/scenarios/components/DemoLiveDagPanel'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type {
  CommandPreviewBlock,
  CommandPreviewCommand,
  CommandPreviewPage,
  CommandPreviewSection,
  DemoExplanationStep,
  DifficultyAccess,
  DifficultyActionIntent,
  ScenarioSkillFocus,
} from '@/features/scenarios/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { cn } from '@/shared/utils/cn'

const emptyDemoSnapshot: RepositorySnapshot = {
  commits: [],
  branches: { 'demo-main': null },
  head: { type: 'branch', name: 'demo-main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const demoBootLines: TerminalLine[] = [
  { id: 'demo-boot-1', kind: 'system', text: 'Inline demo repository loaded.' },
  { id: 'demo-boot-2', kind: 'output', text: 'Run one of the preview commands to watch the shared DAG update.' },
]

type PreviewCommand = {
  id: string
  title: string
  command?: string
  baseCommand: string
  pages: PreviewPage[]
  demo_steps: DemoExplanationStep[]
}

type PreviewPage = CommandPreviewPage & {
  kind: 'content'
  demo_steps: DemoExplanationStep[]
}

type PreviewNavGroup = {
  id: string
  title: string
  commandIndexes: number[]
}

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
    queryKey: ['skill-focus', scenario.slug],
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
          <PreviewNavigatorOverlay
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
                  <p className="text-xs font-semibold uppercase text-primary">Scenario preview</p>
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
                    {isDemoView ? 'Shared demo for this scenario preview' : `Page ${pageIndex + 1} of ${selectedCommand.pages.length}`}
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
              <DemoPage
                commands={supportedDemoCommands}
                disabled={isRunningDemo || supportedDemoCommands.length === 0}
                lines={terminalLines}
                snapshot={snapshot}
                onCommand={runDemoCommand}
              />
            ) : (
              <ContentPage page={selectedPage} />
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

function PreviewNavigatorOverlay({
  groups,
  commands,
  activeCommandIndex,
  activePageIndex,
  collapsedGroups,
  onClose,
  onSelect,
  onToggleGroup,
}: {
  groups: PreviewNavGroup[]
  commands: PreviewCommand[]
  activeCommandIndex: number
  activePageIndex: number
  collapsedGroups: Record<string, boolean>
  onClose: () => void
  onSelect: (commandIndex: number, pageIndex: number) => void
  onToggleGroup: (groupId: string) => void
}) {
  return (
    <div className="absolute inset-0 z-20 bg-background/70 backdrop-blur-sm" role="dialog" aria-label="Command preview contents">
      <div className="flex h-full w-full max-w-md flex-col border-r border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <div>
            <p className="text-xs font-semibold uppercase text-primary">Contents</p>
            <h4 className="text-base font-extrabold">Command guide</h4>
          </div>
          <Button type="button" size="icon" variant="ghost" onClick={onClose} aria-label="Close contents">
            <X className="size-4" />
          </Button>
        </div>
        <nav className="min-h-0 flex-1 overflow-y-auto p-3 app-scrollbar" aria-label="Command preview contents">
          {groups.map((group) => {
            const collapsed = Boolean(collapsedGroups[group.id])
            const active = group.commandIndexes.includes(activeCommandIndex)
            return (
              <section className="border-b border-border/70 py-2 last:border-b-0" key={group.id}>
                <button
                  aria-expanded={!collapsed}
                  className={cn(
                    'flex w-full min-w-0 items-center gap-2 rounded-md px-2 py-2 text-left transition hover:bg-secondary',
                    active && 'text-foreground',
                  )}
                  type="button"
                  onClick={() => onToggleGroup(group.id)}
                >
                  {collapsed ? <ChevronRight className="size-4 shrink-0" /> : <ChevronDown className="size-4 shrink-0" />}
                  <span className="min-w-0 flex-1 truncate font-mono text-sm font-bold">{group.title}</span>
                  <span className="rounded-sm border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground">
                    {group.commandIndexes.reduce((total, commandIndex) => total + commands[commandIndex].pages.length, 0)}
                  </span>
                </button>
                {!collapsed ? (
                  <div className="mt-1 grid gap-1 pl-6">
                    {group.commandIndexes.map((commandIndex) => {
                      const command = commands[commandIndex]
                      return command.pages.map((page, pageIndex) => {
                        const selected = commandIndex === activeCommandIndex && pageIndex === activePageIndex
                        const label = page.heading ?? page.title
                        return (
                          <button
                            aria-current={selected ? 'page' : undefined}
                            aria-label={`Open ${command.command || command.title}: ${label}`}
                            className={cn(
                              'grid min-h-12 min-w-0 rounded-md px-2 py-2 text-left transition hover:bg-secondary',
                              selected ? 'bg-primary/10 text-foreground' : 'text-muted-foreground',
                            )}
                            key={`${command.id}-${page.id ?? pageIndex}`}
                            type="button"
                            onClick={() => onSelect(commandIndex, pageIndex)}
                          >
                            <span className="truncate text-sm font-semibold">{label}</span>
                            <span className="truncate font-mono text-[11px]">{command.command || command.title}</span>
                          </button>
                        )
                      })
                    })}
                  </div>
                ) : null}
              </section>
            )
          })}
        </nav>
      </div>
    </div>
  )
}

function ContentPage({ page }: { page: PreviewPage }) {
  return (
    <article className="mx-auto grid min-w-0 max-w-3xl gap-4">
      {page.subtitle ? <p className="text-sm leading-6 text-muted-foreground">{page.subtitle}</p> : null}
      {page.body ? <p className="text-base leading-7 text-muted-foreground">{page.body}</p> : null}
      {(page.blocks ?? []).map((block, index) => (
        <PreviewBlock block={block} key={`${block.title ?? block.type ?? 'block'}-${index}`} />
      ))}
    </article>
  )
}

function PreviewBlock({ block }: { block: CommandPreviewBlock }) {
  const body = block.body ?? block.text
  const codeItems = block.items?.length ? block.items : block.command ? [block.command] : body ? [body] : []

  if (block.type === 'paragraph') {
    return (
      <section className="grid gap-2">
        {block.title ? <h5 className="text-sm font-bold">{block.title}</h5> : null}
        {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
      </section>
    )
  }

  if (block.type === 'code' || block.type === 'command') {
    return (
      <section className="rounded-md border border-border bg-card p-4">
        {block.title ? (
          <h5 className="mb-3 flex items-center gap-2 text-sm font-bold">
            <Code2 className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        <div className="grid gap-2">
          {codeItems.map((item) => (
            <code
              className="block overflow-x-auto rounded-sm border border-border bg-secondary/30 px-3 py-2 text-xs text-foreground"
              key={item}
            >
              {item}
            </code>
          ))}
        </div>
      </section>
    )
  }

  if (block.type === 'terminal_output') {
    return (
      <section className="rounded-md border border-border bg-zinc-950 p-4 text-zinc-100">
        {block.title ? (
          <h5 className="mb-3 flex items-center gap-2 text-sm font-bold">
            <SquareTerminal className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        <pre className="overflow-x-auto whitespace-pre-wrap text-xs leading-5">{body}</pre>
      </section>
    )
  }

  if (block.type === 'warning') {
    return (
      <section className="rounded-md border border-amber-500/30 bg-amber-500/10 p-4">
        {block.title ? (
          <h5 className="mb-2 flex items-center gap-2 text-sm font-bold text-amber-700 dark:text-amber-300">
            <AlertTriangle className="size-4" />
            {block.title}
          </h5>
        ) : null}
        {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
        {block.items?.length ? <BlockList items={block.items} /> : null}
      </section>
    )
  }

  if (block.type === 'bullet_list' || block.type === 'list') {
    return (
      <section className="rounded-md border border-border bg-card p-4">
        {block.title ? (
          <h5 className="mb-2 flex items-center gap-2 text-sm font-bold">
            <GitBranch className="size-4 text-primary" />
            {block.title}
          </h5>
        ) : null}
        {body ? <p className="mb-3 text-sm leading-6 text-muted-foreground">{body}</p> : null}
        {block.items?.length ? <BlockList items={block.items} /> : null}
      </section>
    )
  }

  return (
    <section
      className={cn(
        'rounded-md border border-border bg-card p-4',
        (block.type === 'callout' || block.type === 'dag_note' || block.type === 'demo_step_ref') && 'bg-primary/5',
      )}
    >
      {block.title ? (
        <h5 className="mb-2 flex items-center gap-2 text-sm font-bold">
          <GitBranch className="size-4 text-primary" />
          {block.title}
        </h5>
      ) : null}
      {body ? <p className="text-sm leading-6 text-muted-foreground">{body}</p> : null}
      {block.items?.length ? <BlockList items={block.items} /> : null}
    </section>
  )
}

function BlockList({ items }: { items: string[] }) {
  return (
    <ul className="grid gap-2">
      {items.map((item) => (
        <li className="rounded-sm border border-border bg-secondary/20 px-3 py-2 text-sm leading-6 text-muted-foreground" key={item}>
          {item}
        </li>
      ))}
    </ul>
  )
}

function DemoPage({
  commands,
  disabled,
  lines,
  snapshot,
  onCommand,
}: {
  commands: string[]
  disabled: boolean
  lines: TerminalLine[]
  snapshot: RepositorySnapshot
  onCommand: (command: string) => void
}) {
  return (
    <div className="mx-auto grid max-w-4xl gap-4">
      <DemoLiveDagPanel snapshot={snapshot} />
      <section className="grid gap-3">
        <div className="rounded-md border border-border bg-card p-4">
          <h5 className="flex items-center gap-2 text-sm font-bold">
            <SquareTerminal className="size-4 text-primary" />
            Try it
          </h5>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Run any preview command here. This is a shared demo, separate from scenario attempts.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {commands.map((command) => (
              <button
                className="rounded-sm border border-border bg-secondary/30 px-2 py-1 font-mono text-[11px] text-muted-foreground hover:text-foreground"
                key={command}
                type="button"
                onClick={() => onCommand(command)}
              >
                {command}
              </button>
            ))}
          </div>
        </div>
        <TerminalPanel
          title="Inline command demo"
          className="h-72 rounded-md"
          disabled={disabled}
          lines={lines}
          onCommand={onCommand}
        />
      </section>
    </div>
  )
}

function buildPreviewCommands(
  scenario: ScenarioSkillFocus,
  fallbackSnapshot: RepositorySnapshot,
): PreviewCommand[] {
  const resolvedCommands = scenario.command_preview?.commands?.filter((command) => command.pages?.length || command.sections?.length) ?? []
  if (resolvedCommands.length) {
    return commandsFromResolvedCommands(resolvedCommands, fallbackSnapshot)
  }

  const configuredSections = scenario.command_preview?.sections?.filter(hasSectionContent) ?? []
  if (configuredSections.length) {
    return commandsFromSections(configuredSections, fallbackSnapshot)
  }

  const steps = normalizeDemoSteps(
    scenario.command_preview?.demo_steps?.length ? scenario.command_preview.demo_steps : scenario.demo_explanation_steps,
    fallbackSnapshot,
    scenario.command_preview?.short_explanation ?? scenario.short_explanation,
    scenario.command_preview?.common_mistakes?.[0],
  )

  if (steps.length) {
    return commandsFromSections(
      steps.map((step, index) => (
        {
          id: `${normalize(step.command)}-${index}`,
          title: step.title || step.command,
          command: step.command,
          explanation: step.explanation,
          syntax_examples: [step.command],
          common_mistakes: step.common_mistake ? [step.common_mistake] : [],
          demo_steps: [step],
        }
      )),
      fallbackSnapshot,
    )
  }

  return commandsFromSections(
    [
      {
        id: 'overview',
        title: scenario.focus || 'Scenario focus',
        command: scenario.primary_focus_commands[0],
        explanation: scenario.short_explanation ?? scenario.summary,
        syntax_examples: scenario.command_preview?.syntax_examples ?? scenario.primary_focus_commands,
        common_mistakes: scenario.command_preview?.common_mistakes ?? [],
        demo_steps: [],
      },
    ],
    fallbackSnapshot,
  )
}

function navigationGroupsFromCommands(commands: PreviewCommand[]): PreviewNavGroup[] {
  const groups: PreviewNavGroup[] = []
  const indexByTitle = new Map<string, number>()
  commands.forEach((command, commandIndex) => {
    const title = command.baseCommand || canonicalCommand(command.command ?? command.title)
    const groupIndex = indexByTitle.get(title)
    if (groupIndex === undefined) {
      indexByTitle.set(title, groups.length)
      groups.push({ id: `${normalize(title)}-${groups.length}`, title, commandIndexes: [commandIndex] })
      return
    }
    groups[groupIndex].commandIndexes.push(commandIndex)
  })
  return groups
}

function previousReadingLocation(commands: PreviewCommand[], commandIndex: number, pageIndex: number) {
  if (pageIndex > 0) return { commandIndex, pageIndex: pageIndex - 1 }
  for (let index = commandIndex - 1; index >= 0; index -= 1) {
    const previousCommand = commands[index]
    if (previousCommand?.pages.length) {
      return { commandIndex: index, pageIndex: previousCommand.pages.length - 1 }
    }
  }
  return null
}

function nextReadingLocation(commands: PreviewCommand[], commandIndex: number, pageIndex: number) {
  const currentCommand = commands[commandIndex]
  if (currentCommand && pageIndex < currentCommand.pages.length - 1) {
    return { commandIndex, pageIndex: pageIndex + 1 }
  }
  for (let index = commandIndex + 1; index < commands.length; index += 1) {
    if (commands[index]?.pages.length) {
      return { commandIndex: index, pageIndex: 0 }
    }
  }
  return null
}

function hasSectionContent(section: CommandPreviewSection) {
  return Boolean(section.title && (section.explanation || section.content?.length || section.pages?.length))
}

function commandsFromResolvedCommands(
  commands: CommandPreviewCommand[],
  fallbackSnapshot: RepositorySnapshot,
): PreviewCommand[] {
  return commands.map((command, index) => {
    const title = command.title || command.command || `Command ${index + 1}`
    const demoSteps = normalizeDemoSteps(
      command.demo_steps ?? [],
      fallbackSnapshot,
      command.summary,
    )
    const sourcePages = command.pages?.length
      ? command.pages
      : (command.sections ?? []).flatMap((section) => generatedPagesFromSection(section))
    const pages = sourcePages.map((page, pageIndex): PreviewPage => ({
      ...page,
      id: page.id ?? `${command.key ?? command.id ?? index}-page-${pageIndex}`,
      kind: 'content',
      demo_steps: normalizeDemoSteps(page.demo_steps ?? [], fallbackSnapshot, page.body ?? command.summary),
    }))
    return {
      id: command.id ?? command.key ?? `${normalize(title)}-${index}`,
      title,
      command: command.command || command.canonical_command,
      baseCommand: command.base_command || canonicalCommand(command.command || command.canonical_command || title),
      pages,
      demo_steps: demoSteps,
    }
  })
}

function commandsFromSections(sections: CommandPreviewSection[], fallbackSnapshot: RepositorySnapshot): PreviewCommand[] {
  const groups = new Map<string, CommandPreviewSection[]>()
  for (const section of sections) {
    const label = canonicalCommand(section.command ?? section.title)
    const group = groups.get(label) ?? []
    group.push(section)
    groups.set(label, group)
  }

  return Array.from(groups.entries()).map(([label, group], index) =>
    commandFromSections(label, group, index, fallbackSnapshot),
  )
}

function commandFromSections(
  label: string,
  sections: CommandPreviewSection[],
  index: number,
  fallbackSnapshot: RepositorySnapshot,
): PreviewCommand {
  const demoSteps = sections.flatMap((section) =>
    normalizeDemoSteps(section.demo_steps ?? [], fallbackSnapshot, section.explanation ?? '', section.common_mistakes?.[0]),
  )
  const authoredPages = sections.flatMap((section, sectionIndex) =>
    section.pages?.length
      ? section.pages.map((page, pageIndex): PreviewPage => ({
          ...page,
          id: page.id ?? `${section.id ?? index}-${sectionIndex}-page-${pageIndex}`,
          kind: 'content',
          demo_steps: normalizeDemoSteps(page.demo_steps ?? [], fallbackSnapshot, page.body ?? section.explanation ?? '', section.common_mistakes?.[0]),
        }))
      : generatedPagesFromSection(section),
  )

  return {
    id: `${normalize(label)}-${index}`,
    title: label,
    command: label,
    baseCommand: canonicalCommand(label),
    pages: authoredPages.length ? authoredPages : generatedPagesFromSection(sections[0]),
    demo_steps: demoSteps,
  }
}

function generatedPagesFromSection(section: CommandPreviewSection): PreviewPage[] {
  if (section.content?.length) {
    return [
      {
        id: section.id ?? `${section.title}-content`,
        title: section.title,
        eyebrow: section.command ?? section.token,
        heading: section.title,
        kind: 'content',
        section_type: section.type,
        blocks: section.content,
        demo_steps: [],
      },
    ]
  }

  const detailBlockCandidates: CommandPreviewBlock[] = [
    { type: 'code', title: 'Syntax examples', items: section.syntax_examples },
    { type: 'list', title: 'What it changes', items: section.what_changes },
    { type: 'list', title: 'What it does not change', items: section.what_does_not_change },
    { type: 'callout', title: 'Common mistakes', items: section.common_mistakes },
    { type: 'list', title: 'Readiness notes', items: section.readiness_notes },
  ]
  const detailBlocks = detailBlockCandidates.filter((block) => Boolean(block.items?.length))

  return [
    {
      id: `${section.id ?? section.title}-intro`,
      title: 'Introduction',
      eyebrow: section.command,
      heading: section.title,
      body: section.explanation ?? '',
      kind: 'content',
      demo_steps: [],
    },
    {
      id: `${section.id ?? section.title}-details`,
      title: 'Details',
      heading: 'Behavior and boundaries',
      kind: 'content',
      demo_steps: [],
      blocks: detailBlocks,
    },
  ]
}

function normalizeDemoSteps(
  value: unknown,
  fallbackSnapshot: RepositorySnapshot,
  fallbackExplanation?: string,
  fallbackCommonMistake = 'Skipping inspection before choosing an action.',
): DemoExplanationStep[] {
  if (!Array.isArray(value)) return []
  return value
    .map((item, index): DemoExplanationStep | null => {
      if (typeof item === 'string') {
        return {
          command: `Demo step ${index + 1}`,
          title: `Demo step ${index + 1}`,
          explanation: item || fallbackExplanation || '',
          repository_state: fallbackSnapshot,
          common_mistake: fallbackCommonMistake,
          diagnostic: false,
          counted: true,
        }
      }
      if (!item || typeof item !== 'object') return null
      const candidate = item as Partial<DemoExplanationStep>
      const command = typeof candidate.command === 'string' && candidate.command.trim()
        ? candidate.command
        : `Demo step ${index + 1}`
      return {
        command,
        title: typeof candidate.title === 'string' && candidate.title.trim() ? candidate.title : command,
        explanation:
          typeof candidate.explanation === 'string' && candidate.explanation.trim()
            ? candidate.explanation
            : fallbackExplanation || `Demo step ${index + 1}`,
        repository_state: isRepositorySnapshot(candidate.repository_state) ? candidate.repository_state : fallbackSnapshot,
        common_mistake:
          typeof candidate.common_mistake === 'string' && candidate.common_mistake.trim()
            ? candidate.common_mistake
            : fallbackCommonMistake,
        diagnostic: candidate.diagnostic ?? false,
        counted: candidate.counted ?? true,
      }
    })
    .filter((step): step is DemoExplanationStep => Boolean(step))
}

function normalize(command: string) {
  return command.trim().replace(/\s+/g, ' ').toLowerCase()
}

function canonicalCommand(command: string) {
  const normalized = normalize(command)
  if (!normalized) return 'Command'
  if (normalized === '.gitignore') return '.gitignore'
  const parts = normalized.split(' ')
  if (parts[0] !== 'git') return command
  if (!parts[1]) return 'git'
  return `git ${parts[1]}`
}

function isRepositorySnapshot(value: unknown): value is RepositorySnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as Partial<RepositorySnapshot>
  return Array.isArray(snapshot.commits) && Boolean((snapshot as RepositorySnapshot).head)
}
