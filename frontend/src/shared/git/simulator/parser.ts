import {
  GitCommandParseError,
  NonGitCommandError,
  type ParsedGitCommand,
} from '@/shared/git/simulator/types'

const COMMAND_ALIASES: Record<string, string> = {
  st: 'status',
  ci: 'commit',
  co: 'checkout',
  br: 'branch',
}

function shellJoin(parts: string[]) {
  return parts.map((part) => (needsQuote(part) ? quote(part) : part)).join(' ')
}

function quote(value: string) {
  return `'${value.replaceAll("'", "'\"'\"'")}'`
}

function needsQuote(value: string) {
  return /\s/.test(value) || /["';&|<>`$]/.test(value)
}

export class GitCommandParser {
  parse(command: string): ParsedGitCommand {
    const rawText = command
    const stripped = command.trim()
    if (!stripped) throw new GitCommandParseError('No command entered.')

    const argv = splitSafely(stripped)
    if (!argv.length) throw new GitCommandParseError('No command entered.')
    if (argv[0] !== 'git') throw new NonGitCommandError(argv[0])

    const originalSubcommand = argv[1] ?? ''
    const subcommand = originalSubcommand ? COMMAND_ALIASES[originalSubcommand] ?? originalSubcommand : ''
    const { options, args, pathspecs, message, normalizedTail } = parseTail(subcommand, argv.slice(2))
    const normalizedArgv = ['git', ...(subcommand ? [subcommand] : []), ...normalizedTail]

    return {
      rawText,
      normalizedText: shellJoin(normalizedArgv),
      argv: subcommand ? ['git', subcommand, ...normalizedTail] : ['git'],
      subcommand,
      originalSubcommand,
      args,
      options,
      pathspecs,
      message,
    }
  }
}

function splitSafely(command: string) {
  const tokens: string[] = []
  let current = ''
  let quote: '"' | "'" | null = null
  let escaped = false

  for (let index = 0; index < command.length; index += 1) {
    const char = command[index]
    if (escaped) {
      current += char
      escaped = false
      continue
    }
    if (char === '\\' && quote !== "'") {
      escaped = true
      continue
    }
    if (quote) {
      if (char === quote) quote = null
      else current += char
      continue
    }
    if (char === '"' || char === "'") {
      quote = char
      continue
    }
    if (/\s/.test(char)) {
      if (current) {
        tokens.push(current)
        current = ''
      }
      continue
    }
    current += char
  }
  if (quote) throw new GitCommandParseError('fatal: could not parse command line')
  if (escaped) current += '\\'
  if (current) tokens.push(current)

  const forbidden = new Set([';', '&&', '&', '|', '||', '>', '>>', '<', '<<'])
  const badToken = tokens.find((token) => forbidden.has(token))
  if (badToken) throw new GitCommandParseError(`fatal: unsupported shell syntax near '${badToken}'`)
  if (tokens.some((token) => token.includes('$(') || token.includes('`'))) {
    throw new GitCommandParseError('fatal: command substitution is not supported')
  }
  return tokens
}

type Tail = {
  options: Record<string, Array<string | true>>
  args: string[]
  pathspecs: string[]
  message: string | null
  normalizedTail: string[]
}

function parseTail(subcommand: string, tokens: string[]): Tail {
  if (subcommand === 'commit') return parseCommitTail(tokens)
  if (subcommand === 'init') return parseValueOptionTail(tokens, new Set(['-b', '--initial-branch']))
  if (subcommand === 'clone') return parseValueOptionTail(tokens, new Set(['-b', '--branch', '--depth']))
  if (subcommand === 'log') return parseValueOptionTail(tokens, new Set(['-n', '--max-count']))
  if (subcommand === 'mergetool') return parseValueOptionTail(tokens, new Set(['--tool']))
  if (subcommand === 'rebase') return parseValueOptionTail(tokens, new Set(['--onto']))
  if (subcommand === 'restore') return parseValueOptionTail(tokens, new Set(['--source']))
  if (subcommand === 'stash') return parseMessageTail(tokens)
  if (subcommand === 'tag') return parseMessageTail(tokens)
  return parseGenericTail(tokens)
}

function appendOption(options: Record<string, Array<string | true>>, option: string, value: string | true = true) {
  options[option] ??= []
  options[option].push(value)
}

function parseCommitTail(tokens: string[]): Tail {
  const options: Record<string, Array<string | true>> = {}
  const args: string[] = []
  const pathspecs: string[] = []
  const normalizedTail: string[] = []
  let message: string | null = null
  let index = 0

  while (index < tokens.length) {
    const token = tokens[index]
    if (token === '--') {
      pathspecs.push(...tokens.slice(index + 1))
      normalizedTail.push(...tokens.slice(index))
      break
    }
    if (token === '-m' || token === '--message') {
      if (index + 1 >= tokens.length) throw new GitCommandParseError("error: switch `m' requires a value.")
      message = tokens[index + 1]
      appendOption(options, '-m', message)
      normalizedTail.push('-m', message)
      index += 2
      continue
    }
    if (token.startsWith('--message=')) {
      message = token.split('=', 2)[1]
      appendOption(options, '-m', message)
      normalizedTail.push('-m', message)
      index += 1
      continue
    }
    if (token.startsWith('-am') && token !== '-am') {
      message = token.slice(3)
      appendOption(options, '-a')
      appendOption(options, '-m', message)
      normalizedTail.push('-a', '-m', message)
      index += 1
      continue
    }
    if (token === '-am') {
      if (index + 1 >= tokens.length) throw new GitCommandParseError("error: switch `m' requires a value.")
      message = tokens[index + 1]
      appendOption(options, '-a')
      appendOption(options, '-m', message)
      normalizedTail.push('-a', '-m', message)
      index += 2
      continue
    }
    if (['-a', '--all', '--amend', '--no-edit', '--allow-empty'].includes(token)) {
      appendOption(options, token)
      normalizedTail.push(token)
      index += 1
      continue
    }
    if (token.startsWith('-')) {
      appendOption(options, token)
      normalizedTail.push(token)
      index += 1
      continue
    }
    args.push(token)
    pathspecs.push(token)
    normalizedTail.push(token)
    index += 1
  }

  return { options, args, pathspecs, message, normalizedTail }
}

function parseMessageTail(tokens: string[]): Tail {
  const valueOptions = new Set(['-m', '--message'])
  return parseValueOptionTail(tokens, valueOptions, true)
}

function parseValueOptionTail(tokens: string[], valueOptions: Set<string>, captureMessage = false): Tail {
  const options: Record<string, Array<string | true>> = {}
  const args: string[] = []
  const pathspecs: string[] = []
  const normalizedTail: string[] = []
  let message: string | null = null
  let index = 0
  let positionalOnly = false

  while (index < tokens.length) {
    const token = tokens[index]
    // `--` ends option parsing: everything after it is a pathspec, even if it
    // begins with a dash. The separator itself is not an option.
    if (!positionalOnly && token === '--') {
      positionalOnly = true
      normalizedTail.push(token)
      index += 1
      continue
    }
    if (positionalOnly) {
      args.push(token)
      pathspecs.push(token)
      normalizedTail.push(token)
      index += 1
      continue
    }
    const eqOption = token.startsWith('--') && token.includes('=') ? token.split('=', 2)[0] : null
    if (eqOption && valueOptions.has(eqOption)) {
      const value = token.split('=', 2)[1]
      appendOption(options, eqOption, value)
      if (captureMessage && (eqOption === '-m' || eqOption === '--message')) message = value
      normalizedTail.push(eqOption, value)
      index += 1
      continue
    }
    if (valueOptions.has(token)) {
      if (index + 1 >= tokens.length) throw new GitCommandParseError(`error: option ${token} requires a value.`)
      const value = tokens[index + 1]
      appendOption(options, token, value)
      if (captureMessage && (token === '-m' || token === '--message')) message = value
      normalizedTail.push(token, value)
      index += 2
      continue
    }
    if (token.startsWith('-')) {
      appendOption(options, token)
      normalizedTail.push(token)
      index += 1
      continue
    }
    args.push(token)
    pathspecs.push(token)
    normalizedTail.push(token)
    index += 1
  }

  return { options, args, pathspecs, message, normalizedTail }
}

function parseGenericTail(tokens: string[]): Tail {
  const options: Record<string, Array<string | true>> = {}
  const args: string[] = []
  const pathspecs: string[] = []
  const normalizedTail: string[] = []
  let positionalOnly = false

  for (const token of tokens) {
    if (!positionalOnly && token === '--') {
      // `--` ends option parsing; the rest are pathspecs (the separator itself
      // is not an option). Mirrors git's behaviour for `diff/restore/rm -- <path>`.
      positionalOnly = true
      normalizedTail.push(token)
      continue
    }
    if (!positionalOnly && token.startsWith('-')) {
      appendOption(options, token)
      normalizedTail.push(token)
    } else {
      args.push(token)
      pathspecs.push(token)
      normalizedTail.push(token)
    }
  }

  return { options, args, pathspecs, message: null, normalizedTail }
}

export function hasOption(parsed: ParsedGitCommand, option: string) {
  return option in parsed.options
}

export function optionValues(parsed: ParsedGitCommand, ...options: string[]) {
  return options.flatMap((option) => parsed.options[option] ?? [])
}
