// The Storey Book is a read-only reference: every command registered for a storey,
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

export type BookDiagramLegendItem = {
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
  title?: string
  body?: string
  text?: string
  items?: string[]
  command?: string
  language?: string
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

export type BookCommand = {
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  tags: string[]
  pages: BookPage[]
}

export type StoreyBook = {
  storey_id: number
  slug: string
  number: number
  title: string
  description: string
  command_count: number
  commands: BookCommand[]
}
