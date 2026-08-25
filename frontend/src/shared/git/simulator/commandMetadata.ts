import { hasOption, optionValues } from '@/shared/git/simulator/parser'
import type { ParsedGitCommand } from '@/shared/git/simulator/types'

export const SUPPORTED_OPTIONS: Record<string, Set<string>> = {
  init: new Set(['-b', '--initial-branch', '-q', '--quiet']),
  clone: new Set(['-b', '--branch', '--depth']),
  status: new Set(['-s', '--short', '--porcelain', '-sb', '--ignored']),
  add: new Set(['-A', '--all', '-u', '--update', '-p', '--patch']),
  commit: new Set(['-a', '--all', '-m', '--message', '--amend', '--no-edit', '--allow-empty']),
  log: new Set(['--oneline', '--graph', '--all', '-n', '--max-count', '-p', '--patch', '--stat']),
  show: new Set(['--name-only']),
  diff: new Set(['--staged', '--cached', '--name-only', '--stat', '--ours', '--theirs', '--base', '--check']),
  branch: new Set(['-v', '-vv', '-a', '-d', '-D', '--delete', '-m', '--move', '--merged']),
  remote: new Set(['-v', '--verbose']),
  rm: new Set(['--cached', '-r']),
  restore: new Set(['--staged', '--source']),
  'check-ignore': new Set(['-v']),
  'ls-files': new Set(['-u', '--unmerged']),
  merge: new Set(['--abort', '--continue', '--no-ff', '--squash']),
  mergetool: new Set(['--tool']),
  checkout: new Set(['--ours', '--theirs', '-b']),
  config: new Set(['--global', '--list', '-l', '--get']),
  fetch: new Set(['--prune', '-p', '--all']),
  'cherry-pick': new Set(['--no-commit', '-n', '--abort']),
  reset: new Set(['--soft', '--mixed', '--hard']),
  revert: new Set(['--no-edit']),
  switch: new Set(['-c', '--create', '--detach']),
  stash: new Set(['-u', '--include-untracked', '-m', '--message']),
  push: new Set(['-u', '--set-upstream', '--force-with-lease', '-f', '--force', '--delete', '-d', '--tags']),
  pull: new Set(['--rebase', '--ff-only']),
  rebase: new Set(['-i', '--interactive', '--continue', '--abort', '--onto']),
  tag: new Set(['-a', '--annotate', '-m', '--message', '-d', '--delete']),
  'merge-base': new Set(),
  'rev-list': new Set(['--count']),
  reflog: new Set(),
  shortlog: new Set(['-s', '-n', '-sn']),
  'rev-parse': new Set(['--show-toplevel']),
  blame: new Set(),
  grep: new Set(),
  describe: new Set(['--tags']),
  'range-diff': new Set(),
  'merge-tree': new Set(),
  'verify-commit': new Set(),
  'verify-tag': new Set(),
  fsck: new Set(['--full']),
  'count-objects': new Set(['-v', '-H', '-vH']),
  'cat-file': new Set(['-p', '-t']),
  'ls-tree': new Set(),
  'show-ref': new Set(),
  'for-each-ref': new Set(),
  'symbolic-ref': new Set(),
  bisect: new Set(),
  rerere: new Set(),
  worktree: new Set(),
  'sparse-checkout': new Set(),
  submodule: new Set(),
}

export const GIT_COMMAND_NAMES = Object.keys(SUPPORTED_OPTIONS).sort()

