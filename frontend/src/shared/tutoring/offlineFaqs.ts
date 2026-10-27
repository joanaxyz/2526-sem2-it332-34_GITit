export const OFFLINE_FAQS = [
  {
    id: 'uncommon', question: 'What are some less common Git commands?',
    keywords: /\b(uncommon|less.common|advanced|bisect|worktree|reflog|blame)\b/i,
    answer: '`git reflog` shows recent local reference movements, which can help you locate earlier work. `git bisect` narrows down the commit that introduced a bug. `git worktree` lets you check out another branch in a separate directory. `git blame` shows which commit last changed each line. These tools help you investigate and organize work; they are not solutions to a specific scenario.',
  },
  {
    id: 'head', question: 'What is HEAD, and what does detached HEAD mean?',
    keywords: /\bhead\b/i,
    answer: 'HEAD identifies the branch or commit you currently have checked out. Normally it points to a branch, which moves forward when you commit. In detached HEAD, it points directly to a commit. You can still make commits there, but create a branch to keep an easy reference to that work before switching away.',
  },
  {
    id: 'staging', question: 'How do the working tree, staging area, and commits differ?',
    keywords: /\b(stage|staging|index|add|working.tree)\b/i,
    answer: 'The working tree contains the files you are editing. The staging area holds the changes proposed for your next commit. A commit records that staged snapshot in history. Editing a file after staging it can leave one version staged and newer changes unstaged.',
  },
  {
    id: 'branches', question: 'What is a branch?',
    keywords: /\b(branch|branches|checkout|switch)\b/i,
    answer: 'A branch is a movable name for a commit. It lets you develop a line of work independently. Creating a branch does not copy the whole repository; it creates a reference. New commits advance the branch you have checked out.',
  },
  {
    id: 'commits', question: 'What does a commit save?',
    keywords: /\b(commit|commits|history|log)\b/i,
    answer: 'A commit records a snapshot of staged changes, a message, author information, and links to its parent commits. Unstaged edits are not automatically included. The links between commits form the history shown in a repository graph.',
  },
  {
    id: 'conflicts', question: 'Why do merge conflicts happen?',
    keywords: /\b(merge|merging|conflict|conflicts)\b/i,
    answer: 'A merge combines two lines of work. A conflict occurs when Git cannot automatically combine changes, such as overlapping edits to the same lines. Review both versions and decide what the combined file should contain. A conflict is a request for a human decision, not a sign that your history is lost.',
  },
  {
    id: 'remotes', question: 'What is the difference between fetch, pull, and push?',
    keywords: /\b(remote|fetch|pull|push|origin)\b/i,
    answer: 'A remote is another repository location. Fetch downloads objects and updates your remote-tracking references without integrating them into your current branch. Pull fetches and then integrates changes, using merge or rebase depending on configuration. Push publishes local commits to a remote.',
  },
  {
    id: 'undo', question: 'How do restore, reset, and revert differ?',
    keywords: /\b(reset|restore|revert|undo|recover)\b/i,
    answer: 'Restore changes working files or staged content. Reset can move a branch reference and, depending on its mode, change staging or working files. Revert adds a new commit that reverses an earlier commit. Before choosing, identify whether you want to change files, staging, or history, and whether others already share that history.',
  },
  {
    id: 'rebase', question: 'How is rebase different from merge?',
    keywords: /\b(rebase|rebasing|cherry.pick)\b/i,
    answer: 'Merge joins lines of history while preserving existing commits. Rebase replays commits onto a new base, creating new commit identities. Cherry-pick also replays changes, but selects individual commits. Rewriting history that other people already use requires coordination.',
  },
  {
    id: 'stash', question: 'What is a stash?',
    keywords: /\bstash\b/i,
    answer: 'A stash temporarily stores uncommitted work so you can return to a cleaner working state. You can later apply those saved changes. Untracked files are not included by default, and applying a stash can cause conflicts if the surrounding files have changed.',
  },
] as const

export function findOfflineFaq(message: string) {
  return OFFLINE_FAQS.find((faq) => faq.keywords.test(message))
}
