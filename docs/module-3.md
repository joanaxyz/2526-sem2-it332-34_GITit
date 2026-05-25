# **Module 3 — Conflict Resolution**

**6 Lessons · 4 Scenario Skill Focuses · Based on Chapter 6**  
 *Mapped to: SO 3.1 – SO 3.5*

---

## **Module Overview**

This module addresses conflict resolution — one of the most anxiety-inducing situations for junior developers. Students learn what causes merge conflicts, how to read conflict markers precisely, resolve conflicts manually and with a merge tool, apply conflict prevention strategies, and selectively apply commits through cherry-picking.

The framing throughout this module is deliberate: **conflicts are not failures**. They are a normal outcome of parallel development on shared files. Every conflict is resolvable. The platform's Contextual Feedback Panel on Easy level is particularly valuable here — it narrates what each unresolved marker means and what the consequence of premature staging would be.

**Module KPIs:** CAR, HLCR, RTA, ARC, SCR (validity gate)  
 **Measurement validity condition:** SCR ≥ 80% before module KPI data is reportable  
 **RTA applies from this module onward** — structurally changed retry variants test genuine skill transfer

---

## **Curriculum Note — Scenario Skill Focus Count**

| Lesson | Title | Scenario practice? | Scenario Skill Focus |
| ----- | ----- | ----- | ----- |
| 3.1 | What Causes Merge Conflicts | ◆ Yes | Conflict identification |
| 3.2 | Reading Conflict Markers | No | — (conceptual prep) |
| 3.3 | Resolving Conflicts Manually | ◆ Yes | Manual conflict resolution |
| 3.4 | Using a Merge Tool | ◆ Yes | Mergetool workflow |
| 3.5 | Conflict Prevention Strategies | No | — (conceptual/strategic) |
| 3.6 | Cherry-Picking Commits | ◆ Yes | Cherry-pick workflow |

4 scenario skill focuses. Lessons 3.2 and 3.5 are concept-only. The original curriculum draft stated 5 scenario skill focuses; the correct count is 4\.

---

## **Read-Only Commands Active in This Module**

| Command | Introduced | Purpose |
| ----- | ----- | ----- |
| `git status` | 0.4 | 🔍 DIAGNOSTIC — Identify which files are in conflict |
| `git diff` | 1.8 | 🔍 DIAGNOSTIC — Inspect remaining conflict markers |
| `git log --oneline --graph --all` | 0.6 | 🔍 DIAGNOSTIC — Visualize branch structure before merging |
| `git diff main..feature` | 3.5 | 🔍 DIAGNOSTIC — Preview changes a merge would introduce |

---

## **Lesson 3.1 — What Causes Merge Conflicts ◆**

**Type:** Scenario · **Scenario Skill Focus:** Conflict identification  
 **Mapped to:** SO 3.1 (CAR ≥ 70%)

**Note on CAR applicability:** The primary skill in this lesson is diagnosing a conflict cause using `git status` and reading the resulting conflict state. The action commands (`git merge`) trigger the conflict state. CAR measures whether students can reach the target conflict state (correctly initiated merge) within the command threshold. Diagnostic inspection of the conflict state uses `git status` and `git diff` — non-counted.

### **Learning Outcomes**

* Identify the three main causes of merge conflicts: overlapping edits, divergent histories, and delete-modify conflicts  
* Initiate a merge that produces a conflict state  
* Recognize a conflict state in `git status` output  
* Understand why Git cannot automatically resolve certain conflicts

### **Content Summary**

Before students can resolve conflicts, they need to understand why they happen. Not all merges produce conflicts — Git can resolve many changes automatically. Conflicts occur specifically when Git cannot determine the correct merged result without human judgment.

**The three conflict causes:**

**1\. Overlapping edits (most common):**  
 Two branches modified the same lines of the same file differently. Neither change is wrong — both are valid contributions. Git cannot determine which version should prevail or how to combine them, so it marks the section as a conflict and waits for human resolution.

**2\. Divergent histories with structural changes:**  
 Branches that have been separate for a long time often accumulate changes that interact in complex ways. A function renamed on one branch and extended on another; a file restructured on one branch and modified on another. The longer branches stay separate, the more potential for conflict.

**3\. Delete-modify conflicts:**  
 One branch deleted a file; another branch modified it. Git doesn't know whether to keep the modification (and un-delete the file) or honor the deletion. This is explicitly flagged as a separate conflict type because it requires a different resolution decision.

