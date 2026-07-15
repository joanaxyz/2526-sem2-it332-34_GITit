import { hasOption } from '@/shared/git/simulator/parser'
import {
  commitById,
  headBranch,
  isRecord,
  treeForCommit,
} from '@/shared/git/simulator/state'
import { history, resolveRevision } from '@/shared/git/simulator/commands/refs'
import {
  SimulatorCommandError,
  type CommandOutcome,
  type MutableRepositoryState,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'

export function gitVerifyCommit(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const commitId = requireRevision(state, parsed.args[0])
  return {
    command: 'verify-commit',
    stdout: signatureOutput(state, 'commit', commitId),
  }
}

export function gitVerifyTag(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const tagName = parsed.args[0]
  const tag = state.tags?.[tagName]
  if (tag === undefined) throw new SimulatorCommandError(`error: tag '${tagName}' not found.`)
  const target = isRecord(tag) ? String(tag.target ?? '') : String(tag)
  return {
    command: 'verify-tag',
    stdout: signatureOutput(state, 'tag', tagName, target),
  }
}

export function gitFsck(state: MutableRepositoryState): CommandOutcome {
  const known = new Set((state.commits ?? []).map((commit) => commit.id))
  const errors: string[] = []
  for (const commit of state.commits ?? []) {
    for (const parent of commit.parents ?? []) {
      if (!known.has(parent)) errors.push(`broken link from commit ${commit.id} to commit ${parent}`)
    }
  }
  const reachable = new Set<string>()
  for (const target of [
    ...Object.values(state.branches ?? {}),
    ...Object.values(state.remote_branches ?? {}),
    ...Object.values(state.tags ?? {}).map((value) =>
      isRecord(value) ? String(value.target ?? '') : String(value ?? ''),
    ),
  ]) {
    for (const commitId of history(state, typeof target === 'string' ? target : null)) {
      reachable.add(commitId)
    }
  }
  for (const commit of state.commits ?? []) {
    if (!reachable.has(commit.id)) errors.push(`dangling commit ${commit.id}`)
  }
  return {
    command: 'fsck',
    stdout: errors.length
      ? errors.join('\n')
      : 'Checking object directories: 100% (256/256), done.\nChecking objects: 100%, done.',
  }
}

export function gitCountObjects(state: MutableRepositoryState): CommandOutcome {
  const commits = state.commits?.length ?? 0
  const blobs = new Set(
    (state.commits ?? []).flatMap((commit) =>
      Object.entries(commit.tree ?? {}).map(([path, value]) => `${path}:${JSON.stringify(value)}`),
    ),
  ).size
  const count = commits + blobs
  return {
    command: 'count-objects',
    stdout: [
      `count: ${count}`,
      `size: ${Math.max(1, Math.ceil(count / 4))} KiB`,
      'in-pack: 0',
      'packs: 0',
      'size-pack: 0 bytes',
      'prune-packable: 0',
      'garbage: 0',
    ].join('\n'),
  }
}

export function gitCatFile(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const objectName = parsed.args[0]
  const commitId = resolveRevision(state, objectName)
  const commit = commitById(state, commitId)
  if (!commit) throw new SimulatorCommandError(`fatal: Not a valid object name ${objectName}`)
  if (hasOption(parsed, '-t')) return { command: 'cat-file', stdout: 'commit' }
  return {
    command: 'cat-file',
    stdout: [
      `tree ${syntheticObjectId(JSON.stringify(commit.tree ?? {}))}`,
      ...(commit.parents ?? []).map((parent) => `parent ${parent}`),
      `author ${commit.author ?? 'GIT it'}`,
      '',
      commit.message,
    ].join('\n'),
  }
}

export function gitLsTree(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  const commitId = requireRevision(state, parsed.args[0])
  const tree = treeForCommit(state, commitId)
  return {
    command: 'ls-tree',
    stdout: Object.entries(tree)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([path, value]) => `100644 blob ${syntheticObjectId(JSON.stringify(value))}\t${path}`)
      .join('\n'),
  }
}

export function gitShowRef(state: MutableRepositoryState): CommandOutcome {
  const rows = [
    ...Object.entries(state.branches ?? {}).map(([name, target]) => [
      target,
      `refs/heads/${name}`,
    ]),
    ...Object.entries(state.tags ?? {}).map(([name, value]) => [
      isRecord(value) ? String(value.target ?? '') : String(value ?? ''),
      `refs/tags/${name}`,
    ]),
    ...Object.entries(state.remote_branches ?? {}).map(([name, target]) => [
      target,
      `refs/remotes/${name}`,
    ]),
  ]
  return {
    command: 'show-ref',
    stdout: rows
      .filter(([target]) => target)
      .sort((left, right) => String(left[1]).localeCompare(String(right[1])))
      .map(([target, ref]) => `${target} ${ref}`)
      .join('\n'),
  }
}

export function gitForEachRef(state: MutableRepositoryState): CommandOutcome {
  return gitShowRef(state)
}

export function gitSymbolicRef(
  state: MutableRepositoryState,
  parsed: ParsedGitCommand,
): CommandOutcome {
  if (parsed.args[0] !== 'HEAD') {
    throw new SimulatorCommandError('fatal: only symbolic-ref HEAD is supported')
  }
  const branch = headBranch(state)
  if (!branch) throw new SimulatorCommandError('fatal: ref HEAD is not a symbolic ref', 1)
  return { command: 'symbolic-ref', stdout: `refs/heads/${branch}` }
}

function requireRevision(state: MutableRepositoryState, revision: string) {
  const resolved = resolveRevision(state, revision)
  if (!resolved) throw new SimulatorCommandError(`fatal: ambiguous argument '${revision}'`)
  return resolved
}

function signatureOutput(
  state: MutableRepositoryState,
  kind: 'commit' | 'tag',
  name: string,
  target = name,
) {
  const signatures = isRecord(state.operation_metadata?.signatures)
    ? state.operation_metadata?.signatures
    : {}
  const authored = signatures?.[name]
  const signer = isRecord(authored) ? String(authored.signer ?? 'GIT it') : 'GIT it'
  return [
    `object ${target}`,
    `gpg: Good signature from "${signer}" [simulated trust]`,
    `${kind} ${name} verified`,
  ].join('\n')
}

function syntheticObjectId(value: string) {
  const chunks: string[] = []
  for (let salt = 0; salt < 5; salt += 1) {
    let hash = 0x811c9dc5 ^ salt
    for (let index = 0; index < value.length; index += 1) {
      hash ^= value.charCodeAt(index)
      hash = Math.imul(hash, 0x01000193)
    }
    chunks.push((hash >>> 0).toString(16).padStart(8, '0'))
  }
  return chunks.join('')
}
