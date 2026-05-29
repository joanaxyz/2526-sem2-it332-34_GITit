# GIT it! Scenario Design Principles

Global standards that apply to every module, every lesson, every difficulty.

---

## 1. Scenarios Must Be Realistic

Every scenario must place the student in a believable professional or academic situation.
The narrative context must explain **why** the Git operation is needed — not just **what** to do.

Bad: "You have a file called `file_A.py`. Stage and commit it."
Good: "You're a junior dev who just finished the login validation function. Your team lead
      asked you to commit only that function before pushing — there are unrelated debug prints
      in the same file that shouldn't go in this commit."

The environment, project type, and task brief must cohere. A capstone project scenario
does not reference a corporate ticketing system. A startup scenario does not use
government-style documentation language.

---

## 2. Difficulty is Determined by Reasoning Demand, Not Parameter Substitution

The three difficulty levels represent different cognitive loads:

| Difficulty | Student is given | Student must infer |
|------------|------------------|--------------------|
| Easy | Explicit instructions with specific filenames and commands | Nothing — the path is clear |
| Medium | Context and goal, partial hints | Which command variant / which files |
| Hard | Context and goal only | Full reasoning: what state is this in? what do I need? how? |

**What difficulty is NOT:**
- Swapping one filename for another
- Increasing the number of files from 1 to 3
- Changing the project name from "todo-app" to "weather-app"

If two variants at the same difficulty differ only by project name or file name,
they are parameter substitutions — not distinct variants. The expected reasoning
path and the Git command applied must differ.

---

## 3. Every Variant Must Have a Distinct Expected Repository State

A variant is only valid when its `target_state` differs from all other variants in
the same scenario × difficulty pool.

Distinct state means one or more of:
- Different files staged/committed
- Different commit message
- Different file content in HEAD
- Different repository structure (branches, tracked files)
- Different combination of `git add` + `git commit` targets

Story text alone does not make a valid variant.

---

## 4. Environment Variety Requirement

Across variants in any lesson, the following environments must not repeat more than once
unless the lesson explicitly focuses on a single environment:

| Environment Tag | Description |
|----------------|-------------|
| `student-capstone` | Group capstone / thesis project |
| `startup` | Small startup codebase |
| `corporate` | Enterprise / ticketing-system context |
| `open-source` | Public contributor / OSS fork context |
| `freelance` | Solo dev, client project |
| `qa-testing` | QA / test engineer context |
| `devops` | Infrastructure / CI pipeline context |
| `docs-project` | Documentation / content repo |

Easy, Medium, and Hard variants for the same lesson should cover different environments
where possible. Never use the same environment for all three difficulties of one lesson.

---

## 5. Scenario Pool Sizing

For every lesson × difficulty combination:

```
pool_size ≥ completion_requirement + 2
```

Default completion requirements (from `SESSION_COUNTS`):
- Easy: 3 required → pool must have ≥ 5 variants
- Medium: 2 required → pool must have ≥ 4 variants
- Hard: 2 required → pool must have ≥ 4 variants

Exception: Module 1 UI Lesson 1 (SO 1.1 — Initializing Repositories) Easy has `required_attempts=1` override → pool ≥ 3 variants.

---

## 6. Solution Commands Must Be Genuine and Minimal

`solution_commands` must represent an actual valid solution path — not a maximally
verbose path and not an artificially constrained one.

- Do not include redundant diagnostic commands in the solution path.
- Do not include commands that aren't needed to reach the target state.
- The solution must pass the State-Based Evaluator.
- Multiple valid solution paths are acceptable; document the canonical one.

---

## 7. Case IDs Must Generate Unique Slugs

The `_variant_slug()` builder in `scenarios/builders.py` truncates case IDs to 18 chars
as a suffix. All case IDs for the same scenario × difficulty must produce distinct
18-char slug suffixes after `slugify()`.

Naming rule: use short, distinct prefixes rather than long shared prefixes.

Bad:  `branch-checkout-easy-login`, `branch-checkout-easy-signup`, `branch-checkout-easy-portal`
      → all truncate to `branch-checkout-ea` → collision

Good: `bc-easy-portal`, `bc-easy-api`, `bc-easy-hotfix`
      → distinct 18-char tails: `bc-easy-portal`, `bc-easy-api`, `bc-easy-hotfi`

For new seeds: keep case IDs under 30 characters total and ensure the first 18 characters
after slugification are unique within the scenario × difficulty pool.

---

## 8. Non-Counted Commands

Diagnostic commands must appear in `CommandCountPolicy.non_counted_patterns`.
Students should always be able to run diagnostics without penalty.

Standard non-counted set for Module 1 (applies to all lessons):
`git status`, `git log`, `git log --oneline`, `git diff`, `git diff --staged`,
`git diff HEAD`, `git diff --name-only`, `git remote -v`, `git check-ignore -v`,
`git ls-files`, `git reflog`, `git branch`, `git show`

---

## 9. Pedagogical Integrity of Commit Messages

When a scenario involves committing, the required commit message must:
- Use imperative mood ("Add", "Fix", "Update", "Remove", "Create")
- Describe what the commit does, not what the developer did
- Be ≤ 72 characters
- Match the scenario context (a login feature commit should say something about login)

The platform's message-quality validator enforces these rules.
Design scenarios so the required message is obvious from context — students should
not have to guess the "right" message wording.

When message wording matters (e.g., an amend scenario), the student_context must
explicitly state what the message should say.

---

## 10. `git add .` Is a Valid Counted Action

`git add .` stages all changes in the current directory. It is introduced in Lesson 1.3
and is a legitimate solution path wherever staging all modified/untracked files is correct.

Do not design scenarios where `git add .` accidentally reaches the target state
when a more selective staging is required. If the task requires partial staging,
the initial state must contain files that must NOT be staged.


