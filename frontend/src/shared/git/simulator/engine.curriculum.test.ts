import { describe, expect, it } from 'vitest'

import { executeGitCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

// Coverage net for authored curriculum: every command form a chapter
// teaches must be *recognised and executed* by the browser engine (no "unknown option",
// "unknown switch", or "not a git command"). Behavioural depth for the tricky
// forms (rebase --onto, pull --ff-only) lives in the dedicated blocks below.

function uninitialized(): MutableRepositoryState {
  return {
    repository_initialized: false,
    commits: [],
    branches: {},
    head: { type: 'none', name: null },
    staging: {},
    working_tree: {},
    conflicts: [],
    remote_fixtures: {
      branches: { 'origin/main': 'r0', 'origin/starter': 'r0' },
      default_branch: 'origin/main',
      commits: [{ id: 'r0', message: 'Remote base', parents: [], tree: { 'README.md': 'remote' } }],
    },
  } as unknown as MutableRepositoryState
}

// main: c0 -> c1 ; feature branches off c0 at c2 (diverged, so merge/rebase/
// cherry-pick all have real work to do). Dirty worktree + a staged file + a
// .gitignore so add/restore/rm/diff/check-ignore have something to act on.
function repo(): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [
      { id: 'c0', message: 'init', parents: [], tree: { 'README.md': 'r0', 'src/app.py': 'a0' } },
      { id: 'c1', message: 'main work', parents: ['c0'], tree: { 'README.md': 'r1', 'src/app.py': 'a0' } },
      { id: 'c2', message: 'feature work', parents: ['c0'], tree: { 'README.md': 'r0', 'src/feature.py': 'f0' } },
    ],
    // `legacy` sits at c0 (an ancestor of main's tip) so `branch -d` accepts it;
    // `feature` diverged at c2 so it needs `-D`.
    branches: { main: 'c1', feature: 'c2', legacy: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c1' },
    staging: { 'staged.txt': { status: 'added', content: 's0' } },
    working_tree: {
      'README.md': { status: 'modified', content: 'r2' },
      'notes.txt': { status: 'untracked', content: 'n' },
      '.gitignore': '*.log\n',
    },
    conflicts: [],
    config: { 'user.name': 'Tester' },
    reflog: [
      { ref: 'HEAD@{0}', target: 'c1', message: 'commit: main work' },
      { ref: 'HEAD@{1}', target: 'c0', message: 'commit: init' },
    ],
    tags: { v0: { target: 'c0', annotated: false, message: '' } },
  } as MutableRepositoryState
}

function remoteRepo(): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [
      { id: 'c0', message: 'init', parents: [], tree: { 'README.md': 'r0' } },
      { id: 'c1', message: 'work', parents: ['c0'], tree: { 'README.md': 'r1' } },
    ],
    branches: { main: 'c1' },
    head: { type: 'branch', name: 'main', target: 'c1' },
    staging: {},
    working_tree: {},
    conflicts: [],
    remotes: { origin: 'https://example.test/app.git' },
    remote_branches: { 'origin/main': 'c1', 'origin/stale': 'c0' },
    upstream_tracking: { main: 'origin/main' },
    tags: { v1: { target: 'c1', annotated: true, message: 'release' } },
  } as MutableRepositoryState
}

// A state with a tracked file split into two hunks so `add -p` has a target hunk.
function partialHunkRepo(): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [{ id: 'c0', message: 'base', parents: [], tree: { 'src/auth.py': 'auth-v1' } }],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c0' },
    staging: {},
    working_tree: { 'src/auth.py': { status: 'modified', hunks: ['hunk-a', 'hunk-b'] } },
    partial_hunks: { 'src/auth.py': { target_hunks: ['hunk-a'], leftover_hunks: ['hunk-b'] } },
    conflicts: [],
  } as MutableRepositoryState
}

function assertRecognised(command: string, result: ReturnType<typeof executeGitCommand>) {
  expect(result.exit_code, `${command} -> ${result.output}`).not.toBe(127)
  expect(result.exit_code, `${command} -> ${result.output}`).not.toBe(129)
  expect(result.output).not.toMatch(/is not a git command|unknown option|unknown switch/i)
  expect(result.processed, `${command} -> ${result.output}`).toBe(true)
}

