import type { ComponentProps } from 'react'

import { cn } from '@/shared/utils/cn'

export type GitCommandDefinition = {
  slug: GitCommandSlug
  command: string
  title: string
}

const COMMAND_ICON_URLS = {
  'git-init': new URL('../../../assets/images/git-commands/git-init.svg', import.meta.url).href,
  'git-clone': new URL('../../../assets/images/git-commands/git-clone.svg', import.meta.url).href,
  'git-status': new URL('../../../assets/images/git-commands/git-status.svg', import.meta.url).href,
  'git-config': new URL('../../../assets/images/git-commands/git-config.svg', import.meta.url).href,
  'git-log': new URL('../../../assets/images/git-commands/git-log.svg', import.meta.url).href,
  'git-show': new URL('../../../assets/images/git-commands/git-show.svg', import.meta.url).href,
  'git-diff': new URL('../../../assets/images/git-commands/git-diff.svg', import.meta.url).href,
  'git-add': new URL('../../../assets/images/git-commands/git-add.svg', import.meta.url).href,
  'git-commit': new URL('../../../assets/images/git-commands/git-commit.svg', import.meta.url).href,
  'git-rm': new URL('../../../assets/images/git-commands/git-rm.svg', import.meta.url).href,
  'git-check-ignore': new URL('../../../assets/images/git-commands/git-check-ignore.svg', import.meta.url).href,
  'git-restore': new URL('../../../assets/images/git-commands/git-restore.svg', import.meta.url).href,
  'git-branch': new URL('../../../assets/images/git-commands/git-branch.svg', import.meta.url).href,
  'git-switch': new URL('../../../assets/images/git-commands/git-switch.svg', import.meta.url).href,
  'git-checkout': new URL('../../../assets/images/git-commands/git-checkout.svg', import.meta.url).href,
  'git-merge': new URL('../../../assets/images/git-commands/git-merge.svg', import.meta.url).href,
  'git-merge-base': new URL('../../../assets/images/git-commands/git-merge-base.svg', import.meta.url).href,
  'git-checkout-conflict': new URL('../../../assets/images/git-commands/git-checkout-conflict.svg', import.meta.url).href,
  'git-diff-conflict': new URL('../../../assets/images/git-commands/git-diff-conflict.svg', import.meta.url).href,
  'git-ls-files': new URL('../../../assets/images/git-commands/git-ls-files.svg', import.meta.url).href,
  'git-mergetool': new URL('../../../assets/images/git-commands/git-mergetool.svg', import.meta.url).href,
  'git-reset': new URL('../../../assets/images/git-commands/git-reset.svg', import.meta.url).href,
  'git-revert': new URL('../../../assets/images/git-commands/git-revert.svg', import.meta.url).href,
  'git-reflog': new URL('../../../assets/images/git-commands/git-reflog.svg', import.meta.url).href,
  'git-stash': new URL('../../../assets/images/git-commands/git-stash.svg', import.meta.url).href,
  'git-cherry-pick': new URL('../../../assets/images/git-commands/git-cherry-pick.svg', import.meta.url).href,
  'git-remote': new URL('../../../assets/images/git-commands/git-remote.svg', import.meta.url).href,
  'git-fetch': new URL('../../../assets/images/git-commands/git-fetch.svg', import.meta.url).href,
  'git-pull': new URL('../../../assets/images/git-commands/git-pull.svg', import.meta.url).href,
  'git-push': new URL('../../../assets/images/git-commands/git-push.svg', import.meta.url).href,
  'git-rebase': new URL('../../../assets/images/git-commands/git-rebase.svg', import.meta.url).href,
  'git-tag': new URL('../../../assets/images/git-commands/git-tag.svg', import.meta.url).href,
  'git-rev-list': new URL('../../../assets/images/git-commands/git-rev-list.svg', import.meta.url).href,
  default: new URL('../../../assets/images/git-commands/default.svg', import.meta.url).href,
} as const

export type GitCommandSlug = keyof typeof COMMAND_ICON_URLS


