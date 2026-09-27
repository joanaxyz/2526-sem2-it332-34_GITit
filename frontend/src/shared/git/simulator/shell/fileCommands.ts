import type { WorkspaceFileInput } from '@/shared/level/workspaceFileTypes'
import {
  createWorkspaceDirectory,
  createWorkspaceFile,
  deleteWorkspaceFile,
  renameWorkspaceFile,
  writeWorkspaceFile,
} from '@/shared/git/simulator/workspaceFiles'
import { descendantPaths, directoryEntries, pathKind } from '@/shared/git/simulator/workspaceTree'
import {
  baseName,
  fail,
  fileContent,
  joinDisplay,
  joinPath,
  missingParentReason,
  mutate,
  parseFlags,
  resolveOperand,
  type ShellRun,
} from '@/shared/git/simulator/shell/context'

/*
 * File-changing shell commands. Each one only edits the working copy through
 * the same helpers the Project Files panel uses, so git sees exactly what a
 * real shell would leave on disk. The backend replays these commands in
 * `common/git/shell_commands.py`; keep behaviour and state effects in step.
 */

type FileInput = Omit<WorkspaceFileInput, 'content'> & { content: unknown }

function writeFile(run: ShellRun, prefix: string, input: FileInput) {
  const fileInput = input as WorkspaceFileInput
  return mutate(run, prefix, (state) =>
    pathKind(state, input.path) === 'file' ? writeWorkspaceFile(state, fileInput) : createWorkspaceFile(state, fileInput),
  )
}

export function touch(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'touch', args, {})
  if (!parsed) return
  if (!parsed.operands.length) return fail(run, 'touch: missing file operand')
  for (const operand of parsed.operands) {
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `touch: cannot touch '${operand}': ${target.error}`)
      continue
    }
    if (pathKind(run.state, target.path) !== null) continue
    const reason = missingParentReason(run.state, target.path)
    if (reason) {
      fail(run, `touch: cannot touch '${operand}': ${reason}`)
      continue
    }
    writeFile(run, `touch: cannot touch '${operand}'`, { path: target.path, content: '' })
  }
}

export function mkdir(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'mkdir', args, { p: 'parents', '--parents': 'parents' })
  if (!parsed) return
  const parents = parsed.flags.has('parents')
  if (!parsed.operands.length) return fail(run, 'mkdir: missing operand')
  for (const operand of parsed.operands) {
    const prefix = `mkdir: cannot create directory '${operand}'`
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `${prefix}: ${target.error}`)
      continue
    }
    const kind = pathKind(run.state, target.path)
    if (kind === 'directory' && parents) continue
    if (kind !== null) {
      fail(run, `${prefix}: File exists`)
      continue
    }
    const blocked = parents ? fileAncestor(run, target.path) : missingParentReason(run.state, target.path)
    if (blocked) {
      fail(run, `${prefix}: ${blocked}`)
      continue
    }
    mutate(run, prefix, (state) => createWorkspaceDirectory(state, { path: target.path }))
  }
}

function fileAncestor(run: ShellRun, path: string) {
  const parts = path.split('/').slice(0, -1)
  for (let index = 1; index <= parts.length; index += 1) {
    if (pathKind(run.state, parts.slice(0, index).join('/')) === 'file') return 'Not a directory'
  }
  return null
}

export function rmdir(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'rmdir', args, {})
  if (!parsed) return
  if (!parsed.operands.length) return fail(run, 'rmdir: missing operand')
  for (const operand of parsed.operands) {
    const prefix = `rmdir: failed to remove '${operand}'`
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `${prefix}: ${target.error}`)
      continue
    }
    const kind = pathKind(run.state, target.path)
    if (kind === null) fail(run, `${prefix}: No such file or directory`)
    else if (kind === 'file') fail(run, `${prefix}: Not a directory`)
    else if (!target.path) fail(run, `${prefix}: Invalid argument`)
    else if (directoryEntries(run.state, target.path).length) fail(run, `${prefix}: Directory not empty`)
    else mutate(run, prefix, (state) => deleteWorkspaceFile(state, { path: target.path }))
  }
}