const CHAPTER_COMMANDS: Array<{ chapter: string; state: () => MutableRepositoryState; commands: string[] }> = [
  {
    chapter: 'Ch1 Foundations',
    state: uninitialized,
    commands: ['git init', 'git init project', 'git init -b trunk', 'git clone https://example.test/app.git', 'git clone https://example.test/app.git copy', 'git clone -b starter https://example.test/app.git', 'git clone --depth 1 https://example.test/app.git'],
  },
  {
    chapter: 'Ch1 read/save',
    state: repo,
    commands: [
      'git status', 'git status -s', 'git add README.md', 'git add .', 'git commit -m "snap"',
      'git log --oneline', 'git log --oneline --graph --all', 'git log -n 1', 'git log -p', 'git log --stat',
      'git show', 'git show c0', 'git diff', 'git diff --staged', 'git config --global user.email me@example.test',
      'git config --list', 'git config --global alias.co checkout', 'git check-ignore -v build.log',
    ],
  },
  {
    chapter: 'Ch2 Shaping',
    state: repo,
    commands: [
      'git diff HEAD', 'git diff -- README.md', 'git diff --stat', 'git add -u', 'git add -A',
      'git restore README.md', 'git restore --staged staged.txt', 'git restore --source c0 README.md',
      'git rm src/app.py', 'git rm --cached src/app.py', 'git rm -r --cached src',
      'git commit --amend -m "reword"', 'git commit --amend --no-edit',
    ],
  },
  {
    chapter: 'Ch3 Branching',
    state: repo,
    commands: [
      'git branch', 'git branch topic', 'git branch topic2 c0', 'git branch backup HEAD', 'git branch -v', 'git branch -m feature feature-x',
      'git branch -a', 'git switch feature', 'git switch -c brandnew', 'git checkout -b legacy-new',
      'git switch --detach c0', 'git branch -d legacy', 'git branch -D feature', 'git branch --merged',
    ],
  },
  {
    chapter: 'Ch4 Combining',
    state: repo,
    commands: ['git merge feature', 'git merge --no-ff feature', 'git merge --squash feature', 'git merge-base main feature', 'git rebase feature'],
  },
  {
    chapter: 'Ch5 Undo',
    state: repo,
    commands: ['git reset --soft c0', 'git reset --mixed c0', 'git reset --hard c0', 'git reset --hard HEAD~1', 'git reset --hard HEAD@{0}', 'git revert c0', 'git revert --no-edit c0', 'git reflog'],
  },
  {
    chapter: 'Ch6 Stash/Cherry/Tag',
    state: repo,
    commands: [
      'git stash', 'git stash -u', 'git stash -m "wip"', 'git stash list', 'git stash show', 'git stash pop',
      'git cherry-pick c2', 'git cherry-pick --no-commit c2', 'git tag v1', 'git tag -a v2 -m "rel"', 'git tag', 'git tag -d v0',
    ],
  },
  {
    chapter: 'Ch7 Remotes',
    state: remoteRepo,
    commands: [
      'git remote', 'git remote -v', 'git remote add upstream https://example.test/up.git', 'git remote set-url origin https://example.test/new.git',
      'git fetch origin', 'git fetch --prune', 'git fetch --all', 'git pull', 'git pull --rebase', 'git pull --ff-only',
      'git push -u origin main', 'git push', 'git push --force-with-lease', 'git push origin --delete stale', 'git push --tags',
    ],
  },
]

describe('curriculum command coverage', () => {
  for (const { chapter, state, commands } of CHAPTER_COMMANDS) {
    describe(chapter, () => {
      for (const command of commands) {
        it(`recognises ${command}`, () => {
          assertRecognised(command, executeGitCommand(state(), command))
        })
      }
    })
  }

  it('recognises add -p (hunk staging)', () => {
    assertRecognised('git add -p src/auth.py', executeGitCommand(partialHunkRepo(), 'git add -p src/auth.py'))
  })
})

// Conflict-dependent forms (Ch4 resolve): set up a real merge conflict first,
// then exercise the read/resolve commands against that state.
describe('conflict resolution commands', () => {
  function conflictedState(): MutableRepositoryState {
    const base: MutableRepositoryState = {
      repository_initialized: true,
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'app.js': 'base' } },
        { id: 'c1', message: 'ours', parents: ['c0'], tree: { 'app.js': 'ours' } },
        { id: 'c2', message: 'theirs', parents: ['c0'], tree: { 'app.js': 'theirs' } },
      ],
      branches: { main: 'c1', feature: 'c2' },
      head: { type: 'branch', name: 'main', target: 'c1' },
      staging: {},
      working_tree: {},
      conflicts: [],
    } as MutableRepositoryState
    const merged = executeGitCommand(base, 'git merge feature')
    expect(merged.next_state.conflicts).toContain('app.js')
    return merged.next_state as MutableRepositoryState
  }

  for (const command of ['git diff --base app.js', 'git diff --ours app.js', 'git diff --theirs app.js', 'git ls-files -u', 'git mergetool', 'git checkout --ours app.js', 'git checkout --theirs app.js', 'git merge --abort']) {
    it(`recognises ${command}`, () => {
      assertRecognised(command, executeGitCommand(conflictedState(), command))
    })
  }

  it('resolves then continues the merge', () => {
    let state = conflictedState()
    state = executeGitCommand(state, 'git checkout --theirs app.js').next_state as MutableRepositoryState
    state = executeGitCommand(state, 'git add app.js').next_state as MutableRepositoryState
    const continued = executeGitCommand(state, 'git merge --continue')
    assertRecognised('git merge --continue', continued)
    expect(continued.next_state.conflicts ?? []).toHaveLength(0)
  })
})

