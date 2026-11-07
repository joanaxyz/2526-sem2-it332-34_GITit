import { describe, expect, it } from 'vitest'

import { executeTerminalCommand } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { pathKind } from '@/shared/git/simulator/workspaceTree'

function repo(overrides: Partial<MutableRepositoryState> = {}): MutableRepositoryState {
  return {
    repository_initialized: true,
    commits: [
      {
        id: 'c0',
        message: 'base',
        parents: [],
        tree: { 'README.md': 'hello\n', '.gitignore': '*.log\n', 'src/app.ts': 'app', 'src/util.ts': 'util' },
      },
    ],
    branches: { main: 'c0' },
    head: { type: 'branch', name: 'main', target: 'c0' },
    staging: {},
    working_tree: {},
    conflicts: [],
    conflict_details: {},
    ...overrides,
  }
}

/** Run commands in order, threading state and location like the terminal does. */
function session(commands: string[], start = repo()) {
  let state = start
  let cwd = ''
  let outside = false
  const executions = commands.map((command) => {
    const terminal = executeTerminalCommand(state, command, { cwd, outside, projectName: 'demo' })
    state = terminal.execution.next_state
    cwd = terminal.cwd
    outside = terminal.outside
    return terminal.execution
  })
  return { state, cwd, outside, executions, last: executions.at(-1)! }
}

function emptyFolder(overrides: Partial<MutableRepositoryState> = {}) {
  return repo({
    repository_initialized: false,
    commits: [],
    branches: {},
    head: { type: 'branch', name: 'main', target: null },
    working_tree: { 'recipes.md': { status: 'untracked', content: 'soup\n' } },
    ...overrides,
  })
}