export function validateCommand(parsed: ParsedGitCommand) {
  const allowed = SUPPORTED_OPTIONS[parsed.subcommand]
  if (!allowed) return null
  for (const option of Object.keys(parsed.options)) {
    if (!allowed.has(option)) return unknownOptionMessage(parsed.subcommand, option)
  }

  switch (parsed.subcommand) {
    case 'init':
      if (parsed.args.length > 1) return 'usage: git init [-q | --quiet] [--initial-branch=<branch-name>] [<directory>]'
      if (optionValues(parsed, '-b', '--initial-branch').length > 1) return 'error: only one initial branch may be specified'
      return null
    case 'clone':
      if (!parsed.args.length) return 'fatal: You must specify a repository to clone.'
      if (parsed.args.length > 2) return 'usage: git clone <repository> [<directory>]'
      if (optionValues(parsed, '-b', '--branch').length > 1) return 'error: only one branch may be specified for clone'
      return positiveIntOption(optionValues(parsed, '--depth')[0], 'depth')
    case 'add':
      if (hasOption(parsed, '-p') || hasOption(parsed, '--patch')) return null
      if (hasOption(parsed, '-A') || hasOption(parsed, '--all')) return null
      if (hasOption(parsed, '-u') || hasOption(parsed, '--update')) return null
      return parsed.pathspecs.length ? null : 'Nothing specified, nothing added.'
    case 'commit':
      if (optionValues(parsed, '-m').length > 1) return 'error: only one -m option is supported in this session.'
      if (hasOption(parsed, '--allow-empty')) return unknownOptionMessage(parsed.subcommand, '--allow-empty')
      if (hasOption(parsed, '--no-edit') && !hasOption(parsed, '--amend')) {
        return "fatal: options '--no-edit' and '--amend' must be used together"
      }
      if (parsed.pathspecs.length) return 'fatal: paths with git commit are not supported in this simulator'
      return null
    case 'remote':
      if ((hasOption(parsed, '-v') || hasOption(parsed, '--verbose')) && parsed.args.length) return 'usage: git remote [-v]'
      if (!parsed.args.length) return null
      if (parsed.args[0] === 'add' && parsed.args.length === 3) return null
      if (parsed.args[0] === 'set-url' && parsed.args.length === 3) return null
      return 'Only git remote and git remote -v are supported in Chapter 1.'
    case 'restore':
      return parsed.pathspecs.length ? null : 'fatal: you must specify path(s) to restore'
    case 'rm':
      if (!parsed.pathspecs.length) return 'fatal: No pathspec was given.'
      if (hasOption(parsed, '-r') && !hasOption(parsed, '--cached')) return 'fatal: git rm -r is only supported with --cached in Chapter 1'
      return null
    case 'check-ignore':
      return hasOption(parsed, '-v') && parsed.pathspecs.length === 1 ? null : 'usage: git check-ignore -v <path>'
    case 'merge':
      if (hasOption(parsed, '--abort') && hasOption(parsed, '--continue')) return 'fatal: --abort and --continue cannot be used together'
      if (hasOption(parsed, '--abort') || hasOption(parsed, '--continue')) return parsed.args.length ? 'fatal: --abort/--continue does not take a branch name' : null
      if (hasOption(parsed, '--no-ff') && hasOption(parsed, '--squash')) return 'fatal: --no-ff and --squash cannot be combined'
      return parsed.args.length === 1 ? null : 'usage: git merge [--no-ff | --squash] <branch>'
    case 'checkout':
      if (hasOption(parsed, '-b')) return parsed.args.length >= 1 && parsed.args.length <= 2 ? null : 'usage: git checkout -b <branch> [<start-point>]'
      if ([hasOption(parsed, '--ours'), hasOption(parsed, '--theirs')].filter(Boolean).length !== 1) {
        return 'git checkout in this simulator supports -b to create a branch, or --ours/--theirs for conflicted files.'
      }
      return parsed.pathspecs.length ? null : 'fatal: git checkout --ours/--theirs requires a conflicted path.'
    case 'config':
      if (hasOption(parsed, '--list') || hasOption(parsed, '-l')) return parsed.args.length ? 'usage: git config [--list|-l]' : null
      if (hasOption(parsed, '--get')) return parsed.args.length === 1 ? null : 'usage: git config --get <key>'
      if (!hasOption(parsed, '--global')) return 'error: expected git config --global <key> <value>, git config --get <key>, or git config --list'
      return parsed.args.length === 2 ? null : 'usage: git config --global <key> <value>'
    case 'fetch':
      return parsed.args.length > 1 ? 'usage: git fetch [--prune] [<remote>]' : null
    case 'cherry-pick':
      if (hasOption(parsed, '--abort')) return parsed.args.length || hasOption(parsed, '--no-commit') || hasOption(parsed, '-n') ? 'fatal: --abort cannot be combined with commit arguments' : null
      if (hasOption(parsed, '--no-commit') && hasOption(parsed, '-n')) return 'error: use only one no-commit option'
      return parsed.args.length === 1 ? null : 'usage: git cherry-pick [--no-commit] <commit>'
    case 'reset':
      if (!hasOption(parsed, '--soft') && !hasOption(parsed, '--mixed') && !hasOption(parsed, '--hard')) return 'error: this simulator only supports git reset --hard <target>'
      return parsed.args.length === 1 ? null : 'usage: git reset --hard <target>'
    case 'revert':
      return parsed.args.length === 1 ? null : 'usage: git revert [--no-edit] <commit>'
    case 'switch':
      if (hasOption(parsed, '-c') || hasOption(parsed, '--create')) {
        return parsed.args.length >= 1 && parsed.args.length <= 2 ? null : 'usage: git switch -c <branch> [<start-point>]'
      }
      if (!parsed.args.length && !hasOption(parsed, '--detach')) return 'usage: git switch <branch>'
      return parsed.args.length > 1 ? 'fatal: too many arguments' : null
    case 'stash': {
      const subcommand = parsed.args[0] ?? 'push'
      return ['push', 'pop', 'list', 'drop', 'apply', 'show'].includes(subcommand) ? null : `error: unknown stash subcommand: '${subcommand}'`
    }
    case 'push':
      if (hasOption(parsed, '--delete') || hasOption(parsed, '-d')) return parsed.args.length >= 2 ? null : 'usage: git push <remote> --delete <branch>'
      return parsed.args.length > 2 ? 'usage: git push [<remote>] [<branch>]' : null
    case 'pull':
      return parsed.args.length > 2 ? 'usage: git pull [--rebase] [<remote>] [<branch>]' : null
    case 'rebase':
      if (hasOption(parsed, '--abort') && hasOption(parsed, '--continue')) return 'fatal: --abort and --continue cannot be used together'
      if (hasOption(parsed, '--abort') || hasOption(parsed, '--continue')) return parsed.args.length || hasOption(parsed, '-i') ? 'fatal: --abort/--continue do not take additional arguments' : null
      return parsed.args.length >= 1 ? null : 'usage: git rebase [-i] <upstream>'
    case 'merge-base':
      return parsed.args.length === 2 ? null : 'usage: git merge-base <commit> <commit>'
    case 'rev-list':
      return hasOption(parsed, '--count') && parsed.args.length === 1 && parsed.args[0].includes('..') ? null : 'usage: git rev-list --count <left>..<right>'
    case 'shortlog':
      return parsed.args.length <= 1 ? null : 'usage: git shortlog [-sn] [<revision>]'
    case 'rev-parse':
      if (hasOption(parsed, '--show-toplevel')) return parsed.args.length ? 'usage: git rev-parse --show-toplevel' : null
      return parsed.args.length === 1 ? null : 'usage: git rev-parse <revision>'
    case 'blame':
      return parsed.args.length === 1 ? null : 'usage: git blame <path>'
    case 'grep':
      return parsed.args.length >= 1 && parsed.args.length <= 2 ? null : 'usage: git grep <pattern> [<tree>]'
    case 'describe':
      return parsed.args.length <= 1 ? null : 'usage: git describe --tags [<commit-ish>]'
    case 'range-diff':
      return parsed.args.length === 2 ? null : 'usage: git range-diff <old-range> <new-range>'
    case 'merge-tree':
      return parsed.args.length === 2 ? null : 'usage: git merge-tree <branch-a> <branch-b>'
    case 'verify-commit':
      return parsed.args.length === 1 ? null : 'usage: git verify-commit <commit>'
    case 'verify-tag':
      return parsed.args.length === 1 ? null : 'usage: git verify-tag <tag>'
    case 'fsck':
    case 'count-objects':
    case 'show-ref':
    case 'for-each-ref':
      return parsed.args.length ? `usage: git ${parsed.subcommand}` : null
    case 'cat-file':
      if (hasOption(parsed, '-p') === hasOption(parsed, '-t')) return 'usage: git cat-file (-p | -t) <object>'
      return parsed.args.length === 1 ? null : 'usage: git cat-file (-p | -t) <object>'
    case 'ls-tree':
      return parsed.args.length === 1 ? null : 'usage: git ls-tree <tree>'
    case 'symbolic-ref':
      return parsed.args.length === 1 ? null : 'usage: git symbolic-ref HEAD'
    case 'bisect':
      if (parsed.args[0] === 'run') return parsed.args.length >= 2 ? null : 'usage: git bisect run <authored-test>'
      return parsed.args[0] === 'log' && parsed.args.length === 1 ? null : 'usage: git bisect (run <authored-test> | log)'
    case 'rerere':
      return ['status', 'diff'].includes(parsed.args[0] ?? '') && parsed.args.length === 1 ? null : 'usage: git rerere (status | diff)'
    case 'worktree':
      return parsed.args[0] === 'list' && parsed.args.length === 1 ? null : 'usage: git worktree list'
    case 'sparse-checkout':
      return parsed.args[0] === 'list' && parsed.args.length === 1 ? null : 'usage: git sparse-checkout list'
    case 'submodule':
      return parsed.args[0] === 'status' && parsed.args.length === 1 ? null : 'usage: git submodule status'
    default:
      return null
  }
}