**Reading conflict state in `git status`:**  
 When a merge produces conflicts, `git status` shows:

On branch main  
You have unmerged paths.  
  (fix conflicts and run "git commit")

Unmerged paths:  
  (use "git add \<file\>..." to mark resolution)  
        both modified:   src/auth.js  
        deleted by us:   src/legacy.js

The labels tell you the conflict type: `both modified` is overlapping edits; `deleted by us` / `modified by them` is delete-modify.

**Git cannot resolve conflicts without human judgment:**  
 Git uses a three-way merge algorithm: it compares the common ancestor with both branch tips. When both branches have changed the same region, and the changes differ, the algorithm has no basis for choosing — it surfaces the conflict for human resolution.

🔍 **`git status` is the primary diagnostic tool for understanding conflict state.** Non-counted. Run it after any merge attempt to identify conflicted files and conflict types.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git merge <branch>` | ⚡ ACTION | Attempt a merge (may produce conflict state) |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Identify which files are in conflict and conflict type |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** conflict cause types, repository divergence patterns, pre-merge DAG reading tasks.

---

## **Lesson 3.2 — Reading Conflict Markers**

**Type:** Conceptual · No scenario practice

### **Learning Outcomes**

* Identify the three sections of a Git conflict marker block  
* Understand what HEAD, the separator, and the branch name represent  
* Recognize a fully resolved file vs a partially resolved file (stray marker)  
* Use `git diff` to spot accidentally remaining markers

### **Content Summary**

Conflict markers are the format Git uses to annotate conflicting sections of a file. Reading them accurately is prerequisite to resolving them correctly — the most common resolution mistake is leaving a stray marker in the file after editing, which breaks build tools and parsers.

**Conflict marker anatomy:**

\<\<\<\<\<\<\< HEAD  
const timeout \= 5000;  
\=======  
const timeout \= 3000;  
\>\>\>\>\>\>\> feature/performance-tuning

| Section | Meaning |
| ----- | ----- |
| `<<<<<<< HEAD` | Start of the current branch's version of this section |
| Everything between `<<<<<<<` and `=======` | The current branch's content |
| `=======` | Separator between the two versions |
| Everything between `=======` and `>>>>>>>` | The incoming branch's content |
| `>>>>>>> branch-name` | End of the incoming branch's version |

**Resolving means replacing the entire block:**  
 The resolution process is:

1. Decide what the correct final content should be (keep current, keep incoming, combine, or write new)  
2. Delete all three marker lines (`<<<<<<<`, `=======`, `>>>>>>>`) and replace the entire block with the correct content  
3. The file should look exactly as if the conflict never occurred — clean, valid code

**After resolution, the file should have no `<<<<`, `====`, or `>>>>` in it.** Build tools and syntax checkers will fail if markers remain. Running `git diff` after editing and before staging is the safest way to confirm no stray markers exist.

🔍 **`git diff` is a diagnostic command.** Non-counted. Use it after resolving each file to confirm the markers are gone before staging.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git diff` | 🔍 DIAGNOSTIC — Non-Counted | Inspect files for remaining conflict markers |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Check which files still have unresolved conflicts |

### **No Scenario Practice**

This lesson is conceptual preparation for Lesson 3.3.

---

## **Lesson 3.3 — Resolving Conflicts Manually ◆**

**Type:** Scenario · **Scenario Skill Focus:** Manual conflict resolution  
 **Mapped to:** SO 3.1 (CAR ≥ 70%)  
 *(Maps to original curriculum Lesson 3.3)*

### **Learning Outcomes**

* Edit conflicted files to produce a correct resolved version  
* Stage resolved files to signal completion to Git  
* Complete the merge commit after all conflicts are resolved  
* Abort a merge in progress and return to the pre-merge state

### **Content Summary**

Manual conflict resolution is the core skill. Students work through conflicts by editing the marker blocks directly — deciding which version to keep, how to combine both, or how to write an entirely new resolution that satisfies both branches' intent.

**The resolution workflow:**

1. **Run `git status`** — identify all conflicted files  
2. **Open each conflicted file** — find and read all conflict marker blocks  
3. **Edit the file** — replace the entire marker block (all three sections \+ all three marker lines) with the correct content  
4. **Run `git diff`** — confirm no stray markers remain and the content is correct  
5. **Stage the file** — `git add <resolved-file>` tells Git this file is resolved  
6. **Repeat** for all conflicted files  
7. **Run `git status`** — confirm all files are staged and no unmerged paths remain  
8. **Commit** — `git commit` completes the merge commit (Git pre-fills the message)

