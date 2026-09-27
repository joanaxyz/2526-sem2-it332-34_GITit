import type { MutableRepositoryState } from '@/shared/git/simulator/types'
import { directoryEntries, pathKind } from '@/shared/git/simulator/workspaceTree'

/**
 * Shell syntax for the workspace terminal. The backend mirrors this module in
 * `common/git/shell_commands.py` so it can replay file-changing commands; keep
 * the two in step.
 */

export class ShellSyntaxError extends Error {}

export type ShellWord = { text: string; glob: boolean }

export type ShellInvocation = {
  program: string
  args: ShellWord[]
  redirect: { append: boolean; target: string } | null
}

type Token = { kind: 'word'; word: ShellWord } | { kind: 'redirect'; append: boolean }

const UNSUPPORTED_OPERATORS = new Set(['|', ';', '&', '<', '`'])

function tokenizeShell(command: string): Token[] {
  const tokens: Token[] = []
  let text = ''
  let glob = false
  let inWord = false
  let quote: '"' | "'" | null = null
  let index = 0

  const endWord = () => {
    if (inWord) tokens.push({ kind: 'word', word: { text, glob } })
    text = ''
    glob = false
    inWord = false
  }

  while (index < command.length) {
    const char = command[index]
    if (quote === "'") {
      if (char === "'") quote = null
      else text += char
      index += 1
      continue
    }
    if (char === '$' && command[index + 1] === '(') {
      throw new ShellSyntaxError('command substitution is not supported')
    }
    if (quote === '"') {
      const next = command[index + 1]
      if (char === '\\' && next !== undefined && '"\\$`'.includes(next)) {
        text += next
        index += 2
        continue
      }
      if (char === '"') quote = null
      else if (char === '`') throw new ShellSyntaxError('command substitution is not supported')
      else text += char
      index += 1
      continue
    }
    if (char === '\\' && index + 1 < command.length) {
      text += command[index + 1]
      inWord = true
      index += 2
      continue
    }
    if (char === '"' || char === "'") {
      quote = char
      inWord = true
      index += 1
      continue
    }
    if (/\s/.test(char)) {
      endWord()
      index += 1
      continue
    }
    if (char === '>') {
      endWord()
      const append = command[index + 1] === '>'
      tokens.push({ kind: 'redirect', append })
      index += append ? 2 : 1
      continue
    }
    if (UNSUPPORTED_OPERATORS.has(char)) {
      throw new ShellSyntaxError(`syntax error near unexpected token '${char}' (run one command at a time)`)
    }
    if (char === '*' || char === '?') glob = true
    text += char
    inWord = true
    index += 1
  }
  if (quote) throw new ShellSyntaxError(`unexpected EOF while looking for matching \`${quote}'`)
  endWord()
  return tokens
}

export function parseShellCommand(command: string): ShellInvocation {
  const tokens = tokenizeShell(command.trim())
  const words: ShellWord[] = []
  let redirect: ShellInvocation['redirect'] = null
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index]
    if (token.kind === 'word') {
      words.push(token.word)
      continue
    }
    const target = tokens[index + 1]
    if (!target || target.kind !== 'word') {
      throw new ShellSyntaxError("syntax error near unexpected token 'newline'")
    }
    if (redirect) throw new ShellSyntaxError('only one output redirection is supported')
    redirect = { append: token.append, target: target.word.text }
    index += 1
  }
  if (!words.length) throw new ShellSyntaxError('No command entered.')
  const [program, ...args] = words
  return { program: program.text, args, redirect }
}

/**
 * Resolve a path typed at `cwd` to a project-relative path (`''` is the
 * project root), or `null` when it leaves the project. `~` is the project
 * root, and `/workspace/<project>/...` (what `pwd` prints) maps back into it.
 */
export function resolveShellPath(cwd: string, input: string): string | null {
  if (!input) return null
  let base = cwd
  let rest = input
  if (rest === '~' || rest.startsWith('~/')) {
    base = ''
    rest = rest.slice(1)
  } else if (rest.startsWith('/')) {
    const parts = rest.split('/').filter(Boolean)
    if (parts[0] !== 'workspace' || parts.length < 2) return null
    base = ''
    rest = parts.slice(2).join('/')
  }
  const segments = base ? base.split('/') : []
  for (const part of rest.split('/')) {
    if (!part || part === '.') continue
    if (part === '..') {
      if (!segments.length) return null
      segments.pop()
      continue
    }
    segments.push(part)
  }
  return segments.join('/')
}

export function isInsideGitDirectory(path: string) {
  return path === '.git' || path.startsWith('.git/')
}

/** Expand `*` and `?` in unquoted words against the working copy, like bash. */
export function expandShellWords(state: MutableRepositoryState, cwd: string, words: ShellWord[]) {
  return words.flatMap((word) => (word.glob ? expandGlob(state, cwd, word.text) : [word.text]))
}

function expandGlob(state: MutableRepositoryState, cwd: string, pattern: string) {
  if (pattern.startsWith('/') || pattern.startsWith('~')) return [pattern]
  const segments = pattern.split('/')
  let candidates: Array<{ display: string; resolved: string }> = [{ display: '', resolved: cwd }]
  segments.forEach((segment, index) => {
    const last = index === segments.length - 1
    const next: typeof candidates = []
    for (const candidate of candidates) {
      if (!segment) {
        next.push({ display: `${candidate.display}/`, resolved: candidate.resolved })
        continue
      }
      if (!/[*?]/.test(segment)) {
        const resolved = resolveShellPath(candidate.resolved, segment)
        if (resolved !== null) next.push({ display: joinDisplay(candidate.display, segment), resolved })
        continue
      }
      if (pathKind(state, candidate.resolved) !== 'directory') continue
      const matcher = globMatcher(segment)
      for (const entry of directoryEntries(state, candidate.resolved)) {
        if (!matcher(entry.name)) continue
        if (!last && entry.kind !== 'directory') continue
        next.push({ display: joinDisplay(candidate.display, entry.name), resolved: entry.path })
      }
    }
    candidates = next
  })
  const matches = candidates
    .filter((candidate) => pathKind(state, candidate.resolved) !== null)
    .map((candidate) => candidate.display)
  return matches.length ? matches : [pattern]
}

function joinDisplay(display: string, segment: string) {
  if (!display) return segment
  return display.endsWith('/') ? `${display}${segment}` : `${display}/${segment}`
}

function globMatcher(segment: string) {
  const source = [...segment]
    .map((char) => {
      if (char === '*') return '[^/]*'
      if (char === '?') return '[^/]'
      return char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    })
    .join('')
  const pattern = new RegExp(`^${source}$`)
  const matchesHidden = segment.startsWith('.')
  return (name: string) => (matchesHidden || !name.startsWith('.')) && pattern.test(name)
}