describe('branching from fetched remote refs', () => {
  it('creates a local branch at origin/main and switches to it', () => {
    const created = executeGitCommand(remoteRepo(), 'git branch feature/from-origin origin/main')
    assertRecognised('git branch feature/from-origin origin/main', created)

    const switched = executeGitCommand(created.next_state, 'git switch feature/from-origin')
    assertRecognised('git switch feature/from-origin', switched)
    expect(switched.next_state.head).toMatchObject({ type: 'branch', name: 'feature/from-origin' })
  })
})

describe('rebase --onto <newbase> <upstream> <branch>', () => {
  // main: c0 -> c1 -> c2.  topic forks at c1: c1 -> c3 -> c4.
  // `rebase --onto main c1 topic` should replay c3,c4 onto main's tip (c2).
  function divergedTopic(): MutableRepositoryState {
    return {
      repository_initialized: true,
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'a.txt': '0' } },
        { id: 'c1', message: 'old base', parents: ['c0'], tree: { 'a.txt': '1' } },
        { id: 'c2', message: 'main tip', parents: ['c1'], tree: { 'a.txt': '2' } },
        { id: 'c3', message: 'topic one', parents: ['c1'], tree: { 'a.txt': '1', 't.txt': '3' } },
        { id: 'c4', message: 'topic two', parents: ['c3'], tree: { 'a.txt': '1', 't.txt': '4' } },
      ],
      branches: { main: 'c2', topic: 'c4' },
      head: { type: 'branch', name: 'main', target: 'c2' },
      staging: {},
      working_tree: {},
      conflicts: [],
    } as MutableRepositoryState
  }

  it('moves the branch onto the new base and checks it out', () => {
    const result = executeGitCommand(divergedTopic(), 'git rebase --onto main c1 topic')
    const state = result.next_state

    expect(result.processed).toBe(true)
    // HEAD is now the rebased topic branch, not main.
    expect(state.head).toMatchObject({ type: 'branch', name: 'topic' })
    // main is untouched.
    expect(state.branches.main).toBe('c2')

    const commits = new Map(state.commits.map((c) => [c.id, c]))
    // Walk first-parents: replayed topic commits now sit on top of main's tip c2.
    const tip = commits.get(String(state.branches.topic))!
    const tipParent = commits.get(String(tip.parents[0]))!
    expect(tipParent.parents[0]).toBe('c2')
    // Topic's content (t.txt) survived the replay.
    expect(tip.tree?.['t.txt']).toBe('4')
    expect(tip.tree?.['a.txt']).toBe('2')
  })

  it('still supports plain rebase <upstream>', () => {
    // topic forked at c1; rebase topic onto main (c2).
    let state = divergedTopic()
    state = executeGitCommand(state, 'git switch topic').next_state as MutableRepositoryState
    const result = executeGitCommand(state, 'git rebase main')
    expect(result.processed).toBe(true)
    const tip = result.next_state.commits.find((c) => c.id === result.next_state.branches.topic)!
    expect(tip.tree?.['a.txt']).toBe('2')
    expect(tip.tree?.['t.txt']).toBe('4')
  })
})

describe('pull --ff-only', () => {
  function withRemote(localMain: string, remoteMain: string): MutableRepositoryState {
    return {
      repository_initialized: true,
      commits: [
        { id: 'c0', message: 'base', parents: [], tree: { 'a.txt': '0' } },
        { id: 'c1', message: 'remote', parents: ['c0'], tree: { 'a.txt': '1' } },
        { id: 'c2', message: 'local', parents: ['c0'], tree: { 'a.txt': '2' } },
      ],
      branches: { main: localMain },
      head: { type: 'branch', name: 'main', target: localMain },
      staging: {},
      working_tree: {},
      conflicts: [],
      remotes: { origin: 'https://example.test/app.git' },
      remote_branches: { 'origin/main': remoteMain },
      upstream_tracking: { main: 'origin/main' },
    } as MutableRepositoryState
  }

  it('fast-forwards when the local branch is behind', () => {
    const result = executeGitCommand(withRemote('c0', 'c1'), 'git pull --ff-only')
    expect(result.processed).toBe(true)
    expect(result.next_state.branches.main).toBe('c1')
    expect(result.output).toContain('Fast-forward')
  })

  it('refuses (does not merge) on divergence', () => {
    const result = executeGitCommand(withRemote('c2', 'c1'), 'git pull --ff-only')
    expect(result.processed).toBe(false)
    expect(result.exit_code).toBe(128)
    expect(result.output).toContain('Not possible to fast-forward')
    // The local branch is left exactly where it was - no merge commit created.
    expect(result.next_state.branches.main).toBe('c2')
  })
})
