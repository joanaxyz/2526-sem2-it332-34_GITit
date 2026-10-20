# Curriculum Blueprint — Arcane Spire Modules 1–4

The content blueprint for the wave-based curriculum: what every level teaches, which waves each tier plays and why, which scenarios fill them, and which new scenarios still need writing. It describes the target design. The implementation steps are in [../PLAN.md](../PLAN.md), and the machine-checked placement contract is [../WAVE_MAP.md](../WAVE_MAP.md); this blueprint is generated from the same data, so the three always agree.

## Module files

- [Module 1 — Local Repository Foundations](MODULE_1.md)
- [Module 2 — Branching and Collaboration](MODULE_2.md)
- [Module 3 — Conflict Resolution](MODULE_3.md)
- [Module 4 — Advanced Recovery and History](MODULE_4.md)

## How to read the blueprint

- **Level:** one of the 21 adventure levels. Levels, their order, and the command each teaches are fixed by the team.
- **Tier:** Easy, Medium or Hard inside a level. Medium unlocks after Easy, Hard after Medium.
- **Wave:** one step inside a tier — the unit the level map's n/n counter counts. Each wave needs one clear, and the tier completes on its last wave.
- **Variant:** an interchangeable scenario for a wave. The first one listed is what a first-time learner plays; a retry after a failure draws another variant of the same wave.
- **Command guide:** shown the first time a step needs a form the learner hasn't used, in any tier.

| Role | What the wave is for |
|---|---|
| debut | First use of a command form, with the command guide. Easy, or Medium for a level's advanced form. Never Hard. |
| practice | The same commands again in a different repository, without the guide. |
| compose | Several of this level's commands in one task. |
| spiral | This level's command together with commands from earlier levels: spaced review in a realistic workflow. |
| transfer | Hard: an unfamiliar situation with distractors and minimal help, using known commands only. |

| Tier | Scaffolding | First-clear reward |
|---|---|---:|
| Easy | Live DAG + Expected State + contextual feedback | 25 GitCoins |
| Medium | Live DAG + Expected State | 35 GitCoins |
| Hard | Live DAG only | 50 GitCoins |

## Module sequence

| Module | Levels | Waves | New scenarios | Time, no failures | Today | Mapped to |
|---|---:|---:|---:|---:|---:|---|
| [Module 1](MODULE_1.md) | 6 | 37 | 18 | ~70 min | ~71 min | SO 1.1–SO 1.6 |
| [Module 2](MODULE_2.md) | 9 | 54 | 33 | ~113 min | ~117 min | SO 2.1–SO 2.9 |
| [Module 3](MODULE_3.md) | 3 | 21 | 15 | ~64 min | ~65 min | SO 3.1–SO 3.3 |
| [Module 4](MODULE_4.md) | 3 | 20 | 18 | ~49 min | ~28 min | SO 4.1–SO 4.3 |
| **All** | **21** | **132** | **84** | **~4.9 h** | **~4.7 h** | SO 1.1–SO 4.3 |

Time is estimated for a learner who never fails: 1 min per wave for the brief and outcome, 0.4 min per typed command, 1 min per file edit, 0.5 min per first-time guide. Retries add time to both columns.

## Level index

