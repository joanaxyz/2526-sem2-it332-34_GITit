import { directoryEntries, pathKind, type WorkspaceEntry } from '@/shared/git/simulator/workspaceTree'
import {
  fail,
  fileContent,
  parseFlags,
  resolveOperand,
  type ShellRun,
} from '@/shared/git/simulator/shell/context'
import { redirectOutput } from '@/shared/git/simulator/shell/fileCommands'

/** Read-only shell commands, plus `cd`, which only moves the terminal. */

function workingDirectoryLabel(projectName: string, cwd: string) {
  return `/workspace/${projectName}${cwd ? `/${cwd}` : ''}`
}

export function pwd(run: ShellRun) {
  run.out.push(workingDirectoryLabel(run.projectName, run.cwd))
}

export function cd(run: ShellRun, args: string[], enterableNames: string[]) {
  if (args.length > 1) return fail(run, 'cd: too many arguments')
  const operand = args[0] ?? '~'
  if (operand === '-') return fail(run, 'cd: OLDPWD not set')
  const target = resolveOperand(run, operand)
  if ('error' in target) return fail(run, `cd: ${operand}: ${target.error}`)
  const kind = pathKind(run.state, target.path)
  if (kind === 'directory') {
    run.cwd = target.path
    return
  }
  if (kind === 'file') return fail(run, `cd: ${operand}: Not a directory`)
  // `git clone <url> <dir>` / `git init <dir>` then `cd <dir>`: the simulator's
  // project root already is that folder, so entering it keeps you at the root.
  if (!run.cwd && enterableNames.includes(operand.replace(/\/+$/, ''))) return
  fail(run, `cd: ${operand}: No such file or directory`)
}

const LS_FLAGS = { a: 'all', A: 'almost-all', l: 'long', '1': 'one', F: 'classify', '--all': 'all' }

export function ls(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'ls', args, LS_FLAGS)
  if (!parsed) {
    run.exitCode = 2
    return
  }
  const { flags } = parsed
  const operands = parsed.operands.length ? parsed.operands : ['.']
  const files: string[] = []
  const directories: Array<{ operand: string; path: string }> = []
  for (const operand of operands) {
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `ls: cannot access '${operand}': ${target.error}`, 2)
      continue
    }
    const kind = pathKind(run.state, target.path)
    if (kind === null) fail(run, `ls: cannot access '${operand}': No such file or directory`, 2)
    else if (kind === 'file') files.push(operand)
    else directories.push({ operand, path: target.path })
  }

  const blocks: string[] = []
  if (files.length) blocks.push(formatNames(files, flags.has('long') || flags.has('one'), flags.has('long')))
  const showHeaders = operands.length > 1
  for (const { operand, path } of directories) {
    const names = listingNames(run, path, flags)
    const body = formatNames(names, flags.has('long') || flags.has('one'), flags.has('long'))
    blocks.push(showHeaders ? [`${operand}:`, body].filter(Boolean).join('\n') : body)
  }
  const text = blocks.filter((block) => block !== '').join(showHeaders ? '\n\n' : '\n')
  if (text) run.out.push(text)
}

function listingNames(run: ShellRun, path: string, flags: Set<string>) {
  const showHidden = flags.has('all') || flags.has('almost-all')
  const names = directoryEntries(run.state, path)
    .filter((entry) => showHidden || !entry.name.startsWith('.'))
    .map(displayName)
  if (showHidden && !path && run.state.repository_initialized) names.unshift('.git/')
  if (flags.has('all')) names.unshift('./', '../')
  return names.sort((left, right) => left.replace(/^\.+/, '').localeCompare(right.replace(/^\.+/, '')))
}

function displayName(entry: WorkspaceEntry) {
  return entry.kind === 'directory' ? `${entry.name}/` : entry.name
}

function formatNames(names: string[], onePerLine: boolean, long: boolean) {
  if (long) return names.map((name) => `${name.endsWith('/') ? 'drwxr-xr-x' : '-rw-r--r--'}  ${name}`).join('\n')
  return names.join(onePerLine ? '\n' : '  ')
}

export function tree(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'tree', args, { a: 'all' })
  if (!parsed) return
  const operand = parsed.operands[0] ?? '.'
  const target = resolveOperand(run, operand)
  if ('error' in target) return fail(run, `tree: ${operand}: ${target.error}`)
  const kind = pathKind(run.state, target.path)
  if (kind !== 'directory') {
    return fail(run, `tree: ${operand}: ${kind === 'file' ? 'Not a directory' : 'No such file or directory'}`)
  }
  const counts = { directories: 0, files: 0 }
  const lines = [operand]
  const walk = (path: string, indent: string) => {
    const entries = directoryEntries(run.state, path).filter(
      (entry) => parsed.flags.has('all') || !entry.name.startsWith('.'),
    )
    entries.forEach((entry, index) => {
      const last = index === entries.length - 1
      lines.push(`${indent}${last ? '└── ' : '├── '}${entry.name}`)
      if (entry.kind === 'directory') {
        counts.directories += 1
        walk(entry.path, `${indent}${last ? '    ' : '│   '}`)
      } else {
        counts.files += 1
      }
    })
  }
  walk(target.path, '')
  const directoryWord = counts.directories === 1 ? 'directory' : 'directories'
  const fileWord = counts.files === 1 ? 'file' : 'files'
  lines.push('', `${counts.directories} ${directoryWord}, ${counts.files} ${fileWord}`)
  run.out.push(lines.join('\n'))
}

export function cat(run: ShellRun, args: string[], redirect: { append: boolean; target: string } | null) {
  const parsed = parseFlags(run, 'cat', args, {})
  if (!parsed) return
  if (!parsed.operands.length) return fail(run, 'cat: reading from the keyboard is not supported; name a file')
  const chunks: string[] = []
  for (const operand of parsed.operands) {
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `cat: ${operand}: ${target.error}`)
      continue
    }
    const kind = pathKind(run.state, target.path)
    if (kind === null) {
      fail(run, `cat: ${operand}: No such file or directory`)
      continue
    }
    if (kind === 'directory') {
      fail(run, `cat: ${operand}: Is a directory`)
      continue
    }
    const content = fileContent(run.state, target.path)
    if (redirect && typeof content !== 'string') {
      fail(run, `cat: ${operand}: cannot copy this file's content in the simulator`)
      continue
    }
    chunks.push(typeof content === 'string' ? content : JSON.stringify(content, null, 2))
  }
  if (redirect) return redirectOutput(run, redirect, chunks.join(''))
  const text = chunks.join('').replace(/\n$/, '')
  if (text) run.out.push(text)
}

export function echo(run: ShellRun, args: string[], redirect: { append: boolean; target: string } | null) {
  let noNewline = false
  let rest = args
  while (rest[0] === '-n') {
    noNewline = true
    rest = rest.slice(1)
  }
  const text = rest.join(' ')
  if (redirect) return redirectOutput(run, redirect, noNewline ? text : `${text}\n`)
  run.out.push(text)
}

