import { SimulatorCommandError, type CommandOutcome, type MutableRepositoryState, type ParsedGitCommand } from '@/shared/git/simulator/types'
import {
  gitBlame,
  gitCatFile,
  gitCountObjects,
  gitDescribe,
  gitForEachRef,
  gitFsck,
  gitGrep,
  gitLsTree,
  gitMergeTree,
  gitRangeDiff,
  gitRevParse,
  gitShortlog,
  gitShowRef,
  gitSymbolicRef,
  gitVerifyCommit,
  gitVerifyTag,
} from '@/shared/git/simulator/commands/advancedDiagnostics'
import { gitBranch, gitCheckout, gitSwitch } from '@/shared/git/simulator/commands/branching'
import { gitCherryPick, gitCommit, gitRevert, gitTag } from '@/shared/git/simulator/commands/commits'
import { formatDiff, formatLog, formatLsFiles, formatReflog, formatShow, formatStatus } from '@/shared/git/simulator/commands/formatters'
import { gitMerge, gitMergetool, gitRebase } from '@/shared/git/simulator/commands/merge'
import { gitCheckIgnore, gitMergeBase, gitRevList } from '@/shared/git/simulator/commands/misc'
import { gitFetch, gitPull, gitPush, gitRemote } from '@/shared/git/simulator/commands/remote'
import { gitClone, gitConfig, gitInit } from '@/shared/git/simulator/commands/repository'
import { gitBisect, gitRerere, gitSparseCheckout, gitSubmodule, gitWorktree } from '@/shared/git/simulator/commands/scenarioDiagnostics'
import { gitStash } from '@/shared/git/simulator/commands/stash'
import { gitAdd, gitReset, gitRestore, gitRm } from '@/shared/git/simulator/commands/staging'

export function dispatch(state: MutableRepositoryState, parsed: ParsedGitCommand): CommandOutcome {
  switch (parsed.subcommand) {
    case 'init':
      return gitInit(state, parsed)
    case 'clone':
      return gitClone(state, parsed)
    case 'status':
      return { command: 'status', stdout: formatStatus(state, parsed) }
    case 'config':
      return gitConfig(state, parsed)
    case 'add':
      return gitAdd(state, parsed)
    case 'commit':
      return gitCommit(state, parsed)
    case 'rm':
      return gitRm(state, parsed)
    case 'restore':
      return gitRestore(state, parsed)
    case 'branch':
      return gitBranch(state, parsed)
    case 'switch':
      return gitSwitch(state, parsed)
    case 'checkout':
      return gitCheckout(state, parsed)
    case 'merge':
      return gitMerge(state, parsed)
    case 'mergetool':
      return gitMergetool(state, parsed)
    case 'reset':
      return gitReset(state, parsed)
    case 'revert':
      return gitRevert(state, parsed)
    case 'stash':
      return gitStash(state, parsed)
    case 'cherry-pick':
      return gitCherryPick(state, parsed)
    case 'remote':
      return gitRemote(state, parsed)
    case 'fetch':
      return gitFetch(state, parsed)
    case 'pull':
      return gitPull(state, parsed)
    case 'push':
      return gitPush(state, parsed)
    case 'rebase':
      return gitRebase(state, parsed)
    case 'tag':
      return gitTag(state, parsed)
    case 'log':
      return { command: 'log', stdout: formatLog(state, parsed) }
    case 'show':
      return { command: 'show', stdout: formatShow(state, parsed) }
    case 'diff':
      return { command: 'diff', stdout: formatDiff(state, parsed) }
    case 'reflog':
      return { command: 'reflog', stdout: formatReflog(state) }
    case 'check-ignore':
      return gitCheckIgnore(state, parsed)
    case 'ls-files':
      return { command: 'ls-files', stdout: formatLsFiles(state, parsed) }
    case 'merge-base':
      return gitMergeBase(state, parsed)
    case 'rev-list':
      return gitRevList(state, parsed)
    case 'shortlog':
      return gitShortlog(state, parsed)
    case 'rev-parse':
      return gitRevParse(state, parsed)
    case 'blame':
      return gitBlame(state, parsed)
    case 'grep':
      return gitGrep(state, parsed)
    case 'describe':
      return gitDescribe(state, parsed)
    case 'range-diff':
      return gitRangeDiff(state, parsed)
    case 'merge-tree':
      return gitMergeTree(state, parsed)
    case 'verify-commit':
      return gitVerifyCommit(state, parsed)
    case 'verify-tag':
      return gitVerifyTag(state, parsed)
    case 'fsck':
      return gitFsck(state)
    case 'count-objects':
      return gitCountObjects(state)
    case 'cat-file':
      return gitCatFile(state, parsed)
    case 'ls-tree':
      return gitLsTree(state, parsed)
    case 'show-ref':
      return gitShowRef(state)
    case 'for-each-ref':
      return gitForEachRef(state)
    case 'symbolic-ref':
      return gitSymbolicRef(state, parsed)
    case 'bisect':
      return gitBisect(state, parsed)
    case 'rerere':
      return gitRerere(state, parsed)
    case 'worktree':
      return gitWorktree(state, parsed)
    case 'sparse-checkout':
      return gitSparseCheckout(state, parsed)
    case 'submodule':
      return gitSubmodule(state, parsed)
    default:
      throw new SimulatorCommandError(`fatal: unsupported ${parsed.subcommand} operation`, 129)
  }
}
