import { ArrowRight, FolderGit2, FolderOpen } from 'lucide-react'
import type { ReactNode } from 'react'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import type { RepositorySnapshot } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

type Change = CommandIntroduction['needs'][number]
type ChipState = 'stay' | 'leave' | 'arrive'
type Chip = { name: string; state: ChipState }

const MAX_CHIPS = 4
// Changes that draw something fading out, so the legend only explains what is on screen.
const LEAVING = new Set([
  'staging:add', 'staging:remove', 'commit:create', 'working_tree:remove', 'branch:delete', 'head:move',
])
const MAX_COMMITS = 3

/**
 * A before/after sketch of what the next command changes, drawn from the
 * current repository and the move's structured changes. It picks the picture
 * that fits: a folder becoming a repository, files moving between the working
 * tree, staging area and history, or branch and HEAD pointers moving. Other
 * changes have no picture; the change list beside it already says them.
 *
 * Decorative for assistive technology: the change list carries the same facts.
 */
export function RepositoryChangeDiagram({
  changes,
  repository,
}: {
  changes: readonly Change[]
  repository: RepositorySnapshot | undefined
}) {
  const kinds = new Set(changes.map((change) => change.kind))
  let picture: ReactNode = null
  if (kinds.has('repository')) picture = <NewRepository repository={repository} />
  else if (kinds.has('staging') || kinds.has('working_tree') || kinds.has('commit')) {
    picture = <Areas changes={changes} repository={repository} />
  } else if (kinds.has('branch') || kinds.has('head')) {
    picture = <Pointers changes={changes} repository={repository} />
  } else if (kinds.has('remote')) {
    picture = <Remotes changes={changes} />
  }
  if (!picture) return null
  const leaves = changes.some((change) => LEAVING.has(`${change.kind}:${change.action ?? ''}`))
  return (
    <figure className="change-diagram" aria-hidden="true">
      {picture}
      <figcaption className="change-diagram__legend">
        <span className="change-diagram__key is-arrive">new or moved here</span>
        {leaves ? <span className="change-diagram__key is-leave">leaves</span> : null}
      </figcaption>
    </figure>
  )
}

function NewRepository({ repository }: { repository: RepositorySnapshot | undefined }) {
  const files = Object.keys(repository?.working_tree ?? {})
  return (
    <div className="change-diagram__row">
      <div className="change-diagram__area">
        <p className="change-diagram__area-title"><FolderOpen aria-hidden="true" />Project folder</p>
        <Chips chips={files.map((name) => ({ name, state: 'stay' }))} empty="Your files" />
      </div>
      <ArrowRight className="change-diagram__arrow" aria-hidden="true" />
      <div className="change-diagram__area is-target">
        <p className="change-diagram__area-title"><FolderGit2 aria-hidden="true" />Repository</p>
        <Chips chips={[{ name: '.git', state: 'arrive' }, ...files.map((name) => ({ name, state: 'stay' as const }))]} />
      </div>
    </div>
  )
}

function Areas({ changes, repository }: { changes: readonly Change[]; repository: RepositorySnapshot | undefined }) {
  const working = new Map<string, ChipState>(Object.keys(repository?.working_tree ?? {}).map((name) => [name, 'stay']))
  const staged = new Map<string, ChipState>(Object.keys(repository?.staging ?? {}).map((name) => [name, 'stay']))
  let newCommit: Change | null = null
  let toStaging = false
  let toWorking = false
  for (const change of changes) {
    const subjects = change.subjects ?? []
    if (change.kind === 'staging' && change.action === 'add') {
      toStaging = true
      for (const name of subjects) {
        if (working.has(name)) working.set(name, 'leave')
        staged.set(name, 'arrive')
      }
    } else if (change.kind === 'staging' && change.action === 'remove') {
      toWorking = true
      for (const name of subjects) {
        staged.set(name, 'leave')
        working.set(name, 'arrive')
      }
    } else if (change.kind === 'working_tree') {
      for (const name of subjects) working.set(name, change.action === 'remove' ? 'leave' : 'arrive')
    } else if (change.kind === 'commit') {
      newCommit = change
      for (const name of subjects) if (staged.has(name)) staged.set(name, 'leave')
    }
  }
  const commits = headChain(repository).slice(-MAX_COMMITS)
  // Stacked top to bottom: file names get the full width, and the order reads
  // like the path a change takes (edit, stage, commit).
  return (
    <div className="change-diagram__row is-stacked">
      <div className={cn('change-diagram__area', toWorking && 'is-target')}>
        <p className="change-diagram__area-title">Working tree</p>
        <Chips chips={[...working].map(([name, state]) => ({ name, state }))} empty="No edits" />
      </div>
      <Flow active={toStaging} reverse={toWorking} />
      <div className={cn('change-diagram__area', toStaging && 'is-target')}>
        <p className="change-diagram__area-title">Staging area</p>
        <Chips chips={[...staged].map(([name, state]) => ({ name, state }))} empty="Empty" />
      </div>
      <Flow active={Boolean(newCommit)} />
      <div className={cn('change-diagram__area', newCommit && 'is-target')}>
        <p className="change-diagram__area-title">History</p>
        <ol className="change-diagram__commits">
          {commits.map((commit) => <li key={commit} className="change-diagram__commit" />)}
          {newCommit ? <li className="change-diagram__commit is-arrive" /> : null}
          {!commits.length && !newCommit ? <li className="change-diagram__empty">No commits yet</li> : null}
        </ol>
        {newCommit?.ref ? <p className="change-diagram__ref">{newCommit.ref}</p> : null}
      </div>
    </div>
  )
}