describe('workspace shell', () => {
  it('lists folders and files, hiding dotfiles unless asked', () => {
    expect(session(['ls']).last.output).toBe('README.md  src/')
    expect(session(['ls -a']).last.output).toBe('./  ../  .git/  .gitignore  README.md  src/')
    expect(session(['ls src']).last.output).toBe('app.ts  util.ts')
    expect(session(['ls missing']).last).toMatchObject({ exit_code: 2, stderr: "ls: cannot access 'missing': No such file or directory" })
  })

  it('navigates folders and keeps git paths relative to the working directory', () => {
    const { cwd, executions } = session(['cd src', 'pwd', 'cd ..', 'pwd'])
    expect(executions.map((execution) => execution.output)).toEqual(['', '/workspace/demo/src', '', '/workspace/demo'])
    expect(cwd).toBe('')
    expect(session(['cd ..', 'cd ..']).last.output).toBe('cd: ..: outside the project folder')
    expect(session(['cd README.md']).last.output).toBe('cd: README.md: Not a directory')
  })

  it('marks read-only commands as free diagnostics and file commands as replayable changes', () => {
    const { executions } = session(['ls', 'cd src', 'touch notes.md', 'echo hi'])
    expect(executions.map((execution) => [execution.command_family, execution.diagnostic])).toEqual([
      ['ls', true],
      ['cd', true],
      ['touch', false],
      ['echo', true],
    ])
    expect(executions[2]).toMatchObject({ processed: true, cwd: 'src' })
  })

  it('creates files and folders the way a real shell does', () => {
    const { state, executions } = session([
      'touch notes.md',
      'touch docs/guide.md',
      'mkdir docs',
      'mkdir docs',
      'mkdir -p assets/img',
      'touch docs/guide.md',
    ])
    expect(executions.map((execution) => execution.exit_code)).toEqual([0, 1, 0, 1, 0, 0])
    expect(executions[1].output).toBe("touch: cannot touch 'docs/guide.md': No such file or directory")
    expect(executions[3].output).toBe("mkdir: cannot create directory 'docs': File exists")
    expect(state.working_tree['notes.md']).toEqual({ status: 'untracked', content: '' })
    expect(state.working_tree['docs/guide.md']).toEqual({ status: 'untracked', content: '' })
    expect(state.directories).toEqual(['assets/img'])
  })

  it('removes files and folders with rm and rmdir', () => {
    const { state, executions } = session([
      'rm src',
      'rmdir src',
      'rm src/util.ts',
      'rm -r src',
      'rm -f missing.txt',
      'rm missing.txt',
    ])
    expect(executions.map((execution) => execution.output)).toEqual([
      "rm: cannot remove 'src': Is a directory",
      "rmdir: failed to remove 'src': Directory not empty",
      '',
      '',
      '',
      "rm: cannot remove 'missing.txt': No such file or directory",
    ])
    expect(state.working_tree['src/app.ts']).toBe('deleted')
    expect(state.working_tree['src/util.ts']).toBe('deleted')
    expect(pathKind(state, 'src')).toBeNull()
  })

  it('leaves an emptied folder in place and falls back when the working directory disappears', () => {
    const emptied = session(['cd src', 'rm app.ts util.ts', 'ls'])
    expect(emptied.cwd).toBe('src')
    expect(pathKind(emptied.state, 'src')).toBe('directory')

    const removed = session(['cd src', 'rm -r ../src', 'pwd'])
    expect(removed.last.output).toBe('/workspace/demo')
  })

  it('moves and copies files and folders', () => {
    const { state } = session(['mkdir lib', 'mv src/util.ts lib', 'cp README.md lib/README.copy', 'cp -r lib vendor', 'mv src source'])
    expect(state.working_tree['lib/util.ts']).toEqual({ status: 'untracked', content: 'util' })
    expect(state.working_tree['lib/README.copy']).toEqual({ status: 'untracked', content: 'hello\n' })
    expect(state.working_tree['vendor/util.ts']).toEqual({ status: 'untracked', content: 'util' })
    expect(state.working_tree['source/app.ts']).toEqual({ status: 'untracked', content: 'app' })
    expect(pathKind(state, 'src')).toBeNull()
    expect(session(['cp src copy']).last.output).toBe("cp: -r not specified; omitting directory 'src'")
    expect(session(['mv src src/inner']).last.output).toBe("mv: cannot move 'src' to a subdirectory of itself, 'src/inner'")
  })

  it('writes and appends with echo redirection and reads files back with cat', () => {
    const { state, executions } = session(['echo "# Demo" > README.md', 'echo more >> README.md', 'echo -n draft > notes.txt', 'cat README.md notes.txt'])
    expect(state.working_tree['README.md']).toEqual({ status: 'modified', content: '# Demo\nmore\n' })
    expect(state.working_tree['notes.txt']).toEqual({ status: 'untracked', content: 'draft' })
    expect(executions[3].output).toBe('# Demo\nmore\ndraft')
    expect(session(['ls > listing.txt']).last.exit_code).toBe(1)
  })

  it('expands globs against the working copy and respects ignore rules', () => {
    const { state } = session(['touch debug.log trace.log keep.txt', 'rm *.log'])
    expect(state.working_tree['debug.log']).toBeUndefined()
    expect(state.working_tree['keep.txt']).toEqual({ status: 'untracked', content: '' })
    expect(session(['touch a.log']).state.working_tree['a.log']).toEqual({ status: 'ignored', content: '' })
    expect(session(['echo src/*.ts']).last.output).toBe('src/app.ts src/util.ts')
    expect(session(["echo 'src/*.ts'"]).last.output).toBe('src/*.ts')
  })

  it('draws the project tree', () => {
    expect(session(['mkdir docs', 'tree']).last.output).toBe(
      ['.', '├── README.md', '├── docs', '└── src', '    ├── app.ts', '    └── util.ts', '', '2 directories, 3 files'].join('\n'),
    )
  })

  it('reports unsupported shell syntax without costing a command', () => {
    const { last } = session(['ls | grep src'])
    expect(last).toMatchObject({ processed: true, diagnostic: true, exit_code: 2 })
    expect(last.output).toContain('run one command at a time')
  })

  it('stages paths relative to the working directory', () => {
    const edited = session(['echo changed > README.md', 'cd src', 'echo v2 > app.ts', 'git add .'])
    expect(edited.last.normalized_command).toBe('git add .')
    expect(Object.keys(edited.state.staging)).toEqual(['src/app.ts'])
    expect(Object.keys(edited.state.working_tree)).toEqual(['README.md'])

    const named = session(['cd src', 'echo v2 > app.ts', 'git add app.ts', 'git restore --staged app.ts'])
    expect(named.executions[2].next_state.staging).toHaveProperty('src/app.ts')
    expect(named.state.staging).toEqual({})
  })

  it('steps up into the workspace folder and back into the project', () => {
    const { executions, outside } = session(['cd ..', 'pwd', 'ls', 'ls -a', 'tree', 'cat demo/README.md', 'cd demo/src', 'pwd'])
    expect(executions.map((execution) => execution.output)).toEqual([
      '',
      '/workspace',
      'demo/',
      './  ../  demo/',
      ['.', '└── demo', '    ├── README.md', '    └── src', '        ├── app.ts', '        └── util.ts', '', '2 directories, 3 files'].join('\n'),
      'hello',
      '',
      '/workspace/demo/src',
    ])
    expect(outside).toBe(false)
    expect(session(['cd demo']).last.output).toBe('cd: demo: No such file or directory')
    expect(session(['cd ../demo', 'pwd']).last.output).toBe('/workspace/demo')
    expect(session(['cd /workspace', 'cd missing']).last.output).toBe('cd: missing: No such file or directory')
  })

  it('leaves the learner above a folder made by git init <dir> until they cd in, like a real shell', () => {
    const { executions, outside } = session(['git init df', 'pwd', 'ls', 'cd df', 'pwd', 'cd df'], emptyFolder())
    expect(executions.map((execution) => [execution.exit_code, execution.output])).toEqual([
      [0, 'Initialized empty Git repository in df/.git/'],
      [0, '/workspace'],
      [0, 'df/'],
      [0, ''],
      [0, '/workspace/df'],
      [1, 'cd: df: No such file or directory'],
    ])
    expect(outside).toBe(false)
    expect(session(['git init'], emptyFolder()).outside).toBe(false)
  })

  it('refuses file edits from the workspace folder instead of guessing where they go', () => {
    const { state, last } = session(['git init df', 'touch notes.md'], emptyFolder())
    expect(last).toMatchObject({ processed: false, diagnostic: false, command_family: 'touch', exit_code: 1 })
    expect(last.output).toBe("touch: not run: this terminal only edits files inside df/ (run 'cd df' first)")
    expect(state.working_tree['notes.md']).toBeUndefined()
  })

  it('deletes the repository with rm -rf .git and keeps every file as untracked', () => {
    const edited = session(['echo draft > notes.md', 'git add notes.md', 'rm -rf .git'])
    expect(edited.last).toMatchObject({ processed: true, diagnostic: false, exit_code: 0, output: '' })
    expect(edited.state.repository_initialized).toBe(false)
    expect(edited.state.commits).toEqual([])
    expect(edited.state.branches).toEqual({})
    expect(edited.state.staging).toEqual({})
    expect(edited.state.working_tree).toEqual({
      '.gitignore': { status: 'untracked', content: '*.log\n' },
      'README.md': { status: 'untracked', content: 'hello\n' },
      'notes.md': { status: 'untracked', content: 'draft\n' },
      'src/app.ts': { status: 'untracked', content: 'app' },
      'src/util.ts': { status: 'untracked', content: 'util' },
    })

    const after = session(['rm -rf .git', 'ls -a', 'git status', 'git init', 'git status'])
    expect(after.executions[1].output).toBe('./  ../  .gitignore  README.md  src/')
    expect(after.executions[2].output).toContain('not a git repository')
    expect(after.executions[3].output).toBe('Initialized empty Git repository')
    expect(after.last.output).toContain('Untracked files')
  })

  it('treats .git like a real folder for rm and rmdir', () => {
    expect(session(['rm .git']).last.output).toBe("rm: cannot remove '.git': Is a directory")
    expect(session(['rmdir .git']).last.output).toBe("rmdir: failed to remove '.git': Directory not empty")
    expect(session(['rm -rf .git/HEAD']).last.output).toBe("rm: cannot remove '.git/HEAD': only the whole .git folder can be removed")
    expect(session(['cd src', 'rm -r ../.git']).state.repository_initialized).toBe(false)
    expect(session(['rm -rf .git', 'rm -rf .git']).last).toMatchObject({ exit_code: 0, output: '' })
    expect(session(['rm -rf .git', 'rm -r .git']).last.output).toBe("rm: cannot remove '.git': No such file or directory")
  })

  it('names the working directory after a named clone destination', () => {
    const empty = repo({
      repository_initialized: false,
      commits: [],
      branches: {},
      head: { type: 'branch', name: 'main', target: null },
      remote_fixtures: {
        default_branch: 'origin/main',
        branches: { 'origin/main': 'r1' },
        commits: [{ id: 'r1', message: 'Create logs', parents: [], tree: { 'README.md': 'logs\n' } }],
      },
    })
    const cloned = session(['git clone https://git.corp.example/it/audit-logs.git audit-logs-local', 'cd audit-logs-local', 'pwd', 'ls -a'], empty)
    expect(cloned.executions.map((execution) => execution.exit_code)).toEqual([0, 0, 0, 0])
    expect(cloned.executions[2].output).toBe('/workspace/audit-logs-local')
    expect(cloned.last.output).toBe('./  ../  .git/  README.md')
  })
})