**"Premature staging":**  
 Staging a file that still contains conflict markers tells Git the conflict is resolved. The merge commit will succeed, but the file in the repository will contain raw conflict markers — breaking the codebase. The Easy-level Contextual Feedback Panel warns about this and describes the consequence. At higher difficulty levels, students must catch this themselves using `git diff`.

**`git merge --abort`:**  
 At any point during a conflicted merge (before the final commit), `git merge --abort` cancels the merge entirely and returns the repository to its pre-merge state. The branches are unchanged; no merge commit is created. This is the correct choice when a conflict is too complex to resolve immediately and you need time to understand the changes involved.

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git add <resolved-file>` | ⚡ ACTION | Mark a file as conflict-resolved |
| `git commit` | ⚡ ACTION | Complete the merge commit |
| `git merge --abort` | ⚡ ACTION | Abort the merge and return to pre-merge state |
| `git diff` | 🔍 DIAGNOSTIC — Non-Counted | Verify no stray conflict markers before staging |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Check resolution progress |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×3 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** conflict complexity, file types, resolution strategies (keep current / keep incoming / combine / write fresh), abort-then-retry scenarios.

---

## **Lesson 3.4 — Using a Merge Tool ◆**

**Type:** Scenario · **Scenario Skill Focus:** Mergetool workflow  
 **Mapped to:** SO 3.2 (CAR ≥ 70%)  
 *(Maps to original curriculum Lesson 3.4)*

### **Learning Outcomes**

* Configure a merge tool in Git's global configuration  
* Launch `git mergetool` to resolve conflicts in a structured interface  
* Complete the merge after resolving all conflicts through the tool  
* Understand the four panels a merge tool shows and what each represents  
* Know when a merge tool adds value vs when manual resolution is faster

### **Content Summary**

Merge tools provide a structured three- or four-panel view of a conflict, making it easier to understand what changed on each branch and to construct the correct resolution without editing raw marker syntax.

**The four panels (varies by tool):**

| Panel | Content |
| ----- | ----- |
| LOCAL | The current branch's version of the file |
| REMOTE (or THEIRS) | The incoming branch's version |
| BASE | The common ancestor's version (the last shared state) |
| MERGED | The result — what you are building toward |

The BASE panel is particularly useful — seeing the common ancestor makes it clear what each branch *changed*, not just what they currently contain. This context often makes the right resolution obvious.

**`git mergetool` behavior:**  
 Launches the configured merge tool for each conflicted file in sequence. After you save and close each file in the tool, Git asks whether the conflict was resolved. After all files are processed, the merge state is ready for `git commit`.

**Common merge tools:**

* `vimdiff` (terminal-based, always available)  
* `VS Code` (configured via `git config --global merge.tool vscode`)  
* `IntelliJ/IDEA` (configured similarly)  
* `meld` (graphical, Linux)  
* `kdiff3` (cross-platform graphical)

The platform's simulator models the mergetool workflow abstractly — the specific tool is not required to match. The scenario's target state is defined by the resulting resolved file content, not the tool used.

**Configuring a merge tool:**

git config \--global merge.tool vscode  
git config \--global mergetool.vscode.cmd 'code \--wait $MERGED'

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git config --global merge.tool <tool>` | ⚡ ACTION | Set the global merge tool |
| `git mergetool` | ⚡ ACTION | Launch the configured merge tool for all conflicts |
| `git status` | 🔍 DIAGNOSTIC — Non-Counted | Confirm all conflicts resolved after mergetool |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×2 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×2 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** tool configuration contexts, conflict complexity levels, multi-file conflict scenarios.

---

## **Lesson 3.5 — Conflict Prevention Strategies**

**Type:** Conceptual · No scenario practice

### **Learning Outcomes**

* Apply fetch-before-merge as a proactive conflict prevention habit  
* Use branch comparison to identify divergence before merging  
* Understand how small, frequent integrations reduce conflict severity  
* Recognize conflict-prone repository patterns and team behaviors

### **Content Summary**

Prevention is better than resolution. This lesson shifts from reactive to proactive — teaching the habits that reduce conflict frequency and severity. These are team behaviors, not just individual commands.

**Fetch-before-merge:**  
 Before starting a merge, fetch the latest remote state. This ensures you are merging against the current remote tip, not a stale view of it. A merge that would have been clean yesterday might conflict today if a teammate pushed changes.