function unknownOptionMessage(subcommand: string, option: string) {
  if (subcommand === 'clone') return `error: unknown option \`${option}\`. Chapter 1 clone supports only -b/--branch and --depth.`
  if (subcommand === 'log') return `fatal: unrecognized argument: ${option}`
  if (subcommand === 'branch') return `error: unknown switch \`${option}\`.`
  return `error: unknown option \`${option}\`.`
}

function positiveIntOption(value: string | true | undefined, option: string) {
  if (value === undefined) return null
  return value === true || !/^\d+$/.test(String(value)) || Number(value) < 1 ? `fatal: invalid ${option} value: ${value}` : null
}

export function isDiagnosticCommand(parsed: ParsedGitCommand) {
  switch (parsed.subcommand) {
    case 'status':
    case 'log':
    case 'show':
    case 'diff':
    case 'reflog':
    case 'check-ignore':
    case 'ls-files':
    case 'merge-base':
    case 'rev-list':
    case 'shortlog':
    case 'rev-parse':
    case 'blame':
    case 'grep':
    case 'describe':
    case 'range-diff':
    case 'merge-tree':
    case 'verify-commit':
    case 'verify-tag':
    case 'fsck':
    case 'count-objects':
    case 'cat-file':
    case 'ls-tree':
    case 'show-ref':
    case 'for-each-ref':
    case 'symbolic-ref':
    case 'bisect':
    case 'rerere':
    case 'worktree':
    case 'sparse-checkout':
    case 'submodule':
      return true
    case 'help':
    case 'version':
      return true
    case 'config':
      return hasOption(parsed, '--get') || hasOption(parsed, '--list') || hasOption(parsed, '-l')
    case 'branch':
      return !parsed.args.length && !hasOption(parsed, '-d') && !hasOption(parsed, '-D') && !hasOption(parsed, '--delete') && !hasOption(parsed, '-m') && !hasOption(parsed, '--move')
    case 'remote':
      return !parsed.args.length && Object.keys(parsed.options).every((option) => ['-v', '--verbose'].includes(option))
    case 'stash':
      return parsed.args[0] === 'list' || parsed.args[0] === 'show'
    case 'tag':
      return !parsed.args.length
    default:
      return false
  }
}