export const GIT_COMMAND_CATALOG: GitCommandDefinition[] = [
  { slug: 'git-init', command: 'git init', title: 'Initialize repository' },
  { slug: 'git-clone', command: 'git clone', title: 'Clone repository' },
  { slug: 'git-status', command: 'git status', title: 'Read repository state' },
  { slug: 'git-config', command: 'git config', title: 'Configure identity' },
  { slug: 'git-log', command: 'git log', title: 'Inspect history' },
  { slug: 'git-show', command: 'git show', title: 'Inspect object' },
  { slug: 'git-diff', command: 'git diff', title: 'Compare changes' },
  { slug: 'git-add', command: 'git add', title: 'Stage changes' },
  { slug: 'git-commit', command: 'git commit', title: 'Create snapshot' },
  { slug: 'git-rm', command: 'git rm', title: 'Remove tracked paths' },
  { slug: 'git-check-ignore', command: 'git check-ignore', title: 'Explain ignores' },
  { slug: 'git-restore', command: 'git restore', title: 'Restore files' },
  { slug: 'git-branch', command: 'git branch', title: 'Manage branches' },
  { slug: 'git-switch', command: 'git switch', title: 'Switch branches' },
  { slug: 'git-checkout', command: 'git checkout', title: 'Checkout legacy paths' },
  { slug: 'git-merge', command: 'git merge', title: 'Merge histories' },
  { slug: 'git-merge-base', command: 'git merge-base', title: 'Find common base' },
  { slug: 'git-checkout-conflict', command: 'git checkout --ours', title: 'Choose conflict side' },
  { slug: 'git-diff-conflict', command: 'git diff --ours', title: 'Compare conflict side' },
  { slug: 'git-ls-files', command: 'git ls-files', title: 'Inspect index files' },
  { slug: 'git-mergetool', command: 'git mergetool', title: 'Open merge tool' },
  { slug: 'git-reset', command: 'git reset', title: 'Reset history' },
  { slug: 'git-revert', command: 'git revert', title: 'Revert safely' },
  { slug: 'git-reflog', command: 'git reflog', title: 'Recover history' },
  { slug: 'git-stash', command: 'git stash', title: 'Shelve work' },
  { slug: 'git-cherry-pick', command: 'git cherry-pick', title: 'Pick a commit' },
  { slug: 'git-remote', command: 'git remote', title: 'Inspect remotes' },
  { slug: 'git-fetch', command: 'git fetch', title: 'Fetch remote refs' },
  { slug: 'git-pull', command: 'git pull', title: 'Pull upstream work' },
  { slug: 'git-push', command: 'git push', title: 'Publish work' },
  { slug: 'git-rebase', command: 'git rebase', title: 'Replay commits' },
  { slug: 'git-tag', command: 'git tag', title: 'Mark releases' },
  { slug: 'git-rev-list', command: 'git rev-list', title: 'List revisions' },
]

const KNOWN_COMMAND_SLUGS = new Set<GitCommandSlug>(Object.keys(COMMAND_ICON_URLS) as GitCommandSlug[])

function slugFromVerb(verb: string): GitCommandSlug {
  const candidate = `git-${verb}` as GitCommandSlug
  return KNOWN_COMMAND_SLUGS.has(candidate) ? candidate : 'default'
}

export function gitCommandSlug(command: string | null | undefined): GitCommandSlug {
  const normalized = command?.trim().toLowerCase().replace(/\s+/g, ' ') ?? ''
  if (!normalized) return 'default'
  if (normalized.startsWith('git checkout --ours') || normalized.startsWith('git checkout --theirs')) {
    return 'git-checkout-conflict'
  }
  if (
    normalized.startsWith('git diff --ours') ||
    normalized.startsWith('git diff --theirs') ||
    normalized.startsWith('git diff --base')
  ) {
    return 'git-diff-conflict'
  }

  const parts = normalized.split(' ')
  if (parts[0] !== 'git' || !parts[1]) return 'default'
  return slugFromVerb(parts[1])
}

export function gitCommandFamily(command: string | null | undefined): string {
  const slug = gitCommandSlug(command)
  return slug === 'default' ? 'default' : slug.replace(/^git-/, '')
}

export function gitCommandIconUrl(command: string | null | undefined): string {
  return COMMAND_ICON_URLS[gitCommandSlug(command)]
}

export function GitCommandIcon({
  command,
  slug,
  label,
  className,
  ...props
}: Omit<ComponentProps<'img'>, 'src' | 'alt'> & {
  command?: string | null
  slug?: GitCommandSlug
  label?: string
}) {
  const resolvedSlug = slug ?? gitCommandSlug(command)
  return (
    <img
      {...props}
      className={cn('git-command-icon', className)}
      src={COMMAND_ICON_URLS[resolvedSlug]}
      alt={label ?? ''}
      aria-hidden={label ? props['aria-hidden'] : true}
    />
  )
}
