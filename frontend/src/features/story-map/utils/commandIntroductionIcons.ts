import {
  Archive,
  Cloud,
  Crosshair,
  FilePen,
  FolderGit2,
  GitBranch,
  GitCommitHorizontal,
  GitCompareArrows,
  GitMerge,
  Hourglass,
  ListPlus,
  ScrollText,
  Settings2,
  Tag,
  TerminalSquare,
  Undo2,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type ChangeKind = ApiSchemas['RepositoryChange']['kind']

const iconByFamily: Record<string, LucideIcon> = {
  init: FolderGit2,
  clone: FolderGit2,
  add: ListPlus,
  rm: ListPlus,
  mv: ListPlus,
  commit: GitCommitHorizontal,
  branch: GitBranch,
  switch: GitBranch,
  checkout: GitBranch,
  merge: GitMerge,
  rebase: GitMerge,
  'cherry-pick': GitMerge,
  mergetool: GitMerge,
  restore: Undo2,
  reset: Undo2,
  revert: Undo2,
  remote: Cloud,
  fetch: Cloud,
  pull: Cloud,
  push: Cloud,
  stash: Archive,
  tag: Tag,
  config: Settings2,
  log: ScrollText,
  show: ScrollText,
  diff: ScrollText,
  status: ScrollText,
}

const iconByChange: Record<ChangeKind, LucideIcon> = {
  repository: FolderGit2,
  commit: GitCommitHorizontal,
  branch: GitBranch,
  head: Crosshair,
  staging: ListPlus,
  working_tree: FilePen,
  conflict: GitCompareArrows,
  tag: Tag,
  remote: Cloud,
  config: Settings2,
  stash: Archive,
  operation: Hourglass,
}

/** The icon for a command form, from its Git family (`git switch …` → branch). */
export function commandFamilyIcon(usageForm: string): LucideIcon {
  const family = usageForm.trim().split(/\s+/)[1] ?? ''
  return iconByFamily[family] ?? TerminalSquare
}

export function repositoryChangeIcon(kind: ChangeKind): LucideIcon {
  return iconByChange[kind] ?? TerminalSquare
}
