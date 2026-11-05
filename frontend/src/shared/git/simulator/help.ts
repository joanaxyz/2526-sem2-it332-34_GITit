import { GIT_COMMAND_NAMES, SUPPORTED_OPTIONS } from '@/shared/git/simulator/commandMetadata'

// General documentation only: never read scenario targets, hints, or solutions.
const SYNOPSES: Record<string, string> = {
  init: '[<options>] [<directory>]',
  clone: '[<options>] <repository> [<directory>]',
  status: '[<options>] [--] [<pathspec>...]',
  add: '[<options>] [--] <pathspec>...',
  commit: '[<options>] [--] <pathspec>...',
  branch: '[<options>] [<branch-name>] [<start-point>]',
  checkout: '[<options>] <branch>\n   or: git checkout [<options>] [<tree-ish>] -- <pathspec>...',
  switch: '[<options>] [<branch>]',
  restore: '[<options>] [--source=<tree>] <path>...',
  config: '[<options>]\n   or: git config [<options>] <name> [<value>]',
  log: '[<options>] [<revision-range>] [[--] <path>...]',
  diff: '[<options>] [<commit>] [--] [<path>...]',
  remote: '[-v | --verbose]\n   or: git remote <subcommand> [<args>]',
  merge: '[<options>] [<commit>...]',
  reset: '[<options>] [<commit>] [[--] <path>...]',
  rebase: '[<options>] [<upstream> [<branch>]]',
  push: '[<options>] [<repository> [<refspec>...]]',
  pull: '[<options>] [<repository> [<refspec>...]]',
}

export function commandHelpText(command: string): string | null {
  const options = SUPPORTED_OPTIONS[command]
  if (!options) return null
  return [
    `usage: git ${command} ${SYNOPSES[command] ?? '[<options>] [<args>]'}`,
    '',
    ...[...options].map((option) => `    ${option}`),
    '    -h, --help    show help',
  ].join('\n')
}

export function gitHelpText(all = false) {
  if (all) return ['Available commands:', '', ...GIT_COMMAND_NAMES.map((name) => `  git ${name}`)].join('\n')
  return [
    'usage: git [--version] [--help] <command> [<args>]',
    '',
    'These are common Git commands used in various situations:',
    '',
    'start a working area',
    '   clone      Clone a repository into a new directory',
    '   init       Create an empty Git repository or reinitialize an existing one',
    '',
    'work on the current change',
    '   add        Add file contents to the index',
    '   restore    Restore working tree files',
    '',
    'examine the history and state',
    '   diff       Show changes between commits, commit and working tree, etc',
    '   log        Show commit logs',
    '   status     Show the working tree status',
    '',
    'grow, mark and tweak your common history',
    '   branch     List, create, or delete branches',
    '   commit     Record changes to the repository',
    '   merge      Join two or more development histories together',
    '   switch     Switch branches',
    '',
    "'git help -a' lists available commands.",
    "See 'git help <command>' to read about a specific subcommand.",
  ].join('\n')
}
