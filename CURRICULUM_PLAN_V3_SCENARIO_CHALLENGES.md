# Git-it Curriculum V3 — Scenario-First Challenges

## Non-negotiable curriculum rules

1. **Command Adventure introduces. Git-it Challenge applies.**  
   A Challenge must not require a Git concept, command form, or problem type that the learner has not already met in Command Adventure.

2. **A Challenge may combine earlier storeys.**  
   A Challenge in Storey 5 may use commands from Storeys 1–5. It may not use a Storey 6 or Storey 7 concept.

3. **Challenge is not a command drill.**  
   Every Challenge variant is authored as a repository scenario with an initial DAG/ref state and an intended graph transition.

4. **The curriculum leads the engine, not the other way around.**  
   If a high-quality scenario needs richer graph/evaluator support, the curriculum records that contract through `evaluation_spec.curriculum_contract`. The command engine can be expanded later.

5. **The diagram is central.**  
   Challenge stories must involve visible changes to local branches, remote-tracking branches, HEAD, commit parents, merge commits, replaced commits, stash state, or published refs.

## Storey progression

| Storey | Command Adventure introduces | Challenge applies |
|---|---|---|
| 1. Repository Foundations | `init`, `clone`, `status`, `log`, `show` | Clone the correct remote history and read the resulting branch/remote DAG. |
| 2. Tracking Changes and Snapshots | `diff`, `add`, `commit`, `restore`, `rm` | Create focused commits while keeping accidental files out of history. |
| 3. Branch Navigation | `branch`, `switch`, legacy `checkout` branch movement | Create branch pointers, move HEAD, branch from older commits, and delete safe merged refs. |
| 4. Merging and Conflict Resolution | `merge`, conflict-side commands, merge continue/abort | Fast-forward, create merge commits, and resolve conflicts into a clean two-parent commit. |
| 5. Undoing and Recovery | `commit --amend`, `reset`, `revert`, `reflog` | Choose safe recovery based on whether history is local or shared. |
| 6. Temporary Work and Patch Movement | `stash`, `cherry-pick` | Shelve WIP and transplant selected commits without merging an entire branch. |
| 7. Remotes and Collaboration | `remote`, `fetch`, `pull`, `push` | Coordinate local branches, remote-tracking refs, upstreams, merge remote history, and publish. |

## Challenge set

### Storey 1 — Onboard an Existing Repository
The learner creates a local repository from authored remote history. The graph changes from no local DAG into branches and remote-tracking refs.

- Easy: clone default `main` history.
- Medium: clone a specific starter branch.
- Hard: shallow clone the default branch.

### Storey 2 — Compose Clean History
The learner creates the first authored local snapshots. The graph changes because `main` moves to new commits.

- Easy: commit one tracked file edit.
- Medium: commit only intended source changes while leaving scratch work outside history.
- Hard: stop tracking a secret file while preserving the local copy.

### Storey 3 — Branch the Workstream
The learner moves work onto the right branch/ref. The graph changes through new branch refs, HEAD movement, and branch cleanup.

- Easy: create a feature branch and commit there.
- Medium: create a hotfix branch at an older release point.
- Hard: delete a branch pointer that is already merged into main.

### Storey 4 — Integrate Diverging History
The learner brings histories together. The graph changes through fast-forward branch movement, merge commits, and conflict completion.

- Easy: fast-forward main to a feature tip.
- Medium: create an explicit merge commit with two parents.
- Hard: resolve a conflict and finish a two-parent merge commit.

### Storey 5 — Recover History Safely
The learner decides between replacement, movement, and inverse commits. The graph changes differently depending on safety.

- Easy: amend an unshared local tip.
- Medium: hard-reset an unshared bad local tip.
- Hard: revert a bad shared commit without deleting history.

### Storey 6 — Pause and Transplant Work
The learner keeps unfinished workspace changes separate from commit history and moves only selected commits.

- Easy: stash WIP before switching branch.
- Medium: cherry-pick one approved fix without merging the rest of a branch.
- Hard: stash local notes, cherry-pick a fix, and leave the release branch clean.

### Storey 7 — Coordinate with Remote History
The learner uses remote-tracking refs as part of the visible graph, not as vague “online Git.”

- Easy: fetch remote updates without moving local main.
- Medium: pull a fast-forward upstream update.
- Hard: fetch, merge diverged remote history, and push the integrated merge commit.

## Seed validation added

The seed command now validates the curriculum contract:

- each Challenge level must declare `uses_adventure_quests`;
- every referenced Adventure quest must exist;
- referenced Adventure quests must belong to the same or an earlier storey;
- every Challenge variant must start from authored local or remote commit history;
- every Challenge variant must include `evaluation_spec.curriculum_contract.dag_transition`.

This protects the rule: **Challenge never introduces what Adventure has not taught.**
