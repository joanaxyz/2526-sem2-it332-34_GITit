// The Chapter Book is a read-only reference: every command registered for a chapter,
// resolved to its rich authored content from the command library. Unlike the
// scenario command preview it carries no terminal demo - its blocks instead support
// richer authored content such as diagrams.

export type BookDiagramNode = {
  id: string
  label: string
  // dag: lane index + commit type; flow: stage accent.
  lane?: number
  type?: 'commit' | 'head' | 'branch' | 'merge'
  accent?: 'cyan' | 'purple' | 'muted'
}

export type BookDiagramEdge = {
  from: string
  to: string
  label?: string
}

type BookDiagramLegendItem = {
  label: string
  accent?: 'cyan' | 'purple' | 'muted'
}

export type BookBlock = {
  type?:
    | 'paragraph'
    | 'bullet_list'
    | 'list'
    | 'command'
    | 'code'
    | 'callout'
    | 'warning'
    | 'terminal_output'
    | 'diagram'
    | 'before_after'
    | 'comparison_table'
    | 'scenario'
    | 'quiz'
    | 'state_flow'
    | 'do_dont'
  title?: string
  body?: string
  text?: string
  items?: string[]
  command?: string
  language?: string
  before?: string[]
  after?: string[]
  do_items?: string[]
  dont_items?: string[]
  steps?: string[]
  question?: string
  choices?: string[]
  answer?: string
  rows?: Array<{ command?: string; use_when?: string; not_for?: string }>
  // diagram block
  diagram_kind?: 'dag' | 'flow' | string
  caption?: string
  nodes?: BookDiagramNode[]
  edges?: BookDiagramEdge[]
  legend?: BookDiagramLegendItem[]
}

export type BookPage = {
  id?: string
  title: string
  heading?: string
  eyebrow?: string
  subtitle?: string
  body?: string
  section_type?: string
  blocks?: BookBlock[]
}

type BookCommandForm = {
  id: number
  slug: string
  usage_form: string
  label: string
  summary: string
  is_playable: boolean
}

export type BookCommand = {
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  tags: string[]
  forms: BookCommandForm[]
  pages: BookPage[]
}

export type BookLesson = {
  item_type: 'lesson'
  id: number
  slug: string
  title: string
  summary: string
  pages: BookPage[]
}

export type ChapterBook = {
  chapter_id: number
  slug: string
  number: number
  title: string
  description: string
  command_count: number
  commands: BookCommand[]
  lesson_count: number
  lessons: BookLesson[]
}
