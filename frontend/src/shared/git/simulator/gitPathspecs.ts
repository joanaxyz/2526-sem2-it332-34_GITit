import { defaultCloneDirectory } from '@/shared/git/simulator/commands/repository'
import { COMMAND_ALIASES, shellJoin, splitSafely } from '@/shared/git/simulator/parser'
import { resolveShellPath } from '@/shared/git/simulator/shell/syntax'

/**
 * Git reads pathspecs relative to the directory it runs in. The simulator
 * models paths from the project root, so a command typed inside a subfolder
 * is rewritten to root-relative paths before it runs: `git add app.ts` in
 * `src` becomes `git add src/app.ts`, and `git add .` becomes `git add src`.
 *
 * Positional arguments are paths for the families below; for every other
 * family only arguments after `--` are paths (the rest are refs or names).
 * The backend applies the same rewrite in `common/git/git_pathspecs.py`
 * before verifying the transition.
 */
const PATH_ARGUMENT_FAMILIES = new Set(['add', 'rm', 'restore', 'commit', 'check-ignore', 'ls-files'])

const VALUE_OPTIONS: Record<string, Set<string>> = {
  commit: new Set(['-m', '--message', '-am', '-F', '--file', '-C', '-c', '--author', '--date', '--fixup', '--squash']),
  restore: new Set(['-s', '--source']),
}

export function rebaseGitPathspecs(command: string, cwd: string) {
  if (!cwd) return command
  let words: string[]
  try {
    words = splitSafely(command.trim())
  } catch {
    return command
  }
  if (words[0] !== 'git' || words.length < 2) return command

  const family = COMMAND_ALIASES[words[1]] ?? words[1]
  if (family === 'init' || family === 'clone') return rebaseRepositoryDirectory(command, words, family, cwd)
  if (words.length < 3) return command
  const valueOptions = VALUE_OPTIONS[family] ?? new Set<string>()
  const pathArguments = PATH_ARGUMENT_FAMILIES.has(family)
  const rebased = words.slice(0, 2)
  let positionalOnly = false
  for (let index = 2; index < words.length; index += 1) {
    const word = words[index]
    if (!positionalOnly && word === '--') {
      positionalOnly = true
      rebased.push(word)
      continue
    }
    if (!positionalOnly && word.startsWith('-') && word !== '-') {
      rebased.push(word)
      if (valueOptions.has(word) && index + 1 < words.length) {
        rebased.push(words[index + 1])
        index += 1
      }
      continue
    }
    rebased.push(positionalOnly || pathArguments ? rebasePath(word, cwd) : word)
  }
  return rebased.every((word, index) => word === words[index]) ? command : shellJoin(rebased)
}

// `git init` and `git clone` create a repository in a folder, which is relative
// to the folder they run in: `git init` inside `site` initializes `site`.
const REPOSITORY_VALUE_OPTIONS: Record<'init' | 'clone', Set<string>> = {
  init: new Set(['-b', '--initial-branch', '--template', '--separate-git-dir', '--object-format']),
  clone: new Set(['-b', '--branch', '--depth', '-o', '--origin', '--template', '--reference', '-c', '--config']),
}

function rebaseRepositoryDirectory(command: string, words: string[], family: 'init' | 'clone', cwd: string) {
  const valueOptions = REPOSITORY_VALUE_OPTIONS[family]
  const rebased = words.slice(0, 2)
  const positional: number[] = []
  for (let index = 2; index < words.length; index += 1) {
    const word = words[index]
    rebased.push(word)
    if (word.startsWith('-') && word !== '-') {
      if (valueOptions.has(word) && index + 1 < words.length) {
        rebased.push(words[index + 1])
        index += 1
      }
      continue
    }
    positional.push(rebased.length - 1)
  }
  const slot = family === 'init' ? 0 : 1
  if (positional.length > slot) rebased[positional[slot]] = rebasePath(rebased[positional[slot]], cwd)
  else if (family === 'init') rebased.push(cwd)
  else if (positional.length === 1) rebased.push(rebasePath(defaultCloneDirectory(rebased[positional[0]]), cwd))
  const unchanged = rebased.length === words.length && rebased.every((word, index) => word === words[index])
  return unchanged ? command : shellJoin(rebased)
}

function rebasePath(path: string, cwd: string) {
  if (path.startsWith(':')) return path
  const resolved = resolveShellPath(cwd, path)
  if (resolved === null) return path
  return resolved || '.'
}
