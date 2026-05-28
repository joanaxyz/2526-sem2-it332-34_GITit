import type { RepositorySnapshot } from '@/features/practice/types'

export type OrientationLayout =
  | 'storyboard'
  | 'guide_terminal'
  | 'explorer_shell'
  | 'pipeline_status'
  | 'anatomy'
  | 'dag_log'
  | 'command_builder'
  | 'platform_tour'

export type OrientationStep = {
  id: string
  kind: string
  title: string
  prompt: string
  body?: string
  hint?: string
  accept_prefixes?: string[]
  accept_exact?: string[]
  require_processed?: boolean
  success_output?: string
  initial_state?: RepositorySnapshot
  options?: Array<{ id: string; label: string; detail: string }>
  pairs?: Array<{ scenario: string; problem: string }>
  stages?: string[]
  sample_output?: string
  parts?: string[]
  target?: string
  error_text?: string
  answer?: string
  hotspots?: string[]
}

export type OrientationLessonSession = {
  id: number
  lesson_id: number
  repository_state: RepositorySnapshot
  command_log: Array<{
    command: string
    normalized_command: string
    stdout: string
    stderr: string
    exit_code: number
    processed: boolean
    accepted: boolean
  }>
}

export type OrientationCommandResult = {
  accepted: boolean
  hint: string | null
  session: OrientationLessonSession
  output: string
  stderr: string
  exit_code: number
  normalized_command: string
}

export const LESSON_LAYOUT_BY_SLUG: Record<string, OrientationLayout> = {
  'what-is-git-and-why-it-matters': 'storyboard',
  'installing-git-and-environment': 'guide_terminal',
  'command-line-basics': 'explorer_shell',
  'git-diagram-four-areas': 'pipeline_status',
  'commits-and-history': 'anatomy',
  'reading-a-dag': 'dag_log',
  'git-command-anatomy': 'command_builder',
  'how-git-it-works': 'platform_tour',
}

export const CRITICAL_LESSON_SLUGS = new Set([
  'git-diagram-four-areas',
  'reading-a-dag',
  'git-command-anatomy',
])

export function displayLessonTitle(title: string) {
  return title.replace(/^Lesson\s+0\.\d+\s*[—–-]\s*/i, '').trim()
}

export function normalizeBuilderCommand(command: string) {
  return command
    .toLowerCase()
    .replace(/[""]/g, '"')
    .replace(/\s+/g, ' ')
    .trim()
}
