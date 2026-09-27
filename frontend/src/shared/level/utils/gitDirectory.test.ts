import { describe, expect, it } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'
import { buildGitDirectory, repositoryFolderName, type GitDirectoryNode } from './gitDirectory'

const cloned: RepositorySnapshot = {
  repository_initialized: true,
  commits: [
    { id: 'r40', message: 'Export Q1 access log', parents: [], tree: { 'README.md': 'audit' } },
    { id: 'r41', message: 'Document CSV columns', parents: ['r40'], tree: { 'README.md': 'audit v2' } },
  ],
  branches: { main: 'r41' },
  head: { type: 'branch', name: 'main', target: 'r41' },
  staging: {},
  working_tree: {},
  conflicts: [],
  remotes: { origin: 'https://git.corp.example/it/audit-logs.git' },
  remote_branches: { 'origin/main': 'r41' },
  upstream_tracking: { main: 'origin/main' },
  tags: { 'v1.0': { target: 'r40', annotated: true, message: 'first' } },
  operation_metadata: {
    last_clone_url: 'https://git.corp.example/it/audit-logs.git',
    last_clone_directory: 'audit-logs-local',
    last_clone_branch: 'main',
    last_clone_shallow: false,
  },
}

function files(node: GitDirectoryNode): Record<string, string> {
  if (node.type === 'file') return { [node.path]: node.content ?? '' }
  return Object.assign({}, ...node.children.map(files))
}

describe('buildGitDirectory', () => {
  it('has no .git before git init or git clone', () => {
    expect(buildGitDirectory({ ...cloned, repository_initialized: false })).toBeNull()
  })

  it('writes HEAD, config and refs the way git clone does', () => {
    const git = buildGitDirectory(cloned)!
    expect(files(git)).toEqual({
      '.git/HEAD': 'ref: refs/heads/main\n',
      '.git/config': [
        '[core]',
        '\trepositoryformatversion = 0',
        '\tfilemode = true',
        '\tbare = false',
        '[remote "origin"]',
        '\turl = https://git.corp.example/it/audit-logs.git',
        '\tfetch = +refs/heads/*:refs/remotes/origin/*',
        '[branch "main"]',
        '\tremote = origin',
        '\tmerge = refs/heads/main',
        '',
      ].join('\n'),
      '.git/refs/heads/main': 'r41\n',
      '.git/refs/remotes/origin/HEAD': 'ref: refs/remotes/origin/main\n',
      '.git/refs/remotes/origin/main': 'r41\n',
      '.git/refs/tags/v1.0': 'r40\n',
    })
    expect(git.children.map((child) => child.name)).toEqual(['refs', 'config', 'HEAD'])
  })

  it('keeps empty refs folders after git init and marks detached HEAD, merges and shallow clones', () => {
    const fresh = buildGitDirectory({
      ...cloned,
      commits: [],
      branches: { main: null },
      head: { type: 'branch', name: 'main', target: null },
      remotes: {},
      remote_branches: {},
      upstream_tracking: {},
      tags: {},
      operation_metadata: {},
    })!
    const refs = fresh.children.find((child) => child.name === 'refs')!
    expect(refs.children.map((child) => child.name)).toEqual(['heads', 'tags'])

    const busy = files(
      buildGitDirectory({
        ...cloned,
        commits: [cloned.commits[1]].map((commit) => ({ ...commit, parents: [] })),
        head: { type: 'detached', target: 'r41' },
        merge_parent: 'r99',
        operation_metadata: { ...cloned.operation_metadata, last_clone_shallow: true },
      })!,
    )
    expect(busy['.git/HEAD']).toBe('r41\n')
    expect(busy['.git/MERGE_HEAD']).toBe('r99\n')
    expect(busy['.git/shallow']).toBe('r41\n')
  })
})

describe('repositoryFolderName', () => {
  it('uses a named clone or init destination, else the project folder', () => {
    expect(repositoryFolderName(cloned, 'cloning-a-remote-repository')).toBe('audit-logs-local')
    expect(repositoryFolderName({ operation_metadata: { last_init_directory: 'new-app/' } }, 'demo')).toBe('new-app')
    expect(repositoryFolderName({ operation_metadata: { last_init_directory: '.' } }, 'demo')).toBe('demo')
    expect(repositoryFolderName({ operation_metadata: { last_init_directory: null } }, 'demo')).toBe('demo')
    expect(repositoryFolderName({}, 'demo')).toBe('demo')
  })
})