export function rm(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'rm', args, {
    r: 'recursive',
    R: 'recursive',
    f: 'force',
    '--recursive': 'recursive',
    '--force': 'force',
  })
  if (!parsed) return
  const recursive = parsed.flags.has('recursive')
  const force = parsed.flags.has('force')
  if (!parsed.operands.length) {
    if (!force) fail(run, 'rm: missing operand')
    return
  }
  for (const operand of parsed.operands) {
    const prefix = `rm: cannot remove '${operand}'`
    if (['.', '..'].includes(baseName(operand))) {
      fail(run, `rm: refusing to remove '.' or '..' directory: skipping '${operand}'`)
      continue
    }
    const target = resolveOperand(run, operand)
    if ('error' in target) {
      fail(run, `${prefix}: ${target.error}`)
      continue
    }
    if (!target.path) {
      fail(run, `rm: refusing to remove '.' or '..' directory: skipping '${operand}'`)
      continue
    }
    const kind = pathKind(run.state, target.path)
    if (kind === null) {
      if (!force) fail(run, `${prefix}: No such file or directory`)
      continue
    }
    if (kind === 'directory' && !recursive) {
      fail(run, `${prefix}: Is a directory`)
      continue
    }
    mutate(run, prefix, (state) => deleteWorkspaceFile(state, { path: target.path }))
  }
}

type Transfer = { operand: string; path: string; kind: 'file' | 'directory'; target: string; targetDisplay: string }

/** Shared `mv`/`cp` operand handling: resolve sources against the destination. */
function planTransfers(run: ShellRun, program: 'mv' | 'cp', operands: string[], recursive: boolean) {
  if (!operands.length) return fail(run, `${program}: missing file operand`)
  if (operands.length === 1) return fail(run, `${program}: missing destination file operand after '${operands[0]}'`)
  const destinationOperand = operands.at(-1) as string
  const destination = resolveOperand(run, destinationOperand)
  if ('error' in destination) return fail(run, `${program}: cannot ${program === 'mv' ? 'move' : 'copy'} to '${destinationOperand}': ${destination.error}`)
  const destinationKind = pathKind(run.state, destination.path)
  const sources = operands.slice(0, -1)
  if (sources.length > 1 && destinationKind !== 'directory') {
    return fail(run, `${program}: target '${destinationOperand}' is not a directory`)
  }

  const transfers: Transfer[] = []
  for (const operand of sources) {
    const source = resolveOperand(run, operand)
    if ('error' in source) {
      fail(run, `${program}: cannot stat '${operand}': ${source.error}`)
      continue
    }
    const kind = pathKind(run.state, source.path)
    if (kind === null) {
      fail(run, `${program}: cannot stat '${operand}': No such file or directory`)
      continue
    }
    if (!source.path) {
      fail(run, `${program}: cannot ${program === 'mv' ? 'move' : 'copy'} '${operand}': Invalid argument`)
      continue
    }
    if (kind === 'directory' && program === 'cp' && !recursive) {
      fail(run, `cp: -r not specified; omitting directory '${operand}'`)
      continue
    }
    const intoDirectory = destinationKind === 'directory'
    const target = intoDirectory ? joinPath(destination.path, baseName(source.path)) : destination.path
    const targetDisplay = intoDirectory ? joinDisplay(destinationOperand, baseName(source.path)) : destinationOperand
    if (target === source.path) {
      fail(run, `${program}: '${operand}' and '${targetDisplay}' are the same file`)
      continue
    }
    if (target.startsWith(`${source.path}/`)) {
      fail(run, program === 'mv'
        ? `mv: cannot move '${operand}' to a subdirectory of itself, '${targetDisplay}'`
        : `cp: cannot copy a directory, '${operand}', into itself, '${targetDisplay}'`)
      continue
    }
    transfers.push({ operand, path: source.path, kind, target, targetDisplay })
  }
  return transfers
}