| Level | Title | Teaches | Waves E/M/H | Runs today → plan | Time |
|---|---|---|---|---|---:|
| [1.1](MODULE_1.md) | Initializing Repositories | `git init` | 2/2/2 | 5 → 6 | ~9 min |
| [1.2](MODULE_1.md) | Cloning Remote Repositories | `git clone` | 3/2/2 | 7 → 7 | ~12 min |
| [1.3](MODULE_1.md) | Staging and Committing | `git add` + `git commit` | 2/2/2 | 7 → 6 | ~12 min |
| [1.4](MODULE_1.md) | Partial Staging | `git add -p` | 2/2/2 | 7 → 6 | ~12 min |
| [1.5](MODULE_1.md) | Amending Commits | `git commit --amend` | 2/2/2 | 7 → 6 | ~11 min |
| [1.6](MODULE_1.md) | Unstaging and Discarding Changes | `git restore` | 2/2/2 | 7 → 6 | ~12 min |
| [2.1](MODULE_2.md) | Creating and Switching Branches | `git switch` / `git branch` | 2/2/2 | 7 → 6 | ~11 min |
| [2.2](MODULE_2.md) | Branch Naming Conventions | branch naming + `git branch -d` | 2/2/2 | 7 → 6 | ~11 min |
| [2.3](MODULE_2.md) | Stashing Work in Progress | `git stash` | 2/2/2 | 7 → 6 | ~14 min |
| [2.4](MODULE_2.md) | Pushing to a Remote | `git push` | 2/2/2 | 7 → 6 | ~12 min |
| [2.5](MODULE_2.md) | Fetching and Pulling from a Remote | `git fetch` / `git pull` | 2/2/2 | 7 → 6 | ~12 min |
| [2.6](MODULE_2.md) | Reconciling Diverged Local and Remote Histories | fetch/pull + merge + push | 2/2/2 | 7 → 6 | ~14 min |
| [2.7](MODULE_2.md) | Completing Branch Merges | `git merge` | 2/2/2 | 7 → 6 | ~12 min |
| [2.8](MODULE_2.md) | Squash Merging | `git merge --squash` | 2/2/2 | 7 → 6 | ~14 min |
| [2.9](MODULE_2.md) | Deleting and Recovering Remote Branches | `git push --delete` / `git fetch --prune` | 2/2/2 | 7 → 6 | ~13 min |
| [3.1](MODULE_3.md) | Resolving Merge Conflicts Manually | merge conflicts by hand | 3/2/2 | 8 → 7 | ~22 min |
| [3.2](MODULE_3.md) | Resolving Conflicts Using a Merge Tool | `git mergetool` | 2/2/2 | 6 → 6 | ~22 min |
| [3.3](MODULE_3.md) | Cherry-Picking Commits | `git cherry-pick` | 3/3/2 | 8 → 8 | ~20 min |
| [4.1](MODULE_4.md) | Recovering from Hard Resets | `git reflog` + recovery branch | 2/2/2 | 4 → 6 | ~14 min |
| [4.2](MODULE_4.md) | Reversing Pushed Commits Safely | `git revert` | 2/2/2 | 4 → 6 | ~14 min |
| [4.3](MODULE_4.md) | Completing Rebase Recovery Sequences | `git rebase` recovery | 3/2/3 | 4 → 8 | ~20 min |

## Blueprint rules

Rules 1–4 and 8 were checked by machine against every wave, using the game's own command resolver. Rules 5–7 are authoring rules: they are checked when the new scenarios are written (PLAN.md, Tasks 5–8).

1. Every one of the team's 265 scenarios is used exactly once, and every wave has at least two variants.
2. Nothing new is introduced at Hard. Only two Hard waves show a guide, both for forms built from parts the learner already knows (plain `git init`; `git clone --depth … -b …`).
3. Whatever a wave introduces, every variant of that wave uses, so a retry never skips the lesson.
4. Every guided command is used again later: everyday commands at least twice, including once in a later level; specialized commands at a harder tier.
5. Variants in a wave practice the same skill; anything else they use is already known.
6. Diagnostics (`status`, `log`, `show`, `reflog`, `diff`) are never introduced as lessons and never cost commands.
7. No two variants share both a starting state and a target, so a retry is always a new situation.
8. The whole curriculum takes about 4.9 hours with no failures (today about 4.7).

## Spaced review across modules

| Module | Earlier commands it keeps using |
|---|---|
| Module 1 | none (first module) |
| Module 2 | `git add <path>...`, `git commit -m <message>`, `git commit --amend -m <message>`, `git restore --staged <path>...`, `git restore <path>...` |
| Module 3 | `git add <path>...`, `git commit -m <message>`, `git switch <branch>`, `git push <remote> <branch>`, `git pull <remote> <branch>`, `git merge <branch>` |
| Module 4 | `git add <path>...`, `git commit --amend -m <message>`, `git switch <branch>`, `git branch <branch> [<start-point>]`, `git push -u <remote> <branch>`, `git push --force-with-lease <remote> <branch>`, `git pull <remote> <branch>`, `git cherry-pick <commit>` |