**Branch comparison before merging:**  
 `git diff main..feature` shows all changes the feature branch would bring into main — before the merge happens. Reading this output before merging helps identify potential conflict zones and prepares you for what to expect.

🔍 **`git diff main..feature` is a diagnostic command.** Non-counted. Use it before any significant merge to preview the incoming changes.

**Short-lived branches:**  
 The longer a feature branch lives without integrating back to `main`, the more potential for conflicts. Short-lived branches (resolved within a day or two) almost never produce serious conflicts because the codebase hasn't changed significantly since the branch was created. Long-lived branches accumulate drift.

**Coordination patterns:**

* Establish who merges to `main` (usually via pull requests rather than direct `git merge`)  
* Agree on a branching strategy (GitFlow, trunk-based development, GitHub Flow)  
* Communicate before starting large refactors that will touch many files  
* Review incoming changes via `git fetch` and inspect before integrating

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git fetch origin` | ⚡ ACTION | Check remote for new commits before merging |
| `git diff main..feature` | 🔍 DIAGNOSTIC — Non-Counted | Preview changes a merge would introduce |

### **No Scenario Practice**

This lesson is conceptual and strategic.

---

## **Lesson 3.6 — Cherry-Picking Commits ◆**

**Type:** Scenario · **Scenario Skill Focus:** Cherry-pick workflow  
 **Mapped to:** SO 3.3 (CAR ≥ 70%)  
 *(Maps to original curriculum Lesson 3.6)*

### **Learning Outcomes**

* Apply a specific commit from one branch to another using `git cherry-pick`  
* Cherry-pick without immediately committing to review changes first  
* Abort a cherry-pick operation in progress  
* Understand when cherry-pick is and is not the right tool  
* Read the resulting DAG after a cherry-pick (new commit, new hash, same changes)

### **Content Summary**

Cherry-picking is selective history application — taking one commit's diff and replaying it on a different branch without merging the entire source branch. The canonical use case is backporting a bug fix from `main` to a release branch.

**What cherry-pick actually does:**  
 `git cherry-pick <hash>` takes the diff introduced by the specified commit (changes relative to its parent) and applies that same diff on top of the current branch, creating a new commit. The new commit has a different hash than the original — it is a new commit that happens to contain the same changes. Both commits coexist in the repository.

**The DAG after cherry-pick:**

Before:  
main:    A → B → C (HEAD)  
release: A → D → E (release/1.0)

After cherry-picking B onto release:  
main:    A → B → C  
release: A → D → E → B' (same diff as B, new hash)

**`--no-commit` mode:**  
 `git cherry-pick --no-commit <hash>` applies the changes to the staging area without creating a commit. This allows you to review and potentially modify the changes before committing — useful when the cherry-picked changes need minor adaptation for the target branch context.

**When cherry-pick is appropriate:**

* Backporting a specific bug fix to a release branch  
* Applying a hotfix to multiple maintenance branches  
* Extracting an accidentally committed change that belongs on a different branch

**When cherry-pick is not appropriate:**

* Moving large feature work (use merge or rebase instead — cherry-pick loses branch context)  
* When the same commit will later be merged through a regular merge (can cause duplicate commit confusion)  
* When the commit depends on other commits not present on the target branch

### **Commands Introduced**

| Command | Type | Purpose |
| ----- | ----- | ----- |
| `git cherry-pick <hash>` | ⚡ ACTION | Apply a specific commit to the current branch |
| `git cherry-pick --no-commit <hash>` | ⚡ ACTION | Apply changes to staging area without committing |
| `git cherry-pick --abort` | ⚡ ACTION | Abort a cherry-pick in progress |
| `git log --oneline --graph --all` | 🔍 DIAGNOSTIC — Non-Counted | Verify resulting DAG after cherry-pick |

### **Scenario Practice**

| Difficulty | Sessions | Scaffolding Available |
| ----- | ----- | ----- |
| Easy | ×3 | Live DAG \+ Expected-state diagram \+ Contextual feedback panel |
| Medium | ×3 | Live DAG \+ Expected-state diagram |
| Hard | ×2 | Live DAG only |

**Scenario variants rotate:** source/target branch combinations, single vs multi-commit cherry-picks, `--no-commit` review contexts, abort-and-retry scenarios.

---

*→ Next: Module 4 — Advanced Recovery and History*