export function mv(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'mv', args, { f: 'force', '--force': 'force' })
  if (!parsed) return
  for (const transfer of planTransfers(run, 'mv', parsed.operands, true) ?? []) {
    const { operand, path, kind, target, targetDisplay } = transfer
    const prefix = `mv: cannot move '${operand}' to '${targetDisplay}'`
    const targetKind = pathKind(run.state, target)
    if (targetKind === 'directory') {
      if (kind === 'file') {
        fail(run, `mv: cannot overwrite directory '${targetDisplay}' with non-directory`)
        continue
      }
      if (directoryEntries(run.state, target).length) {
        fail(run, `${prefix}: Directory not empty`)
        continue
      }
    } else if (targetKind === 'file' && kind === 'directory') {
      fail(run, `mv: cannot overwrite non-directory '${targetDisplay}' with directory '${operand}'`)
      continue
    } else if (targetKind === null) {
      const reason = missingParentReason(run.state, target)
      if (reason) {
        fail(run, `${prefix}: ${reason}`)
        continue
      }
    }
    if (targetKind !== null && !mutate(run, prefix, (state) => deleteWorkspaceFile(state, { path: target }))) continue
    mutate(run, prefix, (state) => renameWorkspaceFile(state, { path, newPath: target }))
  }
}

export function cp(run: ShellRun, args: string[]) {
  const parsed = parseFlags(run, 'cp', args, { r: 'recursive', R: 'recursive', '--recursive': 'recursive' })
  if (!parsed) return
  for (const transfer of planTransfers(run, 'cp', parsed.operands, parsed.flags.has('recursive')) ?? []) {
    const { operand, path, kind, target, targetDisplay } = transfer
    const prefix = `cp: cannot create '${targetDisplay}'`
    const targetKind = pathKind(run.state, target)
    if (targetKind === null) {
      const reason = missingParentReason(run.state, target)
      if (reason) {
        fail(run, `${prefix}: ${reason}`)
        continue
      }
    }
    if (kind === 'file') {
      if (targetKind === 'directory') fail(run, `cp: cannot overwrite directory '${targetDisplay}' with non-directory`)
      else writeFile(run, prefix, { path: target, content: fileContent(run.state, path) })
      continue
    }
    if (targetKind === 'file') {
      fail(run, `cp: cannot overwrite non-directory '${targetDisplay}' with directory '${operand}'`)
      continue
    }
    copyDirectory(run, prefix, path, target)
  }
}

function copyDirectory(run: ShellRun, prefix: string, source: string, target: string) {
  const { files, directories } = descendantPaths(run.state, source)
  const relocate = (path: string) => `${target}${path.slice(source.length)}`
  if (pathKind(run.state, target) === null) {
    if (!mutate(run, prefix, (state) => createWorkspaceDirectory(state, { path: target }))) return
  }
  for (const directory of directories) {
    const destination = relocate(directory)
    const kind = pathKind(run.state, destination)
    if (kind === 'file') fail(run, `cp: cannot overwrite non-directory '${destination}' with directory`)
    else if (kind === null) mutate(run, prefix, (state) => createWorkspaceDirectory(state, { path: destination }))
  }
  for (const file of files) {
    const destination = relocate(file)
    if (pathKind(run.state, destination) === 'directory') {
      fail(run, `cp: cannot overwrite directory '${destination}' with non-directory`)
      continue
    }
    writeFile(run, prefix, { path: destination, content: fileContent(run.state, file) })
  }
}

/** `>`/`>>` redirection of `text` into a working-copy file. */
export function redirectOutput(run: ShellRun, redirect: { append: boolean; target: string }, text: string) {
  const prefix = `bash: ${redirect.target}`
  const target = resolveOperand(run, redirect.target)
  if ('error' in target) return fail(run, `${prefix}: ${target.error}`)
  const kind = pathKind(run.state, target.path)
  if (kind === 'directory') return fail(run, `${prefix}: Is a directory`)
  if (kind === null) {
    const reason = missingParentReason(run.state, target.path)
    if (reason) return fail(run, `${prefix}: ${reason}`)
  }
  let content = text
  if (redirect.append && kind === 'file') {
    const existing = fileContent(run.state, target.path)
    if (typeof existing !== 'string') return fail(run, `${prefix}: cannot append to this file in the simulator`)
    content = `${existing}${text}`
  }
  writeFile(run, prefix, { path: target.path, content })
}

