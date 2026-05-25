import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import type {
  CommandPreviewBlock,
  CommandPreviewCommand,
  CommandPreviewPage,
  CommandPreviewSection,
  DemoExplanationStep,
  ScenarioSkillFocus,
} from '@/features/scenarios/types'

export const emptyDemoSnapshot: RepositorySnapshot = {
  commits: [],
  branches: { 'demo-main': null },
  head: { type: 'branch', name: 'demo-main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

export const demoBootLines: TerminalLine[] = [
  { id: 'demo-boot-1', kind: 'system', text: 'Inline demo repository loaded.' },
  { id: 'demo-boot-2', kind: 'output', text: 'Run one of the preview commands to watch the shared DAG update.' },
]

export type PreviewCommand = {
  id: string
  title: string
  command?: string
  baseCommand: string
  summary?: string
  pages: PreviewPage[]
  demo_steps: DemoExplanationStep[]
}

export type PreviewPage = Omit<CommandPreviewPage, 'id'> & {
  id: string
  kind: 'content'
  demo_steps: DemoExplanationStep[]
}

export type PreviewNavGroup = {
  id: string
  title: string
  commandIndexes: number[]
}

export type PreviewAnchor = {
  id: string
  label: string
  sectionType?: string
}

export function buildPreviewCommands(
  scenario: ScenarioSkillFocus,
  fallbackSnapshot: RepositorySnapshot,
): PreviewCommand[] {
  const resolvedCommands = scenario.command_preview?.commands?.filter((command) => command.pages?.length || command.sections?.length) ?? []
  if (resolvedCommands.length) {
    return commandsFromResolvedCommands(resolvedCommands, fallbackSnapshot).filter(hasReadableCommand)
  }

  const configuredSections = scenario.command_preview?.sections?.filter(hasSectionContent) ?? []
  if (configuredSections.length) {
    return commandsFromSections(configuredSections, fallbackSnapshot).filter(hasReadableCommand)
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
    ).filter(hasReadableCommand)
  }

  return commandsFromSections(
    [
      {
        id: 'overview',
        title: scenario.focus || 'Command focus',
        command: scenario.primary_focus_commands[0],
        explanation: scenario.short_explanation ?? scenario.summary,
        syntax_examples: scenario.command_preview?.syntax_examples ?? scenario.primary_focus_commands,
        common_mistakes: scenario.command_preview?.common_mistakes ?? [],
        demo_steps: [],
      },
    ],
    fallbackSnapshot,
  ).filter(hasReadableCommand)
}

export function navigationGroupsFromCommands(commands: PreviewCommand[]): PreviewNavGroup[] {
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

export function navigationAnchorsForCommand(command: PreviewCommand): PreviewAnchor[] {
  const anchors = command.pages
    .map((page, index) => ({ page, index }))
    .filter(({ page }) => isNavigationSection(page.section_type))
    .map(({ page, index }) => ({
      id: page.id,
      label: navigationLabelForPage(page, command.baseCommand),
      sectionType: page.section_type,
      order: navigationSectionOrder(page.section_type),
      index,
    }))
    .filter((anchor) => anchor.label)
    .sort((first, second) => first.order - second.order || first.index - second.index)

  const seen = new Set<string>()
  const deduped: PreviewAnchor[] = []
  for (const anchor of anchors) {
    const key = normalize(anchor.label)
    if (seen.has(key)) continue
    seen.add(key)
    deduped.push({ id: anchor.id, label: anchor.label, sectionType: anchor.sectionType })
  }
  return deduped
}

export function previewAnchorDomId(commandId: string, anchorId: string) {
  return `preview-${slugForDomId(commandId)}-${slugForDomId(anchorId)}`
}

export function previousReadingLocation(commands: PreviewCommand[], commandIndex: number, pageIndex: number) {
  if (pageIndex > 0) return { commandIndex, pageIndex: pageIndex - 1 }
  for (let index = commandIndex - 1; index >= 0; index -= 1) {
    const previousCommand = commands[index]
    if (previousCommand?.pages.length) {
      return { commandIndex: index, pageIndex: previousCommand.pages.length - 1 }
    }
  }
  return null
}

export function nextReadingLocation(commands: PreviewCommand[], commandIndex: number, pageIndex: number) {
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

export function normalize(command: string) {
  return command.trim().replace(/\s+/g, ' ').toLowerCase()
}

export function isRepositorySnapshot(value: unknown): value is RepositorySnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as Partial<RepositorySnapshot>
  return Array.isArray(snapshot.commits) && Boolean((snapshot as RepositorySnapshot).head)
}

function hasSectionContent(section: CommandPreviewSection) {
  return Boolean(section.title && (section.explanation || section.content?.length || section.pages?.length))
}

function hasReadableCommand(command: PreviewCommand) {
  return Boolean(command.command?.trim() || command.pages.some((page) => page.eyebrow?.trim()))
}

function isNavigationSection(sectionType?: string) {
  return sectionType === 'form' || sectionType === 'option' || sectionType === 'argument'
}

function navigationSectionOrder(sectionType?: string) {
  if (sectionType === 'form') return 0
  if (sectionType === 'option') return 1
  if (sectionType === 'argument') return 2
  return 3
}

function navigationLabelForPage(page: PreviewPage, baseCommand: string) {
  const source = page.eyebrow || page.heading || page.title
  if (!source) return ''
  if (page.section_type === 'option' || page.section_type === 'argument') {
    return source.replace(/^Option:\s*/i, '').replace(/^Argument:\s*/i, '')
  }
  const normalizedSource = normalize(source)
  const normalizedBase = normalize(baseCommand)
  if (normalizedBase && normalizedSource.startsWith(normalizedBase)) {
    const suffix = source.slice(baseCommand.length).trim()
    return suffix
  }
  return source
}

function slugForDomId(value: string) {
  return normalize(value).replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '') || 'section'
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
      summary: command.summary,
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
    summary: sections.find((section) => section.explanation)?.explanation,
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
  fallbackCommonMistake = 'Skipping diagnostics before choosing an action.',
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

function canonicalCommand(command: string) {
  const normalized = normalize(command)
  if (!normalized) return 'Command'
  if (normalized === '.gitignore') return '.gitignore'
  const parts = normalized.split(' ')
  if (parts[0] !== 'git') return command
  if (!parts[1]) return 'git'
  return `git ${parts[1]}`
}