function Pointers({ changes, repository }: { changes: readonly Change[]; repository: RepositorySnapshot | undefined }) {
  const commits = headChain(repository).slice(-MAX_COMMITS)
  const headBranch = repository?.head?.type === 'branch' ? repository.head.name ?? null : null
  const created = new Set<string>()
  const deleted = new Set<string>()
  let headTo: string | null = null
  let headMoves = false
  for (const change of changes) {
    const subjects = change.subjects ?? []
    if (change.kind === 'branch' && change.action === 'create') subjects.forEach((name) => created.add(name))
    if (change.kind === 'branch' && change.action === 'delete') subjects.forEach((name) => deleted.add(name))
    if (change.kind === 'head') {
      headMoves = true
      headTo = subjects[0] ?? null
    }
  }
  // Labels on the current commit: its branches, plus new ones created there.
  const tip = commits[commits.length - 1]
  const onTip = Object.entries(repository?.branches ?? {})
    .filter(([, target]) => (tip ? target === tip : target === null))
    .map(([name]) => name)
  const labels = [...new Set([...onTip, ...created])]
  const headOn = headMoves ? headTo : headBranch
  return (
    <div className="change-diagram__pointers">
      <ol className="change-diagram__commits is-line">
        {commits.map((commit) => <li key={commit} className="change-diagram__commit" />)}
        {!commits.length ? <li className="change-diagram__empty">No commits yet</li> : null}
      </ol>
      <ul className="change-diagram__labels">
        {labels.map((name) => (
          <li
            key={name}
            className={cn(
              'change-diagram__label',
              created.has(name) && 'is-arrive',
              deleted.has(name) && 'is-leave',
            )}
          >
            {name}
            {headOn === name ? <span className="change-diagram__head is-arrive">HEAD</span> : null}
            {headMoves && headBranch === name && headOn !== name ? (
              <span className="change-diagram__head is-leave">HEAD</span>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Remotes({ changes }: { changes: readonly Change[] }) {
  const updated = changes.filter((change) => change.kind === 'remote').flatMap((change) => change.subjects ?? [])
  const remotes = [...new Set(updated.map((name) => name.split('/')[0]))]
  return (
    <div className="change-diagram__row">
      <div className="change-diagram__area">
        <p className="change-diagram__area-title">Your repository</p>
        <Chips chips={updated.map((name) => ({ name, state: 'arrive' }))} empty="Remote-tracking branches" />
      </div>
      <ArrowRight className="change-diagram__arrow is-both" aria-hidden="true" />
      <div className="change-diagram__area">
        <p className="change-diagram__area-title">{remotes.join(', ') || 'Remote'}</p>
        <p className="change-diagram__empty">Shared copy</p>
      </div>
    </div>
  )
}

function Flow({ active, reverse = false }: { active: boolean; reverse?: boolean }) {
  return (
    <ArrowRight
      className={cn('change-diagram__arrow', (active || reverse) && 'is-active', reverse && 'is-reverse')}
      aria-hidden="true"
    />
  )
}

function Chips({ chips, empty }: { chips: readonly Chip[]; empty?: string }) {
  // Moving files first, so what the command touches is never hidden in "+ more".
  const ordered = [...chips].sort((left, right) => Number(right.state !== 'stay') - Number(left.state !== 'stay'))
  const shown = ordered.slice(0, MAX_CHIPS)
  const hidden = ordered.length - shown.length
  if (!ordered.length) return empty ? <p className="change-diagram__empty">{empty}</p> : null
  return (
    <ul className="change-diagram__chips">
      {shown.map((chip) => (
        <li key={chip.name} className={cn('change-diagram__chip', `is-${chip.state}`)}>{chip.name}</li>
      ))}
      {hidden > 0 ? <li className="change-diagram__more">+{hidden} more</li> : null}
    </ul>
  )
}

/** The commits behind HEAD, oldest first, following first parents. */
function headChain(repository: RepositorySnapshot | undefined): string[] {
  if (!repository) return []
  const byId = new Map(repository.commits.map((commit) => [commit.id, commit]))
  const head = repository.head
  let current = head?.type === 'branch' ? repository.branches[head.name ?? ''] ?? null : head?.target ?? null
  const chain: string[] = []
  while (current && byId.has(current) && chain.length < 12) {
    chain.unshift(current)
    current = byId.get(current)?.parents?.[0] ?? null
  }
  return chain
}