export function diagnosticMetadataForCommand(parsed: ParsedGitCommand) {
  const byCommand: Record<string, string[]> = {
    status: ['inspected_status'],
    log: ['inspected_log'],
    show: ['inspected_show'],
    diff: ['inspected_diff'],
    reflog: ['inspected_reflog'],
    branch: ['inspected_branch_list'],
    remote: ['inspected_remotes'],
    'check-ignore': ['inspected_ignore_rule'],
    'ls-files': ['inspected_index'],
    'merge-base': ['inspected_merge_base'],
    'rev-list': ['inspected_rev_list'],
    shortlog: ['inspected_shortlog'],
    'rev-parse': ['resolved_revision'],
    blame: ['inspected_blame'],
    grep: ['searched_repository'],
    describe: ['described_revision'],
    'range-diff': ['compared_patch_series'],
    'merge-tree': ['inspected_virtual_merge'],
    'verify-commit': ['verified_commit_signature'],
    'verify-tag': ['verified_tag_signature'],
    fsck: ['checked_repository_integrity'],
    'count-objects': ['inspected_object_storage'],
    'cat-file': ['inspected_object'],
    'ls-tree': ['inspected_tree'],
    'show-ref': ['inspected_refs'],
    'for-each-ref': ['inspected_refs'],
    'symbolic-ref': ['inspected_symbolic_ref'],
    bisect: ['inspected_bisect_search'],
    rerere: ['inspected_rerere_cache'],
    worktree: ['inspected_worktrees'],
    'sparse-checkout': ['inspected_sparse_checkout'],
    submodule: ['inspected_submodules'],
    config: ['inspected_config'],
    stash: parsed.args[0] === 'show' ? ['inspected_stash_show'] : ['inspected_stash_list'],
    tag: ['inspected_tags'],
    help: ['inspected_git_help'],
    version: ['inspected_git_version'],
  }
  return byCommand[parsed.subcommand] ?? []
}
