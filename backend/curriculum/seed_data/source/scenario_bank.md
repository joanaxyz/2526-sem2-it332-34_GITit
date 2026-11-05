# GIT it! — Scenario Bank

### 1.1.1 Initialize the current folder · Easy

**Variant ID:** `init-easy-current-empty`

**Story**

Your team has finally started its first project together. Raven, your group leader, has created the project folder, assigned the work, and confidently announced that everyone should “*stay organized.*”

Ten minutes later, someone asks whether they should make a backup before editing, and another teammate suggests copying the folder every afternoon. Raven pauses. “*Let’s avoid creating a museum of backup folders.*”

Nothing has been recorded yet, and the current folder has no version control. Before anyone starts changing files, the team needs a way to keep track of its work. You have been given the setup job; the first actual snapshot will come later.

**Starting point:** You are in an empty project folder. It is not a repository yet.

**Real-World Context**

Teams often begin with an ordinary folder. Initializing it gives Git a place to record future snapshots, while the files remain unstaged until someone deliberately adds them.

**Your Task**

Initialize the current directory as a Git repository, explicitly choosing `main` as its initial branch during initialization.

**Do not stage files or create a commit.**

**Objective Checklist**

- [ ] Initialize the current folder as a Git repository.
- [ ] Set main as the initial branch during initialization.
- [ ] Nothing is staged and no commit exists.

**Answer Key**

1. `git init -b main`

**Accepted Alternatives**

- Pattern: `git init -b main`. Equivalent syntax: `git init --initial-branch=main` or `git init --initial-branch main`. Option order does not matter; the current folder may be written explicitly as `.`. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing another folder, staging or committing files.
- Explicit initial-branch selection is required when creating this repository. Not accepted: `git init` alone, initializing on another branch and renaming it to main, or reinitializing an existing repository with an initial-branch option.
- Common patterns that apply: P19.

**Not accepted**

- Plain `git init` creates a valid repository but does not demonstrate choosing its initial branch. Start a fresh attempt and explicitly choose main during initialization.

**Expected Result**

The current folder is now a repository on `main`. It has no commits and nothing is staged.

**Evaluation**

- Repository at `.`; HEAD on `main`; 0 commits; nothing staged; backend-verified repository creation explicitly selected main as the initial branch.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.1.2 Initialize with trunk as the first branch · Easy

**Variant ID:** `init-easy-trunk-branch`

**Story**

It’s your first morning at a software company, and Sage is helping you prepare your workspace. The onboarding guide looks straightforward until you notice that the team calls its main development line `trunk`.

You ask whether that is a typo. “Nope. Someone picked the tree metaphor years ago, and now we’re committed,” Sage says, pointing to the same name in the build instructions and team handbook.

Your current project folder is still outside version control. Before development begins, its setup needs to match the team’s naming convention. Sage promises the rest of onboarding involves fewer trees, although you haven’t reached the branching discussion yet.

**Starting point:** You are in an empty project folder. It is not a repository yet.

**Real-World Context**

Branch names appear in build scripts, review instructions, and teammate habits. Starting this repository on `trunk` avoids a naming mismatch before work begins.

**Your Task**

Initialize the current directory as a Git repository with `trunk` as its initial branch.

**Objective Checklist**

- [ ] Initialize the current folder as a Git repository.
- [ ] Set trunk as the initial branch.

**Answer Key**

1. `git init --initial-branch=trunk`

**Accepted Alternatives**

- Pattern: `git init -b trunk`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Two commands: `git init`, then a branch rename inside the new repository (`git branch -m trunk`, `git branch -M trunk`, `git branch --move trunk`, `git switch -c trunk`, `git checkout -b trunk`); accepted, not CAR-accurate. The simulator must support renaming a branch that has no commits.
- Common patterns that apply: P19.

**Expected Result**

The current folder is now a repository on `trunk`.

**Evaluation**

- Repository at `.`; HEAD on `trunk`; 0 commits.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.1.3 Initialize invoice-tracker · Easy

**Variant ID:** `init-easy-invoice`

**Story**

Your first freelance client wants a simple invoice tracker: customer names, amounts, and payment status.

Then the follow-up messages arrive. *Could it also handle overdue invoices? Discounts? A printable receipt with a slightly bigger logo?* Raven, your group leader, reads the conversation and smiles. “Congratulations. Your simple project has discovered its personality.”

You haven’t written any code yet, and there is no project repository. Before those requests start turning into files, you need a dedicated workspace called `invoice-tracker` with version control ready. The client can keep thinking about the logo while you give the project a more dependable beginning.

**Starting point:** You are in your workspace. There is no `invoice-tracker` folder yet.

**Real-World Context**

A client project can grow beyond its first brief. Giving `invoice-tracker` its own repository prepares a change history the developer can use as new requests arrive.

**Your Task**

Create a new `invoice-tracker` folder that is a Git repository, with `main` as its first branch.

**Objective Checklist**

- [ ] Initialize invoice-tracker as a Git repository.
- [ ] Set main as the initial branch.

**Answer Key**

1. `git init -b main invoice-tracker`

**Accepted Alternatives**

- Pattern: `git init -b main invoice-tracker`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init invoice-tracker` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Common patterns that apply: P19.

**Not accepted**

- `mkdir invoice-tracker` then `git init -b main invoice-tracker`, or `mkdir invoice-tracker`, `cd invoice-tracker`, `git init -b main` are accepted (`mkdir` counts). `git -C invoice-tracker init` on its own is NOT valid because the folder does not exist yet.

**Expected Result**

`invoice-tracker` exists and is a repository on `main`.

**Evaluation**

- Repository at `invoice-tracker`; HEAD on `main`; 0 commits.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.1.4 Initialize oss-contrib · Medium

**Variant ID:** `init-med-oss`

**Story**

You have found an open-source project you’d love to contribute to, but opening its issue tracker feels like walking into a conversation that started three years ago.

Finn, your teammate, suggests a smaller first step: prepare a local practice workspace where you can organize your contribution notes and try ideas before touching the real project. “*You don’t have to fix the entire internet this afternoon,*” he says.

The workspace should be called `oss-contrib`, and it needs its own version control. There is no existing repository there yet. For now, your assignment is simply to give your preparation work a proper home.

**Starting point:** You are in your workspace. There is no `oss-contrib` folder yet.

**Real-World Context**

Contribution notes and practice changes are easier to manage in their own workspace. An `oss-contrib` repository lets this preparation evolve without mixing it with unrelated local projects.

**Your Task**

Create a new `oss-contrib` folder that is a Git repository, with `main` as its first branch.

**Objective Checklist**

- [ ] Initialize oss-contrib as a Git repository.
- [ ] Set main as the initial branch.

**Answer Key**

1. `git init -b main oss-contrib`

**Accepted Alternatives**

- Pattern: `git init -b main oss-contrib`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init oss-contrib` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Common patterns that apply: P19.

**Not accepted**

- `mkdir oss-contrib` then `git init -b main oss-contrib`, or `mkdir oss-contrib`, `cd oss-contrib`, `git init -b main` are accepted (`mkdir` counts). `git -C oss-contrib init` on its own is NOT valid because the folder does not exist yet.

**Expected Result**

`oss-contrib` exists and is a repository on `main`.

**Evaluation**

- Repository at `oss-contrib`; HEAD on `main`; 0 commits.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.1.5 Initialize docs-site · Medium

**Variant ID:** `init-medium-docs-site`

**Story**

A new teammate has spent the morning following installation instructions scattered across a chat thread, an old presentation, and a document titled “*Use This One.*” By lunch, the team agrees that its documentation needs a proper home.

Sage volunteers to organize the content, then discovers that three people have different copies of the setup guide. “Wonderful. We already have a research project,” she says.

The team decides to keep its new documentation site in a separate workspace called `docs-site`. Before Sage starts gathering pages, you need to prepare that workspace with version control so future improvements can be tracked together.

**Starting point:** You are in your workspace. There is no `docs-site` folder yet.

**Real-World Context**

Documentation changes need a shared, reviewable history, especially when several teammates hold different copies. A separate `docs-site` repository gives those revisions one home.

**Your Task**

Create a new `docs-site` folder that is a Git repository, with `main` as its first branch.

**Objective Checklist**

- [ ] Initialize docs-site as a Git repository.
- [ ] Set main as the initial branch.

**Answer Key**

1. `git init -b main docs-site`

**Accepted Alternatives**

- Pattern: `git init -b main docs-site`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init docs-site` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Common patterns that apply: P19.

**Not accepted**

- `mkdir docs-site` then `git init -b main docs-site`, or `mkdir docs-site`, `cd docs-site`, `git init -b main` are accepted (`mkdir` counts). `git -C docs-site init` on its own is NOT valid because the folder does not exist yet.

**Expected Result**

`docs-site` exists and is a repository on `main`.

**Evaluation**

- Repository at `docs-site`; HEAD on `main`; 0 commits.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.1.6 Initialize api-playground with trunk · Medium

**Variant ID:** `init-medium-trunk-api-playground`

**Story**

Raven wants somewhere to test API ideas without cluttering the team’s production project. Yesterday’s quick experiment produced six files, two promising approaches, and one endpoint nobody remembers writing.

“*Let’s give the experiments an actual address,*” she says. The team has chosen `api-playground` as the new workspace name. It will be separate from the production code, but it still needs to follow the team’s convention of naming the initial branch `trunk`.

No repository has been prepared there yet. Your job is to get the space ready before the next round of experiments spreads across someone’s desktop again.

**Starting point:** You are in your workspace. There is no `api-playground` folder yet.

**Real-World Context**

Experiments can be isolated from production code while still being tracked. Starting `api-playground` on the team’s `trunk` convention makes even this sandbox follow their usual workflow.

**Your Task**

Create a new `api-playground` folder that is a Git repository, with `trunk` as its first branch.

**Objective Checklist**

- [ ] Initialize api-playground as a Git repository.
- [ ] Set trunk as the initial branch.

**Answer Key**

1. `git init -b trunk api-playground`

**Accepted Alternatives**

- Pattern: `git init -b trunk api-playground`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Two commands: `git init api-playground`, then a branch rename inside the new repository (`git branch -m trunk`, `git branch -M trunk`, `git branch --move trunk`, `git switch -c trunk`, `git checkout -b trunk`); accepted, not CAR-accurate. The simulator must support renaming a branch that has no commits.
- Common patterns that apply: P19.

**Not accepted**

- `mkdir api-playground` then `git init -b trunk api-playground`, or `mkdir api-playground`, `cd api-playground`, `git init -b trunk` are accepted (`mkdir` counts). `git -C api-playground init` on its own is NOT valid because the folder does not exist yet.

**Expected Result**

`api-playground` exists and is a repository on `trunk`.

**Evaluation**

- Repository at `api-playground`; HEAD on `trunk`; 0 commits.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.1.7 Initialize field-notes with existing files · Medium

**Variant ID:** `init-medium-existing-files`

**Story**

A field researcher has kept weeks of observations in a folder called `field-notes`: a `notes.txt` file and a `data.csv` file.

Sage looks at the folder, then at the file dates, and asks the question nobody wants to hear: “*What happens if one of these gets overwritten?*” Nothing has ever tracked these files, and neither has been touched today.

Sage wants the folder under version control before the next field trip, but **without changing a single file inside it**. No renamed files, no first commit yet. The files simply need a history to start from.

**Starting point:** You are in your workspace. The folder `field-notes` already contains `notes.txt` and `data.csv`. It is not a repository yet.

**Real-World Context**

Many projects begin as an ordinary folder. Starting a repository in an existing folder leaves its files exactly as they are and lets future changes be recorded.

**Your Task**

Make the existing `field-notes` folder a Git repository with `main` as its first branch.

**Do not stage or commit its files.**

**Objective Checklist**

- [ ] Initialize field-notes as a Git repository.
- [ ] Set main as the initial branch.
- [ ] notes.txt and data.csv are unchanged and not staged.

**Answer Key**

1. `git init -b main field-notes`

**Accepted Alternatives**

- Pattern: `git init -b main field-notes`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init field-notes` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Because `field-notes` already exists, `git -C field-notes init -b main` and `cd field-notes` then `git init -b main` are accepted too. `cd`, `ls`, `pwd` are free; `mkdir` is counted.
- Common patterns that apply: P19.

**Expected Result**

`field-notes` is a repository on `main`. It has no commits, and its two files are untouched and not staged.

**Evaluation**

- Repository at `field-notes`; HEAD on `main`; 0 commits; nothing staged; `notes.txt` and `data.csv` unchanged.
- NOT accepted: `git init` run from the parent folder (wrong folder).
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.1.8 Initialize ci-configs · Hard

**Variant ID:** `init-hard-ci`

**Story**

The operations team has asked you to prepare `ci-configs`, a dedicated repository for pipeline configuration. Finn has already left a build file at `pipelines/build.yml` in the surrounding workspace, alongside material from other tasks.

His handover message is impressively brief: **“Please get the repository ready before the deployment meeting.”**

You look at the clock, then at the collection of folders. There is enough time to do this carefully, but not enough to untangle an oversized repository afterward. The requested project needs **its own boundary**, and the existing workspace files need to remain where they are while you prepare it.

**Starting point:** You are in a workspace that contains `pipelines/build.yml` and folders from other tasks. The folder `ci-configs` does not exist yet.

**Real-World Context**

Pipeline configuration deserves a **clear repository boundary**. Initializing `ci-configs` alone avoids treating the surrounding deployment workspace as part of its history.

**Your Task**

Create a repository in a new `ci-configs` folder, with `main` as its first branch.

**Leave every other file in the workspace where it is.**

**Objective Checklist**

- [ ] Initialize ci-configs as a Git repository.
- [ ] Set main as the initial branch.
- [ ] The rest of the workspace (including pipelines/build.yml) is not part of the repository and is unchanged.

**Answer Key**

1. `git init -b main ci-configs`

**Accepted Alternatives**

- Pattern: `git init -b main ci-configs`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init ci-configs` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Common patterns that apply: P19.

**Not accepted**

- `mkdir ci-configs` then `git init -b main ci-configs`, or `mkdir ci-configs`, `cd ci-configs`, `git init -b main` are accepted (`mkdir` counts). `git -C ci-configs init` on its own is NOT valid because the folder does not exist yet.

**Expected Result**

Only `ci-configs` is a repository, on `main`. **Every other file is unchanged.**

**Evaluation**

- Repository at `ci-configs`; HEAD on `main`; 0 commits; the workspace root is NOT a repository; `pipelines/build.yml` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.1.9 Initialize research-log subfolder only · Hard

**Variant ID:** `init-hard-research-log`

**Story**

Finn’s workspace contains three very different kinds of material: current research in `research-log`, rough ideas in `notes`, and old work in `archive`. Unfortunately, they all sit beneath the same parent folder, making it easy to mistake the whole collection for one project.

“The archive includes an approach we abandoned for excellent reasons,” Finn explains. “*It doesn’t need a comeback.*”

Only `research-log` should receive its own version control, with `main` as the initial branch. **The parent workspace and its neighboring folders must remain outside it.** The existing files should come through the preparation untouched.

**Starting point:** You are in a parent folder that contains `research-log`, `notes` and `archive`. None of them is a repository.

**Real-World Context**

A parent folder can hold several unrelated projects. Initializing only `research-log` keeps `notes` and `archive` outside its repository while preserving the existing files.

**Your Task**

Initialize only the `research-log` subfolder as a Git repository with `main` as its initial branch.

**Leave the parent folder and the sibling folders outside the repository.**

**Objective Checklist**

- [ ] Initialize research-log as a Git repository on main.
- [ ] notes, archive and the parent folder are not repositories.
- [ ] Existing files are unchanged.

**Answer Key**

1. `git init -b main research-log`

**Accepted Alternatives**

- Pattern: `git init -b main research-log`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Bare `git init research-log` is accepted when the simulator's default first branch is `main` (the end state is identical). A hint should tell the learner that real Git may start on another name and that `-b main` removes the doubt.
- Because `research-log` already exists, `git -C research-log init -b main` and `cd research-log` then `git init -b main` are accepted too. `cd`, `ls`, `pwd` are free; `mkdir` is counted.
- Common patterns that apply: P19.

**Expected Result**

Only `research-log` is a repository, on `main`. Everything else is unchanged.

**Evaluation**

- Repository at `research-log`; HEAD on `main`; 0 commits; parent, `notes`, `archive` are NOT repositories; all files unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.1.10 Initialize ui-kit with trunk · Hard

**Variant ID:** `init-hard-ui-kit`

**Story**

The design team is turning its reusable interface styles into a proper project. Inside the parent workspace, `ui-kit` contains the actual kit, `brand-assets` holds the company artwork, and `experiments` contains several ideas that seemed better during the meeting.

Finn opens the last folder, considers a glowing navigation bar, and closes it again. “*Let’s keep that discussion for another day.*”

**Only `ui-kit` should become a repository.** Its initial branch must be named `trunk`. The brand assets, experiments, and existing file contents all need to stay as they are.

**Starting point:** You are in a parent folder that contains `ui-kit`, `brand-assets` and `experiments`. None of them is a repository.

**Real-World Context**

The design kit, brand artwork, and experiments have different owners and lifecycles. Setting up only `ui-kit` with `trunk` gives only the kit its own history and matches the team’s naming rule.

**Your Task**

Initialize only the `ui-kit` subfolder as a Git repository with `trunk` as its initial branch.

**Leave the parent and sibling folders untouched.**

**Objective Checklist**

- [ ] Initialize ui-kit as a Git repository on trunk.
- [ ] brand-assets, experiments and the parent folder are not repositories.
- [ ] Existing files are unchanged.

**Answer Key**

1. `git init --initial-branch=trunk ui-kit`

**Accepted Alternatives**

- Pattern: `git init -b trunk ui-kit`. Option order does not matter; `-b main` = `-bmain` = `--initial-branch=main` = `--initial-branch main`; the folder may be written `dir`, `./dir`, `dir/` or as an absolute path. Not accepted: `git init --bare`, a different branch name or capitalization (`Main`), initializing the parent folder, staging or committing files.
- Two commands: `git init ui-kit`, then a branch rename inside the new repository (`git branch -m trunk`, `git branch -M trunk`, `git branch --move trunk`, `git switch -c trunk`, `git checkout -b trunk`); accepted, not CAR-accurate. The simulator must support renaming a branch that has no commits.
- Because `ui-kit` already exists, `git -C ui-kit init -b trunk` and `cd ui-kit` then `git init -b trunk` are accepted too. `cd`, `ls`, `pwd` are free; `mkdir` is counted.
- Common patterns that apply: P19.

**Expected Result**

Only `ui-kit` is a repository, on `trunk`. Everything else is unchanged.

**Evaluation**

- Repository at `ui-kit`; HEAD on `trunk`; 0 commits; parent, `brand-assets`, `experiments` are NOT repositories; all files unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.1.11 Safely reinitialize the current repository · Hard

**Variant ID:** `init-hard-safe-rerun`

**Story**

Sage is reviewing a maintenance script when you notice that it repeats repository setup inside `release-notes`. The folder is already a repository: it has one commit, `main` is active, and `notes/today.md` contains work that hasn’t been committed yet.

You point this out before running anything. “Good catch,” Sage says. “*A maintenance script should leave us with fewer questions, not a missing afternoon.*”

The setup step still needs to be repeated as part of the check. This time, success means keeping what already exists: **the same recorded history, the same branch position, and every current file edit intact**.

**Starting point:** You are in `release-notes`. It is already a repository with one commit, you are on `main`, and `notes/today.md` has uncommitted edits.

**Real-World Context**

Maintenance scripts sometimes repeat initialization. Running it inside an existing repository should keep the recorded commits, current branch, and uncommitted edits intact.

**Your Task**

Run repository initialization again in the current repository.

**Keep its existing commit, its `main` branch and every uncommitted change.**

**Objective Checklist**

- [ ] The repository is still on main.
- [ ] The existing commit is unchanged (same commit ID and content).
- [ ] The uncommitted edits in notes/today.md are still present in the working folder.

**Answer Key**

1. `git init`

**Accepted Alternatives**

- `git init .`, `git -C . init`, `git init -b main` or `--initial-branch=main` (Git ignores the branch option on an existing repository; the simulator must not move the branch or history).
- `-q` / `--quiet` is accepted, never required.

**Not accepted**

- Not accepted: `git init --bare`, `git init --reinitialize`-style flags that do not exist, or any command that changes history.

**Expected Result**

Nothing was lost. The history, the branch and the edits are exactly as before.

**Evaluation**

- Repository at `.`; HEAD on `main`; same commit ID as at the start; `notes/today.md` still modified and unstaged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.2.1 Clone docs-portal · Easy

**Variant ID:** `clone-easy-docs-portal`

**Story**

The department's documentation portal has outdated pages for every capstone project, and Maeve wants the groups to fix their own sections before the end-of-semester review.

You pull up the shared server address. The portal is there, but you have no local copy to edit — anything you change has to go through a copy on your machine first.

**Starting point:** You are in your workspace, outside any repository. The remote repository is reachable at the address in the task.

**Real-World Context**

A contributor needs the same documentation project and history the team already has. Cloning supplies a local working copy instead of starting an empty folder.

**Your Task**

Clone the remote repository from `https://example.test/training/docs-portal.git`.

**Objective Checklist**

- [ ] Clone docs-portal into a local folder named docs-portal.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone https://example.test/training/docs-portal.git`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`docs-portal` is a copy of `docs-portal`, on `main`, with its full history.

**Evaluation**

- Repository at `docs-portal`; remote `origin` = `https://example.test/training/docs-portal.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.2.2 Clone api-lab into api-workshop · Easy

**Variant ID:** `clone-easy-api-lab`

**Story**

Your internship starts Monday, and the onboarding page says every new intern keeps their repositories in a folder named `api-workshop`, because the team's setup scripts look for it there.

The backend API lives on the company's server. Finn, who interned there last year, says people who skip this step spend their first day fixing paths.

**Starting point:** You are in your workspace, outside any repository. No folder named `api-workshop` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

Onboarding is smoother when a remote project lands in the folder named by the team’s setup instructions. A custom clone destination gives the API a predictable local location.

**Your Task**

Clone the remote repository from `https://example.test/training/api-lab.git` into a local folder named `api-workshop`.

**Objective Checklist**

- [ ] Clone the repository into the api-workshop folder.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone https://example.test/training/api-lab.git api-workshop`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`api-workshop` is a copy of `api-lab`, on `main`, with its full history.

**Evaluation**

- Repository at `api-workshop`; remote `origin` = `https://example.test/training/api-lab.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.2.3 Clone profile-site at the starter branch · Easy

**Variant ID:** `clone-easy-profile-starter`

**Story**

Maeve wants everyone in the capstone group to have a personal profile site by next week. She published a starter template on its own branch so nobody has to begin from a blank page.

You open the repository. The default branch shows the finished example — **not the `starter` branch you should actually be working from**.

**Starting point:** You are in your workspace, outside any repository. The remote repository is reachable at the address in the task.

**Real-World Context**

The `starter` branch contains the template intended for new contributors. Checking it out as part of the clone puts the local workspace on the correct starting line immediately.

**Your Task**

Clone the remote repository from `https://example.test/training/profile-site.git` with `starter` checked out.

**Objective Checklist**

- [ ] Clone profile-site into a local folder named profile-site.
- [ ] starter is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone -b starter https://example.test/training/profile-site.git`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3, P38.

**Expected Result**

`profile-site` is a copy of `profile-site`, on `starter`, with its full history.

**Evaluation**

- Repository at `profile-site`; remote `origin` = `https://example.test/training/profile-site.git`; HEAD on `starter`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.2.4 Clone oss-toolkit via SSH · Easy

**Variant ID:** `clone-easy-oss-ssh`

**Story**

You have put off contributing to an open-source toolkit for months.

Last night you finally added your SSH key to your account. Sage, who has contributed before, says the SSH address is the one to use now that your key is in place, since it skips the password prompts.

**Starting point:** You are in your workspace, outside any repository. The remote repository is reachable at the address in the task.

**Real-World Context**

SSH cloning authenticates using a key pair instead of a password, which means no login prompt on every push or pull. Once a key is registered with the server, the SSH URL is the address to use for all subsequent operations on that project.

**Your Task**

Clone the remote repository from `git@github.com:open-dev/oss-toolkit.git` using SSH.

**Objective Checklist**

- [ ] Clone oss-toolkit into a local folder named oss-toolkit.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone git@github.com:open-dev/oss-toolkit.git`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`oss-toolkit` is a copy of `oss-toolkit`, on `main`, with its full history.

**Evaluation**

- Repository at `oss-toolkit`; remote `origin` = `git@github.com:open-dev/oss-toolkit.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.2.5 Clone audit-logs into audit-logs-local · Easy

**Variant ID:** `clone-easy-corp`

**Story**

The university's IT office has flagged a week of unusual audit log entries and asked your team to investigate. The logs live in a repository on the internal Git server, but you need a local copy to work from.

Raven is firm about the folder name: "`audit-logs-local`. Not `audit-logs`," she says. "The last time someone mixed those up, we spent an hour figuring out which copy was authoritative."

**Starting point:** You are in your workspace, outside any repository. No folder named `audit-logs-local` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

Internal repositories are usually copied into a local workspace before analysis or changes. Naming the destination `audit-logs-local` makes the copy easy to distinguish from other projects.

**Your Task**

Clone the remote repository from `https://git.corp.example/it/audit-logs.git` into a local folder named `audit-logs-local`.

**Objective Checklist**

- [ ] Clone the repository into the audit-logs-local folder.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone https://git.corp.example/it/audit-logs.git audit-logs-local`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`audit-logs-local` is a copy of `audit-logs`, on `main`, with its full history.

**Evaluation**

- Repository at `audit-logs-local`; remote `origin` = `https://git.corp.example/it/audit-logs.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.2.6 Clone backend-api at feature/auth · Medium

**Variant ID:** `clone-med-feature`

**Story**

Your group's backend is mid-sprint and everyone is working on login, which lives on its own branch rather than the default one.

Finn is tired of teammates cloning, forgetting to switch branches, and committing to the wrong place. You want your copy to open on the login work from the first minute.

**Starting point:** You are in your workspace, outside any repository. The remote repository is reachable at the address in the task.

**Real-World Context**

When a team is mid-sprint on a feature branch, cloning with `-b feature/auth` means your working copy is on the right branch from the first command. The alternative — cloning, then manually switching — takes an extra step and leaves room to forget.

**Your Task**

Clone the remote repository from `https://github.com/acme-startup/backend-api.git` with `feature/auth` checked out.

**Objective Checklist**

- [ ] Clone backend-api into a local folder named backend-api.
- [ ] feature/auth is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone -b feature/auth https://github.com/acme-startup/backend-api.git`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3, P38.

**Expected Result**

`backend-api` is a copy of `backend-api`, on `feature/auth`, with its full history.

**Evaluation**

- Repository at `backend-api`; remote `origin` = `https://github.com/acme-startup/backend-api.git`; HEAD on `feature/auth`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.2.7 Clone analytics-lab via SSH into analytics-worktree · Medium

**Variant ID:** `clone-medium-analytics-ssh`

**Story**

Maeve added you to the department's analytics lab repository yesterday. Your SSH key is registered.

There's one catch: you already have three repositories on this laptop with similar names, and mixing them up last month cost you an afternoon. This copy goes in `analytics-worktree` — specific enough that you won't confuse it with anything else.

**Starting point:** You are in your workspace, outside any repository. No folder named `analytics-worktree` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

The analytics team uses an SSH remote and a conventional local worktree name. A clone can honor both the access method and the folder layout used in their instructions.

**Your Task**

Clone the remote repository from `git@example.test:training/analytics-lab.git` into a local folder named `analytics-worktree` using SSH.

**Objective Checklist**

- [ ] Clone the repository into the analytics-worktree folder.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone git@example.test:training/analytics-lab.git analytics-worktree`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`analytics-worktree` is a copy of `analytics-lab`, on `main`, with its full history.

**Evaluation**

- Repository at `analytics-worktree`; remote `origin` = `git@example.test:training/analytics-lab.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.2.8 Clone cli-tool at starter into cli-starter-lab · Medium

**Variant ID:** `clone-medium-cli-starter-folder`

**Story**

A contributor workshop starts today.

The facilitators prepared a starter branch of their command-line tool so beginners don't have to understand the whole project first. Raven has asked you to set up a workshop copy in `cli-starter-lab` that opens on that branch straight away.

**Starting point:** You are in your workspace, outside any repository. No folder named `cli-starter-lab` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

An onboarding branch and a dedicated practice folder serve different purposes. Choosing both during cloning creates a workspace ready for the CLI exercises.

**Your Task**

Clone the remote repository from `https://example.test/tools/cli-tool.git` into a local folder named `cli-starter-lab` with `starter` checked out.

**Objective Checklist**

- [ ] Clone the repository into the cli-starter-lab folder.
- [ ] starter is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone --branch starter https://example.test/tools/cli-tool.git cli-starter-lab`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3, P38.

**Expected Result**

`cli-starter-lab` is a copy of `cli-tool`, on `starter`, with its full history.

**Evaluation**

- Repository at `cli-starter-lab`; remote `origin` = `https://example.test/tools/cli-tool.git`; HEAD on `starter`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.2.9 Shallow clone css-kit · Medium

**Variant ID:** `clone-medium-css-kit-shallow`

**Story**

Your group's build server needs the CSS kit only to compile one stylesheet, and it has very little disk space.

Sage points out that the kit carries years of history the build will never read. All you need is its current state, and quickly.

**Starting point:** You are in your workspace, outside any repository. The remote repository is reachable at the address in the task.

**Real-World Context**

A one-time build usually needs current files rather than the entire history. A depth-one clone reduces the history copied, though older local commits will not be available.

**Your Task**

Clone the remote repository from `https://example.test/frontend/css-kit.git` using a history depth of 1.

**Objective Checklist**

- [ ] Clone css-kit into a local folder named css-kit.
- [ ] The default branch (main) is checked out.
- [ ] The copy is shallow: only the latest commit is downloaded (history depth of 1).
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone --depth 1 https://example.test/frontend/css-kit.git`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`css-kit` is a copy of `css-kit`, on `main`, with its history limited to one commit.

**Evaluation**

- Repository at `css-kit`; remote `origin` = `https://example.test/frontend/css-kit.git`; HEAD on `main`; shallow depth 1; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 1.2.10 Shallow SSH clone of oss-toolkit into oss-review · Hard

**Variant ID:** `clone-hard-ssh-shallow`

**Story**

You are reviewing a single contribution to the open-source toolkit, and your laptop's storage is nearly full. Your SSH key is set up.

All you need is the latest snapshot, in a folder called `oss-review` so it stays apart from the copy you made last week. Raven reminds you that anything extra you download will have to be deleted later.

**Starting point:** You are in your workspace, outside any repository. No folder named `oss-review` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

Combining SSH with `--depth 1` creates a minimal, authenticated copy of a repository: SSH handles the access credentials, while shallow depth limits how many commits are transferred. The tradeoff is that operations requiring older history — like inspecting early commits or comparing to a distant ancestor — will fail until the missing history is fetched.

**Your Task**

Clone the remote repository from `git@github.com:open-dev/oss-toolkit.git` into a local folder named `oss-review` over SSH with a history depth of 1.

**Objective Checklist**

- [ ] Clone the repository into the oss-review folder.
- [ ] The default branch (main) is checked out.
- [ ] The copy is shallow: only the latest commit is downloaded (history depth of 1).
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone --depth 1 git@github.com:open-dev/oss-toolkit.git oss-review`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Expected Result**

`oss-review` is a copy of `oss-toolkit`, on `main`, with its history limited to one commit.

**Evaluation**

- Repository at `oss-review`; remote `origin` = `git@github.com:open-dev/oss-toolkit.git`; HEAD on `main`; shallow depth 1; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.2.11 Shallow clone mobile-ui at starter into mobile-ui-lab · Hard

**Variant ID:** `clone-hard-mobile-ui-shallow-branch`

**Story**

Finn needs to see the current state of the mobile UI starter branch before tonight's group meeting. The presentation is in three hours, and he doesn't have time to wait for the team's connection to transfer the full history.

"Just get the latest snapshot," he says. "Put it in `mobile-ui-lab` so it doesn't overwrite the full copy."

**Starting point:** You are in your workspace, outside any repository. No folder named `mobile-ui-lab` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

Combining `--depth 1` with `-b` at clone time gets you a lightweight snapshot of a specific branch in a single command. The resulting copy is small and fast to set up, though operations that need older commits — like inspecting early history or comparing to an ancestor — won't work until more history is fetched.

**Your Task**

Clone the remote repository from `https://example.test/frontend/mobile-ui.git` into a local folder named `mobile-ui-lab` with `starter` checked out using a history depth of 1.

**Objective Checklist**

- [ ] Clone the repository into the mobile-ui-lab folder.
- [ ] starter is checked out.
- [ ] The copy is shallow: only the latest commit is downloaded (history depth of 1).
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone --depth 1 -b starter https://example.test/frontend/mobile-ui.git mobile-ui-lab`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Not accepted**

- Two-step routes are NOT accepted for a shallow copy of a non-default branch: a depth-1 clone only downloads the default branch, so the branch option must be given at clone time.

**Expected Result**

`mobile-ui-lab` is a copy of `mobile-ui`, on `starter`, with its history limited to one commit.

**Evaluation**

- Repository at `mobile-ui-lab`; remote `origin` = `https://example.test/frontend/mobile-ui.git`; HEAD on `starter`; shallow depth 1; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.2.12 Shallow clone lab-notebook at review into notebook-review · Hard

**Variant ID:** `clone-hard-lab-notebook-depth-branch`

**Story**

Maeve is running the lab notebook entries through a final review before they go public next week. She's flagged the ones on the `review` branch as ready to check, but the full repository is large and she needs an answer today.

"Shallow copy is fine," she says. "Just don't put it in the same folder as your notebook — that confusion cost us an hour last time."

**Starting point:** You are in your workspace, outside any repository. No folder named `notebook-review` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

A shallow branch clone gives you just enough to review the latest state of a specific line of work, without the storage cost of unrelated commits or branches. For large repositories with long histories, this can be the difference between a fast setup and a slow one.

**Your Task**

Clone the remote repository from `https://example.test/docs/lab-notebook.git` into a local folder named `notebook-review` with `review` checked out using a history depth of 1.

**Objective Checklist**

- [ ] Clone the repository into the notebook-review folder.
- [ ] review is checked out.
- [ ] The copy is shallow: only the latest commit is downloaded (history depth of 1).
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone --depth 1 --branch review https://example.test/docs/lab-notebook.git notebook-review`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Not accepted**

- Two-step routes are NOT accepted for a shallow copy of a non-default branch: a depth-1 clone only downloads the default branch, so the branch option must be given at clone time.

**Expected Result**

`notebook-review` is a copy of `lab-notebook`, on `review`, with its history limited to one commit.

**Evaluation**

- Repository at `notebook-review`; remote `origin` = `https://example.test/docs/lab-notebook.git`; HEAD on `review`; shallow depth 1; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.2.13 Clone research-log via SSH into research-log-lab · Hard

**Variant ID:** `clone-hard-research-log-ssh`

**Story**

Your thesis analysis will run on a laptop that won't have Wi-Fi at the field site.

**You need the whole research log, history included, available offline**, because you'll be tracing when each entry changed. Your SSH key is already set up. The copy belongs in `research-log-lab`, separate from the shared one.

**Starting point:** You are in your workspace, outside any repository. No folder named `research-log-lab` exists yet. The remote repository is reachable at the address in the task.

**Real-World Context**

When a repository needs to work fully without a network connection, a complete clone is the right choice — commands like `git log`, `git blame`, and ancestor comparisons rely on having the full commit history available locally. SSH cloning ensures the initial transfer is authenticated; once cloned, the repository works identically regardless of which protocol was used.

**Your Task**

Clone the remote repository from `git@example.test:docs/research-log.git` into a local folder named `research-log-lab` using SSH.

**Objective Checklist**

- [ ] Clone the repository into the research-log-lab folder.
- [ ] The default branch (main) is checked out.
- [ ] origin points to the URL given in the task.
- [ ] The cloned repository is clean, with no staged or unstaged changes.

**Answer Key**

1. `git clone git@example.test:docs/research-log.git research-log-lab`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P3.

**Not accepted**

- Do NOT add `--depth`: the story needs the complete history.

**Expected Result**

`research-log-lab` is a copy of `research-log`, on `main`, with its full history.

**Evaluation**

- Repository at `research-log-lab`; remote `origin` = `git@example.test:docs/research-log.git`; HEAD on `main`; full history; clean working tree.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.3.1 Initial commit for library-system · Easy

**Variant ID:** `commit-easy-initial`

**Story**

Your capstone group has finally settled on a topic: a library system for the department. Until now the plan has lived in a group chat and the code on three laptops.

Raven, the group leader, wants everyone starting from the same place before more gets written. You have `README.md`, `main.py` and `requirements.txt` ready, and the repository you just created has no history yet.

**Starting point:** You are on `main`; the repository has no commits; working files include `README.md`, `main.py`, `requirements.txt`.

**Real-World Context**

The first commit establishes a baseline for `library-system`. Recording the README, program, and dependencies together makes later changes easier to compare with the project’s starting point.

**Your Task**

Stage `README.md`, `main.py`, `requirements.txt` and create a commit with the message `Initial commit`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Initial commit" on main.
- [ ] Include README.md, main.py, requirements.txt in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add README.md main.py requirements.txt`
2. `git commit -m "Initial commit"`

**Accepted Alternatives**

- `git commit --message "Initial commit"`, `git commit --message="Initial commit"`, `git commit -m"Initial commit"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`README.md`, `main.py`, `requirements.txt` are saved in one commit named “`Initial commit`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Initial commit` and contains exactly: README.md, main.py, requirements.txt.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.3.2 Commit the auth module directory · Easy

**Variant ID:** `commit-easy-auth-dir`

**Story**

Login and logout now work on your laptop, and both files sit in a new `src/auth/` folder. Finn is waiting to build the borrowing screens on top of them. "I'd rather pull one clean change than ask you which files to copy," he says.

Nothing about auth is in the project history yet.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/auth/login.py`, `src/auth/logout.py`.

**Real-World Context**

Login and logout belong to the same new auth module. A single commit for the directory makes the feature’s initial shape clear to reviewers.

**Your Task**

Stage `src/auth/` and create a commit with the message `Add auth module`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Add auth module" on main.
- [ ] Include src/auth/ in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add src/auth/`
2. `git commit -m "Add auth module"`

**Accepted Alternatives**

- `git commit --message "Add auth module"`, `git commit --message="Add auth module"`, `git commit -m"Add auth module"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`src/auth/` is saved in one commit named “`Add auth module`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Add auth module` and contains exactly: src/auth/.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.3.3 Commit form validation update · Easy

**Variant ID:** `commit-easy-form-validation`

**Story**

The borrower form used to accept an empty name and a return date in the past. After an evening of fixes, `src/form.js` finally rejects both. Sage wants to try it, but the fix exists only in your working folder.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/form.js`.

**Real-World Context**

Once the form validation update works, a commit records that completed change. Teammates can then review or revert the validation behavior as one unit.

**Your Task**

Stage `src/form.js` and create a commit with the message `Update form validation`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Update form validation" on main.
- [ ] Include src/form.js in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add src/form.js`
2. `git commit -m "Update form validation"`

**Accepted Alternatives**

- `git commit --message "Update form validation"`, `git commit --message="Update form validation"`, `git commit -m"Update form validation"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`src/form.js` is saved in one commit named “`Update form validation`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Update form validation` and contains exactly: src/form.js.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.3.4 Commit README clarification · Easy

**Variant ID:** `commit-easy-readme-setup`

**Story**

Maeve tried to run your project from the README and got stuck on step two.

You rewrote the setup instructions so the next reader can follow them. The new `README.md` is saved, but nobody else can see it until it becomes part of the project history.

**Starting point:** You are on `main`; local branches include `main`; working files include `README.md`.

**Real-World Context**

Setup instructions affect every new contributor. A clear documentation commit makes the revised steps easy to find in project history.

**Your Task**

Stage `README.md` and create a commit with the message `Clarify setup steps`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Clarify setup steps" on main.
- [ ] Include README.md in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add README.md`
2. `git commit -m "Clarify setup steps"`

**Accepted Alternatives**

- `git commit --message "Clarify setup steps"`, `git commit --message="Clarify setup steps"`, `git commit -m"Clarify setup steps"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`README.md` is saved in one commit named “`Clarify setup steps`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Clarify setup steps` and contains exactly: README.md.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.3.5 Commit navbar spacing fix · Easy

**Variant ID:** `commit-easy-navbar-spacing`

**Story**

On Finn's wide monitor the navbar links sat in a tidy row. On yours they crowded the logo.

You adjusted the spacing in `styles/navbar.css`, and it now looks right on both screens. That one file is the only change since the last saved version.

**Starting point:** You are on `main`; local branches include `main`; working files include `styles/navbar.css`.

**Real-World Context**

A small visual correction deserves a clear checkpoint. Recording the navbar CSS change separately helps reviewers see exactly what fixed the alignment.

**Your Task**

Stage `styles/navbar.css` and create a commit with the message `Adjust navbar spacing`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Adjust navbar spacing" on main.
- [ ] Include styles/navbar.css in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add styles/navbar.css`
2. `git commit -m "Adjust navbar spacing"`

**Accepted Alternatives**

- `git commit --message "Adjust navbar spacing"`, `git commit --message="Adjust navbar spacing"`, `git commit -m"Adjust navbar spacing"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`styles/navbar.css` is saved in one commit named “`Adjust navbar spacing`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Adjust navbar spacing` and contains exactly: styles/navbar.css.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.3.6 Commit Docker configuration · Medium

**Variant ID:** `commit-med-docker`

**Story**

Half the group can't run the project because their setups differ. Raven asks you to package it so every laptop behaves the same.

You wrote a `Dockerfile` and a matching `.env.example` listing the settings each teammate must fill in. One without the other leaves a teammate with a setup that half works.

**Starting point:** You are on `main`; local branches include `main`; working files include `Dockerfile`, `.env.example`.

**Real-World Context**

Container setup depends on both the build instructions and example environment settings. Saving them together keeps the configuration change coherent.

**Your Task**

Stage `Dockerfile`, `.env.example` and create a commit with the message `Add Docker configuration`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Add Docker configuration" on main.
- [ ] Include Dockerfile, .env.example in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add Dockerfile .env.example`
2. `git commit -m "Add Docker configuration"`

**Accepted Alternatives**

- `git commit --message "Add Docker configuration"`, `git commit --message="Add Docker configuration"`, `git commit -m"Add Docker configuration"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`Dockerfile`, `.env.example` are saved in one commit named “`Add Docker configuration`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Add Docker configuration` and contains exactly: Dockerfile, .env.example.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.3.7 Commit profile card layout · Medium

**Variant ID:** `commit-medium-profile-card`

**Story**

You redesigned the borrower profile card.

The new layout needs both the JavaScript that builds the card and the stylesheet that arranges it, and either one alone would render a broken card. Finn will review the redesign as a single piece of work tomorrow morning.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/profile-card.js`, `styles/profile-card.css`.

**Real-World Context**

The profile card’s behavior and styling change together. A commit containing both files presents one complete layout update for review.

**Your Task**

Stage `src/profile-card.js`, `styles/profile-card.css` and create a commit with the message `Update profile card layout`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Update profile card layout" on main.
- [ ] Include src/profile-card.js, styles/profile-card.css in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add src/profile-card.js styles/profile-card.css`
2. `git commit -m "Update profile card layout"`

**Accepted Alternatives**

- `git commit --message "Update profile card layout"`, `git commit --message="Update profile card layout"`, `git commit -m"Update profile card layout"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`src/profile-card.js`, `styles/profile-card.css` are saved in one commit named “`Update profile card layout`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Update profile card layout` and contains exactly: src/profile-card.js, styles/profile-card.css.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.3.8 Commit search results view · Medium

**Variant ID:** `commit-medium-search-results`

**Story**

Catalog search used to return a plain list of titles.

Your version shows author and availability, which meant changing the handler in `src/search.js` and the layout in `templates/search.html`. Sage is testing the borrowing flow tomorrow and needs search to work as a whole, not half rewritten.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/search.js`, `templates/search.html`.

**Real-World Context**

A search view can involve both the handler and the page template. Committing the pair together captures the behavior the user actually sees.

**Your Task**

Stage `src/search.js`, `templates/search.html` and create a commit with the message `Refine search results view`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Refine search results view" on main.
- [ ] Include src/search.js, templates/search.html in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add src/search.js templates/search.html`
2. `git commit -m "Refine search results view"`

**Accepted Alternatives**

- `git commit --message "Refine search results view"`, `git commit --message="Refine search results view"`, `git commit -m"Refine search results view"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`src/search.js`, `templates/search.html` are saved in one commit named “`Refine search results view`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Refine search results view` and contains exactly: src/search.js, templates/search.html.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.3.9 Commit export flow update · Medium

**Variant ID:** `commit-medium-export-flow`

**Story**

Maeve asked how a librarian would export the borrowing report, and you realized the real answer had changed since anyone wrote it down.

You updated `src/export.py` and rewrote `docs/export.md` to match. Code and documentation that disagree are worse than no documentation.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/export.py`, `docs/export.md`.

**Real-World Context**

When export behavior changes, its instructions should match. Saving the code and documentation together avoids a history point where they disagree.

**Your Task**

Stage `src/export.py`, `docs/export.md` and create a commit with the message `Document export flow update`. Finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Document export flow update" on main.
- [ ] Include src/export.py, docs/export.md in that commit.
- [ ] Nothing else was committed.
- [ ] Finish on main.

**Answer Key**

1. `git add src/export.py docs/export.md`
2. `git commit -m "Document export flow update"`

**Accepted Alternatives**

- `git commit --message "Document export flow update"`, `git commit --message="Document export flow update"`, `git commit -m"Document export flow update"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P20.

**Expected Result**

`src/export.py`, `docs/export.md` are saved in one commit named “`Document export flow update`” on `main`.

**Evaluation**

- Latest commit on `main` has message `Document export flow update` and contains exactly: src/export.py, docs/export.md.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.3.10 Commit handler fix, leave experimental file out · Hard

**Variant ID:** `commit-hard-selective`

**Story**

A librarian added a book with no title and the whole request crashed. The cause was a missing null check in `api/handler.py`, and you fixed it this afternoon.

You are also halfway through a faster lookup in `api/experimental.py`, which sometimes works and sometimes returns nothing. Raven is demoing to the department tomorrow, and the experiment is not something anyone should show.

**Starting point:** You are on `main`; local branches include `main`; working files include `api/handler.py`, `api/experimental.py`.

**Real-World Context**

A ready handler fix can be reviewed while an experimental file stays local. Choosing only the finished file keeps the commit focused on the null-check bug.

**Your Task**

Stage `api/handler.py` and create a commit with the message `Fix request handler null check`.

**Leave `api/experimental.py` uncommitted**; finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix request handler null check" on main.
- [ ] Include api/handler.py in that commit.
- [ ] api/experimental.py is not committed and still changed in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add api/handler.py`
2. `git commit -m "Fix request handler null check"`

**Accepted Alternatives**

- `git commit --message "Fix request handler null check"`, `git commit --message="Fix request handler null check"`, `git commit -m"Fix request handler null check"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1.

**Not accepted**

- `git add .`, `git add -A`, `git add --all`, `git commit -a` are NOT accepted: they would include the file that must stay uncommitted.

**Expected Result**

`api/handler.py` is saved in one commit named “`Fix request handler null check`” on `main`. `api/experimental.py` remains uncommitted.

**Evaluation**

- Latest commit on `main` has message `Fix request handler null check` and contains exactly: api/handler.py.
- Working tree still shows changes in: api/experimental.py.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.3.11 Commit parser and tests, leave debug/scratch files out · Hard

**Variant ID:** `commit-hard-parser`

**Story**

The catalog importer is finally passing: `src/parser.py` and `tests/test_parser.py` are done.

Debugging it left a `debug.log` full of stack traces and a `scratch.py` where you tried six different ideas. Maeve will open your work as a pull request, and she has said before that she doesn't want to read your debugging leftovers.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/parser.py`, `tests/test_parser.py`, `debug.log`, `scratch.py`.

**Real-World Context**

The parser and its tests form one reviewable feature. Debug logs and scratch code are working aids and should not enter that saved change.

**Your Task**

Stage `src/parser.py`, `tests/test_parser.py` and create a commit with the message `Add parser module with unit tests`.

**Leave `debug.log` and `scratch.py` uncommitted**; finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Add parser module with unit tests" on main.
- [ ] Include src/parser.py, tests/test_parser.py in that commit.
- [ ] debug.log and scratch.py are not committed and still changed in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add src/parser.py tests/test_parser.py`
2. `git commit -m "Add parser module with unit tests"`

**Accepted Alternatives**

- `git commit --message "Add parser module with unit tests"`, `git commit --message="Add parser module with unit tests"`, `git commit -m"Add parser module with unit tests"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1.

**Not accepted**

- `git add .`, `git add -A`, `git add --all`, `git commit -a` are NOT accepted: they would include the file that must stay uncommitted.

**Expected Result**

`src/parser.py`, `tests/test_parser.py` are saved in one commit named “`Add parser module with unit tests`” on `main`. `debug.log` and `scratch.py` remain uncommitted.

**Evaluation**

- Latest commit on `main` has message `Add parser module with unit tests` and contains exactly: src/parser.py, tests/test_parser.py.
- Working tree still shows changes in: debug.log and scratch.py.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.3.12 Commit profile card change, leave notes out · Hard

**Variant ID:** `commit-hard-profile-distractor`

**Story**

You changed how the profile card behaves when a borrower has no photo, and `src/profile-card.js` is ready.

In the same folder, `notes/profile-ideas.md` holds your running thoughts: a few good ideas, a few bad ones, and a reminder to change the logo color. Sage is about to pull the group's latest work.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/profile-card.js`, `notes/profile-ideas.md`.

**Real-World Context**

Implementation work and personal design notes have different audiences. Commit the profile behavior while keeping unfinished ideas in the working folder.

**Your Task**

Stage `src/profile-card.js` and create a commit with the message `Update profile card behavior`.

**Leave `notes/profile-ideas.md` uncommitted**; finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Update profile card behavior" on main.
- [ ] Include src/profile-card.js in that commit.
- [ ] notes/profile-ideas.md is not committed and still changed in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add src/profile-card.js`
2. `git commit -m "Update profile card behavior"`

**Accepted Alternatives**

- `git commit --message "Update profile card behavior"`, `git commit --message="Update profile card behavior"`, `git commit -m"Update profile card behavior"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1.

**Not accepted**

- `git add .`, `git add -A`, `git add --all`, `git commit -a` are NOT accepted: they would include the file that must stay uncommitted.

**Expected Result**

`src/profile-card.js` is saved in one commit named “`Update profile card behavior`” on `main`. `notes/profile-ideas.md` remains uncommitted.

**Evaluation**

- Latest commit on `main` has message `Update profile card behavior` and contains exactly: src/profile-card.js.
- Working tree still shows changes in: notes/profile-ideas.md.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.3.13 Commit export fix, leave scratch output out · Hard

**Variant ID:** `commit-hard-export-distractor`

**Story**

The export rejected valid dates, and you traced it to the validation in `src/export.py`. To check the fix you ran several test exports, and one left `scratch/export-test-output.txt` in your folder.

Maeve grades each member's contribution by reading the commit history, and raw test output is a strange thing to be remembered for.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/export.py`, `scratch/export-test-output.txt`.

**Real-World Context**

Test output helped verify the export fix but is not part of the product change. A selective commit saves the fix without the scratch result.

**Your Task**

Stage `src/export.py` and create a commit with the message `Fix export validation`.

**Leave `scratch/export-test-output.txt` uncommitted**; finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix export validation" on main.
- [ ] Include src/export.py in that commit.
- [ ] scratch/export-test-output.txt is not committed and still changed in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add src/export.py`
2. `git commit -m "Fix export validation"`

**Accepted Alternatives**

- `git commit --message "Fix export validation"`, `git commit --message="Fix export validation"`, `git commit -m"Fix export validation"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1.

**Not accepted**

- `git add .`, `git add -A`, `git add --all`, `git commit -a` are NOT accepted: they would include the file that must stay uncommitted.

**Expected Result**

`src/export.py` is saved in one commit named “`Fix export validation`” on `main`. `scratch/export-test-output.txt` remains uncommitted.

**Evaluation**

- Latest commit on `main` has message `Fix export validation` and contains exactly: src/export.py.
- Working tree still shows changes in: scratch/export-test-output.txt.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.3.14 Commit search ranking display, leave notes out · Hard

**Variant ID:** `commit-hard-search-two-targets-one-distractor`

**Story**

You changed how search results are ranked, which touched both `src/search.js` and `templates/search.html`, and neither works without the other.

While planning the next step you also started `notes/search-ranking.md`, a rough outline that isn't ready for anyone. Raven plans to build the demo version tonight from whatever has been saved.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/search.js`, `templates/search.html`, `notes/search-ranking.md`.

**Real-World Context**

The search handler and template make one visible update; planning notes remain unfinished. Staging the two product files keeps the commit complete and focused.

**Your Task**

Stage `src/search.js`, `templates/search.html` and create a commit with the message `Refine search ranking display`.

**Leave `notes/search-ranking.md` uncommitted**; finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Refine search ranking display" on main.
- [ ] Include src/search.js, templates/search.html in that commit.
- [ ] notes/search-ranking.md is not committed and still changed in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add src/search.js templates/search.html`
2. `git commit -m "Refine search ranking display"`

**Accepted Alternatives**

- `git commit --message "Refine search ranking display"`, `git commit --message="Refine search ranking display"`, `git commit -m"Refine search ranking display"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1.

**Not accepted**

- `git add .`, `git add -A`, `git add --all`, `git commit -a` are NOT accepted: they would include the file that must stay uncommitted.

**Expected Result**

`src/search.js`, `templates/search.html` are saved in one commit named “`Refine search ranking display`” on `main`. `notes/search-ranking.md` remains uncommitted.

**Evaluation**

- Latest commit on `main` has message `Refine search ranking display` and contains exactly: src/search.js, templates/search.html.
- Working tree still shows changes in: notes/search-ranking.md.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.4.1 Stage the billing fix hunk only · Easy

**Variant ID:** `partial-easy-billing`

**Story**

You fixed a rounding error in `src/billing.py`, then added a few print statements further down the same file to see what the numbers looked like.

Maeve is checking the project tonight, and the group needs the rounding fix saved now. The prints were only ever for you.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/billing.py`.

**Real-World Context**

A rounding fix and temporary print statements can live in the same file. Partial staging saves the client-ready fix while the diagnostic experiment stays in the working copy.

**Your Task**

Stage __only__ the billing rounding fix and commit it with the message `Fix billing calculation rounding error`. Leave the diagnostic print statements out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix billing calculation rounding error" on main.
- [ ] It contains only the billing rounding fix.
- [ ] The diagnostic print statements is not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/billing.py`
2. `git commit -m "Fix billing calculation rounding error"`

**Accepted Alternatives**

- `git commit --message "Fix billing calculation rounding error"`, `git commit --message="Fix billing calculation rounding error"`, `git commit -m"Fix billing calculation rounding error"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the billing rounding fix is saved in the commit “`Fix billing calculation rounding error`”. The diagnostic print statements stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix billing calculation rounding error`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.4.2 Stage the routes handler hunk only · Easy

**Variant ID:** `partial-easy-routes`

**Story**

`src/routes.py` holds two pieces of work: the updated route handlers, which are finished, and an experimental auth middleware you commented out after starting it *on a whim*. Finn is waiting on the handlers to connect the frontend.

Both changes sit in the same file, which makes this awkward.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/routes.py`.

**Real-World Context**

Updated route handlers are ready before the experimental middleware. Staging only the handler hunk prevents an unreviewed auth idea from joining the commit.

**Your Task**

Stage __only__ the updated route handlers and commit it with the message `Update API route handlers`. Leave the experimental auth middleware out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Update API route handlers" on main.
- [ ] It contains only the updated route handlers.
- [ ] The experimental auth middleware is not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/routes.py`
2. `git commit -m "Update API route handlers"`

**Accepted Alternatives**

- `git commit --message "Update API route handlers"`, `git commit --message="Update API route handlers"`, `git commit -m"Update API route handlers"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the updated route handlers is saved in the commit “`Update API route handlers`”. The experimental auth middleware stays in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Update API route handlers`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.4.3 Stage the auth validation hunk only · Easy

**Variant ID:** `partial-easy-auth-validation`

**Story**

Halfway through a large cleanup of `src/auth.py`, you spotted a validation bug and fixed it. The cleanup is nowhere near done, but the bug fix can't wait. Raven hit it while testing the sign-in page.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/auth.py`.

**Real-World Context**

A narrow validation fix can be released before a larger auth refactor is finished. Partial staging separates the safe fix from the ongoing work.

**Your Task**

Stage __only__ the auth validation fix and commit it with the message `Fix auth validation`. Leave the unfinished refactor out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix auth validation" on main.
- [ ] It contains only the auth validation fix.
- [ ] The unfinished refactor is not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/auth.py`
2. `git commit -m "Fix auth validation"`

**Accepted Alternatives**

- `git commit --message "Fix auth validation"`, `git commit --message="Fix auth validation"`, `git commit -m"Fix auth validation"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the auth validation fix is saved in the commit “`Fix auth validation`”. The unfinished refactor stays in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix auth validation`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.4.4 Stage the search ranking hunk only · Easy

**Variant ID:** `partial-easy-search-ranking`

**Story**

In `src/search.py` you corrected the ranking so exact title matches come first, and while you were there you started tidying the surrounding code.

Sage is demoing search to Maeve tomorrow and needs the ranking fix. The tidying is unfinished.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/search.py`.

**Real-World Context**

A ranking correction and code cleanup may have different review risks. Committing only the correction keeps its effect easy to assess.

**Your Task**

Stage __only__ the ranking algorithm fix and commit it with the message `Fix search ranking`. Leave the cleanup refactor out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix search ranking" on main.
- [ ] It contains only the ranking algorithm fix.
- [ ] The cleanup refactor is not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/search.py`
2. `git commit -m "Fix search ranking"`

**Accepted Alternatives**

- `git commit --message "Fix search ranking"`, `git commit --message="Fix search ranking"`, `git commit -m"Fix search ranking"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the ranking algorithm fix is saved in the commit “`Fix search ranking`”. The cleanup refactor stays in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix search ranking`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.4.5 Stage the export formatting hunk only · Easy

**Variant ID:** `partial-easy-export-format`

**Story**

Librarians complained that exported dates came out in the wrong format.

You fixed it in `src/export.py` and, to see what was happening, added some temporary logging lines in the same file. Finn wants the format fix in before the weekly build, and nobody wants the logging there.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/export.py`.

**Real-World Context**

The formatting fix can stand on its own while new logging remains experimental. Selecting just that hunk produces a focused export change.

**Your Task**

Stage __only__ the export formatting fix and commit it with the message `Fix export formatting`. Leave the extra logging out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix export formatting" on main.
- [ ] It contains only the export formatting fix.
- [ ] The extra logging is not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/export.py`
2. `git commit -m "Fix export formatting"`

**Accepted Alternatives**

- `git commit --message "Fix export formatting"`, `git commit --message="Fix export formatting"`, `git commit -m"Fix export formatting"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the export formatting fix is saved in the commit “`Fix export formatting`”. The extra logging stays in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix export formatting`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.4.6 Stage only the parser bug fix hunk · Medium

**Variant ID:** `partial-med-three-hunk`

**Story**

`src/parser.py` holds *three separate pieces* of work: a bug that made the importer choke on blank lines, which is fixed; a half-finished rewrite of token handling; and an experimental section you aren't sure about. Maeve will review the bug fix on its own.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/parser.py`.

**Real-World Context**

The parser file holds a finished bug fix, a refactor, and an experiment. Partial staging can save the fix alone while the other two sections stay available locally.

**Your Task**

Stage __only__ the parser bug fix and commit it with the message `Fix parser blank-line bug`. Leave the refactor and experiment out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix parser blank-line bug" on main.
- [ ] It contains only the parser bug fix.
- [ ] The refactor and experiment are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/parser.py`
2. `git commit -m "Fix parser blank-line bug"`

**Accepted Alternatives**

- `git commit --message "Fix parser blank-line bug"`, `git commit --message="Fix parser blank-line bug"`, `git commit -m"Fix parser blank-line bug"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the parser bug fix is saved in the commit “`Fix parser blank-line bug`”. The refactor and experiment stay in the working folder, uncommitted.


**Evaluation**

- Latest commit on `main` = `Fix parser blank-line bug`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.4.7 Stage only the profile validation hunk · Medium

**Variant ID:** `partial-medium-profile-validation`

**Story**

`src/profile.py` has three changes in it: a validation fix, a wording update for the profile page, and a cleanup you haven't finished. Next to it, `notes/profile-todo.md` is still full of your reminders.

Only the validation fix is ready for Sage to review.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/profile.py`, `notes/profile-todo.md`.

**Real-World Context**

The validation change is ready, but copy and cleanup edits are still in progress. A focused patch keeps that unfinished work and the notes file out of the commit.

**Your Task**

Stage __only__ the profile validation fix and commit it with the message `Fix profile validation`. Leave the copy, cleanup, and notes out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix profile validation" on main.
- [ ] It contains only the profile validation fix.
- [ ] The copy, cleanup, and notes are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/profile.py`
2. `git commit -m "Fix profile validation"`

**Accepted Alternatives**

- `git commit --message "Fix profile validation"`, `git commit --message="Fix profile validation"`, `git commit -m"Fix profile validation"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the profile validation fix is saved in the commit “`Fix profile validation`”. The copy, cleanup, and notes stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix profile validation`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.4.8 Stage only the payment rounding hunk · Medium

**Variant ID:** `partial-medium-payment-rounding`

**Story**

Over the afternoon you changed `src/payment.py` three ways: a rounding fix, some added logging, and a comment you reworded. `tmp/payment-scratch.txt` is also in your folder from your test calculations. Raven's rule is one reason per commit, so you're stopping before you save any of it.

Only the rounding fix belongs to the bug report.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/payment.py`, `tmp/payment-scratch.txt`.

**Real-World Context**

A payment rounding bug should be reviewed independently of logging and comments. Selecting its hunk also leaves the scratch file outside the saved change.

**Your Task**

Stage __only__ the payment rounding fix and commit it with the message `Fix payment rounding`. Leave the logging, comment edit, and scratch file out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix payment rounding" on main.
- [ ] It contains only the payment rounding fix.
- [ ] The logging, comment edit, and scratch file are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/payment.py`
2. `git commit -m "Fix payment rounding"`

**Accepted Alternatives**

- `git commit --message "Fix payment rounding"`, `git commit --message="Fix payment rounding"`, `git commit -m"Fix payment rounding"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the payment rounding fix is saved in the commit “`Fix payment rounding`”. The logging, comment edit, and scratch file stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix payment rounding`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.4.9 Stage only the dashboard filter hunk · Medium

**Variant ID:** `partial-medium-dashboard-filter`

**Story**

`src/dashboard.js` has three changes: the filter logic you fixed, a theme update you were trying out, and some `console.log` lines left from debugging. `notes/dashboard-ideas.md` is still in the folder too. Finn needs the filter fix for tomorrow's demo, but the theme and the logging aren't something he should have to review.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/dashboard.js`, `notes/dashboard-ideas.md`.

**Real-World Context**

The filter fix, theme work, and console output share a file but serve different purposes. Partial staging isolates the functional correction for review.

**Your Task**

Stage __only__ the dashboard filter fix and commit it with the message `Fix dashboard filter`. Leave the theme work, console output, and notes out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix dashboard filter" on main.
- [ ] It contains only the dashboard filter fix.
- [ ] The theme work, console output, and notes are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/dashboard.js`
2. `git commit -m "Fix dashboard filter"`

**Accepted Alternatives**

- `git commit --message "Fix dashboard filter"`, `git commit --message="Fix dashboard filter"`, `git commit -m"Fix dashboard filter"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the dashboard filter fix is saved in the commit “`Fix dashboard filter`”. The theme work, console output, and notes stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix dashboard filter`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.4.10 Stage only the network Terraform hunk · Hard

**Variant ID:** `partial-hard-terraform`

**Story**

Your group deploys its project from `terraform/main.tf`.

In one sitting you updated the network configuration and also started trying out some experimental feature flags, so both changes sit in the same file. `terraform/debug.txt` is in the folder too. Raven reviews the network change tomorrow, and she doesn't want to wonder what the flags are for.

**Starting point:** You are on `main`; local branches include `main`; working files include `terraform/main.tf`, `terraform/debug.txt`.

**Real-World Context**

Network configuration and experimental feature flags share a Terraform file. Saving only the network hunk keeps unapproved flags and debug material out of the infrastructure change.

**Your Task**

Stage __only__ the network configuration hunk and commit it with the message `Update network Terraform configuration`. Leave the experimental flags and debug file out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Update network Terraform configuration" on main.
- [ ] It contains only the network configuration hunk.
- [ ] The experimental flags and debug file are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p terraform/main.tf`
2. `git commit -m "Update network Terraform configuration"`

**Accepted Alternatives**

- `git commit --message "Update network Terraform configuration"`, `git commit --message="Update network Terraform configuration"`, `git commit -m"Update network Terraform configuration"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the network configuration hunk is saved in the commit “`Update network Terraform configuration`”. The experimental flags and debug file stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Update network Terraform configuration`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.4.11 Stage validation hunks across auth code and tests · Hard

**Variant ID:** `partial-hard-auth-cross-file`

**Story**

Your validation fix touched two files, `src/auth.py` and `tests/test_auth.py`, and in each one there's also unfinished work: a refactor in the code and a cleanup in the tests. `notes/auth-debug.md` is still around from debugging. Maeve wants one commit that shows the fix and the test that proves it, and nothing else.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/auth.py`, `tests/test_auth.py`, `notes/auth-debug.md`.

**Real-World Context**

A validation fix is meaningful alongside its matching test. Partial staging can take those two hunks across files without sweeping in the refactor, cleanup, or debug notes.

**Your Task**

Stage __only__ the auth validation fix and matching test and commit it with the message `Fix auth validation and add its test`. Leave the refactor, test cleanup, and debug notes out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix auth validation and add its test" on main.
- [ ] It contains only the auth validation fix and matching test.
- [ ] The refactor, test cleanup, and debug notes are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/auth.py`
2. `git add -p tests/test_auth.py`
3. `git commit -m "Fix auth validation and add its test"`

**Accepted Alternatives**

- `git commit --message "Fix auth validation and add its test"`, `git commit --message="Fix auth validation and add its test"`, `git commit -m"Fix auth validation and add its test"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the auth validation fix and matching test are saved in the commit “`Fix auth validation and add its test`”. The refactor, test cleanup, and debug notes stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix auth validation and add its test`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 1.4.12 Stage ranking hunks across search code and tests · Hard

**Variant ID:** `partial-hard-search-cross-file`

**Story**

The ranking change touched `src/search.py` and `tests/test_search.py`, and each file also carries something unrelated: cleanup in the code, a fixture tidy-up in the tests.

A `tmp/search-output.txt` file is lying around from a test run. Sage is going to cite this commit as the one that fixed ranking, so it should contain exactly that.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/search.py`, `tests/test_search.py`, `tmp/search-output.txt`.

**Real-World Context**

The ranking logic and its test should be reviewed together. The unrelated cleanup, fixture edits, and temporary output can remain outside this commit.

**Your Task**

Stage __only__ the search ranking fix and matching test and commit it with the message `Fix search ranking and add its test`. Leave the cleanup, fixture edits, and temporary output out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix search ranking and add its test" on main.
- [ ] It contains only the search ranking fix and matching test.
- [ ] The cleanup, fixture edits, and temporary output are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/search.py`
2. `git add -p tests/test_search.py`
3. `git commit -m "Fix search ranking and add its test"`

**Accepted Alternatives**

- `git commit --message "Fix search ranking and add its test"`, `git commit --message="Fix search ranking and add its test"`, `git commit -m"Fix search ranking and add its test"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the search ranking fix and matching test are saved in the commit “`Fix search ranking and add its test`”. The cleanup, fixture edits, and temporary output stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix search ranking and add its test`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 1.4.13 Stage formatting hunks across export code and tests · Hard

**Variant ID:** `partial-hard-export-cross-file`

**Story**

Fixing the export date format meant changing `src/export.py` and `tests/test_export.py`.

Each file also has changes that don't belong to the fix: logging in the code and a cleanup in the tests. `notes/export-followup.md` is waiting beside them. Raven wants a commit that tells the story of the format fix and nothing else.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/export.py`, `tests/test_export.py`, `notes/export-followup.md`.

**Real-World Context**

The export formatting fix and its test form one change. Selecting their hunks keeps extra logging, test cleanup, and follow-up notes for later.

**Your Task**

Stage __only__ the export formatting fix and matching test and commit it with the message `Fix export formatting and add its test`. Leave the logging, test cleanup, and follow-up notes out of the commit and finish on `main`.

**Objective Checklist**

- [ ] Create a commit named "Fix export formatting and add its test" on main.
- [ ] It contains only the export formatting fix and matching test.
- [ ] The logging, test cleanup, and follow-up notes are not committed and still in the working folder.
- [ ] Finish on main.

**Answer Key**

1. `git add -p src/export.py`
2. `git add -p tests/test_export.py`
3. `git commit -m "Fix export formatting and add its test"`

**Accepted Alternatives**

- `git commit --message "Fix export formatting and add its test"`, `git commit --message="Fix export formatting and add its test"`, `git commit -m"Fix export formatting and add its test"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P4, P5, P6.

**Not accepted**

- `git add <file>` (whole file) is NOT accepted: it would stage the hunks that must stay out.

**Expected Result**

Only the export formatting fix and matching test are saved in the commit “`Fix export formatting and add its test`”. The logging, test cleanup, and follow-up notes stay in the working folder, uncommitted.

**Evaluation**

- Latest commit on `main` = `Fix export formatting and add its test`; its diff equals ONLY the hunks tagged `fix` in the seed; the remaining hunks are still unstaged changes.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 1.5.1 Fix a typo in the last commit message · Easy

**Variant ID:** `amend-easy-typo`

**Story**

You made the group's first commit and sent a screenshot to the chat before noticing the message reads "Initiall commit". The files are fine. Raven, who likes tidy history, hasn't seen it yet, and nobody else has your commit.

**Starting point:** You are on `main`; local branches include `main`.

**Real-World Context**

A typo in the latest local commit message makes history harder to scan. Amending corrects the label on the existing snapshot without adding a new change.

**Your Task**

Change the latest local commit message to `Initial commit`. Keep its files as they are and finish on `main`.

**Objective Checklist**

- [ ] Correct the latest commit's message to "Initial commit".
- [ ] The files in that commit are unchanged.
- [ ] No extra commit was created.
- [ ] Finish on main.

**Answer Key**

1. `git commit --amend -m "Initial commit"`

**Accepted Alternatives**

- `git commit --amend --message "Initial commit"`, `git commit --amend --message="Initial commit"`, `git commit --amend -m"Initial commit"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P7.

**Expected Result**

The latest commit now reads “`Initial commit`”. Its files are the same and no new commit was added.

**Evaluation**

- HEAD message `Initial commit`; HEAD tree identical to before; commit count unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.5.2 Add a forgotten file to the last commit · Easy

**Variant ID:** `amend-easy-forgot`

**Story**

You committed `login.py` as "`Add auth module`", then noticed `logout.py` is still sitting in your folder. Half an auth module isn't a module, and you haven't shared the commit with anyone.

**Starting point:** You are on `main`; local branches include `main`; working files include `src/logout.py`.

**Real-World Context**

Login and logout are parts of one auth module. Adding the forgotten logout file to the latest local commit keeps that snapshot complete.

**Your Task**

Include `src/logout.py` in the latest local commit while keeping its message `Add auth module`. Finish on `main`.

**Objective Checklist**

- [ ] Add src/logout.py to the latest commit.
- [ ] The latest commit's message is still “Add auth module”.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add src/logout.py`
2. `git commit --amend -m "Add auth module"`

**Accepted Alternatives**

- `git commit --amend --message "Add auth module"`, `git commit --amend --message="Add auth module"`, `git commit --amend -m"Add auth module"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P29, P7.

**Expected Result**

`src/logout.py` is now inside the latest commit, which keeps its message “`Add auth module`”.

**Evaluation**

- HEAD commit contains `src/logout.py`; message `Add auth module`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 1.5.3 Clarify a vague commit message · Easy

**Variant ID:** `amend-easy-login-copy-message`

**Story**

Going through your history, Maeve points at a commit that says only "`Update text`". It reworded the login screen, but nobody reading the log would guess that. The files are right. **You haven't pushed** it.

**Starting point:** You are on `main`; local branches include `main`.

**Real-World Context**

A message like “`Update text`” hides what a change did. Amending the latest local message makes the login copy update findable without touching its files.

**Your Task**

Change the latest local commit message to `Clarify login copy`. Keep its files as they are and finish on `main`.

**Objective Checklist**

- [ ] Change the latest commit's message to "Clarify login copy".
- [ ] The files in that commit are unchanged.
- [ ] No extra commit was created.
- [ ] Finish on main.

**Answer Key**

1. `git commit --amend -m "Clarify login copy"`

**Accepted Alternatives**

- `git commit --amend --message "Clarify login copy"`, `git commit --amend --message="Clarify login copy"`, `git commit --amend -m"Clarify login copy"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P7.

**Expected Result**

The latest commit now reads “`Clarify login copy`”. Its files are the same and no new commit was added.

**Evaluation**

- HEAD message `Clarify login copy`; HEAD tree identical to before; commit count unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.5.4 Clarify the README commit message · Easy

**Variant ID:** `amend-easy-readme-message`

**Story**

Your last commit says "Update README", which tells a reader nothing. What it actually did was spell out what you need installed before the project will run. The content is correct, and the commit is still only on your laptop.

**Starting point:** You are on `main`; local branches include `main`.

**Real-World Context**

A README update can cover many topics. A more specific message helps future contributors locate the setup requirements change in history.

**Your Task**

Change the latest local commit message to `Clarify setup requirements`. Keep its files as they are and finish on `main`.

**Objective Checklist**

- [ ] Change the latest commit's message to "Clarify setup requirements".
- [ ] The files in that commit are unchanged.
- [ ] No extra commit was created.
- [ ] Finish on main.

**Answer Key**

1. `git commit --amend -m "Clarify setup requirements"`

**Accepted Alternatives**

- `git commit --amend --message "Clarify setup requirements"`, `git commit --amend --message="Clarify setup requirements"`, `git commit --amend -m"Clarify setup requirements"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P7.

**Expected Result**

The latest commit now reads “`Clarify setup requirements`”. Its files are the same and no new commit was added.

**Evaluation**

- HEAD message `Clarify setup requirements`; HEAD tree identical to before; commit count unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.5.5 Clarify the navbar commit message · Easy

**Variant ID:** `amend-easy-navbar-message`

**Story**

Your last commit message is just "`CSS updates`", but what you did was fix the navbar spacing.

Sage scans the history to find that sort of change, and "`CSS updates`" would never show up in a search. **The files are fine and the commit hasn't left your laptop.**

**Starting point:** You are on `main`; local branches include `main`.

**Real-World Context**

“`CSS updates`” says little about the visible result. Correcting the latest local message identifies the navbar spacing change for later review.

**Your Task**

Change the latest local commit message to `Adjust navbar spacing`. Keep its files as they are and finish on `main`.

**Objective Checklist**

- [ ] Change the latest commit's message to "Adjust navbar spacing".
- [ ] The files in that commit are unchanged.
- [ ] No extra commit was created.
- [ ] Finish on main.

**Answer Key**

1. `git commit --amend -m "Adjust navbar spacing"`

**Accepted Alternatives**

- `git commit --amend --message "Adjust navbar spacing"`, `git commit --amend --message="Adjust navbar spacing"`, `git commit --amend -m"Adjust navbar spacing"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P7.

**Expected Result**

The latest commit now reads “`Adjust navbar spacing`”. Its files are the same and no new commit was added.

**Evaluation**

- HEAD message `Adjust navbar spacing`; HEAD tree identical to before; commit count unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.5.6 Add changelog and correct the commit message · Medium

**Variant ID:** `amend-med-both`

**Story**

Your last commit is titled "`update stuff`", and you also forgot to include `docs/CHANGELOG.md` with it. Maeve requires that every feature commit mention what it adds and touch the changelog. **Nobody has pulled your commit yet.**

**Starting point:** You are on `main`; local branches include `main`; working files include `docs/CHANGELOG.md`.

**Real-World Context**

The parser feature is missing its changelog entry and has a vague message. One amend can make the latest local commit both complete and understandable.

**Your Task**

Include `docs/CHANGELOG.md` in the latest local commit and change its message to `Add parser feature and update changelog`. Finish on `main`.

**Objective Checklist**

- [ ] Add docs/CHANGELOG.md to the latest commit.
- [ ] Change the latest commit's message to "Add parser feature and update changelog".
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add docs/CHANGELOG.md`
2. `git commit --amend -m "Add parser feature and update changelog"`

**Accepted Alternatives**

- `git commit --amend --message "Add parser feature and update changelog"`, `git commit --amend --message="Add parser feature and update changelog"`, `git commit --amend -m"Add parser feature and update changelog"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P7.

**Expected Result**

`docs/CHANGELOG.md` is now inside the latest commit, and its message is “`Add parser feature and update changelog`”.

**Evaluation**

- HEAD commit contains `docs/CHANGELOG.md`; message `Add parser feature and update changelog`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.5.7 Add missing profile CSS to the last commit · Medium

**Variant ID:** `amend-medium-profile-missing-css`

**Story**

You committed `profile-card.js` and, a minute later, found `styles/profile-card.css` still waiting in your folder.

Without the stylesheet, the commit leaves the card broken for anyone who checks it out. **The message is right, and the commit hasn't left your laptop.**

**Starting point:** You are on `main`; local branches include `main`; working files include `styles/profile-card.css`.

**Real-World Context**

A profile layout commit needs its matching stylesheet. Folding the forgotten CSS into the latest local snapshot keeps the component change together.

**Your Task**

Include `styles/profile-card.css` in the latest local commit while keeping its message `Update profile card layout`. Finish on `main`.

**Objective Checklist**

- [ ] Add styles/profile-card.css to the latest commit.
- [ ] The latest commit's message is still “Update profile card layout”.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add styles/profile-card.css`
2. `git commit --amend -m "Update profile card layout"`

**Accepted Alternatives**

- `git commit --amend --message "Update profile card layout"`, `git commit --amend --message="Update profile card layout"`, `git commit --amend -m"Update profile card layout"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P29, P7.

**Expected Result**

`styles/profile-card.css` is now inside the latest commit, which keeps its message “`Update profile card layout`”.

**Evaluation**

- HEAD commit contains `styles/profile-card.css`; message `Update profile card layout`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.5.8 Add missing export docs to the last commit · Medium

**Variant ID:** `amend-medium-export-doc`

**Story**

You committed the export module but forgot `docs/export.md`, the page that tells librarians how to use it. Finn will review the commit tomorrow, and a review of code without its explanation would be incomplete.

The message is right. **The commit has not been pushed or shared with anyone.**

**Starting point:** You are on `main`; local branches include `main`; working files include `docs/export.md`.

**Real-World Context**

Export behavior and its documentation should describe the same version. Adding the omitted docs to the latest local commit keeps the change coherent.

**Your Task**

Include `docs/export.md` in the latest local commit while keeping its message `Document export flow update`. Finish on `main`.

**Objective Checklist**

- [ ] Add docs/export.md to the latest commit.
- [ ] The latest commit's message is still “Document export flow update”.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add docs/export.md`
2. `git commit --amend -m "Document export flow update"`

**Accepted Alternatives**

- `git commit --amend --message "Document export flow update"`, `git commit --amend --message="Document export flow update"`, `git commit --amend -m"Document export flow update"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P29, P7.

**Expected Result**

`docs/export.md` is now inside the latest commit, which keeps its message “`Document export flow update`”.

**Evaluation**

- HEAD commit contains `docs/export.md`; message `Document export flow update`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.5.9 Add missing search template to the last commit · Medium

**Variant ID:** `amend-medium-search-template`

**Story**

Your commit has the search JavaScript but not `templates/search.html`, which the new handler depends on.

Sage will pull your work tonight, and a search with no template would fail on the first request. **You haven't pushed yet, and the message is fine.**

**Starting point:** You are on `main`; local branches include `main`; working files include `templates/search.html`.

**Real-World Context**

A search handler without its template leaves a partial user-facing update. Amending the latest local commit can include the missing page file.

**Your Task**

Include `templates/search.html` in the latest local commit while keeping its message `Refine search results view`. Finish on `main`.

**Objective Checklist**

- [ ] Add templates/search.html to the latest commit.
- [ ] The latest commit's message is still “Refine search results view”.
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add templates/search.html`
2. `git commit --amend -m "Refine search results view"`

**Accepted Alternatives**

- `git commit --amend --message "Refine search results view"`, `git commit --amend --message="Refine search results view"`, `git commit --amend -m"Refine search results view"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P29, P7.

**Expected Result**

`templates/search.html` is now inside the latest commit, which keeps its message “`Refine search results view`”.

**Evaluation**

- HEAD commit contains `templates/search.html`; message `Refine search results view`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.5.10 Correct a verbose passive-voice commit message · Hard

**Variant ID:** `amend-hard-convention`

**Story**

Your last commit says "`terraform configs have been updated for staging env`".

Maeve's rule is that commit messages read like instructions to the codebase, short and in the imperative, not like reports of what happened. **The files are correct, and you haven't pushed.**

**Starting point:** You are on `main`; local branches include `main`.

**Real-World Context**

A concise, action-oriented message helps teammates scan history. Amending the local Terraform commit improves its description without changing its configuration.

**Your Task**

Change the latest local commit message to `Update Terraform staging environment configuration`. Keep its files as they are and finish on `main`.

**Objective Checklist**

- [ ] Change the latest commit's message to "Update Terraform staging environment configuration".
- [ ] The files in that commit are unchanged.
- [ ] No extra commit was created.
- [ ] Finish on main.

**Answer Key**

1. `git commit --amend -m "Update Terraform staging environment configuration"`

**Accepted Alternatives**

- `git commit --amend --message "Update Terraform staging environment configuration"`, `git commit --amend --message="Update Terraform staging environment configuration"`, `git commit --amend -m"Update Terraform staging environment configuration"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P7.

**Expected Result**

The latest commit now reads “`Update Terraform staging environment configuration`”. Its files are the same and no new commit was added.

**Evaluation**

- HEAD message `Update Terraform staging environment configuration`; HEAD tree identical to before; commit count unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 1.5.11 Add missing CSS and correct the commit message · Hard

**Variant ID:** `amend-hard-profile-message-and-layout`

**Story**

Your last commit has two problems. "`Update profile stuff`" doesn't describe anything, and `styles/profile-layout.css` was left out by mistake.

Raven is about to pull your branch for the demo. **The commit hasn't been shared yet, so it can still be fixed cleanly.**

**Starting point:** You are on `main`; local branches include `main`; working files include `styles/profile-layout.css`.

**Real-World Context**

The profile commit is missing CSS and has an unclear message. Correcting both in one amend makes the latest local snapshot ready for review.

**Your Task**

Include `styles/profile-layout.css` in the latest local commit and change its message to `Polish profile card layout`. Finish on `main`.

**Objective Checklist**

- [ ] Add styles/profile-layout.css to the latest commit.
- [ ] Change the latest commit's message to "Polish profile card layout".
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add styles/profile-layout.css`
2. `git commit --amend -m "Polish profile card layout"`

**Accepted Alternatives**

- `git commit --amend --message "Polish profile card layout"`, `git commit --amend --message="Polish profile card layout"`, `git commit --amend -m"Polish profile card layout"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P7.

**Expected Result**

`styles/profile-layout.css` is now inside the latest commit, and its message is “`Polish profile card layout`”.

**Evaluation**

- HEAD commit contains `styles/profile-layout.css`; message `Polish profile card layout`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.5.12 Add missing test and correct the commit message · Hard

**Variant ID:** `amend-hard-auth-message-and-test`

**Story**

Your last commit is titled "`Auth changes`", which is vague, and it doesn't include `tests/test_auth.py`, the test that proves the change works.

Maeve asked for tests with every auth change, and she is checking the history tonight. **Nobody has seen the commit yet.**

**Starting point:** You are on `main`; local branches include `main`; working files include `tests/test_auth.py`.

**Real-World Context**

Auth validation and its test belong together. An amend can add the missing coverage and replace a vague message with a description reviewers can use.

**Your Task**

Include `tests/test_auth.py` in the latest local commit and change its message to `Add auth validation coverage`. Finish on `main`.

**Objective Checklist**

- [ ] Add tests/test_auth.py to the latest commit.
- [ ] Change the latest commit's message to "Add auth validation coverage".
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add tests/test_auth.py`
2. `git commit --amend -m "Add auth validation coverage"`

**Accepted Alternatives**

- `git commit --amend --message "Add auth validation coverage"`, `git commit --amend --message="Add auth validation coverage"`, `git commit --amend -m"Add auth validation coverage"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P7.

**Expected Result**

`tests/test_auth.py` is now inside the latest commit, and its message is “`Add auth validation coverage`”.

**Evaluation**

- HEAD commit contains `tests/test_auth.py`; message `Add auth validation coverage`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.5.13 Add missing docs and correct the commit message · Hard

**Variant ID:** `amend-hard-export-message-and-doc`

**Story**

"`Export update`" is your last commit message, and it left out `docs/export.md`.

Finn follows the log to see what changed in the export, and this entry would tell him nothing and send him to a page that isn't there. **The commit exists only on your laptop.**

**Starting point:** You are on `main`; local branches include `main`; working files include `docs/export.md`.

**Real-World Context**

The export change needs its documentation and a specific message. Fixing both in the latest local commit keeps the behavior and explanation together.

**Your Task**

Include `docs/export.md` in the latest local commit and change its message to `Document export validation behavior`. Finish on `main`.

**Objective Checklist**

- [ ] Add docs/export.md to the latest commit.
- [ ] Change the latest commit's message to "Document export validation behavior".
- [ ] No extra commit was created (the amended commit replaced the old one).
- [ ] No uncommitted changes remain.
- [ ] Finish on main.

**Answer Key**

1. `git add docs/export.md`
2. `git commit --amend -m "Document export validation behavior"`

**Accepted Alternatives**

- `git commit --amend --message "Document export validation behavior"`, `git commit --amend --message="Document export validation behavior"`, `git commit --amend -m"Document export validation behavior"`, single quotes instead of double. option order swapped (`-m` before `--amend`). The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P1, P7.

**Expected Result**

`docs/export.md` is now inside the latest commit, and its message is “`Document export validation behavior`”.

**Evaluation**

- HEAD commit contains `docs/export.md`; message `Document export validation behavior`; commit count unchanged; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.6.1 Unstage notes.txt without discarding it · Easy

**Variant ID:** `restore-easy-unstage`

**Story**

You staged everything with one quick command and `notes.txt` came along with the files you meant to commit. The notes are yours, not the project's, and you still want them. The commit isn't ready.

**Starting point:** You are on `main`; local branches include `main`; some changes are staged.

**Real-World Context**

Staging `notes.txt` does not mean its edits are lost when it is removed from the index. Unstaging keeps the notes available for a later commit.

**Your Task**

Unstage `notes.txt` while keeping those edits. Finish on `main`.

**Objective Checklist**

- [ ] notes.txt is no longer staged, and its edits are still in the working folder.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged notes.txt`

**Accepted Alternatives**

- `git restore -S notes.txt`, `git reset HEAD -- notes.txt`, `git reset -- notes.txt` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Expected Result**

`notes.txt` is unstaged with the edits kept. You are on `main`, and nothing was committed.

**Evaluation**

- `notes.txt`: not in the index diff; working-tree edits present.
- Branch `main`; no commit created.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.6.2 Discard experimental config.py changes · Easy

**Variant ID:** `restore-easy-discard`

**Story**

You spent an hour trying a new approach in `config.py`, and it didn't work. The edits are still in your folder. You want the file back exactly as the last commit left it, and nothing in these edits is worth keeping.

**Starting point:** You are on `main`; local branches include `main`; working files include `config.py`.

**Real-World Context**

An unsuccessful configuration experiment can be replaced with the last committed version. Restoring this tracked file clears the unwanted local edit.

**Your Task**

Discard the working-tree changes in `config.py` and restore the committed version. Finish on `main`.

**Objective Checklist**

- [ ] Discard the edits in config.py, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore config.py`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree config.py`, `git restore -W config.py`, `git checkout -- config.py`, `git checkout HEAD -- config.py`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`config.py` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `config.py`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.6.3 Unstage src/app.py without discarding it · Easy

**Variant ID:** `restore-easy-unstage-app`

**Story**

You staged `src/app.py` and then realized it isn't ready. There's still a function you haven't finished, and the commit would have broken the build for Sage. **Your edits to the file should survive.**

**Starting point:** You are on `main`; local branches include `main`; some changes are staged.

**Real-World Context**

The app change still needs work, so it should wait outside the next commit. Unstaging keeps the edited source file in the working tree.

**Your Task**

Unstage `src/app.py` while keeping those edits. Finish on `main`.

**Objective Checklist**

- [ ] src/app.py is no longer staged, and its edits are still in the working folder.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged src/app.py`

**Accepted Alternatives**

- `git restore -S src/app.py`, `git reset HEAD -- src/app.py`, `git reset -- src/app.py` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Expected Result**

`src/app.py` is unstaged with the edits kept. You are on `main`, and nothing was committed.

**Evaluation**

- `src/app.py`: not in the index diff; working-tree edits present.
- Branch `main`; no commit created.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.6.4 Unstage docs/guide.md without discarding it · Easy

**Variant ID:** `restore-easy-unstage-guide`

**Story**

You staged `docs/guide.md`, then decided to revise it more before it goes into a commit. **The edits you've made so far are good work and need to stay in your folder.**

**Starting point:** You are on `main`; local branches include `main`; some changes are staged.

**Real-World Context**

A guide that needs another revision should not be part of the next snapshot yet. Unstaging preserves its current edits for continued writing.

**Your Task**

Unstage `docs/guide.md` while keeping those edits. Finish on `main`.

**Objective Checklist**

- [ ] docs/guide.md is no longer staged, and its edits are still in the working folder.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged docs/guide.md`

**Accepted Alternatives**

- `git restore -S docs/guide.md`, `git reset HEAD -- docs/guide.md`, `git reset -- docs/guide.md` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Expected Result**

`docs/guide.md` is unstaged with the edits kept. You are on `main`, and nothing was committed.

**Evaluation**

- `docs/guide.md`: not in the index diff; working-tree edits present.
- Branch `main`; no commit created.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.6.5 Unstage styles/site.css without discarding it · Easy

**Variant ID:** `restore-easy-unstage-css`

**Story**

You staged `styles/site.css` and then realized another CSS change belongs in the same commit. If you commit now, the change is split in two. **Your edits to the file must stay**, and you'll group everything later.

**Starting point:** You are on `main`; local branches include `main`; some changes are staged.

**Real-World Context**

The CSS change will be committed with another styling update later. Unstaging keeps the current edit while the developer prepares the complete set.

**Your Task**

Unstage `styles/site.css` while keeping those edits. Finish on `main`.

**Objective Checklist**

- [ ] styles/site.css is no longer staged, and its edits are still in the working folder.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged styles/site.css`

**Accepted Alternatives**

- `git restore -S styles/site.css`, `git reset HEAD -- styles/site.css`, `git reset -- styles/site.css` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Expected Result**

`styles/site.css` is unstaged with the edits kept. You are on `main`, and nothing was committed.

**Evaluation**

- `styles/site.css`: not in the index diff; working-tree edits present.
- Branch `main`; no commit created.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 1.6.6 Unstage experimental.py, discard README.md changes · Medium

**Variant ID:** `restore-med-unstage-discard`

**Story**

`experimental.py` is staged, but you aren't ready to commit it. It's work you want to keep, only not in the next commit.

Separately, your edits to `README.md` came from a bad paste and are worth nothing. **Once discarded, they can't be recovered.**

**Starting point:** You are on `main`; local branches include `main`; working files include `README.md`; some changes are staged.

**Real-World Context**

The staged experiment should remain editable, while the unwanted README edits should disappear. These two files need different recovery actions.

**Your Task**

Unstage `experimental.py` while keeping those edits. Discard the working-tree changes in `README.md` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] experimental.py is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in README.md, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged experimental.py`
2. `git restore README.md`

**Accepted Alternatives**

- `git restore -S experimental.py`, `git reset HEAD -- experimental.py`, `git reset -- experimental.py` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree README.md`, `git restore -W README.md`, `git checkout -- README.md`, `git checkout HEAD -- README.md`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`experimental.py` is unstaged with the edits kept; `README.md` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `experimental.py`: not in the index diff; working-tree edits present.
- `README.md`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.6.7 Preserve app.py, discard debug.log · Medium

**Variant ID:** `restore-medium-app-debug`

**Story**

`src/app.py` is staged, though you aren't ready to commit it yet, and your work in it is valuable. `debug.log` in the same folder is full of noise from tonight's testing, and you want the file back the way the last commit left it. **One of these edits is worth saving and the other isn't.**

**Starting point:** You are on `main`; local branches include `main`; working files include `debug.log`; some changes are staged.

**Real-World Context**

The app code is unfinished but worth keeping; the tracked debug log is disposable. Cleaning the state means preserving one edit and discarding the other.

**Your Task**

Unstage `src/app.py` while keeping those edits. Discard the working-tree changes in `debug.log` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] src/app.py is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in debug.log, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged src/app.py`
2. `git restore debug.log`

**Accepted Alternatives**

- `git restore -S src/app.py`, `git reset HEAD -- src/app.py`, `git reset -- src/app.py` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree debug.log`, `git restore -W debug.log`, `git checkout -- debug.log`, `git checkout HEAD -- debug.log`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`src/app.py` is unstaged with the edits kept; `debug.log` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `src/app.py`: not in the index diff; working-tree edits present.
- `debug.log`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.6.8 Preserve guide.md, discard scratch.txt · Medium

**Variant ID:** `restore-medium-docs-scratch`

**Story**

You staged `docs/guide.md` for a later commit. You'll keep editing it, and the edits so far matter. `tmp/scratch.txt` was only temporary notes, and nothing in it is worth keeping. Maeve checks for stray files before every review.

**Starting point:** You are on `main`; local branches include `main`; working files include `tmp/scratch.txt`; some changes are staged.

**Real-World Context**

The guide needs further work, whereas temporary scratch notes are no longer useful. Unstaging and restoring serve those separate intentions.

**Your Task**

Unstage `docs/guide.md` while keeping those edits. Discard the working-tree changes in `tmp/scratch.txt` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] docs/guide.md is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in tmp/scratch.txt, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged docs/guide.md`
2. `git restore tmp/scratch.txt`

**Accepted Alternatives**

- `git restore -S docs/guide.md`, `git reset HEAD -- docs/guide.md`, `git reset -- docs/guide.md` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree tmp/scratch.txt`, `git restore -W tmp/scratch.txt`, `git checkout -- tmp/scratch.txt`, `git checkout HEAD -- tmp/scratch.txt`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`docs/guide.md` is unstaged with the edits kept; `tmp/scratch.txt` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `docs/guide.md`: not in the index diff; working-tree edits present.
- `tmp/scratch.txt`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.6.9 Preserve source CSS, discard generated dist CSS · Medium

**Variant ID:** `restore-medium-css-build`

**Story**

You staged `styles/site.css` and need to keep working on it. `dist/site.css` was generated from an old build and is already out of date. Committing the generated file would confuse Finn, who will regenerate it anyway.

**Starting point:** You are on `main`; local branches include `main`; working files include `dist/site.css`; some changes are staged.

**Real-World Context**

Source CSS is work in progress, while the old tracked build output should return to its committed form. Treating them separately protects the source edit.

**Your Task**

Unstage `styles/site.css` while keeping those edits. Discard the working-tree changes in `dist/site.css` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] styles/site.css is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in dist/site.css, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged styles/site.css`
2. `git restore dist/site.css`

**Accepted Alternatives**

- `git restore -S styles/site.css`, `git reset HEAD -- styles/site.css`, `git reset -- styles/site.css` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree dist/site.css`, `git restore -W dist/site.css`, `git checkout -- dist/site.css`, `git checkout HEAD -- dist/site.css`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`styles/site.css` is unstaged with the edits kept; `dist/site.css` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `styles/site.css`: not in the index diff; working-tree edits present.
- `dist/site.css`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 1.6.10 Unstage two files, discard experimental.py · Hard

**Variant ID:** `restore-hard-cleanup`

**Story**

Your folder is in a messy mixed state. `debug.log` and `scratch/notes.txt` are staged, though neither belongs in the next commit, and you still want both. `api/experimental.py` has edits you've decided are a dead end. Nothing is going to be committed tonight, and once the dead-end edits are discarded they're gone for good.

**Starting point:** You are on `main`; local branches include `main`; working files include `api/experimental.py`; some changes are staged.

**Real-World Context**

A mixed workspace may contain staged notes worth keeping and an experiment worth abandoning. Removing files from staging does not discard their edits; restoring the experiment does.

**Your Task**

Unstage `debug.log`, `scratch/notes.txt` while keeping those edits. Discard the working-tree changes in `api/experimental.py` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] debug.log is no longer staged, and its edits are still in the working folder.
- [ ] scratch/notes.txt is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in api/experimental.py, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged debug.log scratch/notes.txt`
2. `git restore api/experimental.py`

**Accepted Alternatives**

- `git restore -S debug.log scratch/notes.txt`, `git reset HEAD -- debug.log scratch/notes.txt`, `git reset -- debug.log scratch/notes.txt` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree api/experimental.py`, `git restore -W api/experimental.py`, `git checkout -- api/experimental.py`, `git checkout HEAD -- api/experimental.py`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`debug.log`, `scratch/notes.txt` are unstaged with the edits kept; `api/experimental.py` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `debug.log`: not in the index diff; working-tree edits present.
- `scratch/notes.txt`: not in the index diff; working-tree edits present.
- `api/experimental.py`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.6.11 Unstage two files, discard debug log · Hard

**Variant ID:** `restore-hard-mixed-profile`

**Story**

`src/profile-card.js` and `notes/profile-ideas.md` are both staged, but neither is ready to commit, and both contain work you want to keep.

Meanwhile `debug/profile.log` has been overwritten with noise from testing. You aren't committing anything now. **Whatever gets discarded here can't be brought back.**

**Starting point:** You are on `main`; local branches include `main`; working files include `debug/profile.log`; some changes are staged.

**Real-World Context**

The profile code and planning notes need more work, while the tracked debug log should be cleared. The cleanup keeps the first two edits and discards the log change.

**Your Task**

Unstage `src/profile-card.js`, `notes/profile-ideas.md` while keeping those edits. Discard the working-tree changes in `debug/profile.log` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] src/profile-card.js is no longer staged, and its edits are still in the working folder.
- [ ] notes/profile-ideas.md is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in debug/profile.log, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged src/profile-card.js notes/profile-ideas.md`
2. `git restore debug/profile.log`

**Accepted Alternatives**

- `git restore -S src/profile-card.js notes/profile-ideas.md`, `git reset HEAD -- src/profile-card.js notes/profile-ideas.md`, `git reset -- src/profile-card.js notes/profile-ideas.md` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree debug/profile.log`, `git restore -W debug/profile.log`, `git checkout -- debug/profile.log`, `git checkout HEAD -- debug/profile.log`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`src/profile-card.js`, `notes/profile-ideas.md` are unstaged with the edits kept; `debug/profile.log` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `src/profile-card.js`: not in the index diff; working-tree edits present.
- `notes/profile-ideas.md`: not in the index diff; working-tree edits present.
- `debug/profile.log`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.6.12 Unstage two files, discard generated output · Hard

**Variant ID:** `restore-hard-mixed-export`

**Story**

`src/export.py` and `notes/export-plan.md` are staged, though you intend to keep working on both before committing. `tmp/export-output.txt` is generated output that keeps changing every time you run a test. Raven wants tonight's folder clean, but nothing needs to be committed, and **what gets thrown away can't come back**.

**Starting point:** You are on `main`; local branches include `main`; working files include `tmp/export-output.txt`; some changes are staged.

**Real-World Context**

The export code and plan should remain editable after they leave staging. The tracked generated output can return to its committed state.

**Your Task**

Unstage `src/export.py`, `notes/export-plan.md` while keeping those edits. Discard the working-tree changes in `tmp/export-output.txt` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] src/export.py is no longer staged, and its edits are still in the working folder.
- [ ] notes/export-plan.md is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in tmp/export-output.txt, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged src/export.py notes/export-plan.md`
2. `git restore tmp/export-output.txt`

**Accepted Alternatives**

- `git restore -S src/export.py notes/export-plan.md`, `git reset HEAD -- src/export.py notes/export-plan.md`, `git reset -- src/export.py notes/export-plan.md` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree tmp/export-output.txt`, `git restore -W tmp/export-output.txt`, `git checkout -- tmp/export-output.txt`, `git checkout HEAD -- tmp/export-output.txt`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`src/export.py`, `notes/export-plan.md` are unstaged with the edits kept; `tmp/export-output.txt` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `src/export.py`: not in the index diff; working-tree edits present.
- `notes/export-plan.md`: not in the index diff; working-tree edits present.
- `tmp/export-output.txt`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 1.6.13 Unstage two files, discard debug search log · Hard

**Variant ID:** `restore-hard-mixed-search`

**Story**

You staged `src/search.js` and `notes/search.md` too early, and you want to keep the edits in both. `debug/search.log` is the only file whose changes you want to throw away. Sage is about to review, but there's nothing to commit yet, and **a wrong choice here can't be undone**.

**Starting point:** You are on `main`; local branches include `main`; working files include `debug/search.log`; some changes are staged.

**Real-World Context**

The search code and notes are still useful, but the tracked debug log is not. Keeping the staged edits while discarding the log produces the requested working state.

**Your Task**

Unstage `src/search.js`, `notes/search.md` while keeping those edits. Discard the working-tree changes in `debug/search.log` and restore their committed versions. Finish on `main`.

**Objective Checklist**

- [ ] src/search.js is no longer staged, and its edits are still in the working folder.
- [ ] notes/search.md is no longer staged, and its edits are still in the working folder.
- [ ] Discard the edits in debug/search.log, restoring it to its committed version.
- [ ] No other file was changed, and you finish on main.

**Answer Key**

1. `git restore --staged src/search.js notes/search.md`
2. `git restore debug/search.log`

**Accepted Alternatives**

- `git restore -S src/search.js notes/search.md`, `git reset HEAD -- src/search.js notes/search.md`, `git reset -- src/search.js notes/search.md` (older equivalents); the named paths in one command or several.
- Common patterns that apply: P8.

**Not accepted**

- `git restore --worktree debug/search.log`, `git restore -W debug/search.log`, `git checkout -- debug/search.log`, `git checkout HEAD -- debug/search.log`. `git restore .` is NOT accepted when other files must keep their edits.

**Expected Result**

`src/search.js`, `notes/search.md` are unstaged with the edits kept; `debug/search.log` was restored to the committed version. You are on `main`, and nothing was committed.

**Evaluation**

- `src/search.js`: not in the index diff; working-tree edits present.
- `notes/search.md`: not in the index diff; working-tree edits present.
- `debug/search.log`: identical to HEAD.
- Branch `main`; no commit created.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.1.1 Create feature/auth and switch to it · Easy

**Variant ID:** `v21e-auth`

**Story**

The ticketing app has plenty of screens, but no way for a customer to sign in. Finn drops the authentication ticket into your queue just as the team is preparing to demo the current build. “*Please don’t turn the demo branch into a construction site,*” he says.

You are on `main`, which holds the team’s existing work. Before touching the sign-in code, give the new feature its own branch called `feature/auth` and move there. The demo can continue while you work.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A branch is a separate line of development. Putting authentication work on its own branch gives reviewers a clear set of changes before it joins `main`.

**Your Task**

Create `feature/auth` from the current tip of `main` and switch to it. Finish on `feature/auth`.

**Objective Checklist**

- [ ] Create feature/auth from the latest commit of main.
- [ ] feature/auth is checked out.

**Answer Key**

1. `git switch -c feature/auth`

**Accepted Alternatives**

- `git switch --create feature/auth`, `git checkout -b feature/auth`, or two commands: `git branch feature/auth` then `git switch feature/auth` / `git checkout feature/auth` (accepted, not CAR-accurate).

**Expected Result**

`feature/auth` exists, starts where `main` is now, and is checked out.

**Evaluation**

- Branch `feature/auth` points to the same commit as `main`; HEAD on `feature/auth`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.1.2 Create bugfix/login and switch to it · Easy

**Variant ID:** `v21e-login`

**Story**

A customer reports that the login form returns to the same page after a successful sign-in. Maeve reproduces it twice, then sticks a note on your desk: “A fix we can review without disturbing `main`, please.”

You are currently on `main`, and there is no branch for this repair yet. The team has agreed to call it `bugfix/login`. First give the bug its own line of work; the actual code change can follow once you are on that branch.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A login fix can be tested and reviewed on its own branch while `main` continues to represent the team’s stable work.

**Your Task**

Create `bugfix/login` from the current tip of `main` and switch to it. Finish on `bugfix/login`.

**Objective Checklist**

- [ ] Create bugfix/login from the latest commit of main.
- [ ] bugfix/login is checked out.

**Answer Key**

1. `git switch -c bugfix/login`

**Accepted Alternatives**

- `git switch --create bugfix/login`, `git checkout -b bugfix/login`, or two commands: `git branch bugfix/login` then `git switch bugfix/login` / `git checkout bugfix/login` (accepted, not CAR-accurate).

**Expected Result**

`bugfix/login` exists, starts where `main` is now, and is checked out.

**Evaluation**

- Branch `bugfix/login` points to the same commit as `main`; HEAD on `bugfix/login`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.1.3 Create experiment/ui and switch to it · Easy

**Variant ID:** `v21e-ui`

**Story**

Sage has a sketch of a dashboard with oversized cards and a neon progress bar. “It might be brilliant,” she says, “or it might look like an arcade cabinet.” The current dashboard works, and the team does not want an experiment mixed into `main` while they decide.

You are on `main`, ready to try the idea. Start a separate branch named `experiment/ui` and work from there; later the team can compare both versions.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

An experimental interface can change rapidly. Its own branch gives the team a place to compare the idea with the existing dashboard.

**Your Task**

Create `experiment/ui` from the current tip of `main` and switch to it. Finish on `experiment/ui`.

**Objective Checklist**

- [ ] Create experiment/ui from the latest commit of main.
- [ ] experiment/ui is checked out.

**Answer Key**

1. `git switch -c experiment/ui`

**Accepted Alternatives**

- `git switch --create experiment/ui`, `git checkout -b experiment/ui`, or two commands: `git branch experiment/ui` then `git switch experiment/ui` / `git checkout experiment/ui` (accepted, not CAR-accurate).

**Expected Result**

`experiment/ui` exists, starts where `main` is now, and is checked out.

**Evaluation**

- Branch `experiment/ui` points to the same commit as `main`; HEAD on `experiment/ui`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.1.4 Create feature/database-models and switch to it · Easy

**Variant ID:** `bc-easy-capstone-db`

**Story**

Your capstone group has made its first commit and divided up the build. One classmate has the interface, another has reports, and your name is beside database models. Raven watches three people open the same project folder and says, “*Let’s each take a lane before anyone starts editing.*”

You are on `main`, which contains that shared first commit. Create `feature/database-models` from it and move onto the new branch before making model changes.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

With the first project commit in place, each group member can start a feature branch from the same shared baseline.

**Your Task**

Create `feature/database-models` from the current tip of `main` and switch to it. Finish on `feature/database-models`.

**Objective Checklist**

- [ ] Create feature/database-models from the latest commit of main.
- [ ] feature/database-models is checked out.

**Answer Key**

1. `git switch -c feature/database-models`

**Accepted Alternatives**

- `git switch --create feature/database-models`, `git checkout -b feature/database-models`, or two commands: `git branch feature/database-models` then `git switch feature/database-models` / `git checkout feature/database-models` (accepted, not CAR-accurate).

**Expected Result**

`feature/database-models` exists, starts where `main` is now, and is checked out.

**Evaluation**

- Branch `feature/database-models` points to the same commit as `main`; HEAD on `feature/database-models`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.1.5 Create hotfix/session-timeout and switch to it · Easy

**Variant ID:** `bc-easy-corp-hotfix`

**Story**

The support channel lights up: sessions are expiring early in production. Finn asks you to investigate while another developer monitors customer reports.

You are already on `main` at its latest commit, the version the team uses as the starting point for urgent repairs. “*Keep this one focused,*” he says. Give the incident a branch named `hotfix/session-timeout` and switch to it so the repair can be reviewed on its own.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A production fix often needs an immediate, focused branch from the current stable commit so it can be reviewed without unrelated changes.

**Your Task**

Create `hotfix/session-timeout` from the current tip of `main` and switch to it. Finish on `hotfix/session-timeout`.

**Objective Checklist**

- [ ] Create hotfix/session-timeout from the latest commit of main.
- [ ] hotfix/session-timeout is checked out.

**Answer Key**

1. `git switch -c hotfix/session-timeout`

**Accepted Alternatives**

- `git switch --create hotfix/session-timeout`, `git checkout -b hotfix/session-timeout`, or two commands: `git branch hotfix/session-timeout` then `git switch hotfix/session-timeout` / `git checkout hotfix/session-timeout` (accepted, not CAR-accurate).

**Expected Result**

`hotfix/session-timeout` exists, starts where `main` is now, and is checked out.

**Evaluation**

- Branch `hotfix/session-timeout` points to the same commit as `main`; HEAD on `hotfix/session-timeout`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.1.6 Create feature/payments and a test branch from the 2-commit main tip · Medium

**Variant ID:** `v21m-payments`

**Story**

The shop’s checkout page is finally on the sprint board. Sage asks you to build the payment step, but first she wants to know which foundation code you are starting from.

The history on `main` has two commits, and you are on its current tip. Those existing commits are the base for the feature; there is no need to start over.

Sage also wants a second branch, `feature/payments-tests`, ready for the payment tests that a teammate will write later. Create both branches from where you are, and finish on `feature/payments` before the checkout work begins.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Several branches can start from the same commit. Making a branch does not move you onto it, so you decide which one to work on.

**Your Task**

Create `feature/payments` and `feature/payments-tests`, both from the current tip of `main`. Finish on `feature/payments`.

**Objective Checklist**

- [ ] Create feature/payments from the latest commit of main.
- [ ] Branch feature/payments-tests exists at the same commit.
- [ ] feature/payments is checked out.

**Answer Key**

1. `git branch feature/payments-tests`
2. `git switch -c feature/payments`

**Accepted Alternatives**

- `git switch --create feature/payments`, `git checkout -b feature/payments`, or two commands: `git branch feature/payments` then `git switch feature/payments` / `git checkout feature/payments` (accepted, not CAR-accurate).

**Not accepted**

- The two creations may happen in either order. `git switch -c feature/payments-tests` followed by `git switch feature/payments` is NOT accepted unless `feature/payments` already exists.

**Expected Result**

Both branches exist at the same commit, and you are on `feature/payments`.

**Evaluation**

- `feature/payments` and `feature/payments-tests` both point to the old tip of `main`; HEAD on `feature/payments`; `main` unchanged.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 2.1.7 Create feature/notifications and a docs branch from the 3-commit main tip · Medium

**Variant ID:** `v21m-notifications`

**Story**

The messaging team has finished three commits of basic infrastructure, and the next sprint item is push notifications. Raven opens the roadmap and points to the notification card. “Let’s give this work its own place before we start wiring up alerts.”

You are on `main` at its latest commit, so its infrastructure is already your starting point. Sage also wants a branch called `feature/notifications-docs` for the documentation, created from the same commit. Create both branches, and finish on `feature/notifications` so the feature can evolve without changing `main`.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Notifications depend on the current messaging infrastructure, so both branches start from the tip of `main`. Creating a branch does not move you onto it.

**Your Task**

Create `feature/notifications` and `feature/notifications-docs`, both from the current tip of `main`. Finish on `feature/notifications`.

**Objective Checklist**

- [ ] Create feature/notifications from the latest commit of main.
- [ ] Branch feature/notifications-docs exists at the same commit.
- [ ] feature/notifications is checked out.

**Answer Key**

1. `git branch feature/notifications-docs`
2. `git switch -c feature/notifications`

**Accepted Alternatives**

- `git switch --create feature/notifications`, `git checkout -b feature/notifications`, or two commands: `git branch feature/notifications` then `git switch feature/notifications` / `git checkout feature/notifications` (accepted, not CAR-accurate).
- The two creations may happen in either order.

**Expected Result**

Both branches exist at the same commit, and you are on `feature/notifications`.

**Evaluation**

- `feature/notifications` and `feature/notifications-docs` both point to the old tip of `main`; HEAD on `feature/notifications`; `main` unchanged.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 2.1.8 Create feature/export and a docs branch from the 4-commit main tip · Medium

**Variant ID:** `v21m-export`

**Story**

A client wants a CSV export from the report generator before the next release. Sage checks the project history: four commits on `main` already contain the renderer the export will use. You are on the latest `main` commit, with no export branch yet.

“*Build on what we have,*” she says, “and keep the export easy to review.” Sage also wants `feature/export-docs` for the user guide, started from the same commit. Create both, and finish on `feature/export` before writing the CSV code.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The export feature needs the renderer already recorded on `main`, so both branches start from its latest commit. Creating a branch does not move you onto it.

**Your Task**

Create `feature/export` and `feature/export-docs`, both from the current tip of `main`. Finish on `feature/export`.

**Objective Checklist**

- [ ] Create feature/export from the latest commit of main.
- [ ] Branch feature/export-docs exists at the same commit.
- [ ] feature/export is checked out.

**Answer Key**

1. `git branch feature/export-docs`
2. `git switch -c feature/export`

**Accepted Alternatives**

- `git switch --create feature/export`, `git checkout -b feature/export`, or two commands: `git branch feature/export` then `git switch feature/export` / `git checkout feature/export` (accepted, not CAR-accurate).
- The two creations may happen in either order.

**Expected Result**

Both branches exist at the same commit, and you are on `feature/export`.

**Evaluation**

- `feature/export` and `feature/export-docs` both point to the old tip of `main`; HEAD on `feature/export`; `main` unchanged.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 2.1.9 Create feature/docs-update from develop's tip · Medium

**Variant ID:** `bc-med-oss-develop`

**Story**

You have cloned an open source project and found its contribution guide. New work begins from `develop`, even though a `main` branch also exists. Raven points to the documentation ticket and says, “A small guide update is a good first contribution.”

You are already on `develop`, so its latest commit is the correct base. Create `feature/docs-update` here and switch to it; starting from `main` would miss the development work the maintainers expect.

**Starting point:** You are on `develop`; available local branches: `develop`, `main`.

**Real-World Context**

Open source projects sometimes use `develop` for new contributions. A branch made while on `develop` starts from that line’s current commit.

**Your Task**

Create `feature/docs-update` from the current tip of `develop` and switch to it. Finish on `feature/docs-update`.

**Objective Checklist**

- [ ] Create feature/docs-update from the latest commit of develop.
- [ ] feature/docs-update is checked out.

**Answer Key**

1. `git switch -c feature/docs-update`

**Accepted Alternatives**

- `git switch --create feature/docs-update`, `git checkout -b feature/docs-update`, or two commands: `git branch feature/docs-update` then `git switch feature/docs-update` / `git checkout feature/docs-update` (accepted, not CAR-accurate).

**Expected Result**

`feature/docs-update` exists, starts where `develop` is now, and is checked out.

**Evaluation**

- Branch `feature/docs-update` points to the same commit as `develop`; HEAD on `feature/docs-update`; `develop` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.1.10 Create hotfix/critical at c1 (not HEAD) · Hard

**Variant ID:** `v21h-hotfix-c1`

**Story**

A group from another section is still running the version 1.0 you handed in at midterm, and they found an order-total bug.

Maeve traces that release to commit `c1`, while `main` has moved well past it with unrelated work. A fix built on today's code wouldn't help the version they actually have.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A release fix may need the code customers actually received. Starting at `c1` keeps later, unrelated `main` changes out of the hotfix.

**Your Task**

Create `hotfix/critical` at the older `c1` commit, __rather than at the current `main` tip__, and finish on that branch.

**Objective Checklist**

- [ ] Create hotfix/critical at commit c1 (not the tip of main).
- [ ] hotfix/critical is checked out.

**Answer Key**

1. `git switch -c hotfix/critical c1`

**Accepted Alternatives**

- `git switch --create hotfix/critical c1`, `git checkout -b hotfix/critical c1`, or two commands: `git branch hotfix/critical c1` then `git switch hotfix/critical` / `git checkout hotfix/critical` (accepted, not CAR-accurate).
- Also accepted: `git branch hotfix/critical c1` then `git switch hotfix/critical` (2 counted commands).

**Expected Result**

`hotfix/critical` points to `c1` and is checked out; `main` did not move.

**Evaluation**

- `hotfix/critical` = c1; HEAD on `hotfix/critical`; `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.1.11 Create saved-work at the detached HEAD position · Hard

**Variant ID:** `v21h-detach-save`

**Story**

While browsing the project's history you checked out an old commit and found a small change you might want later.

Sage glances at your terminal and points out that you aren't on any branch. If you move away now, nothing will remind you where this was.

**Starting point:** `HEAD` is detached at an older commit (you are not on any branch); available local branches: `main`.

**Real-World Context**

When `HEAD` is detached, you are looking at a commit without being on a branch. Naming a branch there gives that position a lasting pointer.

**Your Task**

Create `saved-work` at the commit you are currently viewing and finish on that branch.

**Objective Checklist**

- [ ] Create saved-work at the commit you are viewing.
- [ ] Switch to saved-work.

**Answer Key**

1. `git switch -c saved-work`

**Accepted Alternatives**

- `git switch --create saved-work`, `git checkout -b saved-work`, or two commands: `git branch saved-work` then `git switch saved-work` / `git checkout saved-work` (accepted, not CAR-accurate).
- Also accepted: `git branch saved-work` then `git switch saved-work` (2 counted commands).

**Expected Result**

`saved-work` points to the commit you were viewing and is checked out.

**Evaluation**

- `saved-work` = the detached commit; HEAD attached to `saved-work`.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.1.12 Create feature/workspace from main's tip while on develop · Hard

**Variant ID:** `v21h-from-develop`

**Story**

A maintainer invites you to work on the shared workspace feature. Their project has both `main` and `develop`, and day-to-day work is collected on `develop`, which is where you are standing. This feature, though, is a small patch for the next release, and releases are cut from `main`.

Sage reminds you, “Patches for the release start from the release line, not from whatever you happen to have checked out.”

Both branches exist locally and no workspace branch exists yet. Create `feature/workspace` so that it starts from the latest commit of `main`, and end up working on it.

**Starting point:** You are on `develop`; available local branches: `main`, `develop`.

**Real-World Context**

A new branch starts wherever you tell it to. It does not have to start from the branch you are on, and choosing the right starting point decides which changes your work contains.

**Your Task**

Create `feature/workspace` from the current tip of `main` (__not `develop`__) and switch to it. Finish on `feature/workspace`.

**Objective Checklist**

- [ ] Create feature/workspace from the latest commit of main (develop's extra commits are not included).
- [ ] feature/workspace is checked out.

**Answer Key**

1. `git switch -c feature/workspace main`

**Accepted Alternatives**

- `git switch --create feature/workspace main`, `git checkout -b feature/workspace main`, or two commands: `git branch feature/workspace main` then `git switch feature/workspace` / `git checkout feature/workspace` (accepted, not CAR-accurate).
- Also accepted: `git switch main` then `git switch -c feature/workspace`; `git branch feature/workspace main` then `git switch feature/workspace`.

**Not accepted**

- NOT accepted: creating the branch while on develop with no start point (it would include develop's commits).

**Expected Result**

`feature/workspace` starts at `main`'s tip, without `develop`'s extra commits, and is checked out.

**Evaluation**

- `feature/workspace` = tip of `main`; HEAD on `feature/workspace`; `develop` and `main` unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.1.13 Create review/v1-snapshot at c1, then return to main · Hard

**Variant ID:** `bc-hard-review-snap`

**Story**

You checked out an old version to review how a release behaved, and the review is taking longer than expected. Sage says, “*Give this snapshot a name so we can find it again tomorrow.*”

Your terminal is at that older commit with no active branch. Create `review/v1-snapshot` at the position you are viewing, then go back to `main` for your regular work. The review branch should remain as a pointer to the snapshot.

**Starting point:** You are at a commit without an active branch; available local branches: `main`.

**Real-World Context**

A temporary review branch can mark an older snapshot. You can then return to `main` without losing the convenient name for that commit.

**Your Task**

Create `review/v1-snapshot` at the detached commit you are viewing, then return to `main`.

**Keep the review branch.**

**Objective Checklist**

- [ ] Create review/v1-snapshot at the commit you were viewing (the detached HEAD position).
- [ ] main is checked out and unchanged.

**Answer Key**

1. `git switch -c review/v1-snapshot`
2. `git switch main`

**Accepted Alternatives**

- `git switch --create review/v1-snapshot`, `git checkout -b review/v1-snapshot`, or two commands: `git branch review/v1-snapshot` then `git switch review/v1-snapshot` / `git checkout review/v1-snapshot` (accepted, not CAR-accurate).
- Common patterns that apply: P23.

**Expected Result**

The older commit has a named review branch, and you are back on `main`.

**Evaluation**

- Create or keep branch review/v1-snapshot.
- Finish on main.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.2.1 Create PROJ-418/password-reset · Easy

**Variant ID:** `bn-easy-corp-jira`

**Story**

On your first week, Finn assigns ticket `PROJ-418`: build the password reset flow. You type “password fix” into your notes, and he stops you before that becomes a branch name.

The team’s build system reads names in the form `PROJ-<ticket>/<short-description>` to connect code with tickets. He writes `PROJ-418/password-reset` on the task card. You are on `main`; create that exact branch and move onto it so the build system can recognize your work.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The ticket number in the branch name lets the build system connect the password reset work to its project record.

**Your Task**

Follow the stated naming convention to create `PROJ-418/password-reset` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create PROJ-418/password-reset from the current main commit.
- [ ] PROJ-418/password-reset is checked out.

**Answer Key**

1. `git switch -c PROJ-418/password-reset`

**Accepted Alternatives**

- `git switch --create PROJ-418/password-reset`, `git checkout -b PROJ-418/password-reset`, or two commands: `git branch PROJ-418/password-reset` then `git switch PROJ-418/password-reset` / `git checkout PROJ-418/password-reset` (accepted, not CAR-accurate).

**Expected Result**

`PROJ-418/password-reset` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `PROJ-418/password-reset` = tip of `main`; HEAD on `PROJ-418/password-reset`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.2.2 Create feature/shopping-cart · Easy

**Variant ID:** `bn-easy-startup-feat`

**Story**

Finn walks you through the startup’s task board, where branch names tell everyone what kind of work is in progress. The shopping cart is a new feature, so the team’s `type/short-description` pattern uses `feature/`. “A name people can understand beats `newstuff2`,” he says.

You are on `main` and ready to start the cart. Create `feature/shopping-cart` and switch to it before making the first code change.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The feature/ prefix tells teammates this branch adds a capability, and the readable description identifies the shopping cart.

**Your Task**

Follow the stated naming convention to create `feature/shopping-cart` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create feature/shopping-cart from the current main commit.
- [ ] feature/shopping-cart is checked out.

**Answer Key**

1. `git switch -c feature/shopping-cart`

**Accepted Alternatives**

- `git switch --create feature/shopping-cart`, `git checkout -b feature/shopping-cart`, or two commands: `git branch feature/shopping-cart` then `git switch feature/shopping-cart` / `git checkout feature/shopping-cart` (accepted, not CAR-accurate).

**Expected Result**

`feature/shopping-cart` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `feature/shopping-cart` = tip of `main`; HEAD on `feature/shopping-cart`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.2.3 Create jdelacruz/fix-parser-edge-case · Easy

**Variant ID:** `bn-easy-oss-user`

**Story**

You have found a parser edge case in an open source project and are preparing your first contribution. Several contributors are working at once, so maintainers put a username before each work description. Your username is `jdelacruz`, and the issue is described as `fix-parser-edge-case`.

Finn checks that you are on `main` and asks you to follow the project’s pattern. Create `jdelacruz/fix-parser-edge-case`, then switch to the branch you made.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A contributor prefix helps maintainers see who owns a proposed parser fix when many outside contributions arrive.

**Your Task**

Follow the stated naming convention to create `jdelacruz/fix-parser-edge-case` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create jdelacruz/fix-parser-edge-case from the current main commit.
- [ ] jdelacruz/fix-parser-edge-case is checked out.

**Answer Key**

1. `git switch -c jdelacruz/fix-parser-edge-case`

**Accepted Alternatives**

- `git switch --create jdelacruz/fix-parser-edge-case`, `git checkout -b jdelacruz/fix-parser-edge-case`, or two commands: `git branch jdelacruz/fix-parser-edge-case` then `git switch jdelacruz/fix-parser-edge-case` / `git checkout jdelacruz/fix-parser-edge-case` (accepted, not CAR-accurate).

**Expected Result**

`jdelacruz/fix-parser-edge-case` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `jdelacruz/fix-parser-edge-case` = tip of `main`; HEAD on `jdelacruz/fix-parser-edge-case`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.2.4 Create feature/jm/database-models · Easy

**Variant ID:** `bn-easy-cap-initials`

**Story**

At the capstone meeting, everyone claims a feature and writes their initials beside it. You pick database models, and your initials are `jm`. “That way we can tell whose draft we’re reviewing without asking in the group chat,” Sage says.

Your team agreed on the pattern `feature/<initials>/<work>`. You are on `main`; name your new branch `feature/jm/database-models` and move onto it before editing the models.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The group’s initials convention helps classmates distinguish their database work during parallel development.

**Your Task**

Follow the stated naming convention to create `feature/jm/database-models` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create feature/jm/database-models from the current main commit.
- [ ] feature/jm/database-models is checked out.

**Answer Key**

1. `git switch -c feature/jm/database-models`

**Accepted Alternatives**

- `git switch --create feature/jm/database-models`, `git checkout -b feature/jm/database-models`, or two commands: `git branch feature/jm/database-models` then `git switch feature/jm/database-models` / `git checkout feature/jm/database-models` (accepted, not CAR-accurate).

**Expected Result**

`feature/jm/database-models` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `feature/jm/database-models` = tip of `main`; HEAD on `feature/jm/database-models`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.2.5 Create client/55-contact-form-redesign · Easy

**Variant ID:** `bn-easy-free-client`

**Story**

The client sends you repository access along with ticket 55, a redesign of the contact form. Their project manager is juggling several contractors and wants every branch tied to its ticket. The naming note says `client/<ticket-number>-<description>` and spells out `client/55-contact-form-redesign`.

Finn says, “*Please use that name exactly; it saves the review team a guessing game.*” You are on `main`. Create and switch to the requested branch.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The client’s ticket number keeps the contact form redesign tied to the request it fulfills.

**Your Task**

Follow the stated naming convention to create `client/55-contact-form-redesign` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create client/55-contact-form-redesign from the current main commit.
- [ ] client/55-contact-form-redesign is checked out.

**Answer Key**

1. `git switch -c client/55-contact-form-redesign`

**Accepted Alternatives**

- `git switch --create client/55-contact-form-redesign`, `git checkout -b client/55-contact-form-redesign`, or two commands: `git branch client/55-contact-form-redesign` then `git switch client/55-contact-form-redesign` / `git checkout client/55-contact-form-redesign` (accepted, not CAR-accurate).

**Expected Result**

`client/55-contact-form-redesign` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `client/55-contact-form-redesign` = tip of `main`; HEAD on `client/55-contact-form-redesign`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.2.6 Construct and create PROJ-512/email-notification · Medium

**Variant ID:** `bn-med-corp-notif`

**Story**

A notification email fails to go out in the team’s test environment, and Maeve assigns you `PROJ-512` to build the missing service. The team uses `PROJ-<ticket>/<short-description>`, and this ticket’s description must be `email-notification`. She does not type out the whole name for you: “*You know the pattern.*”

You are on `main`. Put the ticket and description together to make the branch, then switch to it before beginning the service.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A consistent ticket prefix makes the notification branch easy to find beside the issue and its review.

**Your Task**

Follow the stated naming convention to create `PROJ-512/email-notification` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create PROJ-512/email-notification from the current main commit.
- [ ] PROJ-512/email-notification is checked out.

**Answer Key**

1. `git switch -c PROJ-512/email-notification`

**Accepted Alternatives**

- `git switch --create PROJ-512/email-notification`, `git checkout -b PROJ-512/email-notification`, or two commands: `git branch PROJ-512/email-notification` then `git switch PROJ-512/email-notification` / `git checkout PROJ-512/email-notification` (accepted, not CAR-accurate).

**Expected Result**

`PROJ-512/email-notification` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `PROJ-512/email-notification` = tip of `main`; HEAD on `PROJ-512/email-notification`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.2.7 Construct and create bugfix/login-redirect · Medium

**Variant ID:** `bn-med-startup-bugfix`

**Story**

A customer signs in successfully but lands on the wrong page. Finn puts the broken login redirect on your board and reminds you that the team names branches by work type and short description. This is a repair, so use `bugfix`, and the agreed description is `login-redirect`.

You are on `main`, with no branch for the issue yet. Work out the branch name from those pieces, create it, and move there.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A bugfix/ prefix signals that the login redirect is a correction to existing behavior, not a new feature.

**Your Task**

Follow the stated naming convention to create `bugfix/login-redirect` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create bugfix/login-redirect from the current main commit.
- [ ] bugfix/login-redirect is checked out.

**Answer Key**

1. `git switch -c bugfix/login-redirect`

**Accepted Alternatives**

- `git switch --create bugfix/login-redirect`, `git checkout -b bugfix/login-redirect`, or two commands: `git branch bugfix/login-redirect` then `git switch bugfix/login-redirect` / `git checkout bugfix/login-redirect` (accepted, not CAR-accurate).

**Expected Result**

`bugfix/login-redirect` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `bugfix/login-redirect` = tip of `main`; HEAD on `bugfix/login-redirect`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.2.8 Construct and create infra/api-gateway/log-rotation · Medium

**Variant ID:** `bn-med-devops-scope`

**Story**

The API gateway’s logs have grown so large that checking an error takes longer than fixing it. Finn assigns log rotation to you and shows the infrastructure naming pattern: `type/service/short-description`. This job’s pieces are `infra`, `api-gateway`, and `log-rotation`.

You are on `main`. Build the branch name in that order and switch onto it. A reader of the branch list should be able to spot both the service and the kind of work.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

An infrastructure branch with a service scope shows both the type of work and which gateway component it affects.

**Your Task**

Follow the stated naming convention to create `infra/api-gateway/log-rotation` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create infra/api-gateway/log-rotation from the current main commit.
- [ ] infra/api-gateway/log-rotation is checked out.

**Answer Key**

1. `git switch -c infra/api-gateway/log-rotation`

**Accepted Alternatives**

- `git switch --create infra/api-gateway/log-rotation`, `git checkout -b infra/api-gateway/log-rotation`, or two commands: `git branch infra/api-gateway/log-rotation` then `git switch infra/api-gateway/log-rotation` / `git checkout infra/api-gateway/log-rotation` (accepted, not CAR-accurate).

**Expected Result**

`infra/api-gateway/log-rotation` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `infra/api-gateway/log-rotation` = tip of `main`; HEAD on `infra/api-gateway/log-rotation`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.2.9 Infer the convention and create fix/tokenizer-crash · Medium

**Variant ID:** `bn-med-oss-infer`

**Story**

The open source project’s contribution guide has gone missing, but Sage points to the remote branch list: `fix/lexer-null-check`, `fix/parser-overflow`, `feature/dark-mode`, and `feature/keyboard-shortcuts`. You are fixing a crash in the tokenizer, and the agreed short description is `tokenizer-crash`.

“*The other repair branches are giving you a hint,*” Sage says. You are on `main`. Follow their naming pattern to create your own local branch and move onto it.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Existing branches can reveal a project’s naming habit. Matching fix/... makes the tokenizer repair recognizable to maintainers.

**Your Task**

Follow the stated naming convention to create `fix/tokenizer-crash` from the current `main` commit, then switch to it.

**Objective Checklist**

- [ ] Create fix/tokenizer-crash from the current main commit.
- [ ] fix/tokenizer-crash is checked out.

**Answer Key**

1. `git switch -c fix/tokenizer-crash`

**Accepted Alternatives**

- `git switch --create fix/tokenizer-crash`, `git checkout -b fix/tokenizer-crash`, or two commands: `git branch fix/tokenizer-crash` then `git switch fix/tokenizer-crash` / `git checkout fix/tokenizer-crash` (accepted, not CAR-accurate).

**Expected Result**

`fix/tokenizer-crash` exists at `main`'s commit and is checked out.

**Evaluation**

- Branch `fix/tokenizer-crash` = tip of `main`; HEAD on `fix/tokenizer-crash`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.2.10 Replace myFix with fix/renderer-memory-leak · Hard

**Variant ID:** `bn-hard-oss-rename`

**Story**

Finn opens a draft pull request for a memory leak in the renderer and winces at the branch name `myFix`.

The group's convention is that repairs start with `fix/` followed by a short description, and the description here is `renderer-memory-leak`. The wrong name exists only on your laptop, and `main` is where the repair should start from.

**Starting point:** You are on `main`; available local branches: `main`, `myFix`.

**Real-World Context**

A generic name hides the renderer problem. Replacing the incorrect branch name lets checks and reviewers identify the exact fix.

**Your Task**

Remove the incorrectly named local branch `myFix`. Create `fix/renderer-memory-leak` from the current `main` commit and finish on the new branch.

**Objective Checklist**

- [ ] Create fix/renderer-memory-leak from the current main commit.
- [ ] The wrongly named branch myFix no longer exists.
- [ ] fix/renderer-memory-leak is checked out.

**Answer Key**

1. `git branch -d myFix`
2. `git switch -c fix/renderer-memory-leak`

**Accepted Alternatives**

- `git branch --delete myFix`; `git branch -D myFix` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git switch --create fix/renderer-memory-leak`, `git checkout -b fix/renderer-memory-leak`, or two commands: `git branch fix/renderer-memory-leak` then `git switch fix/renderer-memory-leak` / `git checkout fix/renderer-memory-leak` (accepted, not CAR-accurate).
- Rename route: `git branch -m myFix fix/renderer-memory-leak` (also `-M`, `--move`) then `git switch fix/renderer-memory-leak`; accepted only because myFix points to the same commit as main (seed requirement).
- `git branch -D myFix` is accepted (same end state); the feedback should say `-d` is the safe default.
- Common patterns that apply: P30.

**Expected Result**

`myFix` is gone, and `fix/renderer-memory-leak` exists at `main`'s commit and is checked out.

**Evaluation**

- `fix/renderer-memory-leak` = tip of `main`; `myFix` absent; HEAD on `fix/renderer-memory-leak`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.2.11 Replace auth-update with PROJ-301/auth-module-update · Hard

**Variant ID:** `bn-hard-corp-rename`

**Story**

A teammate made `auth-update` for `PROJ-301` before reading the branch rules. Maeve points to the build output: the project expects `PROJ-<ticket>/<description>`, and the description for this task is `auth-module-update`. The old local branch has no commits of its own, so its name can be replaced without losing work.

You are on `main`. Remove `auth-update`, create the correctly named branch from your current position, and move onto it for the review.

**Starting point:** You are on `main`; available local branches: `main`, `auth-update`.

**Real-World Context**

The team’s automated checks expect the ticket ID. Replacing the empty branch is safe here because it has no unique commits.

**Your Task**

Remove the incorrectly named local branch `auth-update`. Create `PROJ-301/auth-module-update` from the current `main` commit and finish on the new branch.

**Objective Checklist**

- [ ] Create PROJ-301/auth-module-update from the current main commit.
- [ ] The wrongly named branch auth-update no longer exists.
- [ ] PROJ-301/auth-module-update is checked out.

**Answer Key**

1. `git branch -d auth-update`
2. `git switch -c PROJ-301/auth-module-update`

**Accepted Alternatives**

- `git branch --delete auth-update`; `git branch -D auth-update` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git switch --create PROJ-301/auth-module-update`, `git checkout -b PROJ-301/auth-module-update`, or two commands: `git branch PROJ-301/auth-module-update` then `git switch PROJ-301/auth-module-update` / `git checkout PROJ-301/auth-module-update` (accepted, not CAR-accurate).
- Rename route: `git branch -m auth-update PROJ-301/auth-module-update` (also `-M`, `--move`) then `git switch PROJ-301/auth-module-update`; accepted only because auth-update points to the same commit as main (seed requirement).
- `git branch -D auth-update` is accepted (same end state); the feedback should say `-d` is the safe default.
- Common patterns that apply: P30.

**Expected Result**

`auth-update` is gone, and `PROJ-301/auth-module-update` exists at `main`'s commit and is checked out.

**Evaluation**

- `PROJ-301/auth-module-update` = tip of `main`; `auth-update` absent; HEAD on `PROJ-301/auth-module-update`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.2.12 Replace fix/cart-total with bugfix/cart-total · Hard

**Variant ID:** `bn-hard-startup-prefix`

**Story**

The cart total is wrong by a few pesos, and someone starts a local branch named `fix/cart-total`. Sage notices that this project reserves `bugfix/` for repairs; `fix/` is not one of its accepted prefixes. “The description is fine; the label at the front is the problem,” she says.

You are on `main`. Remove the incorrectly named local branch, create `bugfix/cart-total` from the current commit, and switch to it.

**Starting point:** You are on `main`; available local branches: `main`, `fix/cart-total`.

**Real-World Context**

Teams sometimes reserve bugfix/ for repairs. Correcting the prefix keeps the cart total branch in the expected category.

**Your Task**

Remove the incorrectly named local branch `fix/cart-total`. Create `bugfix/cart-total` from the current `main` commit and finish on the new branch.

**Objective Checklist**

- [ ] Create bugfix/cart-total from the current main commit.
- [ ] The wrongly named branch fix/cart-total no longer exists.
- [ ] bugfix/cart-total is checked out.

**Answer Key**

1. `git branch -d fix/cart-total`
2. `git switch -c bugfix/cart-total`

**Accepted Alternatives**

- `git branch --delete fix/cart-total`; `git branch -D fix/cart-total` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git switch --create bugfix/cart-total`, `git checkout -b bugfix/cart-total`, or two commands: `git branch bugfix/cart-total` then `git switch bugfix/cart-total` / `git checkout bugfix/cart-total` (accepted, not CAR-accurate).
- Rename route: `git branch -m fix/cart-total bugfix/cart-total` (also `-M`, `--move`) then `git switch bugfix/cart-total`; accepted only because fix/cart-total points to the same commit as main (seed requirement).
- `git branch -D fix/cart-total` is accepted (same end state); the feedback should say `-d` is the safe default.
- Common patterns that apply: P30.

**Expected Result**

`fix/cart-total` is gone, and `bugfix/cart-total` exists at `main`'s commit and is checked out.

**Evaluation**

- `bugfix/cart-total` = tip of `main`; `fix/cart-total` absent; HEAD on `bugfix/cart-total`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.2.13 Replace test/LoginFlow with test/login-flow · Hard

**Variant ID:** `bn-hard-qa-camel`

**Story**

The QA runner is supposed to test a branch for the login flow, but its branch name parser rejects `test/LoginFlow`. Raven finds the rule in the repository README: names must look like `test/<lowercase-hyphenated-description>`. The proper description is `login-flow`.

You are on `main`, and the old local name needs replacing before tests can run. Remove `test/LoginFlow`, create `test/login-flow` from `main`, and move onto the new branch.

**Starting point:** You are on `main`; available local branches: `main`, `test/LoginFlow`.

**Real-World Context**

Consistent lowercase names prevent the QA runner from mistaking the login test branch for a different pattern.

**Your Task**

Remove the incorrectly named local branch `test/LoginFlow`. Create `test/login-flow` from the current `main` commit and finish on the new branch.

**Objective Checklist**

- [ ] Create test/login-flow from the current main commit.
- [ ] The wrongly named branch test/LoginFlow no longer exists.
- [ ] test/login-flow is checked out.

**Answer Key**

1. `git branch -d test/LoginFlow`
2. `git switch -c test/login-flow`

**Accepted Alternatives**

- `git branch --delete test/LoginFlow`; `git branch -D test/LoginFlow` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git switch --create test/login-flow`, `git checkout -b test/login-flow`, or two commands: `git branch test/login-flow` then `git switch test/login-flow` / `git checkout test/login-flow` (accepted, not CAR-accurate).
- Rename route: `git branch -m test/LoginFlow test/login-flow` (also `-M`, `--move`) then `git switch test/login-flow`; accepted only because test/LoginFlow points to the same commit as main (seed requirement).
- `git branch -D test/LoginFlow` is accepted (same end state); the feedback should say `-d` is the safe default.
- Common patterns that apply: P30.

**Expected Result**

`test/LoginFlow` is gone, and `test/login-flow` exists at `main`'s commit and is checked out.

**Evaluation**

- `test/login-flow` = tip of `main`; `test/LoginFlow` absent; HEAD on `test/login-flow`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.3.1 Stash auth work and switch to main · Easy

**Variant ID:** `v23e-auth`

**Story**

You are halfway through changing `src/auth.py` on `feature/auth` when Raven reports that sign-in is broken on `main`. You need to look at `main` right now. **Your edits aren't ready to be a commit, and you don't want to lose them.**

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`, `main`; unfinished edits in `src/auth.py`.

**Real-World Context**

A stash temporarily stores uncommitted edits. It lets you leave the auth changes unfinished while you investigate the urgent report on `main`.

**Your Task**

Save the unfinished edits in a stash, then switch to `main`. Leave the working folder clean; keep the stash for later.

**Objective Checklist**

- [ ] Save your unfinished edits to the stash.
- [ ] main is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git stash`
2. `git switch main`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P14, P23.

**Expected Result**

The unfinished edits are safe in the stash, the requested branch is checked out, and the working folder is clean.

**Evaluation**

- Stash list has 1 entry containing the edits; working tree clean; HEAD on the target branch.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.3.2 Stash notify work and switch to develop · Easy

**Variant ID:** `v23e-notify`

**Story**

Sage asks you to inspect a teammate’s update on `develop` while you are still editing notification templates in `src/notify.py`. The draft on `feature/notify` is useful, just incomplete. Committing it now would make the project history look as though a half-finished feature were ready.

“Park it for ten minutes,” Sage says. Store the current edits temporarily and move to `develop` with a clean working folder; you will be able to return to the draft later.

**Starting point:** You are on `feature/notify`; available local branches: `feature/notify`, `develop`; unfinished edits in `src/notify.py`.

**Real-World Context**

Saving the notification edits in a stash keeps them available when you return from checking `develop`.

**Your Task**

Save the unfinished edits in a stash, then switch to `develop`. Leave the working folder clean; keep the stash for later.

**Objective Checklist**

- [ ] Save your unfinished edits to the stash.
- [ ] develop is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git stash`
2. `git switch develop`

**Accepted Alternatives**

- `git checkout develop`.
- Common patterns that apply: P14.

**Expected Result**

The unfinished edits are safe in the stash, the requested branch is checked out, and the working folder is clean.

**Evaluation**

- Stash list has 1 entry containing the edits; working tree clean; HEAD on the target branch.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.3.3 Stash cache work and switch to release/v2 · Easy

**Variant ID:** `v23e-cache`

**Story**

A production alert arrives while you are in the middle of a cache refactor. You have uncommitted changes in `src/cache.py` on `feature/cache`, and Raven wants you to look at the code on `release/v2`. “We can come back to your refactor,” she says, “but first let’s see what shipped.”

The unfinished edits should not follow you into the release branch. Save them temporarily, then switch to `release/v2` with clean working files.

**Starting point:** You are on `feature/cache`; available local branches: `feature/cache`, `release/v2`; unfinished edits in `src/cache.py`.

**Real-World Context**

The cache refactor is not ready for a commit. Stashing it leaves a clean working folder for checking `release/v2`.

**Your Task**

Save the unfinished edits in a stash, then switch to `release/v2`. Leave the working folder clean; keep the stash for later.

**Objective Checklist**

- [ ] Save your unfinished edits to the stash.
- [ ] release/v2 is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git stash`
2. `git switch release/v2`

**Accepted Alternatives**

- `git checkout release/v2`.
- Common patterns that apply: P14.

**Expected Result**

The unfinished edits are safe in the stash, the requested branch is checked out, and the working folder is clean.

**Evaluation**

- Stash list has 1 entry containing the edits; working tree clean; HEAD on the target branch.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.3.4 Stash models work and switch to review/groupmate-branch · Easy

**Variant ID:** `stash-easy-cap-review`

**Story**

Your capstone groupmate pings you with a request to review her branch before class. You are editing `src/models.py` on `feature/models`, with half the fields still to add. Sage looks at the unfinished file and says, “Keep that draft; just make room to review hers.”

The review branch `review/groupmate-branch` already exists. Store your model edits temporarily, switch there, and leave your working folder clean for the review.

**Starting point:** You are on `feature/models`; available local branches: `feature/models`, `review/groupmate-branch`; unfinished edits in `src/models.py`.

**Real-World Context**

A groupmate’s review can happen before your model edits are finished; the stash keeps those edits out of the review branch.

**Your Task**

Save the unfinished edits in a stash, then switch to `review/groupmate-branch`. Leave the working folder clean; keep the stash for later.

**Objective Checklist**

- [ ] Save your unfinished edits to the stash.
- [ ] review/groupmate-branch is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git stash`
2. `git switch review/groupmate-branch`

**Accepted Alternatives**

- `git checkout review/groupmate-branch`.
- Common patterns that apply: P14.

**Expected Result**

The unfinished edits are safe in the stash, the requested branch is checked out, and the working folder is clean.

**Evaluation**

- Stash list has 1 entry containing the edits; working tree clean; HEAD on the target branch.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.3.5 Stash docs work and switch to release/stable · Easy

**Variant ID:** `stash-easy-docs-switch`

**Story**

You have been updating `docs/api-reference.md` on `feature/api-docs` when a broken link is reported in the stable release. Finn wants you to check `release/stable` now, before more readers hit the problem. The documentation edits on your feature branch are still unfinished.

“No need to publish a half-written guide just to change rooms,” he says. Save your draft temporarily and move to the existing release branch with clean working files.

**Starting point:** You are on `feature/api-docs`; available local branches: `feature/api-docs`, `release/stable`; unfinished edits in `docs/api-reference.md`.

**Real-World Context**

Documentation edits can wait in a stash while you switch to the stable release for an urgent correction.

**Your Task**

Save the unfinished edits in a stash, then switch to `release/stable`. Leave the working folder clean; keep the stash for later.

**Objective Checklist**

- [ ] Save your unfinished edits to the stash.
- [ ] release/stable is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git stash`
2. `git switch release/stable`

**Accepted Alternatives**

- `git checkout release/stable`.
- Common patterns that apply: P14.

**Expected Result**

The unfinished edits are safe in the stash, the requested branch is checked out, and the working folder is clean.

**Evaluation**

- Stash list has 1 entry containing the edits; working tree clean; HEAD on the target branch.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.3.6 Stash payments work, check main, restore · Medium

**Variant ID:** `v23m-to-main`

**Story**

Finn asks you to check a teammate’s commit on `main`, but your `feature/payments` branch has unfinished edits in `src/payments.py`. You will be back in a few minutes, so a permanent commit would be premature.

“Put the draft on a shelf, check the commit, then pick it up again,” he says. Save the edits, visit `main`, return to `feature/payments`, and restore the draft to your working folder so you can continue where you stopped.

**Starting point:** You are on `feature/payments`; available local branches: `feature/payments`, `main`; unfinished edits in `src/payments.py`.

**Real-World Context**

A stash temporarily stores uncommitted edits. Restoring it after you come back puts the saved edits back in your working folder and removes that stash entry.

**Your Task**

Stash the unfinished edits, visit `main`, return to `feature/payments`, and restore the edits to the working folder. Finish on `feature/payments`.

**Objective Checklist**

- [ ] Restore your stashed edits to the working folder on feature/payments.
- [ ] The stash is empty again (the entry was removed when restored).
- [ ] feature/payments is checked out.

**Answer Key**

1. `git stash`
2. `git switch main`
3. `git switch feature/payments`
4. `git stash pop`

**Accepted Alternatives**

- `git checkout feature/payments`.
- Common patterns that apply: P14, P23, P24.

**Expected Result**

The edits are back in your working folder where you left them, and the stash is empty.

**Evaluation**

- HEAD on `feature/payments`; working tree has the original edits; stash list empty.
- Minimum counted commands: 4 · Maximum counted commands: 10

---

### 2.3.7 Stash orders work, check hotfix, restore · Medium

**Variant ID:** `v23m-to-hotfix`

**Story**

A tax calculation on the hotfix branch needs a second pair of eyes. Sage asks you to look, but you are in the middle of `src/orders.py` on `feature/orders`. The orders changes are worth keeping and are not ready to publish.

Save them temporarily before visiting `hotfix/fix-tax`; otherwise your draft could get in the way of the branch switch. When the check is done, return to `feature/orders` and put the edits back in your working folder.

**Starting point:** You are on `feature/orders`; available local branches: `feature/orders`, `hotfix/fix-tax`; unfinished edits in `src/orders.py`.

**Real-World Context**

Keeping the order changes in a stash prevents unfinished work from mixing with the tax hotfix branch.

**Your Task**

Stash the unfinished edits, visit `hotfix/fix-tax`, return to `feature/orders`, and restore the edits to the working folder. Finish on `feature/orders`.

**Objective Checklist**

- [ ] Restore your stashed edits to the working folder on feature/orders.
- [ ] The stash is empty again (the entry was removed when restored).
- [ ] feature/orders is checked out.

**Answer Key**

1. `git stash`
2. `git switch hotfix/fix-tax`
3. `git switch feature/orders`
4. `git stash pop`

**Accepted Alternatives**

- `git checkout hotfix/fix-tax`.
- `git checkout feature/orders`.
- Common patterns that apply: P14, P24.

**Expected Result**

The edits are back in your working folder where you left them, and the stash is empty.

**Evaluation**

- HEAD on `feature/orders`; working tree has the original edits; stash list empty.
- Minimum counted commands: 4 · Maximum counted commands: 10

---

### 2.3.8 Stash analytics work, check release/v2, restore · Medium

**Variant ID:** `v23m-to-release`

**Story**

The release manager wants a quick look at `release/v2` before sending it out. You are working on `src/analytics.py` in `feature/analytics`, and the latest edits have not been committed.

Raven says, “The release check is short; don’t package your draft as a commit for my sake.” Store those edits temporarily, visit the release branch, then return to your feature branch and restore them. The analytics work should be waiting where you left it.

**Starting point:** You are on `feature/analytics`; available local branches: `feature/analytics`, `release/v2`; unfinished edits in `src/analytics.py`.

**Real-World Context**

A short release check should not require a premature analytics commit; stash and restore the edits around the visit.

**Your Task**

Stash the unfinished edits, visit `release/v2`, return to `feature/analytics`, and restore the edits to the working folder. Finish on `feature/analytics`.

**Objective Checklist**

- [ ] Restore your stashed edits to the working folder on feature/analytics.
- [ ] The stash is empty again (the entry was removed when restored).
- [ ] feature/analytics is checked out.

**Answer Key**

1. `git stash`
2. `git switch release/v2`
3. `git switch feature/analytics`
4. `git stash pop`

**Accepted Alternatives**

- `git checkout release/v2`.
- `git checkout feature/analytics`.
- Common patterns that apply: P14, P24.

**Expected Result**

The edits are back in your working folder where you left them, and the stash is empty.

**Evaluation**

- HEAD on `feature/analytics`; working tree has the original edits; stash list empty.
- Minimum counted commands: 4 · Maximum counted commands: 10

---

### 2.3.9 Stash billing work, check hotfix/tax-fix, restore · Medium

**Variant ID:** `stash-med-corp-named`

**Story**

Sage asks you to check `hotfix/tax-fix` while you're editing `src/billing.py` on `feature/billing`.

The billing draft is too early to commit, and you aren't sure whether it would follow you to the other branch or block the switch. Either way, **you'll want it back exactly as it is when the check is done**.

**Starting point:** You are on `feature/billing`; available local branches: `feature/billing`, `hotfix/tax-fix`; unfinished edits in `src/billing.py`.

**Real-World Context**

The billing draft can wait while you inspect the tax fix. Restoring the stash after returning to `feature/billing` puts those edits back where you were working.

**Your Task**

Stash the unfinished edits, visit `hotfix/tax-fix`, return to `feature/billing`, and restore the edits to the working folder. Finish on `feature/billing`.

**Objective Checklist**

- [ ] Restore your stashed edits to the working folder on feature/billing.
- [ ] The stash is empty again (the entry was removed when restored).
- [ ] feature/billing is checked out.

**Answer Key**

1. `git stash`
2. `git switch hotfix/tax-fix`
3. `git switch feature/billing`
4. `git stash pop`

**Accepted Alternatives**

- `git checkout hotfix/tax-fix`.
- `git checkout feature/billing`.
- Common patterns that apply: P14, P24.

**Expected Result**

The edits are back in your working folder where you left them, and the stash is empty.

**Evaluation**

- HEAD on `feature/billing`; working tree has the original edits; stash list empty.
- Minimum counted commands: 4 · Maximum counted commands: 10

---

### 2.3.10 Check main while the auth rework is cancelled · Hard

**Variant ID:** `v23h-dropped-auth`

**Story**

You are experimenting with an auth redesign in `src/auth.py` on `feature/auth-rework` when a production issue pulls you over to `main`. The redesign is unfinished, and you would rather not commit it.

While you are looking at `main`, the team meets and decides the redesign is headed in the wrong direction. Finn says, “Good thing we hadn’t made that draft permanent.”

By the time you are back on your own branch, nothing of that draft should be left anywhere in the repository, and it must not have followed you onto `main` on the way.

**Starting point:** You are on `feature/auth-rework`; available local branches: `feature/auth-rework`, `main`; unfinished edits in `src/auth.py`.

**Real-World Context**

Unfinished edits can follow you between branches or wait on a shelf. When a draft is cancelled, the shelved copy has to go too, or it will resurface later.

**Your Task**

Check `main` without carrying your unfinished edits along, then return to `feature/auth-rework`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Objective Checklist**

- [ ] feature/auth-rework is checked out.
- [ ] The working folder is clean (the cancelled draft is not restored).
- [ ] The stash is empty: the cancelled draft is gone for good.

**Answer Key**

1. `git stash`
2. `git switch main`
3. `git switch feature/auth-rework`
4. `git stash drop`

**Accepted Alternatives**

- `git checkout feature/auth-rework`.
- Common patterns that apply: P14, P23, P39, P40.

**Expected Result**

The cancelled draft is gone from both the working folder and the stash, and you are back on the original branch.

**Evaluation**

- HEAD on `feature/auth-rework`; working tree clean; stash list empty.
- Process: the learner must have visited the other branch (reflog/HEAD history shows it) before returning.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.3.11 Check hotfix/urgent while the api-v2 draft is cancelled · Hard

**Variant ID:** `v23h-dropped-api`

**Story**

Your unfinished `src/api_v2.py` draft sits on `feature/api-v2` when Finn asks you to inspect `hotfix/urgent`. You do not want to commit the draft, and you do not want it tangled up with the hotfix.

During the visit, the team agrees on a new API design that makes the old draft obsolete. “No reason to put it back,” Finn says. When you are back on `feature/api-v2`, the old draft should be completely gone.

**Starting point:** You are on `feature/api-v2`; available local branches: `feature/api-v2`, `hotfix/urgent`; unfinished edits in `src/api_v2.py`.

**Real-World Context**

When a design changes, the old draft should not be left behind in a hidden place where it can be restored by accident.

**Your Task**

Check `hotfix/urgent` without carrying your unfinished edits along, then return to `feature/api-v2`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Objective Checklist**

- [ ] feature/api-v2 is checked out.
- [ ] The working folder is clean (the cancelled draft is not restored).
- [ ] The stash is empty: the cancelled draft is gone for good.

**Answer Key**

1. `git stash`
2. `git switch hotfix/urgent`
3. `git switch feature/api-v2`
4. `git stash drop`

**Accepted Alternatives**

- `git checkout hotfix/urgent`.
- `git checkout feature/api-v2`.
- Common patterns that apply: P14, P39, P40.

**Expected Result**

The cancelled draft is gone from both the working folder and the stash, and you are back on the original branch.

**Evaluation**

- HEAD on `feature/api-v2`; working tree clean; stash list empty.
- Process: the learner must have visited the other branch (reflog/HEAD history shows it) before returning.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.3.12 Check release/v1 while the refactor is cancelled · Hard

**Variant ID:** `v23h-dropped-refactor`

**Story**

The refactor in `src/core.py` is half written when Finn asks you to check `release/v1`. You are on `feature/refactor` and would rather not commit unfinished work. During that visit, the team decides to pursue a different design entirely, and your old draft becomes a dead end.

Back on `feature/refactor`, nothing of the cancelled refactor should come back, neither in your folder nor anywhere Git is keeping it.

**Starting point:** You are on `feature/refactor`; available local branches: `feature/refactor`, `release/v1`; unfinished edits in `src/core.py`.

**Real-World Context**

Once the team cancels the refactor, every saved copy of that abandoned draft should be removed, or it will resurface later.

**Your Task**

Check `release/v1` without carrying your unfinished edits along, then return to `feature/refactor`. The team has cancelled this work, so finish with a clean working folder and no saved copy of the draft left in the stash.

**Objective Checklist**

- [ ] feature/refactor is checked out.
- [ ] The working folder is clean (the cancelled draft is not restored).
- [ ] The stash is empty: the cancelled draft is gone for good.

**Answer Key**

1. `git stash`
2. `git switch release/v1`
3. `git switch feature/refactor`
4. `git stash drop`

**Accepted Alternatives**

- `git checkout release/v1`.
- `git checkout feature/refactor`.
- Common patterns that apply: P14, P39, P40.

**Expected Result**

The cancelled draft is gone from both the working folder and the stash, and you are back on the original branch.

**Evaluation**

- HEAD on `feature/refactor`; working tree clean; stash list empty.
- Process: the learner must have visited the other branch (reflog/HEAD history shows it) before returning.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.3.13 Discard one abandoned stash and restore the other · Hard

**Variant ID:** `stash-hard-oss-multi`

**Story**

Over the week you've parked two drafts while working on `feature/lexer`. The newest is an experiment you've abandoned.

**The older one holds the lexer work you actually need.** Sage warns you that clearing the whole shelf would take the good one with it.

**Starting point:** You are on `feature/lexer`; available local branches: `feature/lexer`; two stash entries exist.

**Real-World Context**

Stash entries are numbered newest first. Dropping `stash@{0}` makes the formerly older entry the one that pop restores.

**Your Task**

Discard __only__ the abandoned newest stash entry. Restore the remaining older stash to your working files and finish on `feature/lexer`.

**Objective Checklist**

- [ ] Only the newest stash entry was discarded.
- [ ] Restore the older stash's edits to the working folder.
- [ ] The stash list is empty.
- [ ] feature/lexer is checked out.

**Answer Key**

1. `git stash drop stash@{0}`
2. `git stash pop`

**Accepted Alternatives**

- `git stash pop stash@{1}` then `git stash drop` is accepted (restore the older one first, then drop the experiment) provided the final working files and empty stash match.
- Common patterns that apply: P24.

**Not accepted**

- Only the named entry may be removed; `git stash clear` is NOT accepted (it would also delete the entry that must survive).
- `git stash clear` is NOT accepted: it would delete the useful entry.

**Expected Result**

The abandoned stash is gone and the useful older edits are restored on `feature/lexer`.

**Evaluation**

- Stash list empty; working tree contains the older stash's edits (not the abandoned experiment's); HEAD on `feature/lexer`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.4.1 Push feature/auth to origin · Easy

**Variant ID:** `v24e-auth`

**Story**

The authentication feature finally passes its local checks. Finn is preparing a review and asks for a link to the branch, but all of your commits are still on your own machine. “I can’t review what I can’t see,” he says with a grin.

Your local branch is `feature/auth`, and the shared remote is named `origin`. Publish that branch so the team can inspect the committed work without putting it on `main` yet.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`, `main`; `origin` is available.

**Real-World Context**

A local commit exists only in your repository until it is pushed. Publishing the auth branch makes its commits available for review.

**Your Task**

Publish the committed local `feature/auth` to `origin` for teammates to access.

**Objective Checklist**

- [ ] Publish feature/auth to origin.
- [ ] The local branch feature/auth still exists and retains its commits.

**Answer Key**

1. `git push origin feature/auth`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P31.

**Expected Result**

`origin/feature/auth` exists and contains your committed work. Teammates can fetch it.

**Evaluation**

- Remote `origin` has `feature/auth` at the same commit as local `feature/auth`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.4.2 Push feature/orders to origin · Easy

**Variant ID:** `v24e-orders`

**Story**

Maeve is ready to test the orders feature on her laptop. You finished it on `feature/orders`, but so far that branch exists only in your local repository. She searches the team’s shared repository and finds nothing.

“Send it up when you’re ready,” she says. The remote is `origin`, and your changes have already been committed. Publish `feature/orders` there so Maeve can get the branch and run her tests.

**Starting point:** You are on `feature/orders`; available local branches: `feature/orders`, `main`; `origin` is available.

**Real-World Context**

Pushing the orders branch sends its committed changes to the shared repository so another developer can use them.

**Your Task**

Publish the committed local `feature/orders` to `origin` for teammates to access.

**Objective Checklist**

- [ ] Publish feature/orders to origin.
- [ ] The local branch feature/orders still exists and retains its commits.

**Answer Key**

1. `git push origin feature/orders`

**Accepted Alternatives**

- `git push origin feature/orders:feature/orders`, `git push origin refs/heads/feature/orders`; bare `git push` only when an upstream is already set.

**Expected Result**

`origin/feature/orders` exists and contains your committed work. Teammates can fetch it.

**Evaluation**

- Remote `origin` has `feature/orders` at the same commit as local `feature/orders`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.4.3 Push feature/parser to origin · Easy

**Variant ID:** `v24e-parser`

**Story**

A parser fix works on your machine, and Sage wants another developer to try the edge case that failed earlier. You have committed the fix on your local `feature/parser` branch, but it has not reached the team’s shared repository.

Sage points to the remote named `origin`: “That’s where reviewers will find it.” Push the branch there so someone else can inspect the fix before it is merged.

**Starting point:** You are on `feature/parser`; available local branches: `feature/parser`, `main`; `origin` is available.

**Real-World Context**

Publishing the parser branch gives reviewers access to the fix without merging it into `main` yet.

**Your Task**

Publish the committed local `feature/parser` to `origin` for teammates to access.

**Objective Checklist**

- [ ] Publish feature/parser to origin.
- [ ] The local branch feature/parser still exists and retains its commits.

**Answer Key**

1. `git push origin feature/parser`

**Accepted Alternatives**

- `git push origin feature/parser:feature/parser`, `git push origin refs/heads/feature/parser`; bare `git push` only when an upstream is already set.

**Expected Result**

`origin/feature/parser` exists and contains your committed work. Teammates can fetch it.

**Evaluation**

- Remote `origin` has `feature/parser` at the same commit as local `feature/parser`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.4.4 Push feature/user-auth to origin · Easy

**Variant ID:** `push-easy-cap-auth`

**Story**

Your capstone group’s authentication work is done on `feature/user-auth`. In the group chat, one classmate asks to test the sign-in screen and another asks whether the commits are available yet.

Raven checks the shared repository: your branch is still only local. `origin` is already configured. Publish the branch so your groupmates can fetch it; this request does not require setting up upstream tracking.

**Starting point:** You are on `feature/user-auth`; available local branches: `feature/user-auth`, `main`; `origin` is available.

**Real-World Context**

Groupmates can fetch a pushed authentication branch to test it on their own machines.

**Your Task**

Publish the committed local `feature/user-auth` to `origin` for teammates to access.

**Objective Checklist**

- [ ] Publish feature/user-auth to origin.
- [ ] The local branch feature/user-auth still exists and retains its commits.

**Answer Key**

1. `git push origin feature/user-auth`

**Accepted Alternatives**

- `git push origin feature/user-auth:feature/user-auth`, `git push origin refs/heads/feature/user-auth`; bare `git push` only when an upstream is already set.

**Expected Result**

`origin/feature/user-auth` exists and contains your committed work. Teammates can fetch it.

**Evaluation**

- Remote `origin` has `feature/user-auth` at the same commit as local `feature/user-auth`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.4.5 Push feature/client-landing to origin · Easy

**Variant ID:** `push-easy-free-landing`

**Story**

The client wants to review the landing page before you continue polishing it. You have finished and committed the draft on `feature/client-landing`, but a screenshot would not let the client inspect the code.

Sage says, “Put your branch in the client’s repository and I’ll send them the review link.” Their repository is configured as `origin`. Publish the branch there; no upstream setup is requested for this handoff.

**Starting point:** You are on `feature/client-landing`; available local branches: `feature/client-landing`, `main`; `origin` is available.

**Real-World Context**

The client needs a remote branch to inspect the landing page work before accepting it.

**Your Task**

Publish the committed local `feature/client-landing` to `origin` for teammates to access.

**Objective Checklist**

- [ ] Publish feature/client-landing to origin.
- [ ] The local branch feature/client-landing still exists and retains its commits.

**Answer Key**

1. `git push origin feature/client-landing`

**Accepted Alternatives**

- `git push origin feature/client-landing:feature/client-landing`, `git push origin refs/heads/feature/client-landing`; bare `git push` only when an upstream is already set.

**Expected Result**

`origin/feature/client-landing` exists and contains your committed work. Teammates can fetch it.

**Evaluation**

- Remote `origin` has `feature/client-landing` at the same commit as local `feature/client-landing`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.4.6 Push feature/auth and set its upstream · Medium

**Variant ID:** `v24m-auth`

**Story**

Finn has reviewed the first auth draft and expects several more rounds of edits. Your local branch is `feature/auth`, and its remote copy needs to be created on `origin`.

“You’ll push again tomorrow,” he says, “so let Git remember where this branch belongs.” Publish the branch and set its remote counterpart as the upstream. After that, future sync commands can use the saved connection instead of spelling out both names each time.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`, `main`; `origin` is available.

**Real-World Context**

An upstream is the remote branch your local branch follows. Setting it on the first push makes later pushes and pulls shorter.

**Your Task**

Publish `feature/auth` to `origin` and set the corresponding remote branch as its upstream.

**Objective Checklist**

- [ ] Publish feature/auth to origin.
- [ ] Local feature/auth tracks origin/feature/auth (upstream is set).

**Answer Key**

1. `git push -u origin feature/auth`

**Accepted Alternatives**

- `git push --set-upstream origin feature/auth`; or `git push origin feature/auth` then `git branch -u origin/feature/auth` / `git branch --set-upstream-to=origin/feature/auth` (accepted, not CAR-accurate).

**Expected Result**

`origin/feature/auth` exists, and your local `feature/auth` is linked to it so later pushes and pulls need no extra names.

**Evaluation**

- Remote `origin` has `feature/auth` = local; `feature/auth`'s upstream = `origin/feature/auth`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.4.7 Push feature/orders and set its upstream · Medium

**Variant ID:** `v24m-orders`

**Story**

The orders feature is ready for its first shared review, but Maeve knows more commits will follow. Your local `feature/orders` branch has no remote counterpart yet. She asks you to publish it and link it to the matching branch on `origin` so later updates are easier to send.

“One setup step now saves us typing that long name all week,” she says. Push the branch and set upstream tracking at the same time.

**Starting point:** You are on `feature/orders`; available local branches: `feature/orders`, `main`; `origin` is available.

**Real-World Context**

Tracking `origin/feature/orders` ties future sync commands to the right remote branch.

**Your Task**

Publish `feature/orders` to `origin` and set the corresponding remote branch as its upstream.

**Objective Checklist**

- [ ] Publish feature/orders to origin.
- [ ] Local feature/orders tracks origin/feature/orders (upstream is set).

**Answer Key**

1. `git push -u origin feature/orders`

**Accepted Alternatives**

- `git push --set-upstream origin feature/orders`; or `git push origin feature/orders` then `git branch -u origin/feature/orders` / `git branch --set-upstream-to=origin/feature/orders` (accepted, not CAR-accurate).

**Expected Result**

`origin/feature/orders` exists, and your local `feature/orders` is linked to it so later pushes and pulls need no extra names.

**Evaluation**

- Remote `origin` has `feature/orders` = local; `feature/orders`'s upstream = `origin/feature/orders`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.4.8 Push feature/parser and set its upstream · Medium

**Variant ID:** `v24m-parser`

**Story**

Sage is reviewing a parser change that will probably need one more round of edge-case tests. You are on the local `feature/parser` branch, and the remote named `origin` is ready. Publishing it once is useful; remembering its remote counterpart is even more useful when you make the next fix.

Sage asks you to do both in this first push. Send the branch to `origin` and set its upstream.

**Starting point:** You are on `feature/parser`; available local branches: `feature/parser`, `main`; `origin` is available.

**Real-World Context**

Publishing and setting an upstream in one step makes later parser updates easier to share.

**Your Task**

Publish `feature/parser` to `origin` and set the corresponding remote branch as its upstream.

**Objective Checklist**

- [ ] Publish feature/parser to origin.
- [ ] Local feature/parser tracks origin/feature/parser (upstream is set).

**Answer Key**

1. `git push -u origin feature/parser`

**Accepted Alternatives**

- `git push --set-upstream origin feature/parser`; or `git push origin feature/parser` then `git branch -u origin/feature/parser` / `git branch --set-upstream-to=origin/feature/parser` (accepted, not CAR-accurate).

**Expected Result**

`origin/feature/parser` exists, and your local `feature/parser` is linked to it so later pushes and pulls need no extra names.

**Evaluation**

- Remote `origin` has `feature/parser` = local; `feature/parser`'s upstream = `origin/feature/parser`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.4.9 Push feature/v2-migration-guide and set its upstream · Medium

**Variant ID:** `push-med-docs-track`

**Story**

The migration guide for version 2 is nearly drafted, and the documentation team wants to start leaving comments today. `feature/v2-migration-guide` exists only on your laptop, and you'll be pushing updates to it all week. Raven would like your pushes and pulls to just work without typing out the full branch name every time.

**Starting point:** You are on `feature/v2-migration-guide`; available local branches: `feature/v2-migration-guide`, `main`; `origin` is available.

**Real-World Context**

The documentation branch will need more edits. Upstream tracking avoids typing its long name on each later push.

**Your Task**

Publish `feature/v2-migration-guide` to `origin` and set the corresponding remote branch as its upstream.

**Objective Checklist**

- [ ] Publish feature/v2-migration-guide to origin.
- [ ] Local feature/v2-migration-guide tracks origin/feature/v2-migration-guide (upstream is set).

**Answer Key**

1. `git push -u origin feature/v2-migration-guide`

**Accepted Alternatives**

- `git push --set-upstream origin feature/v2-migration-guide`; or `git push origin feature/v2-migration-guide` then `git branch -u origin/feature/v2-migration-guide` / `git branch --set-upstream-to=origin/feature/v2-migration-guide` (accepted, not CAR-accurate).

**Expected Result**

`origin/feature/v2-migration-guide` exists, and your local `feature/v2-migration-guide` is linked to it so later pushes and pulls need no extra names.

**Evaluation**

- Remote `origin` has `feature/v2-migration-guide` = local; `feature/v2-migration-guide`'s upstream = `origin/feature/v2-migration-guide`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.4.10 Publish rewritten feature/auth without overwriting a teammate's work · Hard

**Variant ID:** `v24h-auth`

**Story**

Finn asks you to tidy the auth feature history before opening a pull request. After the cleanup, your local commits have new IDs, while `origin/feature/auth` still points to the older version, so a normal push is rejected.

“Make sure nobody published something new while you were rewriting,” he says. “I don’t want to erase a teammate’s work by accident.” You are on `feature/auth`.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`, `main`; `origin` is available. Your local `feature/auth` history was rewritten; `origin/feature/auth` still has the older commits.

**Real-World Context**

After history is rewritten, an ordinary push is rejected because the remote still holds the old commits. A guarded forced update replaces the remote branch only if nobody has added to it since you last looked, so a teammate's newer work is never wiped out.

**Your Task**

Update `origin/feature/auth` so it matches your rewritten local `feature/auth`. The update must be refused if the remote branch has commits you have not seen.

**Do not use an unconditional force.**

**Objective Checklist**

- [ ] origin/feature/auth now has your rewritten history.
- [ ] The force push used --force-with-lease, not plain --force (command-history check).
- [ ] feature/auth is still the current branch.

**Answer Key**

1. `git push --force-with-lease origin feature/auth`

**Accepted Alternatives**

- Only the common patterns below apply.

**Not accepted**

- `git push origin feature/auth --force-with-lease`, `--force-with-lease=feature/auth`, `--force-with-lease=feature/auth:<expected-commit>`. NOT accepted: `-f`, `--force`, `+feature/auth` (unconditional overwrite).

**Expected Result**

`origin/feature/auth` matches your rewritten local branch, and the update was guarded against overwriting newer remote work.

**Evaluation**

- `origin/feature/auth` = local `feature/auth`; the push command contained a lease option, not a bare force (`-f`/`--force`/`+ref` fail with a hint about teammates' work).
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.4.11 Publish rewritten feature/orders without overwriting a teammate's work · Hard

**Variant ID:** `v24h-orders`

**Story**

The orders branch has accumulated several tiny correction commits. Sage helps you squash them into a cleaner history, but `origin/feature/orders` still has the old commits, and your next ordinary push fails because the histories no longer line up.

“We can replace our old version,” she says, “as long as no one else has added to it meanwhile.” You are on `feature/orders`.

**Starting point:** You are on `feature/orders`; available local branches: `feature/orders`, `main`; `origin` is available. Your local `feature/orders` history was rewritten; `origin/feature/orders` still has the older commits.

**Real-World Context**

After history is rewritten, an ordinary push is rejected because the remote still holds the old commits. A guarded forced update replaces the remote branch only if nobody has added to it since you last looked, so a teammate's newer work is never wiped out.

**Your Task**

Update `origin/feature/orders` so it matches your rewritten local `feature/orders`. The update must be refused if the remote branch has commits you have not seen.

**Do not use an unconditional force.**

**Objective Checklist**

- [ ] origin/feature/orders now has your rewritten history.
- [ ] The force push used --force-with-lease, not plain --force (command-history check).
- [ ] feature/orders is still the current branch.

**Answer Key**

1. `git push --force-with-lease origin feature/orders`

**Accepted Alternatives**

- Only the common patterns below apply.

**Not accepted**

- `git push origin feature/orders --force-with-lease`, `--force-with-lease=feature/orders`, `--force-with-lease=feature/orders:<expected-commit>`. NOT accepted: `-f`, `--force`, `+feature/orders` (unconditional overwrite).

**Expected Result**

`origin/feature/orders` matches your rewritten local branch, and the update was guarded against overwriting newer remote work.

**Evaluation**

- `origin/feature/orders` = local `feature/orders`; the push command contained a lease option, not a bare force (`-f`/`--force`/`+ref` fail with a hint about teammates' work).
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.4.12 Publish rewritten feature/parser without overwriting a teammate's work · Hard

**Variant ID:** `v24h-parser`

**Story**

Your parser pull request is almost ready after Maeve helped you squash the draft commits.

The remote copy of `feature/parser` now disagrees with your local one about its commit IDs, and Git won’t take an ordinary push. Another developer sometimes pushes to the same branch, and **you don’t want to wipe out anything of theirs**.

**Starting point:** You are on `feature/parser`; available local branches: `feature/parser`, `main`; `origin` is available. Your local `feature/parser` history was rewritten; `origin/feature/parser` still has the older commits.

**Real-World Context**

After history is rewritten, an ordinary push is rejected because the remote still holds the old commits. A guarded forced update replaces the remote branch only if nobody has added to it since you last looked, so a teammate's newer work is never wiped out.

**Your Task**

Update `origin/feature/parser` so it matches your rewritten local `feature/parser`. The update must be refused if the remote branch has commits you have not seen.

**Do not use an unconditional force.**

**Objective Checklist**

- [ ] origin/feature/parser now has your rewritten history.
- [ ] The force push used --force-with-lease, not plain --force (command-history check).
- [ ] feature/parser is still the current branch.

**Answer Key**

1. `git push --force-with-lease origin feature/parser`

**Accepted Alternatives**

- Only the common patterns below apply.

**Not accepted**

- `git push origin feature/parser --force-with-lease`, `--force-with-lease=feature/parser`, `--force-with-lease=feature/parser:<expected-commit>`. NOT accepted: `-f`, `--force`, `+feature/parser` (unconditional overwrite).

**Expected Result**

`origin/feature/parser` matches your rewritten local branch, and the update was guarded against overwriting newer remote work.

**Evaluation**

- `origin/feature/parser` = local `feature/parser`; the push command contained a lease option, not a bare force (`-f`/`--force`/`+ref` fail with a hint about teammates' work).
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.4.13 Publish rewritten feature/pipeline-config without overwriting a teammate's work · Hard

**Variant ID:** `push-hard-devops-fwl`

**Story**

The CI team asks you to remove debug commits from `feature/pipeline-config` before review. You clean the branch locally, and the new history looks tidy, but `origin` still has the older chain of commits and a normal push is rejected.

Sage says, “I want the cleaner branch up there, but I also want to know if somebody touched the remote while we worked.”

**Starting point:** You are on `feature/pipeline-config`; available local branches: `feature/pipeline-config`, `main`; `origin` is available. Your local `feature/pipeline-config` history was rewritten; `origin/feature/pipeline-config` still has the older commits.

**Real-World Context**

After history is rewritten, an ordinary push is rejected because the remote still holds the old commits. A guarded forced update replaces the remote branch only if nobody has added to it since you last looked, so a teammate's newer work is never wiped out.

**Your Task**

Update `origin/feature/pipeline-config` so it matches your rewritten local `feature/pipeline-config`. The update must be refused if the remote branch has commits you have not seen.

**Do not use an unconditional force.**

**Objective Checklist**

- [ ] origin/feature/pipeline-config now has your rewritten history.
- [ ] The force push used --force-with-lease, not plain --force (command-history check).
- [ ] feature/pipeline-config is still the current branch.

**Answer Key**

1. `git push --force-with-lease origin feature/pipeline-config`

**Accepted Alternatives**

- Only the common patterns below apply.

**Not accepted**

- `git push origin feature/pipeline-config --force-with-lease`, `--force-with-lease=feature/pipeline-config`, `--force-with-lease=feature/pipeline-config:<expected-commit>`. NOT accepted: `-f`, `--force`, `+feature/pipeline-config` (unconditional overwrite).

**Expected Result**

`origin/feature/pipeline-config` matches your rewritten local branch, and the update was guarded against overwriting newer remote work.

**Evaluation**

- `origin/feature/pipeline-config` = local `feature/pipeline-config`; the push command contained a lease option, not a bare force (`-f`/`--force`/`+ref` fail with a hint about teammates' work).
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 2.5.1 Fetch to update origin/main tracking · Easy

**Variant ID:** `v25e-main`

**Story**

Finn says a teammate has just pushed a change to `main`. You are on your local `main`, but you want to see what arrived before combining anything with your work.

“Let’s look at the delivery before we unpack it,” he says. The shared repository is `origin`. Update your local record of its branches, including `origin/main`, while leaving your checked-out `main` and working files as they are.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available.

**Real-World Context**

Fetching updates `origin/main`, your local record of the remote branch. It leaves your own `main` and working files where they are.

**Your Task**

Update your remote tracking information from `origin` so you can see the latest `origin/main`.

**Do not integrate it into your local branch yet.**

**Objective Checklist**

- [ ] Fetch the latest changes from the server so origin/main is up to date.
- [ ] Your local main and your working files did not change.

**Answer Key**

1. `git fetch origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2.

**Expected Result**

`origin/main` now shows what is on the server. Your own `main` and your files are exactly as they were.

**Evaluation**

- `origin/main` advanced to the server's commit; local `main` unchanged; working tree unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.5.2 Fetch to update origin/feature/auth tracking · Easy

**Variant ID:** `v25e-feature`

**Story**

Finn mentions a new commit on the shared authentication branch. You are on local `feature/auth` and would like to compare the remote version before bringing the change into your own branch.

The remote is `origin`. “Get the latest branch information first,” he says. Fetch from the remote so `origin/feature/auth` reflects what was published, without integrating the new commit into your local branch yet.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`; `origin` is available.

**Real-World Context**

On a shared feature branch, fetch lets you see a teammate’s published auth commit before integrating it.

**Your Task**

Update your remote tracking information from `origin` so you can see the latest `origin/feature/auth`.

**Do not integrate it into your local branch yet.**

**Objective Checklist**

- [ ] Fetch the latest changes from the server so origin/feature/auth is up to date.
- [ ] Your local feature/auth and your working files did not change.

**Answer Key**

1. `git fetch origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2.

**Expected Result**

`origin/feature/auth` now shows what is on the server. Your own `feature/auth` and your files are exactly as they were.

**Evaluation**

- `origin/feature/auth` advanced to the server's commit; local `feature/auth` unchanged; working tree unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.5.3 Fetch to update origin/develop tracking · Easy

**Variant ID:** `v25e-develop`

**Story**

A teammate has updated `develop` while you were working on another part of the project. Finn wants to know what changed, but he does not want the local branch advanced before he has a chance to inspect it.

You are on local `develop`, with `origin` configured. Refresh your local view of the remote branches. After this first step, `origin/develop` should show the newer position while your own `develop` stays where it was.

**Starting point:** You are on `develop`; available local branches: `develop`; `origin` is available.

**Real-World Context**

Fetch updates your view of remote `develop` so you can compare it with your local branch first.

**Your Task**

Update your remote tracking information from `origin` so you can see the latest `origin/develop`.

**Do not integrate it into your local branch yet.**

**Objective Checklist**

- [ ] Fetch the latest changes from the server so origin/develop is up to date.
- [ ] Your local develop and your working files did not change.

**Answer Key**

1. `git fetch origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2.

**Expected Result**

`origin/develop` now shows what is on the server. Your own `develop` and your files are exactly as they were.

**Evaluation**

- `origin/develop` advanced to the server's commit; local `develop` unchanged; working tree unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.5.4 Fetch to update origin/feature/models tracking · Easy

**Variant ID:** `fetch-easy-cap-check`

**Story**

Your capstone groupmate announces in chat, “I pushed the model classes.” You are on local `feature/models`, where your own edits may still need review. Raven suggests looking at the remote branch before deciding whether to bring in the teammate’s commits.

The shared repository is `origin`. Fetch its latest information so `origin/feature/models` is current, but do not move your local feature branch in this step.

**Starting point:** You are on `feature/models`; available local branches: `feature/models`; `origin` is available.

**Real-World Context**

Fetching lets the group inspect the model classes on `origin/feature/models` without immediately changing local feature work.

**Your Task**

Update your remote tracking information from `origin` so you can see the latest `origin/feature/models`.

**Do not integrate it into your local branch yet.**

**Objective Checklist**

- [ ] Fetch the latest changes from the server so origin/feature/models is up to date.
- [ ] Your local feature/models and your working files did not change.

**Answer Key**

1. `git fetch origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2.

**Expected Result**

`origin/feature/models` now shows what is on the server. Your own `feature/models` and your files are exactly as they were.

**Evaluation**

- `origin/feature/models` advanced to the server's commit; local `feature/models` unchanged; working tree unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.5.5 Fetch to update origin/release/v2 tracking · Easy

**Variant ID:** `fetch-easy-corp-list`

**Story**

Sage tells the team that the release engineer has updated `release/v2` on the server. You are on the local release branch and want to see that remote state before changing your checkout.

The project uses `origin` as its remote. “First just refresh our view of the server,” Sage says. Fetch so the remote tracking information is current; do not integrate the release commits into local `release/v2` yet.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`; `origin` is available.

**Real-World Context**

An updated release branch on the server appears in your remote tracking information after a fetch; your local release branch is not moved by that step.

**Your Task**

Update your remote tracking information from `origin` so you can see the latest `origin/release/v2`.

**Do not integrate it into your local branch yet.**

**Objective Checklist**

- [ ] Fetch the latest changes from the server so origin/release/v2 is up to date.
- [ ] Your local release/v2 and your working files did not change.

**Answer Key**

1. `git fetch origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2.

**Expected Result**

`origin/release/v2` now shows what is on the server. Your own `release/v2` and your files are exactly as they were.

**Evaluation**

- `origin/release/v2` advanced to the server's commit; local `release/v2` unchanged; working tree unchanged.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.5.6 Pull origin/main into local main · Medium

**Variant ID:** `v25m-main`

**Story**

The team has merged several small changes into remote `main` since you last worked. Finn asks you to bring your local `main` up to date before taking the next ticket. You are already on `main`, and the shared repository is `origin`.

This time the new commits should *actually* enter your local branch, not merely appear in a remote tracking record. Pull the remote `main` work into the branch you have checked out.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available.

**Real-World Context**

Pull downloads remote commits and integrates them into the branch you are on, so local `main` can catch up.

**Your Task**

Bring the latest `origin/main` commits into your current local `main` branch.

**Objective Checklist**

- [ ] Pull the newest commits from origin/main into main.
- [ ] main is checked out.

**Answer Key**

1. `git pull origin main`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P41.

**Expected Result**

Your local `main` has caught up with the server.

**Evaluation**

- Local `main` = `origin/main` (fast-forward, or a clean merge if histories differ).
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.5.7 Pull origin/feature/auth into local feature/auth · Medium

**Variant ID:** `v25m-feature`

**Story**

A teammate pushed to the shared auth branch while you were reviewing another screen. Finn asks whether your `feature/auth` has those changes yet. It doesn't, and you are about to keep building on a version that is already behind.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`; `origin` is available.

**Real-World Context**

Pulling the shared auth branch brings a teammate’s published commits into your current local branch.

**Your Task**

Bring the latest `origin/feature/auth` commits into your current local `feature/auth` branch.

**Objective Checklist**

- [ ] Pull the newest commits from origin/feature/auth into feature/auth.
- [ ] feature/auth is checked out.

**Answer Key**

1. `git pull origin feature/auth`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P42.

**Expected Result**

Your local `feature/auth` has caught up with the server.

**Evaluation**

- Local `feature/auth` = `origin/feature/auth` (fast-forward, or a clean merge if histories differ).
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.5.8 Pull origin/develop into local develop · Medium

**Variant ID:** `v25m-develop`

**Story**

The `develop` branch on `origin` has moved ahead with a teammate’s completed work. Finn wants your local `develop` to include it before you start the next task. You are already on `develop`, and the newer commits are ready on the remote.

“Bring them into your branch,” he says. Pull `origin/develop` into local `develop`, rather than only updating the remote tracking name.

**Starting point:** You are on `develop`; available local branches: `develop`; `origin` is available.

**Real-World Context**

When the remote is simply ahead, pulling can move local `develop` forward to its newer commit.

**Your Task**

Bring the latest `origin/develop` commits into your current local `develop` branch.

**Objective Checklist**

- [ ] Pull the newest commits from origin/develop into develop.
- [ ] develop is checked out.

**Answer Key**

1. `git pull origin develop`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin develop`, `git pull --ff-only origin develop` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/develop` (accepted, not CAR-accurate).

**Expected Result**

Your local `develop` has caught up with the server.

**Evaluation**

- Local `develop` = `origin/develop` (fast-forward, or a clean merge if histories differ).
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.5.9 Pull origin/staging into local staging · Medium

**Variant ID:** `pull-med-free-client`

**Story**

Your client has updated the preview content on `origin/staging`. You are on your own `staging` branch and need those changes before you keep building the preview. Sage says, “If we skip their update, our next screenshot will show yesterday’s copy.”

The remote is already configured as `origin`. Pull its `staging` branch into your current local branch so your preview work starts from the client’s latest content.

**Starting point:** You are on `staging`; available local branches: `staging`; `origin` is available.

**Real-World Context**

The client’s staging edits must be present locally before you continue the preview work.

**Your Task**

Bring the latest `origin/staging` commits into your current local `staging` branch.

**Objective Checklist**

- [ ] Pull the newest commits from origin/staging into staging.
- [ ] staging is checked out.

**Answer Key**

1. `git pull origin staging`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin staging`, `git pull --ff-only origin staging` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/staging` (accepted, not CAR-accurate).

**Expected Result**

Your local `staging` has caught up with the server.

**Evaluation**

- Local `staging` = `origin/staging` (fast-forward, or a clean merge if histories differ).
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.5.10 Review incoming work on main, then update main · Hard

**Variant ID:** `v25h-main`

**Story**

Finn says several new commits have landed on remote `main`. Before they become part of your working branch, he wants you to know exactly what they are. You are on `main`, and `origin` is the shared remote.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available.

**Real-World Context**

Looking at incoming work before accepting it separates reviewing from integrating. Once the commits join your branch, they are part of your history.

**Your Task**

A teammate has pushed new commits to `main`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `main` include it.

**Objective Checklist**

- [ ] The incoming commits on origin/main were inspected before the merge (command-history check).
- [ ] Bring the newest origin/main commits into main.
- [ ] main is checked out.

**Answer Key**

1. `git fetch origin`
2. `git log --oneline main..origin/main`
3. `git pull origin main`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2, P32, P41, P33, P34, P35.

**Expected Result**

You saw what was coming, and your local `main` now includes it.

**Evaluation**

- Local `main` = `origin/main`.
- Process: a read-only comparison command ran after the fetch and before the integrating command.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.5.11 Review incoming work on feature/auth, then update it · Hard

**Variant ID:** `v25h-feature`

**Story**

A teammate has added more authentication work to the remote feature branch. Maeve wants you to know exactly what arrived before it becomes part of your local `feature/auth`.

You are on that local branch, and the shared remote is `origin`.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`; `origin` is available.

**Real-World Context**

`origin/feature/auth` is a remote-tracking name, while `feature/auth` is your editable local branch. Seeing what is new on the remote comes before taking it in.

**Your Task**

A teammate has pushed new commits to `feature/auth`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `feature/auth` include it.

**Objective Checklist**

- [ ] The incoming commits on origin/feature/auth were inspected before the merge (command-history check).
- [ ] Bring the newest origin/feature/auth commits into feature/auth.
- [ ] feature/auth is checked out.

**Answer Key**

1. `git fetch origin`
2. `git log --oneline feature/auth..origin/feature/auth`
3. `git pull origin feature/auth`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P2, P32, P42, P33, P34, P35.

**Expected Result**

You saw what was coming, and your local `feature/auth` now includes it.

**Evaluation**

- Local `feature/auth` = `origin/feature/auth`.
- Process: a read-only comparison command ran after the fetch and before the integrating command.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.5.12 Review incoming work on develop, then update it · Hard

**Variant ID:** `v25h-develop`

**Story**

The remote `develop` branch has moved ahead by several commits. Sage knows you will need them, but she wants you to understand the new history before it becomes part of yours.

You are on local `develop`, with `origin` available. “*Know what is coming before you accept it,*” she says.

**Starting point:** You are on `develop`; available local branches: `develop`; `origin` is available.

**Real-World Context**

Checking the remote state before bringing it in helps you understand which new commits will enter `develop`.

**Your Task**

A teammate has pushed new commits to `develop`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `develop` include it.

**Objective Checklist**

- [ ] The incoming commits on origin/develop were inspected before the merge (command-history check).
- [ ] Bring the newest origin/develop commits into develop.
- [ ] develop is checked out.

**Answer Key**

1. `git fetch origin`
2. `git log --oneline develop..origin/develop`
3. `git pull origin develop`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin develop`, `git pull --ff-only origin develop` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/develop` (accepted, not CAR-accurate).
- Common patterns that apply: P2, P32, P33, P34, P35.

**Expected Result**

You saw what was coming, and your local `develop` now includes it.

**Evaluation**

- Local `develop` = `origin/develop`.
- Process: a read-only comparison command ran after the fetch and before the integrating command.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.5.13 Review incoming work on release/next, then update it · Hard

**Variant ID:** `fetch-hard-oss-review`

**Story**

A maintainer has just merged a large contribution into remote `release/next`. Raven asks you to review what changed before folding it into your own release branch. You are on local `release/next`, and `origin` is configured.

**Starting point:** You are on `release/next`; available local branches: `release/next`; `origin` is available.

**Real-World Context**

After a large upstream change, reviewing is a separate act from integrating; only the second one changes your local `release/next`.

**Your Task**

A teammate has pushed new commits to `release/next`. Look at *exactly* what is new on `origin` before it joins your branch, then make your local `release/next` include it.

**Objective Checklist**

- [ ] The incoming commits on origin/release/next were inspected before the merge (command-history check).
- [ ] Bring the newest origin/release/next commits into release/next.
- [ ] release/next is checked out.

**Answer Key**

1. `git fetch origin`
2. `git log --oneline release/next..origin/release/next`
3. `git pull origin release/next`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin release/next`, `git pull --ff-only origin release/next` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/release/next` (accepted, not CAR-accurate).
- Common patterns that apply: P2, P32, P33, P34, P35.

**Expected Result**

You saw what was coming, and your local `release/next` now includes it.

**Evaluation**

- Local `release/next` = `origin/release/next`.
- Process: a read-only comparison command ran after the fetch and before the integrating command.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.6.1 Reconcile and push feature/auth · Easy

**Variant ID:** `v26e-auth`

**Story**

You finish an auth change and try to push `feature/auth`, but Git rejects the update. Finn points out a teammate’s commit that reached the same remote branch while you were working.

“Both changes belong there,” he says. You are already on local `feature/auth`, and `origin` is available. Bring the remote work into your branch first. Then push again so the shared branch contains both the teammate’s commit and yours.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`; `origin` is available.

**Real-World Context**

A rejected push means the remote feature branch has commits your local branch lacks. Integrate them before publishing your auth work.

**Your Task**

Pull `origin/feature/auth` into your current local branch to reconcile the rejected push, then push `feature/auth` again.

**Objective Checklist**

- [ ] feature/auth now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/auth.
- [ ] feature/auth is checked out.

**Answer Key**

1. `git pull origin feature/auth`
2. `git push origin feature/auth`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P42, P31.

**Expected Result**

`feature/auth` holds the teammate's commits and yours together, and `origin/feature/auth` has the same combined history.

**Evaluation**

- Local `feature/auth` contains all commits from both lines; `origin/feature/auth` = local `feature/auth`; HEAD on `feature/auth`; no conflicts.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.6.2 Reconcile and push feature/payments · Easy

**Variant ID:** `v26e-payments`

**Story**

Sage sees the rejected push from `feature/payments` and checks the remote. Another developer finished a payment validation change just before you tried to publish yours. You are on local `feature/payments`, so the problem is not the branch name; your local history is missing their commit.

“Catch up, then send your work,” Sage says. Pull the remote payments work into your branch and retry the push to `origin`.

**Starting point:** You are on `feature/payments`; available local branches: `feature/payments`; `origin` is available.

**Real-World Context**

Payments commits from two people must both survive. Pull the remote work into your branch before retrying the push.

**Your Task**

Pull `origin/feature/payments` into your current local branch to reconcile the rejected push, then push `feature/payments` again.

**Objective Checklist**

- [ ] feature/payments now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/payments.
- [ ] feature/payments is checked out.

**Answer Key**

1. `git pull origin feature/payments`
2. `git push origin feature/payments`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin feature/payments`, `git pull --ff-only origin feature/payments` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/feature/payments` (accepted, not CAR-accurate).
- Common patterns that apply: P43.

**Expected Result**

`feature/payments` holds the teammate's commits and yours together, and `origin/feature/payments` has the same combined history.

**Evaluation**

- Local `feature/payments` contains all commits from both lines; `origin/feature/payments` = local `feature/payments`; HEAD on `feature/payments`; no conflicts.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.6.3 Reconcile and push hotfix/critical · Easy

**Variant ID:** `v26e-hotfix`

**Story**

The hotfix is urgent, but your push to `origin/hotfix/critical` is rejected. Maeve checks the activity and finds that another engineer pushed a small fix to the same branch minutes earlier.

You are on local `hotfix/critical`. Publishing your version without that newer commit would leave out part of the repair. Bring the remote work into your local branch, then push the combined result back to `origin`.

**Starting point:** You are on `hotfix/critical`; available local branches: `hotfix/critical`; `origin` is available.

**Real-World Context**

A hotfix is shared work. Reconcile the other engineer’s commit before publishing your own fix.

**Your Task**

Pull `origin/hotfix/critical` into your current local branch to reconcile the rejected push, then push `hotfix/critical` again.

**Objective Checklist**

- [ ] hotfix/critical now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/hotfix/critical.
- [ ] hotfix/critical is checked out.

**Answer Key**

1. `git pull origin hotfix/critical`
2. `git push origin hotfix/critical`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin hotfix/critical`, `git pull --ff-only origin hotfix/critical` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/hotfix/critical` (accepted, not CAR-accurate).
- Common patterns that apply: P44.

**Expected Result**

`hotfix/critical` holds the teammate's commits and yours together, and `origin/hotfix/critical` has the same combined history.

**Evaluation**

- Local `hotfix/critical` contains all commits from both lines; `origin/hotfix/critical` = local `hotfix/critical`; HEAD on `hotfix/critical`; no conflicts.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.6.4 Reconcile and push feature/ui-layout · Easy

**Variant ID:** `rec-easy-cap-ui`

**Story**

Your groupmate changes the UI layout while you are changing a different file on the same feature branch. When you try to push `feature/ui-layout`, Git refuses because the groupmate’s commit arrived first.

Sage checks the files: the changes do not overlap, so this exercise should integrate cleanly. You are already on the local feature branch. Pull the remote version into it, then push again so both contributions are available to the group.

**Starting point:** You are on `feature/ui-layout`; available local branches: `feature/ui-layout`; `origin` is available.

**Real-World Context**

The files do not overlap, so this exercise expects the pull to integrate cleanly before you push the combined UI branch.

**Your Task**

Pull `origin/feature/ui-layout` into your current local branch to reconcile the rejected push, then push `feature/ui-layout` again.

**Objective Checklist**

- [ ] feature/ui-layout now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/ui-layout.
- [ ] feature/ui-layout is checked out.

**Answer Key**

1. `git pull origin feature/ui-layout`
2. `git push origin feature/ui-layout`

**Accepted Alternatives**

- `git pull`, `git pull --no-rebase origin feature/ui-layout`, `git pull --ff-only origin feature/ui-layout` (when a fast-forward is possible), or `git fetch origin` then `git merge origin/feature/ui-layout` (accepted, not CAR-accurate).
- `git push origin feature/ui-layout:feature/ui-layout`, `git push origin refs/heads/feature/ui-layout`; bare `git push` only when an upstream is already set.

**Expected Result**

`feature/ui-layout` holds the teammate's commits and yours together, and `origin/feature/ui-layout` has the same combined history.

**Evaluation**

- Local `feature/ui-layout` contains all commits from both lines; `origin/feature/ui-layout` = local `feature/ui-layout`; HEAD on `feature/ui-layout`; no conflicts.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.6.5 Reconcile and push main · Easy

**Variant ID:** `rec-easy-docs-chapter`

**Story**

You and a colleague are writing separate chapters in the documentation repository. Your push to `main` fails because your colleague published a chapter while yours was still local.

Raven compares the changes and sees that the files do not overlap. “We need both chapters,” she says. You are on local `main`, with `origin` configured. Pull the new remote commit into your branch, then push the combined documentation back to the shared repository.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available.

**Real-World Context**

Both documentation commits belong on `main`. Bring the colleague’s chapter in before sharing your own update.

**Your Task**

Pull `origin/main` into your current local branch to reconcile the rejected push, then push `main` again.

**Objective Checklist**

- [ ] main now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/main.
- [ ] main is checked out.

**Answer Key**

1. `git pull origin main`
2. `git push origin main`

**Accepted Alternatives**

- `git push origin main:main`, `git push origin refs/heads/main`; bare `git push` only when an upstream is already set.
- Common patterns that apply: P41.

**Expected Result**

`main` holds the teammate's commits and yours together, and `origin/main` has the same combined history.

**Evaluation**

- Local `main` contains all commits from both lines; `origin/main` = local `main`; HEAD on `main`; no conflicts.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.6.6 Fetch, merge, push feature/auth · Medium

**Variant ID:** `v26m-auth`

**Story**

A push from `feature/auth` is rejected because its remote counterpart has moved. Finn wants to see exactly what is arriving before combining histories, so he chooses separate fetch and merge steps.

You are already on the local auth branch, and `origin` is available. Refresh the remote tracking information, merge `origin/feature/auth` into your branch, then push the result. The goal is to keep both lines of work in the shared branch.

**Starting point:** You are on `feature/auth`; available local branches: `feature/auth`; `origin` is available.

**Real-World Context**

Fetch updates the remote tracking branch; merging `origin/feature/auth` explicitly combines it with your current local branch.

**Your Task**

Fetch from `origin`, merge `origin/feature/auth` into your current `feature/auth` branch, then push the combined result.

**Objective Checklist**

- [ ] The remote work was fetched and then merged in separate steps (command-history check).
- [ ] feature/auth now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/auth.
- [ ] feature/auth is checked out.

**Answer Key**

1. `git fetch origin`
2. `git merge origin/feature/auth`
3. `git push origin feature/auth`

**Accepted Alternatives**

- `git merge --no-edit origin/feature/auth`; `git pull origin feature/auth` replaces both fetch and merge (accepted).
- Common patterns that apply: P2, P31.

**Expected Result**

`feature/auth` holds the teammate's commits and yours together, and `origin/feature/auth` has the same combined history.

**Evaluation**

- Local `feature/auth` contains all commits from both lines; `origin/feature/auth` = local `feature/auth`; HEAD on `feature/auth`; no conflicts.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.6.7 Fetch, merge, push feature/payments · Medium

**Variant ID:** `v26m-payments`

**Story**

The payments team shares `feature/payments`, and someone has pushed to it ahead of you. Sage suggests separating the update into visible steps so you can tell what came from the server.

You are already on local `feature/payments`. Fetch from `origin`, merge the updated `origin/feature/payments` into your branch, then publish the combined history. A second push should succeed once your branch includes the teammate’s commit.

**Starting point:** You are on `feature/payments`; available local branches: `feature/payments`; `origin` is available.

**Real-World Context**

An explicit merge makes the incoming payments commits visible as a separate integration step before publication.

**Your Task**

Fetch from `origin`, merge `origin/feature/payments` into your current `feature/payments` branch, then push the combined result.

**Objective Checklist**

- [ ] The remote work was fetched and then merged in separate steps (command-history check).
- [ ] feature/payments now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/payments.
- [ ] feature/payments is checked out.

**Answer Key**

1. `git fetch origin`
2. `git merge origin/feature/payments`
3. `git push origin feature/payments`

**Accepted Alternatives**

- `git merge --no-edit origin/feature/payments`; `git pull origin feature/payments` replaces both fetch and merge (accepted).
- Common patterns that apply: P2, P43.

**Expected Result**

`feature/payments` holds the teammate's commits and yours together, and `origin/feature/payments` has the same combined history.

**Evaluation**

- Local `feature/payments` contains all commits from both lines; `origin/feature/payments` = local `feature/payments`; HEAD on `feature/payments`; no conflicts.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.6.8 Fetch, merge, push hotfix/critical · Medium

**Variant ID:** `v26m-hotfix`

**Story**

A teammate has pushed a critical hotfix change while you were preparing your own. Your push is rejected, and Raven asks to look at the remote state before combining anything.

You are on local `hotfix/critical`, with `origin` available. Fetch the latest remote information, merge `origin/hotfix/critical` into your checked-out branch, then push the result. Both repair commits need to reach the shared hotfix branch.

**Starting point:** You are on `hotfix/critical`; available local branches: `hotfix/critical`; `origin` is available.

**Real-World Context**

Fetching first confirms the latest remote hotfix position; merging it into the local hotfix prepares a valid push.

**Your Task**

Fetch from `origin`, merge `origin/hotfix/critical` into your current `hotfix/critical` branch, then push the combined result.

**Objective Checklist**

- [ ] The remote work was fetched and then merged in separate steps (command-history check).
- [ ] hotfix/critical now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/hotfix/critical.
- [ ] hotfix/critical is checked out.

**Answer Key**

1. `git fetch origin`
2. `git merge origin/hotfix/critical`
3. `git push origin hotfix/critical`

**Accepted Alternatives**

- `git merge --no-edit origin/hotfix/critical`; `git pull origin hotfix/critical` replaces both fetch and merge (accepted).
- Common patterns that apply: P2, P44.

**Expected Result**

`hotfix/critical` holds the teammate's commits and yours together, and `origin/hotfix/critical` has the same combined history.

**Evaluation**

- Local `hotfix/critical` contains all commits from both lines; `origin/hotfix/critical` = local `hotfix/critical`; HEAD on `hotfix/critical`; no conflicts.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.6.9 Fetch, merge, push feature/test-runner-v2 · Medium

**Variant ID:** `rec-med-qa-testrunner`

**Story**

The QA team is preparing a new test runner, and Sage notices your push to `feature/test-runner-v2` has been rejected. Another tester added fixes to the same remote branch.

“Let’s see their commit before we combine it with yours,” she says. You are on the local feature branch. Fetch from `origin`, explicitly merge its updated test runner branch, and then push the combined work for the rest of QA to use.

**Starting point:** You are on `feature/test-runner-v2`; available local branches: `feature/test-runner-v2`; `origin` is available.

**Real-World Context**

The test runner branch is shared by QA teammates. An explicit fetch and merge preserves their published fixes alongside yours.

**Your Task**

Fetch from `origin`, merge `origin/feature/test-runner-v2` into your current `feature/test-runner-v2` branch, then push the combined result.

**Objective Checklist**

- [ ] The remote work was fetched and then merged in separate steps (command-history check).
- [ ] feature/test-runner-v2 now contains both the teammate's commits and your own.
- [ ] Push the combined history to origin/feature/test-runner-v2.
- [ ] feature/test-runner-v2 is checked out.

**Answer Key**

1. `git fetch origin`
2. `git merge origin/feature/test-runner-v2`
3. `git push origin feature/test-runner-v2`

**Accepted Alternatives**

- `git merge --no-edit origin/feature/test-runner-v2`; `git pull origin feature/test-runner-v2` replaces both fetch and merge (accepted).
- `git push origin feature/test-runner-v2:feature/test-runner-v2`, `git push origin refs/heads/feature/test-runner-v2`; bare `git push` only when an upstream is already set.
- Common patterns that apply: P2.

**Expected Result**

`feature/test-runner-v2` holds the teammate's commits and yours together, and `origin/feature/test-runner-v2` has the same combined history.

**Evaluation**

- Local `feature/test-runner-v2` contains all commits from both lines; `origin/feature/test-runner-v2` = local `feature/test-runner-v2`; HEAD on `feature/test-runner-v2`; no conflicts.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.6.10 Reconcile and publish feature/auth from the wrong branch · Hard

**Variant ID:** `v26h-auth`

**Story**

Your push to `feature/auth` was rejected, and Raven asks you to reconcile it. A glance at your prompt shows you're on `feature/current`, a branch that has nothing to do with auth. `feature/auth` exists locally, and `origin` has newer auth work.

Whatever you do next, **the auth work must not end up on `feature/current`**.

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `feature/auth`; `origin` is available.

**Real-World Context**

A merge or pull changes whichever branch is currently checked out, so the work has to be combined on the branch it belongs to.

**Your Task**

Combine the teammate's newer `origin/feature/auth` work with your own commits on `feature/auth`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `feature/auth`.

**Objective Checklist**

- [ ] feature/auth contains both the teammate's commits and your own.
- [ ] origin/feature/auth has the combined history.
- [ ] feature/current is unchanged (it received none of this work).
- [ ] feature/auth is checked out.

**Answer Key**

1. `git switch feature/auth`
2. `git fetch origin`
3. `git merge origin/feature/auth`
4. `git push origin feature/auth`

**Accepted Alternatives**

- `git checkout feature/auth`.
- `git merge --no-edit origin/feature/auth`; `git pull origin feature/auth` replaces both fetch and merge (accepted).
- Pull route: `git switch feature/auth`, then `git pull origin feature/auth`, then `git push origin feature/auth` (3 counted commands) is accepted.
- Common patterns that apply: P2, P31.

**Not accepted**

- NOT accepted: merging or pulling while on feature/current (it changes the wrong branch).

**Expected Result**

`feature/auth` and `origin/feature/auth` hold both sets of commits, `feature/current` is untouched, and you are on `feature/auth`.

**Evaluation**

- Local `feature/auth` has both lines; `origin/feature/auth` = local; `feature/current` pointer and content unchanged; HEAD on `feature/auth`.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.6.11 Reconcile and publish feature/payments from the wrong branch · Hard

**Variant ID:** `v26h-payments`

**Story**

Finn is about to review a payments update, but the latest push was rejected because a teammate published first. You open the terminal and notice you are on `feature/current`, not `feature/payments`.

Combining commits here would change the wrong line of work. Finn wants to see both sets of payments changes on the shared branch.

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `feature/payments`; `origin` is available.

**Real-World Context**

The work has to be combined on the payments branch itself, so the remote payments commits never enter the unrelated current feature.

**Your Task**

Combine the teammate's newer `origin/feature/payments` work with your own commits on `feature/payments`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `feature/payments`.

**Objective Checklist**

- [ ] feature/payments contains both the teammate's commits and your own.
- [ ] origin/feature/payments has the combined history.
- [ ] feature/current is unchanged (it received none of this work).
- [ ] feature/payments is checked out.

**Answer Key**

1. `git switch feature/payments`
2. `git fetch origin`
3. `git merge origin/feature/payments`
4. `git push origin feature/payments`

**Accepted Alternatives**

- `git checkout feature/payments`.
- `git merge --no-edit origin/feature/payments`; `git pull origin feature/payments` replaces both fetch and merge (accepted).
- Pull route: `git switch feature/payments`, then `git pull origin feature/payments`, then `git push origin feature/payments` (3 counted commands) is accepted.
- Common patterns that apply: P2, P43.

**Not accepted**

- NOT accepted: merging or pulling while on feature/current (it changes the wrong branch).

**Expected Result**

`feature/payments` and `origin/feature/payments` hold both sets of commits, `feature/current` is untouched, and you are on `feature/payments`.

**Evaluation**

- Local `feature/payments` has both lines; `origin/feature/payments` = local; `feature/current` pointer and content unchanged; HEAD on `feature/payments`.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.6.12 Reconcile and publish hotfix/critical from the wrong branch · Hard

**Variant ID:** `v26h-hotfix`

**Story**

A teammate has already pushed to `hotfix/critical`, and Finn wants your urgent repair to land on top of theirs, not over it.

The trouble is that you're on `feature/current`, working on something else entirely. **The fix has to end up on the fix branch and nowhere else.**

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `hotfix/critical`; `origin` is available.

**Real-World Context**

The combined hotfix has to be built on the hotfix branch itself, not on whatever branch you happened to leave checked out.

**Your Task**

Combine the teammate's newer `origin/hotfix/critical` work with your own commits on `hotfix/critical`, and publish the combined result to `origin`. **`feature/current` must not receive any of this work.** Finish on `hotfix/critical`.

**Objective Checklist**

- [ ] hotfix/critical contains both the teammate's commits and your own.
- [ ] origin/hotfix/critical has the combined history.
- [ ] feature/current is unchanged (it received none of this work).
- [ ] hotfix/critical is checked out.

**Answer Key**

1. `git switch hotfix/critical`
2. `git fetch origin`
3. `git merge origin/hotfix/critical`
4. `git push origin hotfix/critical`

**Accepted Alternatives**

- `git checkout hotfix/critical`.
- `git merge --no-edit origin/hotfix/critical`; `git pull origin hotfix/critical` replaces both fetch and merge (accepted).
- Pull route: `git switch hotfix/critical`, then `git pull origin hotfix/critical`, then `git push origin hotfix/critical` (3 counted commands) is accepted.
- Common patterns that apply: P2, P44.

**Not accepted**

- NOT accepted: merging or pulling while on feature/current (it changes the wrong branch).

**Expected Result**

`hotfix/critical` and `origin/hotfix/critical` hold both sets of commits, `feature/current` is untouched, and you are on `hotfix/critical`.

**Evaluation**

- Local `hotfix/critical` has both lines; `origin/hotfix/critical` = local; `feature/current` pointer and content unchanged; HEAD on `hotfix/critical`.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.6.13 Reconcile and publish the audit branch from develop · Hard

**Variant ID:** `rec-hard-corp-audit`

**Story**

Sage needs the compliance audit work published for review. Your earlier push to `feature/compliance-audit` was rejected because another teammate updated that branch first.

You are currently on `develop`, **which should not receive any of the audit work**. The local audit branch already exists.

**Starting point:** You are on `develop`; available local branches: `develop`, `feature/compliance-audit`; `origin` is available.

**Real-World Context**

An audit branch should be reconciled on that branch, not on `develop`, so the resulting push updates the intended review work.

**Your Task**

Combine the teammate's newer `origin/feature/compliance-audit` work with your own commits on `feature/compliance-audit`, and publish the combined result to `origin`. **`develop` must not receive any of this work.** Finish on `feature/compliance-audit`.

**Objective Checklist**

- [ ] feature/compliance-audit contains both the teammate's commits and your own.
- [ ] origin/feature/compliance-audit has the combined history.
- [ ] develop is unchanged (it received none of this work).
- [ ] feature/compliance-audit is checked out.

**Answer Key**

1. `git switch feature/compliance-audit`
2. `git fetch origin`
3. `git merge origin/feature/compliance-audit`
4. `git push origin feature/compliance-audit`

**Accepted Alternatives**

- `git checkout feature/compliance-audit`.
- `git merge --no-edit origin/feature/compliance-audit`; `git pull origin feature/compliance-audit` replaces both fetch and merge (accepted).
- `git push origin feature/compliance-audit:feature/compliance-audit`, `git push origin refs/heads/feature/compliance-audit`; bare `git push` only when an upstream is already set.
- Pull route: `git switch feature/compliance-audit`, then `git pull origin feature/compliance-audit`, then `git push origin feature/compliance-audit` (3 counted commands) is accepted.
- Common patterns that apply: P2.

**Not accepted**

- NOT accepted: merging or pulling while on develop (it changes the wrong branch).

**Expected Result**

`feature/compliance-audit` and `origin/feature/compliance-audit` hold both sets of commits, `develop` is untouched, and you are on `feature/compliance-audit`.

**Evaluation**

- Local `feature/compliance-audit` has both lines; `origin/feature/compliance-audit` = local; `develop` pointer and content unchanged; HEAD on `feature/compliance-audit`.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 2.7.1 Fast-forward merge feature/auth into main · Easy

**Variant ID:** `v27e-auth`

**Story**

The auth branch has passed review, and Finn is ready to include it on `main`. He checks the history: `feature/auth` simply continues from the current `main` commit, with no separate changes on `main` to reconcile.

“This one can move straight ahead,” he says. You are already on `main`. Merge the feature into your current branch; a fast forward is acceptable and does not need an extra merge commit.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`.

**Real-World Context**

A fast forward moves `main` to the feature’s tip because no separate commits need to be combined; Git need not create a merge commit.

**Your Task**

Merge `feature/auth` into the current `main` branch. A fast forward is acceptable; finish on `main`.

**Objective Checklist**

- [ ] main now contains all changes from feature/auth.
- [ ] History stays a straight line (no new merge commit).
- [ ] main is checked out.

**Answer Key**

1. `git merge feature/auth`

**Accepted Alternatives**

- `git merge --no-edit feature/auth`; `git merge --ff feature/auth`; `git merge --ff-only feature/auth` (when a fast-forward is possible).

**Expected Result**

`main` moved forward to `feature/auth`'s latest commit in a straight line, with no merge commit.

**Evaluation**

- `main` = `feature/auth` tip; no merge commit created; HEAD on `main`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.7.2 Fast-forward merge feature/payments into develop · Easy

**Variant ID:** `v27e-payments`

**Story**

The payments work is ready for the next shared build. Finn checks `feature/payments` against `develop` and finds that the feature continues directly from the current development commit. You are on `develop`, the branch that should receive it.

“No detour needed,” he says. Merge the payments branch into `develop`, allowing Git to advance along that straight history. The payment commits should become part of the branch your team builds from.

**Starting point:** You are on `develop`; available local branches: `develop`, `feature/payments`.

**Real-World Context**

When the target is an ancestor of the payments branch, a regular merge can advance `develop` directly.

**Your Task**

Merge `feature/payments` into the current `develop` branch. A fast forward is acceptable; finish on `develop`.

**Objective Checklist**

- [ ] develop now contains all changes from feature/payments.
- [ ] History stays a straight line (no new merge commit).
- [ ] develop is checked out.

**Answer Key**

1. `git merge feature/payments`

**Accepted Alternatives**

- `git merge --no-edit feature/payments`; `git merge --ff feature/payments`; `git merge --ff-only feature/payments` (when a fast-forward is possible).

**Expected Result**

`develop` moved forward to `feature/payments`'s latest commit in a straight line, with no merge commit.

**Evaluation**

- `develop` = `feature/payments` tip; no merge commit created; HEAD on `develop`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.7.3 Fast-forward merge hotfix/fix-critical into release/v2 · Easy

**Variant ID:** `v27e-hotfix`

**Story**

Finn has finished testing `hotfix/fix-critical`. The release branch `release/v2` is behind the hotfix on the same line of commits, so bringing it in should be straightforward.

You are already on `release/v2`. “Let’s get the fix into the release candidate,” Finn says. Merge the hotfix branch into your current release branch, allowing a fast forward. The result should point to the repaired code without a separate merge commit.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`, `hotfix/fix-critical`.

**Real-World Context**

A straight line of commits lets the release branch move to the hotfix tip without an extra merge commit.

**Your Task**

Merge `hotfix/fix-critical` into the current `release/v2` branch. A fast forward is acceptable; finish on `release/v2`.

**Objective Checklist**

- [ ] release/v2 now contains all changes from hotfix/fix-critical.
- [ ] History stays a straight line (no new merge commit).
- [ ] release/v2 is checked out.

**Answer Key**

1. `git merge hotfix/fix-critical`

**Accepted Alternatives**

- `git merge --no-edit hotfix/fix-critical`; `git merge --ff hotfix/fix-critical`; `git merge --ff-only hotfix/fix-critical` (when a fast-forward is possible).

**Expected Result**

`release/v2` moved forward to `hotfix/fix-critical`'s latest commit in a straight line, with no merge commit.

**Evaluation**

- `release/v2` = `hotfix/fix-critical` tip; no merge commit created; HEAD on `release/v2`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.7.4 Fast-forward merge docs/readme-update into staging · Easy

**Variant ID:** `merge-easy-cap-docs`

**Story**

Your capstone group catches a typo in the README just before a staging review. Finn points to `docs/readme-update`, where the correction has already been committed. You are on `staging`, and the documentation branch continues directly from it.

“Please bring in the corrected instructions before the reviewers arrive,” he says. Merge the docs branch into `staging`; because their histories form a straight line, advancing the branch directly is fine.

**Starting point:** You are on `staging`; available local branches: `staging`, `docs/readme-update`.

**Real-World Context**

The README update follows directly from `staging`, so its commits can become the new `staging` history in one merge.

**Your Task**

Merge `docs/readme-update` into the current `staging` branch. A fast forward is acceptable; finish on `staging`.

**Objective Checklist**

- [ ] staging now contains all changes from docs/readme-update.
- [ ] History stays a straight line (no new merge commit).
- [ ] staging is checked out.

**Answer Key**

1. `git merge docs/readme-update`

**Accepted Alternatives**

- `git merge --no-edit docs/readme-update`; `git merge --ff docs/readme-update`; `git merge --ff-only docs/readme-update` (when a fast-forward is possible).

**Expected Result**

`staging` moved forward to `docs/readme-update`'s latest commit in a straight line, with no merge commit.

**Evaluation**

- `staging` = `docs/readme-update` tip; no merge commit created; HEAD on `staging`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.7.5 Fast-forward merge feature/contact-form into integration · Easy

**Variant ID:** `merge-easy-free-contact`

**Story**

A freelancer finishes the contact form and asks Sage to check it in the combined preview. `feature/contact-form` continues directly from `integration`, with no conflicting line of work. You are on `integration`, the branch used for that preview.

“Bring it in so I can click through the whole site,” Sage says. Merge the completed feature into the current branch. A fast forward can carry the contact form commits into the preview.

**Starting point:** You are on `integration`; available local branches: `integration`, `feature/contact-form`.

**Real-World Context**

The completed contact form branch can advance integration directly when the histories have not diverged.

**Your Task**

Merge `feature/contact-form` into the current `integration` branch. A fast forward is acceptable; finish on `integration`.

**Objective Checklist**

- [ ] integration now contains all changes from feature/contact-form.
- [ ] History stays a straight line (no new merge commit).
- [ ] integration is checked out.

**Answer Key**

1. `git merge feature/contact-form`

**Accepted Alternatives**

- `git merge --no-edit feature/contact-form`; `git merge --ff feature/contact-form`; `git merge --ff-only feature/contact-form` (when a fast-forward is possible).

**Expected Result**

`integration` moved forward to `feature/contact-form`'s latest commit in a straight line, with no merge commit.

**Evaluation**

- `integration` = `feature/contact-form` tip; no merge commit created; HEAD on `integration`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.7.6 No-ff merge feature/auth into main · Medium

**Variant ID:** `v27m-auth`

**Story**

The auth feature has been approved, and Finn starts the merge into `main`. Git could advance `main` directly because the histories are linear.

The team, however, likes a visible marker showing where an *entire* feature entered the project. “Give this one a merge commit,” Finn says. You are already on `main`. Bring in `feature/auth` while explicitly preserving that merge event in the history.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`.

**Real-World Context**

Forcing a merge commit even when Git could fast forward, marking the auth feature as one completed unit in history.

**Your Task**

Merge `feature/auth` into `main` with an explicit merge commit, even if a fast forward is possible. Finish on `main`.

**Objective Checklist**

- [ ] main now contains all changes from feature/auth.
- [ ] A separate merge commit records the merge (even though a straight-line move was possible).
- [ ] main is checked out.

**Answer Key**

1. `git merge --no-ff feature/auth`

**Accepted Alternatives**

- `git merge --no-ff --no-edit feature/auth`, `git merge feature/auth --no-ff`, `git merge --no-ff -m "any message" feature/auth`.

**Expected Result**

`main` has a merge commit with `feature/auth` as its second parent, marking where the work arrived.

**Evaluation**

- `main` tip is a merge commit with 2 parents (previous `main` tip and `feature/auth` tip); HEAD on `main`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.7.7 No-ff merge feature/payments into develop · Medium

**Variant ID:** `v27m-payments`

**Story**

The payments branch has passed testing. Maeve notes that it could be fast forwarded into `develop`, but the team’s review log expects a separate merge commit for every completed feature.

“It helps us find the feature later,” she explains. You are on `develop`, ready to receive `feature/payments`. Merge it with the option that creates an explicit merge commit even though the branch histories could have stayed linear.

**Starting point:** You are on `develop`; available local branches: `develop`, `feature/payments`.

**Real-World Context**

The explicit merge commit helps reviewers see where payments entered `develop` as a group of changes.

**Your Task**

Merge `feature/payments` into `develop` with an explicit merge commit, even if a fast forward is possible. Finish on `develop`.

**Objective Checklist**

- [ ] develop now contains all changes from feature/payments.
- [ ] A separate merge commit records the merge (even though a straight-line move was possible).
- [ ] develop is checked out.

**Answer Key**

1. `git merge --no-ff feature/payments`

**Accepted Alternatives**

- `git merge --no-ff --no-edit feature/payments`, `git merge feature/payments --no-ff`, `git merge --no-ff -m "any message" feature/payments`.

**Expected Result**

`develop` has a merge commit with `feature/payments` as its second parent, marking where the work arrived.

**Evaluation**

- `develop` tip is a merge commit with 2 parents (previous `develop` tip and `feature/payments` tip); HEAD on `develop`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.7.8 No-ff merge hotfix/fix-critical into release/v2 · Medium

**Variant ID:** `v27m-hotfix`

**Story**

Sage has approved `hotfix/fix-critical` for `release/v2`. The release branch could advance straight to the hotfix tip, but the release team wants the integration recorded as a distinct event.

“When we look back, I want to see when this repair entered version two,” she says. You are on `release/v2`. Merge the hotfix into the current branch with an explicit merge commit.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`, `hotfix/fix-critical`.

**Real-World Context**

A release audit trail can show exactly when the hotfix entered `release/v2` by retaining a merge commit.

**Your Task**

Merge `hotfix/fix-critical` into `release/v2` with an explicit merge commit, even if a fast forward is possible. Finish on `release/v2`.

**Objective Checklist**

- [ ] release/v2 now contains all changes from hotfix/fix-critical.
- [ ] A separate merge commit records the merge (even though a straight-line move was possible).
- [ ] release/v2 is checked out.

**Answer Key**

1. `git merge --no-ff hotfix/fix-critical`

**Accepted Alternatives**

- `git merge --no-ff --no-edit hotfix/fix-critical`, `git merge hotfix/fix-critical --no-ff`, `git merge --no-ff -m "any message" hotfix/fix-critical`.

**Expected Result**

`release/v2` has a merge commit with `hotfix/fix-critical` as its second parent, marking where the work arrived.

**Evaluation**

- `release/v2` tip is a merge commit with 2 parents (previous `release/v2` tip and `hotfix/fix-critical` tip); HEAD on `release/v2`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.7.9 No-ff merge feature/sso-integration into release/v1 · Medium

**Variant ID:** `merge-med-corp-sso`

**Story**

The single sign-on feature has passed the company’s review process. Raven sees that `feature/sso-integration` extends directly from `release/v1`; a normal merge could move the release pointer without a separate marker. The audit checklist asks for an explicit merge commit, though.

You are on `release/v1`, the intended destination. Bring in the SSO feature with a merge that records the integration as its own commit.

**Starting point:** You are on `release/v1`; available local branches: `release/v1`, `feature/sso-integration`.

**Real-World Context**

The SSO integration gets a distinct merge commit on the release line, which the team can find during an audit.

**Your Task**

Merge `feature/sso-integration` into `release/v1` with an explicit merge commit, even if a fast forward is possible. Finish on `release/v1`.

**Objective Checklist**

- [ ] release/v1 now contains all changes from feature/sso-integration.
- [ ] A separate merge commit records the merge (even though a straight-line move was possible).
- [ ] release/v1 is checked out.

**Answer Key**

1. `git merge --no-ff feature/sso-integration`

**Accepted Alternatives**

- `git merge --no-ff --no-edit feature/sso-integration`, `git merge feature/sso-integration --no-ff`, `git merge --no-ff -m "any message" feature/sso-integration`.

**Expected Result**

`release/v1` has a merge commit with `feature/sso-integration` as its second parent, marking where the work arrived.

**Evaluation**

- `release/v1` tip is a merge commit with 2 parents (previous `release/v1` tip and `feature/sso-integration` tip); HEAD on `release/v1`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.7.10 Land feature/auth on main from the wrong branch, with a visible merge · Hard

**Variant ID:** `v27h-auth`

**Story**

Finn asks you to bring the approved auth feature into `main`, and the team wants its arrival to be clearly visible in `main`’s history. You open the terminal and see that you are on `feature/current`, which contains unrelated work.

“The branch you stand on is the one Git changes,” he reminds you. Both `main` and `feature/auth` already exist locally.

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `main`, `feature/auth`.

**Real-World Context**

Git changes the branch you are standing on. Be on the destination before bringing a feature in, and use a merge that leaves a visible marker.

**Your Task**

Bring `feature/auth` into `main` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `main`.

**Objective Checklist**

- [ ] main now contains all changes from feature/auth.
- [ ] The history shows a separate merge commit for it.
- [ ] feature/current is unchanged.
- [ ] main is checked out.

**Answer Key**

1. `git switch main`
2. `git merge --no-ff feature/auth`

**Accepted Alternatives**

- `git merge --no-ff --no-edit feature/auth`, `git merge feature/auth --no-ff`, `git merge --no-ff -m "any message" feature/auth`.
- Common patterns that apply: P23.

**Not accepted**

- NOT accepted: merging while on feature/current.

**Expected Result**

`main` contains `feature/auth` through a merge commit, `feature/current` is untouched, and you are on `main`.

**Evaluation**

- `main` tip is a 2-parent merge of `feature/auth`; `feature/current` unchanged; HEAD on `main`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.7.11 Land feature/payments on develop from the wrong branch, with a visible merge · Hard

**Variant ID:** `v27h-payments`

**Story**

The payments feature is ready, and Sage wants it in `develop` with the team’s required merge marker.

Your checkout is still on `feature/current`, where you were investigating another ticket. Bringing payments in there would leave `develop` unchanged.

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `develop`, `feature/payments`.

**Real-World Context**

`develop` is the intended destination for payments. The unrelated current branch has to stay as it is.

**Your Task**

Bring `feature/payments` into `develop` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `develop`.

**Objective Checklist**

- [ ] develop now contains all changes from feature/payments.
- [ ] The history shows a separate merge commit for it.
- [ ] feature/current is unchanged.
- [ ] develop is checked out.

**Answer Key**

1. `git switch develop`
2. `git merge --no-ff feature/payments`

**Accepted Alternatives**

- `git checkout develop`.
- `git merge --no-ff --no-edit feature/payments`, `git merge feature/payments --no-ff`, `git merge --no-ff -m "any message" feature/payments`.

**Not accepted**

- NOT accepted: merging while on feature/current.

**Expected Result**

`develop` contains `feature/payments` through a merge commit, `feature/current` is untouched, and you are on `develop`.

**Evaluation**

- `develop` tip is a 2-parent merge of `feature/payments`; `feature/current` unchanged; HEAD on `develop`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.7.12 Land hotfix/critical on release/v1 from the wrong branch, with a visible merge · Hard

**Variant ID:** `v27h-hotfix`

**Story**

The group approves a critical repair for `release/v1`, and Maeve notices you are on `feature/current`, which has nothing to do with it. "*Good fix, wrong desk,*" she says.

Both `hotfix/critical` and `release/v1` exist locally. Maeve wants the release's history to show clearly when the repair was brought in.

**Starting point:** You are on `feature/current`; available local branches: `feature/current`, `release/v1`, `hotfix/critical`.

**Real-World Context**

The source is a hotfix; `release/v1` is the destination. The current feature branch should not receive this merge.

**Your Task**

Bring `hotfix/critical` into `release/v1` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current` exactly as it is** and finish on `release/v1`.

**Objective Checklist**

- [ ] release/v1 now contains all changes from hotfix/critical.
- [ ] The history shows a separate merge commit for it.
- [ ] feature/current is unchanged.
- [ ] release/v1 is checked out.

**Answer Key**

1. `git switch release/v1`
2. `git merge --no-ff hotfix/critical`

**Accepted Alternatives**

- `git checkout release/v1`.
- `git merge --no-ff --no-edit hotfix/critical`, `git merge hotfix/critical --no-ff`, `git merge --no-ff -m "any message" hotfix/critical`.

**Not accepted**

- NOT accepted: merging while on feature/current.

**Expected Result**

`release/v1` contains `hotfix/critical` through a merge commit, `feature/current` is untouched, and you are on `release/v1`.

**Evaluation**

- `release/v1` tip is a 2-parent merge of `hotfix/critical`; `feature/current` unchanged; HEAD on `release/v1`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.7.13 Land hotfix/cert-renewal on release/stable from the wrong branch, with a visible merge · Hard

**Variant ID:** `merge-hard-devops-cert`

**Story**

The operations team has finished a certificate renewal on `hotfix/cert-renewal`. Sage needs that fix on `release/stable` and **wants a merge commit for the release record**.

You are on `feature/current-work`, still dealing with an unrelated task. “*Let’s not put a certificate fix in your feature branch,*” she says.

**Starting point:** You are on `feature/current-work`; available local branches: `feature/current-work`, `release/stable`, `hotfix/cert-renewal`.

**Real-World Context**

The certificate renewal belongs in `release/stable`, and a merge commit records its arrival there.

**Your Task**

Bring `hotfix/cert-renewal` into `release/stable` so that the history shows a distinct merge commit marking its arrival.

**Leave `feature/current-work` exactly as it is** and finish on `release/stable`.

**Objective Checklist**

- [ ] release/stable now contains all changes from hotfix/cert-renewal.
- [ ] The history shows a separate merge commit for it.
- [ ] feature/current-work is unchanged.
- [ ] release/stable is checked out.

**Answer Key**

1. `git switch release/stable`
2. `git merge --no-ff hotfix/cert-renewal`

**Accepted Alternatives**

- `git checkout release/stable`.
- `git merge --no-ff --no-edit hotfix/cert-renewal`, `git merge hotfix/cert-renewal --no-ff`, `git merge --no-ff -m "any message" hotfix/cert-renewal`.

**Not accepted**

- NOT accepted: merging while on feature/current-work.

**Expected Result**

`release/stable` contains `hotfix/cert-renewal` through a merge commit, `feature/current-work` is untouched, and you are on `release/stable`.

**Evaluation**

- `release/stable` tip is a 2-parent merge of `hotfix/cert-renewal`; `feature/current-work` unchanged; HEAD on `release/stable`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.8.1 Squash-merge feature/auth into main · Easy

**Variant ID:** `v28e-auth`

**Story**

The auth branch has collected several small draft commits: form, validation, a correction, and another correction. Raven wants the completed feature on `main`, but the team would prefer one clear commit in that destination’s history.

You are already on `main`, and `feature/auth` exists locally. “Bring over the finished result, not the whole draft trail,” she says. Squash the feature’s changes onto `main`, then record them in one commit named `Add auth feature`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`.

**Real-World Context**

A squash merge stages the feature’s combined changes on `main`; a separate commit is needed to record them as one snapshot.

**Your Task**

Squash the changes from `feature/auth` into your current `main` branch. Commit with the exact message `Add auth feature`.

**Objective Checklist**

- [ ] main has one new commit named “Add auth feature” containing all of feature/auth's changes.
- [ ] feature/auth's individual draft commits were not copied into main.
- [ ] main is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/auth`
2. `git commit -m "Add auth feature"`

**Accepted Alternatives**

- `git merge feature/auth --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P45.

**Expected Result**

`main` gained one new commit, “`Add auth feature`”, holding the combined changes of `feature/auth`. Its draft commits did not come along.

**Evaluation**

- `main` has exactly 1 new commit (1 parent) with message `Add auth feature`; tree = tree of `feature/auth` merged; HEAD on `main`; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.8.2 Squash-merge feature/orders into develop · Easy

**Variant ID:** `v28e-orders`

**Story**

Finn scrolls through the orders branch: “initial version,” “fix totals,” and a few work in progress notes. The behavior is ready, but the team wants its combined result as one commit on `develop`.

You are on `develop`, with `feature/orders` available locally. Squash the branch’s changes into your current branch and make one commit named `Add orders feature`. The orders feature should be present without importing each draft commit separately.

**Starting point:** You are on `develop`; available local branches: `develop`, `feature/orders`.

**Real-World Context**

The orders branch has several steps of work, but `develop` can record the finished result in a single commit.

**Your Task**

Squash the changes from `feature/orders` into your current `develop` branch. Commit with the exact message `Add orders feature`.

**Objective Checklist**

- [ ] develop has one new commit named “Add orders feature” containing all of feature/orders's changes.
- [ ] feature/orders's individual draft commits were not copied into develop.
- [ ] develop is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/orders`
2. `git commit -m "Add orders feature"`

**Accepted Alternatives**

- `git merge feature/orders --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P46.

**Expected Result**

`develop` gained one new commit, “`Add orders feature`”, holding the combined changes of `feature/orders`. Its draft commits did not come along.

**Evaluation**

- `develop` has exactly 1 new commit (1 parent) with message `Add orders feature`; tree = tree of `feature/orders` merged; HEAD on `develop`; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.8.3 Squash-merge feature/parser into release/v2 · Easy

**Variant ID:** `v28e-parser`

**Story**

The parser change is small, but its branch history is crowded with attempts to handle tricky inputs. Sage wants the final behavior in the release branch as one understandable commit.

You are on `release/v2`; `feature/parser` is the local source. “The reviewers need the fix, not every failed experiment,” she says. Squash its combined changes into `release/v2`, then commit them with the message `Add parser feature`.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`, `feature/parser`.

**Real-World Context**

A release branch can receive the parser’s final effect as one commit instead of carrying each work in progress commit.

**Your Task**

Squash the changes from `feature/parser` into your current `release/v2` branch. Commit with the exact message `Add parser feature`.

**Objective Checklist**

- [ ] release/v2 has one new commit named “Add parser feature” containing all of feature/parser's changes.
- [ ] feature/parser's individual draft commits were not copied into release/v2.
- [ ] release/v2 is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/parser`
2. `git commit -m "Add parser feature"`

**Accepted Alternatives**

- `git merge feature/parser --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P47.

**Expected Result**

`release/v2` gained one new commit, “`Add parser feature`”, holding the combined changes of `feature/parser`. Its draft commits did not come along.

**Evaluation**

- `release/v2` has exactly 1 new commit (1 parent) with message `Add parser feature`; tree = tree of `feature/parser` merged; HEAD on `release/v2`; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.8.4 Squash-merge feature/report-generator into integration · Easy

**Variant ID:** `squash-easy-cap-report`

**Story**

Your capstone group has three rough commits on `feature/report-generator`, including one called “try again.” Raven approves the finished report module but asks for a single clean entry in the `integration` branch before submission.

You are already on `integration`. “Future us will thank present us for a readable history,” she says. Squash the feature’s combined changes into the current branch and commit once with the message `Add report generator module`.

**Starting point:** You are on `integration`; available local branches: `integration`, `feature/report-generator`.

**Real-World Context**

One clear report generator commit makes the group submission easier to review than its three intermediate drafts.

**Your Task**

Squash the changes from `feature/report-generator` into your current `integration` branch. Commit with the exact message `Add report generator module`.

**Objective Checklist**

- [ ] integration has one new commit named “Add report generator module” containing all of feature/report-generator's changes.
- [ ] feature/report-generator's individual draft commits were not copied into integration.
- [ ] integration is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/report-generator`
2. `git commit -m "Add report generator module"`

**Accepted Alternatives**

- `git merge feature/report-generator --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git commit --message "Add report generator module"`, `git commit --message="Add report generator module"`, `git commit -m"Add report generator module"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).

**Expected Result**

`integration` gained one new commit, “`Add report generator module`”, holding the combined changes of `feature/report-generator`. Its draft commits did not come along.

**Evaluation**

- `integration` has exactly 1 new commit (1 parent) with message `Add report generator module`; tree = tree of `feature/report-generator` merged; HEAD on `integration`; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.8.5 Squash-merge feature/payment-flow into staging · Easy

**Variant ID:** `squash-easy-free-payment`

**Story**

The client’s payment flow works, but the feature branch contains four drafts with messages such as “wip” and “ok this time.” Sage points to the client’s one-commit-per-feature rule.

You are on `staging`, where the payment flow must land, and `feature/payment-flow` exists locally. Bring over the final combined changes as one squash commit, using the exact message `Add payment flow`. The preview branch should contain the result of the work.

**Starting point:** You are on `staging`; available local branches: `staging`, `feature/payment-flow`.

**Real-World Context**

The client’s one commit policy can be met by staging the payment branch’s combined result and committing it once.

**Your Task**

Squash the changes from `feature/payment-flow` into your current `staging` branch. Commit with the exact message `Add payment flow`.

**Objective Checklist**

- [ ] staging has one new commit named “Add payment flow” containing all of feature/payment-flow's changes.
- [ ] feature/payment-flow's individual draft commits were not copied into staging.
- [ ] staging is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/payment-flow`
2. `git commit -m "Add payment flow"`

**Accepted Alternatives**

- `git merge feature/payment-flow --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git commit --message "Add payment flow"`, `git commit --message="Add payment flow"`, `git commit -m"Add payment flow"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).

**Expected Result**

`staging` gained one new commit, “`Add payment flow`”, holding the combined changes of `feature/payment-flow`. Its draft commits did not come along.

**Evaluation**

- `staging` has exactly 1 new commit (1 parent) with message `Add payment flow`; tree = tree of `feature/payment-flow` merged; HEAD on `staging`; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 2.8.6 Fetch then squash-merge origin/feature/auth into main · Medium

**Variant ID:** `v28m-auth`

**Story**

Finn says a teammate has published the auth feature, but the branch is only on `origin`; you have not fetched it yet.

You are on `main`, the destination for the finished feature. “First get a current view of their branch,” he says, “then bring over its combined changes.” Fetch from `origin`, squash the changes from `origin/feature/auth` onto `main`, and save one commit named `Add auth feature`.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available.

**Real-World Context**

Fetch makes the remote auth branch visible as `origin/feature/auth`; squash merges its changes without creating a local feature branch.

**Your Task**

Fetch from `origin`, then squash the changes from `origin/feature/auth` into your current `main` branch. Commit with the exact message `Add auth feature`.

**Objective Checklist**

- [ ] origin/feature/auth was fetched from origin before the squash (command-history check).
- [ ] main has one new commit named “Add auth feature” containing all of origin/feature/auth's changes.
- [ ] origin/feature/auth's individual draft commits were not copied into main.
- [ ] main is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git fetch origin`
2. `git merge --squash origin/feature/auth`
3. `git commit -m "Add auth feature"`

**Accepted Alternatives**

- `git merge origin/feature/auth --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P2, P45.

**Expected Result**

`main` gained one new commit, “`Add auth feature`”, holding the combined changes of `origin/feature/auth`. Its draft commits did not come along.

**Evaluation**

- `main` has exactly 1 new commit (1 parent) with message `Add auth feature`; tree = tree of `origin/feature/auth` merged; HEAD on `main`; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.8.7 Fetch then squash-merge origin/feature/orders into develop · Medium

**Variant ID:** `v28m-orders`

**Story**

Finn wants the orders feature on `develop` for the next team build.

The branch exists only on `origin`, and you haven't downloaded it, so you have no local copy to work from. The group's rule is that **a feature arrives in `develop` as one commit, not as a trail of drafts**.

**Starting point:** You are on `develop`; available local branches: `develop`; `origin` is available.

**Real-World Context**

The orders branch exists only on the remote, so fetch it before staging its combined changes onto `develop`.

**Your Task**

Fetch from `origin`, then squash the changes from `origin/feature/orders` into your current `develop` branch. Commit with the exact message `Add orders feature`.

**Objective Checklist**

- [ ] origin/feature/orders was fetched from origin before the squash (command-history check).
- [ ] develop has one new commit named “Add orders feature” containing all of origin/feature/orders's changes.
- [ ] origin/feature/orders's individual draft commits were not copied into develop.
- [ ] develop is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git fetch origin`
2. `git merge --squash origin/feature/orders`
3. `git commit -m "Add orders feature"`

**Accepted Alternatives**

- `git merge origin/feature/orders --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P2, P46.

**Expected Result**

`develop` gained one new commit, “`Add orders feature`”, holding the combined changes of `origin/feature/orders`. Its draft commits did not come along.

**Evaluation**

- `develop` has exactly 1 new commit (1 parent) with message `Add orders feature`; tree = tree of `origin/feature/orders` merged; HEAD on `develop`; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.8.8 Fetch then squash-merge origin/feature/parser into release/v2 · Medium

**Variant ID:** `v28m-parser`

**Story**

The parser branch is ready for the version two release, but the only copy you can see is on `origin`. Finn asks you to update your remote information before bringing it into `release/v2`, where you are currently working.

After fetching, the source will be visible as `origin/feature/parser`. Squash its combined changes into the release branch and save one commit named `Add parser feature`.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`; `origin` is available.

**Real-World Context**

Fetching updates `origin/feature/parser`, which provides the source for a single release commit.

**Your Task**

Fetch from `origin`, then squash the changes from `origin/feature/parser` into your current `release/v2` branch. Commit with the exact message `Add parser feature`.

**Objective Checklist**

- [ ] origin/feature/parser was fetched from origin before the squash (command-history check).
- [ ] release/v2 has one new commit named “Add parser feature” containing all of origin/feature/parser's changes.
- [ ] origin/feature/parser's individual draft commits were not copied into release/v2.
- [ ] release/v2 is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git fetch origin`
2. `git merge --squash origin/feature/parser`
3. `git commit -m "Add parser feature"`

**Accepted Alternatives**

- `git merge origin/feature/parser --squash`. Not accepted: a normal merge (it creates a merge commit).
- Common patterns that apply: P2, P47.

**Expected Result**

`release/v2` gained one new commit, “`Add parser feature`”, holding the combined changes of `origin/feature/parser`. Its draft commits did not come along.

**Evaluation**

- `release/v2` has exactly 1 new commit (1 parent) with message `Add parser feature`; tree = tree of `origin/feature/parser` merged; HEAD on `release/v2`; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.8.9 Fetch then squash-merge origin/feature/gdpr-export into staging · Medium

**Variant ID:** `squash-med-corp-gdpr`

**Story**

A teammate has finished the data export endpoint on `feature/gdpr-export`, which exists only on the remote. Sage wants **a single reviewable commit on `staging`, not every draft along the way**. You haven't downloaded the branch yet.

**Starting point:** You are on `staging`; available local branches: `staging`; `origin` is available.

**Real-World Context**

A remote tracking branch can be squash merged into `staging` after a fetch; the new commit uses the team’s requested message.

**Your Task**

Fetch from `origin`, then squash the changes from `origin/feature/gdpr-export` into your current `staging` branch. Commit with the exact message `Add GDPR data export endpoint`.

**Objective Checklist**

- [ ] origin/feature/gdpr-export was fetched from origin before the squash (command-history check).
- [ ] staging has one new commit named “Add GDPR data export endpoint” containing all of origin/feature/gdpr-export's changes.
- [ ] origin/feature/gdpr-export's individual draft commits were not copied into staging.
- [ ] staging is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git fetch origin`
2. `git merge --squash origin/feature/gdpr-export`
3. `git commit -m "Add GDPR data export endpoint"`

**Accepted Alternatives**

- `git merge origin/feature/gdpr-export --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git commit --message "Add GDPR data export endpoint"`, `git commit --message="Add GDPR data export endpoint"`, `git commit -m"Add GDPR data export endpoint"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- Common patterns that apply: P2.

**Expected Result**

`staging` gained one new commit, “`Add GDPR data export endpoint`”, holding the combined changes of `origin/feature/gdpr-export`. Its draft commits did not come along.

**Evaluation**

- `staging` has exactly 1 new commit (1 parent) with message `Add GDPR data export endpoint`; tree = tree of `origin/feature/gdpr-export` merged; HEAD on `staging`; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 2.8.10 Land feature/auth as one commit and clean up · Hard

**Variant ID:** `v28h-auth`

**Story**

Finn has approved the auth feature, but its local branch contains several draft commits. He wants one commit with the finished change on `main`, and he does not want the now-unneeded local `feature/auth` branch lingering afterward.

You are already on `main`. “We’ve got the result; we can clean up the scaffolding afterward,” he says.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`.

**Real-World Context**

A squash merge copies the changes but does not record the branch as merged, so Git treats removing that branch as throwing away unmerged work. The cleanup here removes it deliberately, after the squashed commit is safely on the target branch.

**Your Task**

Bring all of `feature/auth`'s work into `main` as a single new commit named `Add auth feature`, then leave no local `feature/auth` branch behind.

**Objective Checklist**

- [ ] main has one new commit named “Add auth feature” containing all of feature/auth's changes.
- [ ] Delete the local feature/auth branch.
- [ ] main is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/auth`
2. `git commit -m "Add auth feature"`
3. `git branch -D feature/auth`

**Accepted Alternatives**

- `git merge feature/auth --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git branch --delete --force feature/auth` is accepted. `git branch -d feature/auth` is refused by Git itself here (the squash is not recorded as a merge); show that message and nudge toward the force form, do not mark the learner wrong.
- Common patterns that apply: P45, P36.

**Expected Result**

`main` gained one commit, “`Add auth feature`”, and `feature/auth` is gone.

**Evaluation**

- `main` +1 commit `Add auth feature`; `feature/auth` absent; HEAD on `main`.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 2.8.11 Land feature/orders as one commit and clean up · Hard

**Variant ID:** `v28h-orders`

**Story**

Maeve wants the orders feature landed on `develop`, and the branch is full of intermediate commits the team doesn't need to remember. "*One finished feature, one clear commit,*" she says. Once the feature is in, the old branch has no reason to stay.

**Starting point:** You are on `develop`; available local branches: `develop`, `feature/orders`.

**Real-World Context**

A squash merge copies the changes but does not record the branch as merged, so Git treats removing that branch as throwing away unmerged work. The cleanup here removes it deliberately, after the squashed commit is safely on the target branch.

**Your Task**

Bring all of `feature/orders`'s work into `develop` as a single new commit named `Add orders feature`, then leave no local `feature/orders` branch behind.

**Objective Checklist**

- [ ] develop has one new commit named “Add orders feature” containing all of feature/orders's changes.
- [ ] Delete the local feature/orders branch.
- [ ] develop is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/orders`
2. `git commit -m "Add orders feature"`
3. `git branch -D feature/orders`

**Accepted Alternatives**

- `git merge feature/orders --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git branch --delete --force feature/orders` is accepted. `git branch -d feature/orders` is refused by Git itself here (the squash is not recorded as a merge); show that message and nudge toward the force form, do not mark the learner wrong.
- Common patterns that apply: P46, P36.

**Expected Result**

`develop` gained one commit, “`Add orders feature`”, and `feature/orders` is gone.

**Evaluation**

- `develop` +1 commit `Add orders feature`; `feature/orders` absent; HEAD on `develop`.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 2.8.12 Land feature/parser as one commit and clean up · Hard

**Variant ID:** `v28h-parser`

**Story**

The parser team has tested its final change on `feature/parser`. Sage wants one commit on `release/v2` and does not need to keep the local source branch afterward.

You are already on the release branch. “Let’s put the fix where it ships and tidy the workspace,” she says.

**Starting point:** You are on `release/v2`; available local branches: `release/v2`, `feature/parser`.

**Real-World Context**

A squash merge copies the changes but does not record the branch as merged, so Git treats removing that branch as throwing away unmerged work. The cleanup here removes it deliberately, after the squashed commit is safely on the target branch.

**Your Task**

Bring all of `feature/parser`'s work into `release/v2` as a single new commit named `Add parser feature`, then leave no local `feature/parser` branch behind.

**Objective Checklist**

- [ ] release/v2 has one new commit named “Add parser feature” containing all of feature/parser's changes.
- [ ] Delete the local feature/parser branch.
- [ ] release/v2 is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/parser`
2. `git commit -m "Add parser feature"`
3. `git branch -D feature/parser`

**Accepted Alternatives**

- `git merge feature/parser --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git branch --delete --force feature/parser` is accepted. `git branch -d feature/parser` is refused by Git itself here (the squash is not recorded as a merge); show that message and nudge toward the force form, do not mark the learner wrong.
- Common patterns that apply: P47, P36.

**Expected Result**

`release/v2` gained one commit, “`Add parser feature`”, and `feature/parser` is gone.

**Evaluation**

- `release/v2` +1 commit `Add parser feature`; `feature/parser` absent; HEAD on `release/v2`.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 2.8.13 Land feature/log-rotation as one commit and clean up · Hard

**Variant ID:** `squash-hard-devops-log`

**Story**

The operations team has finished log rotation, but `feature/log-rotation` contains a trail of small configuration attempts. Finn asks for one understandable commit on `main`, which is the branch you have checked out, and for the old local branch to be gone afterward.

“Keep the final setup, and we can clear out the old local branch,” he says.

**Starting point:** You are on `main`; available local branches: `main`, `feature/log-rotation`.

**Real-World Context**

A squash merge copies the changes but does not record the branch as merged, so Git treats removing that branch as throwing away unmerged work. The cleanup here removes it deliberately, after the squashed commit is safely on the target branch.

**Your Task**

Bring all of `feature/log-rotation`'s work into `main` as a single new commit named `Add log rotation configuration`, then leave no local `feature/log-rotation` branch behind.

**Objective Checklist**

- [ ] main has one new commit named “Add log rotation configuration” containing all of feature/log-rotation's changes.
- [ ] Delete the local feature/log-rotation branch.
- [ ] main is checked out.
- [ ] The working folder is clean.

**Answer Key**

1. `git merge --squash feature/log-rotation`
2. `git commit -m "Add log rotation configuration"`
3. `git branch -D feature/log-rotation`

**Accepted Alternatives**

- `git merge feature/log-rotation --squash`. Not accepted: a normal merge (it creates a merge commit).
- `git commit --message "Add log rotation configuration"`, `git commit --message="Add log rotation configuration"`, `git commit -m"Add log rotation configuration"`, single quotes instead of double. The message must match exactly (case-sensitive; surrounding spaces ignored).
- `git branch --delete --force feature/log-rotation` is accepted. `git branch -d feature/log-rotation` is refused by Git itself here (the squash is not recorded as a merge); show that message and nudge toward the force form, do not mark the learner wrong.
- Common patterns that apply: P36.

**Expected Result**

`main` gained one commit, “`Add log rotation configuration`”, and `feature/log-rotation` is gone.

**Evaluation**

- `main` +1 commit `Add log rotation configuration`; `feature/log-rotation` absent; HEAD on `main`.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 2.9.1 Delete origin/feature/auth · Easy

**Variant ID:** `v29e-auth`

**Story**

The auth pull request is merged, and Sage closes the ticket. A teammate still sees `feature/auth` in the list of remote branches and asks whether more work is planned there. “No, that name can come down,” Sage says.

You are on `main`, and the remote is `origin`. Remove the merged feature branch from the remote so the shared branch list reflects the work that is still active. The local branch is not part of this request.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`. `origin` is available and has the branch.

**Real-World Context**

After the auth PR is merged, deleting its remote branch removes a completed review branch from the shared repository.

**Your Task**

Delete the merged `feature/auth` branch from `origin`. Keep the local branch.

**Objective Checklist**

- [ ] Delete feature/auth from origin.
- [ ] Your local feature/auth branch still exists.

**Answer Key**

1. `git push origin --delete feature/auth`

**Accepted Alternatives**

- `git push -d origin feature/auth`, `git push origin -d feature/auth`, `git push origin :feature/auth`, `git push origin --delete refs/heads/feature/auth`.

**Expected Result**

`feature/auth` is gone from the server. Your local copy is still there.

**Evaluation**

- Remote `origin` has no `feature/auth`; local `feature/auth` exists; `origin/feature/auth` record removed.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.9.2 Delete origin/feature/orders · Easy

**Variant ID:** `v29e-orders`

**Story**

Finn checks the shared repository after the orders feature is merged. `feature/orders` is still listed on `origin`, even though its changes have already been integrated.

“Someone will think it’s still open,” he says. You are on `main`, and your own local branch also exists. Delete the branch name from `origin` as the requested cleanup. Leave the separate local copy for another task.

**Starting point:** You are on `main`; available local branches: `main`, `feature/orders`. `origin` is available and has the branch.

**Real-World Context**

Removing the completed orders branch from `origin` makes the remote list easier for teammates to scan.

**Your Task**

Delete the merged `feature/orders` branch from `origin`. Keep the local branch.

**Objective Checklist**

- [ ] Delete feature/orders from origin.
- [ ] Your local feature/orders branch still exists.

**Answer Key**

1. `git push origin --delete feature/orders`

**Accepted Alternatives**

- `git push -d origin feature/orders`, `git push origin -d feature/orders`, `git push origin :feature/orders`, `git push origin --delete refs/heads/feature/orders`.

**Expected Result**

`feature/orders` is gone from the server. Your local copy is still there.

**Evaluation**

- Remote `origin` has no `feature/orders`; local `feature/orders` exists; `origin/feature/orders` record removed.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.9.3 Delete origin/feature/parser · Easy

**Variant ID:** `v29e-parser`

**Story**

The parser fix has been merged and released. Maeve notices that `origin` still advertises `feature/parser` among the active branches. The commits are already part of the project history, so the old remote branch name is no longer needed.

You are on `main`. Remove `feature/parser` from the remote; this exercise only asks for the shared branch cleanup, not deletion of the local copy.

**Starting point:** You are on `main`; available local branches: `main`, `feature/parser`. `origin` is available and has the branch.

**Real-World Context**

The parser changes remain in the merged history; deleting its old remote branch removes only the branch name.

**Your Task**

Delete the merged `feature/parser` branch from `origin`. Keep the local branch.

**Objective Checklist**

- [ ] Delete feature/parser from origin.
- [ ] Your local feature/parser branch still exists.

**Answer Key**

1. `git push origin --delete feature/parser`

**Accepted Alternatives**

- `git push -d origin feature/parser`, `git push origin -d feature/parser`, `git push origin :feature/parser`, `git push origin --delete refs/heads/feature/parser`.

**Expected Result**

`feature/parser` is gone from the server. Your local copy is still there.

**Evaluation**

- Remote `origin` has no `feature/parser`; local `feature/parser` exists; `origin/feature/parser` record removed.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.9.4 Delete origin/feature/group-auth · Easy

**Variant ID:** `rb-easy-cap-group`

**Story**

Your capstone group merged `feature/group-auth` into `main` yesterday, then moved straight to presentation slides. Sage opens the remote branch list today and finds the old feature name still there.

“Let’s leave a tidy repository for the next group member,” she says. You are on `main`, with the shared remote named `origin`. Delete `feature/group-auth` from that remote; your local branch can remain.

**Starting point:** You are on `main`; available local branches: `main`, `feature/group-auth`. `origin` is available and has the branch.

**Real-World Context**

The group already merged authentication. Removing the remote feature branch prevents classmates from starting new work on a closed line.

**Your Task**

Delete the merged `feature/group-auth` branch from `origin`. Keep the local branch.

**Objective Checklist**

- [ ] Delete feature/group-auth from origin.
- [ ] Your local feature/group-auth branch still exists.

**Answer Key**

1. `git push origin --delete feature/group-auth`

**Accepted Alternatives**

- `git push -d origin feature/group-auth`, `git push origin -d feature/group-auth`, `git push origin :feature/group-auth`, `git push origin --delete refs/heads/feature/group-auth`.

**Expected Result**

`feature/group-auth` is gone from the server. Your local copy is still there.

**Evaluation**

- Remote `origin` has no `feature/group-auth`; local `feature/group-auth` exists; `origin/feature/group-auth` record removed.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.9.5 Delete origin/feature/sprint12-compliance · Easy

**Variant ID:** `rb-easy-corp-sprint`

**Story**

Sprint 12 is closed in the project tracker, and the compliance feature has already been merged. Raven sees `feature/sprint12-compliance` still sitting on `origin`, making the branch list look as though the ticket is open.

You are on `main`. “Remove the shared branch name so it matches the tracker,” she says. Delete that remote branch; this task does not ask you to remove your separate local copy.

**Starting point:** You are on `main`; available local branches: `main`, `feature/sprint12-compliance`. `origin` is available and has the branch.

**Real-World Context**

The tracker says the sprint branch is closed, so its remote name no longer needs to appear among active branches.

**Your Task**

Delete the merged `feature/sprint12-compliance` branch from `origin`. Keep the local branch.

**Objective Checklist**

- [ ] Delete feature/sprint12-compliance from origin.
- [ ] Your local feature/sprint12-compliance branch still exists.

**Answer Key**

1. `git push origin --delete feature/sprint12-compliance`

**Accepted Alternatives**

- `git push -d origin feature/sprint12-compliance`, `git push origin -d feature/sprint12-compliance`, `git push origin :feature/sprint12-compliance`, `git push origin --delete refs/heads/feature/sprint12-compliance`.

**Expected Result**

`feature/sprint12-compliance` is gone from the server. Your local copy is still there.

**Evaluation**

- Remote `origin` has no `feature/sprint12-compliance`; local `feature/sprint12-compliance` exists; `origin/feature/sprint12-compliance` record removed.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 2.9.6 Prune stale origin/feature/auth ref · Medium

**Variant ID:** `v29m-auth`

**Story**

Finn opens your branch list and sees `origin/feature/auth`, even though someone already deleted that branch from the server. Your local record of remote branches has not caught up.

“That entry is an old address, not a live branch,” he explains. You are on `main` and also have a separate local `feature/auth` branch. Refresh information from `origin` while pruning deleted remote names. Keep your local feature branch untouched.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`; `origin` is available.

**Real-World Context**

Pruning updates your local records of remote branches that have disappeared. It does not delete your separate local `feature/auth` branch.

**Your Task**

Refresh remote tracking information from `origin` and remove the stale `origin/feature/auth` record. Keep your local `feature/auth` branch.

**Objective Checklist**

- [ ] Prune the stale origin/feature/auth remote-tracking ref.
- [ ] Your local feature/auth branch still exists.

**Answer Key**

1. `git fetch --prune origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P37.

**Expected Result**

The outdated `origin/feature/auth` name is gone. Your own `feature/auth` branch is untouched.

**Evaluation**

- `origin/feature/auth` absent; local `feature/auth` exists.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.9.7 Prune stale origin/feature/orders ref · Medium

**Variant ID:** `v29m-orders`

**Story**

A teammate removed `feature/orders` from `origin` after its work was merged. Sage checks your repository and finds the old `origin/feature/orders` tracking name still displayed.

You are on `main`, and a separate local `feature/orders` branch exists as well. “Update our view of the server,” she says. Fetch with pruning to remove the outdated remote tracking record, while leaving your local orders branch alone.

**Starting point:** You are on `main`; available local branches: `main`, `feature/orders`; `origin` is available.

**Real-World Context**

`origin/feature/orders` can remain visible locally after deletion on the server. Fetch with pruning clears that outdated record.

**Your Task**

Refresh remote tracking information from `origin` and remove the stale `origin/feature/orders` record. Keep your local `feature/orders` branch.

**Objective Checklist**

- [ ] Prune the stale origin/feature/orders remote-tracking ref.
- [ ] Your local feature/orders branch still exists.

**Answer Key**

1. `git fetch --prune origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P37.

**Expected Result**

The outdated `origin/feature/orders` name is gone. Your own `feature/orders` branch is untouched.

**Evaluation**

- `origin/feature/orders` absent; local `feature/orders` exists.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.9.8 Prune stale origin/feature/parser ref · Medium

**Variant ID:** `v29m-parser`

**Story**

Raven is looking for active parser work and spots `origin/feature/parser` in your local records. The branch was actually deleted on the remote days ago; only your cached view is stale.

You are on `main` and still have a local `feature/parser`. “Let’s clear the misleading remote entry,” she says. Refresh from `origin` with pruning, which removes records of deleted remote branches without deleting the independent local branch.

**Starting point:** You are on `main`; available local branches: `main`, `feature/parser`; `origin` is available.

**Real-World Context**

A stale remote tracking name can mislead you into thinking parser work is still published. Pruning refreshes that view.

**Your Task**

Refresh remote tracking information from `origin` and remove the stale `origin/feature/parser` record. Keep your local `feature/parser` branch.

**Objective Checklist**

- [ ] Prune the stale origin/feature/parser remote-tracking ref.
- [ ] Your local feature/parser branch still exists.

**Answer Key**

1. `git fetch --prune origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P37.

**Expected Result**

The outdated `origin/feature/parser` name is gone. Your own `feature/parser` branch is untouched.

**Evaluation**

- `origin/feature/parser` absent; local `feature/parser` exists.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.9.9 Prune stale origin/feature/old-landing ref · Medium

**Variant ID:** `rb-med-free-prune`

**Story**

The client abandoned an old landing page concept and deleted `feature/old-landing` from their remote repository. Sage checks your branch list and still sees `origin/feature/old-landing` because your local view has not been refreshed.

You are on `main`, and your separate local feature branch remains. “Let’s show what is actually on the server,” she says. Fetch from `origin` with pruning to clear the stale remote tracking name; keep the local branch.

**Starting point:** You are on `main`; available local branches: `main`, `feature/old-landing`; `origin` is available.

**Real-World Context**

The client removed the old landing branch remotely; pruning removes the obsolete local record of it while leaving local branches alone.

**Your Task**

Refresh remote tracking information from `origin` and remove the stale `origin/feature/old-landing` record. Keep your local `feature/old-landing` branch.

**Objective Checklist**

- [ ] Prune the stale origin/feature/old-landing remote-tracking ref.
- [ ] Your local feature/old-landing branch still exists.

**Answer Key**

1. `git fetch --prune origin`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P37.

**Expected Result**

The outdated `origin/feature/old-landing` name is gone. Your own `feature/old-landing` branch is untouched.

**Evaluation**

- `origin/feature/old-landing` absent; local `feature/old-landing` exists.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 2.9.10 Retire feature/auth on origin and locally · Hard

**Variant ID:** `v29h-auth`

**Story**

The auth work is merged, and Finn wants the finished branch cleaned up in both places. `feature/auth` is still on `origin`, and you also have a local branch with that name. You are on `main`.

“One name is on the server, the other is on your machine,” he reminds you. He also wants the cleanup to refuse if the local branch were ever holding unmerged work.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth`. `origin` is available and has the branch.

**Real-World Context**

Deleting from `origin` and deleting a local branch are separate actions. This exercise asks for both after the auth work was merged.

**Your Task**

The `feature/auth` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Objective Checklist**

- [ ] Delete feature/auth from origin.
- [ ] Delete the local feature/auth branch.
- [ ] main is checked out.

**Answer Key**

1. `git push origin --delete feature/auth`
2. `git branch -d feature/auth`

**Accepted Alternatives**

- `git push -d origin feature/auth`, `git push origin -d feature/auth`, `git push origin :feature/auth`, `git push origin --delete refs/heads/feature/auth`.
- `git branch --delete feature/auth`; `git branch -D feature/auth` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git branch -D feature/auth` is accepted (same end state) but earns the hint that `-d` is the safe default.

**Expected Result**

`feature/auth` is gone from the server and from your repository.

**Evaluation**

- Remote has no `feature/auth`; local `feature/auth` absent; HEAD on `main`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.9.11 Retire feature/orders on origin and locally · Hard

**Variant ID:** `v29h-orders`

**Story**

Finn closes the orders ticket and notices two leftover branch names: `feature/orders` on `origin` and a local copy in your repository. The changes are already merged, so neither name is needed. You are on `main`.

“Let’s clear both lists while the ticket is fresh,” he says. The local cleanup should not be able to throw away unmerged work.

**Starting point:** You are on `main`; available local branches: `main`, `feature/orders`. `origin` is available and has the branch.

**Real-World Context**

Once the orders work is integrated, the team can remove both the shared branch name and its local counterpart.

**Your Task**

The `feature/orders` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Objective Checklist**

- [ ] Delete feature/orders from origin.
- [ ] Delete the local feature/orders branch.
- [ ] main is checked out.

**Answer Key**

1. `git push origin --delete feature/orders`
2. `git branch -d feature/orders`

**Accepted Alternatives**

- `git push -d origin feature/orders`, `git push origin -d feature/orders`, `git push origin :feature/orders`, `git push origin --delete refs/heads/feature/orders`.
- `git branch --delete feature/orders`; `git branch -D feature/orders` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git branch -D feature/orders` is accepted (same end state) but earns the hint that `-d` is the safe default.

**Expected Result**

`feature/orders` is gone from the server and from your repository.

**Evaluation**

- Remote has no `feature/orders`; local `feature/orders` absent; HEAD on `main`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.9.12 Retire feature/parser on origin and locally · Hard

**Variant ID:** `v29h-parser`

**Story**

The parser changes are in the project history, but Sage finds `feature/parser` in both the remote and local branch lists.

You are on `main` and no one is using that old feature line for new work. “Two places to tidy,” she says, tapping the two lists. The actual parser commits remain in the branch where they were merged.

**Starting point:** You are on `main`; available local branches: `main`, `feature/parser`. `origin` is available and has the branch.

**Real-World Context**

A merged parser change remains in history even after its remote and local branch names are removed.

**Your Task**

The `feature/parser` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Objective Checklist**

- [ ] Delete feature/parser from origin.
- [ ] Delete the local feature/parser branch.
- [ ] main is checked out.

**Answer Key**

1. `git push origin --delete feature/parser`
2. `git branch -d feature/parser`

**Accepted Alternatives**

- `git push -d origin feature/parser`, `git push origin -d feature/parser`, `git push origin :feature/parser`, `git push origin --delete refs/heads/feature/parser`.
- `git branch --delete feature/parser`; `git branch -D feature/parser` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git branch -D feature/parser` is accepted (same end state) but earns the hint that `-d` is the safe default.

**Expected Result**

`feature/parser` is gone from the server and from your repository.

**Evaluation**

- Remote has no `feature/parser`; local `feature/parser` absent; HEAD on `main`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 2.9.13 Retire feature/oss-contribution on origin and locally · Hard

**Variant ID:** `rb-hard-oss-full`

**Story**

The open source maintainer merges your contribution and thanks you for the fix. Raven checks your fork afterward: `feature/oss-contribution` still exists on its `origin` remote and in your local repository. The pull request is done, and you are back on `main`.

“Let’s close the loop,” she says. Your contribution remains in the project’s merged history.

**Starting point:** You are on `main`; available local branches: `main`, `feature/oss-contribution`. `origin` is available and has the branch.

**Real-World Context**

The contribution is integrated. Cleaning up both branch names leaves the repository focused on active work.

**Your Task**

The `feature/oss-contribution` branch has been merged, so retire it everywhere: remove it from `origin` and remove your local copy, but __only through a route that would refuse to delete unmerged work__. Finish on `main`.

**Objective Checklist**

- [ ] Delete feature/oss-contribution from origin.
- [ ] Delete the local feature/oss-contribution branch.
- [ ] main is checked out.

**Answer Key**

1. `git push origin --delete feature/oss-contribution`
2. `git branch -d feature/oss-contribution`

**Accepted Alternatives**

- `git push -d origin feature/oss-contribution`, `git push origin -d feature/oss-contribution`, `git push origin :feature/oss-contribution`, `git push origin --delete refs/heads/feature/oss-contribution`.
- `git branch --delete feature/oss-contribution`; `git branch -D feature/oss-contribution` is accepted (same end state) but the explanation should tell the learner `-d` is the safe default.
- `git branch -D feature/oss-contribution` is accepted (same end state) but earns the hint that `-d` is the safe default.

**Expected Result**

`feature/oss-contribution` is gone from the server and from your repository.

**Evaluation**

- Remote has no `feature/oss-contribution`; local `feature/oss-contribution` absent; HEAD on `main`.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 3.1.1 Resolve src/auth.js · Easy

**Variant ID:** `manual-easy-auth-copy`

**Story**

The auth team is merging `feature/auth-timeout` into `main` before a test run. Sage sees that both branches changed `src/auth.js`: one adjusted the timeout, while the other added retry behavior. Git stops at the same lines and asks for a decision.

“We need the longer timeout and retries together,” she says. You are on `main`; the feature branch is available locally.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth-timeout`; the next merge will report a conflict.

**Real-World Context**

When two branches edit the same lines, Git pauses. A person must decide the final file, stage that decision, and commit to finish the merge. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/auth-timeout` into your current `main` branch. Resolve `src/auth.js` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/auth.js`

```
timeout=5000
retry=enabled
```

**Objective Checklist**

- [ ] src/auth.js contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/auth-timeout.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/auth-timeout`
2. In the simulator's file editor, set `src/auth.js` to exactly:

   ```
   timeout=5000
   retry=enabled
   ```
3. `git add src/auth.js`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/auth.js` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/auth-timeout`; `src/auth.js` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.1.2 Resolve src/profile.tsx · Easy

**Variant ID:** `manual-easy-profile-copy`

**Story**

Finn opens the new profile screen and notices that the title and subtitle came from different teammates. Both edits landed in `src/profile.tsx`, so merging `feature/profile-copy` into `main` produces a conflict.

“The heading should say Account profile, but keep Member profile underneath,” he says. You are already on `main`. The preview cannot proceed until the merge is finished.

**Starting point:** You are on `main`; available local branches: `main`, `feature/profile-copy`; the next merge will report a conflict.

**Real-World Context**

UI copy is easy to lose during a conflict. Reviewing the title and subtitle together preserves the intended wording from both lines of work. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/profile-copy` into your current `main` branch. Resolve `src/profile.tsx` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/profile.tsx`

```
title=Account profile
subtitle=Member profile
```

**Objective Checklist**

- [ ] src/profile.tsx contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/profile-copy.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/profile-copy`
2. In the simulator's file editor, set `src/profile.tsx` to exactly:

   ```
   title=Account profile
   subtitle=Member profile
   ```
3. `git add src/profile.tsx`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/profile.tsx` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/profile-copy`; `src/profile.tsx` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.1.3 Resolve src/billing.py · Easy

**Variant ID:** `manual-easy-billing-copy`

**Story**

The billing API is preparing to accept a second currency. Finn finds that `main` and `feature/regional-currency` both edited `src/billing.py` around the currency settings. Git cannot choose which version to keep.

The team wants PHP as the current currency while allowing PHP and EUR as supported options. You are on `main`, with the feature branch ready to merge. The billing tests cannot run until the merge is finished.

**Starting point:** You are on `main`; available local branches: `main`, `feature/regional-currency`; the next merge will report a conflict.

**Real-World Context**

A conflict in currency settings affects customer amounts. The agreed current and supported currencies must be recorded together before the merge can finish. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/regional-currency` into your current `main` branch. Resolve `src/billing.py` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/billing.py`

```
currency='PHP'
supported=['PHP','EUR']
```

**Objective Checklist**

- [ ] src/billing.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/regional-currency.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/regional-currency`
2. In the simulator's file editor, set `src/billing.py` to exactly:

   ```
   currency='PHP'
   supported=['PHP','EUR']
   ```
3. `git add src/billing.py`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/billing.py` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/regional-currency`; `src/billing.py` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.1.4 Resolve src/config.py · Easy

**Variant ID:** `manual-easy-config-copy`

**Story**

Finn is preparing a configuration change for the next deployment. The feature branch adds more helpful error messages, while `main` keeps debug mode off and the log level at INFO. Both branches changed `src/config.py`, so the merge stops.

“We can improve messages without turning on debug in production,” he says. You are on `main`. The deployment cannot proceed until the merge is finished.

**Starting point:** You are on `main`; available local branches: `main`, `feature/debug-config`; the next merge will report a conflict.

**Real-World Context**

Configuration conflicts can change runtime behavior. Keeping debug off while adding verbose error handling is a deliberate resolution, not a choice of one entire side. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/debug-config` into your current `main` branch. Resolve `src/config.py` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/config.py`

```
debug=False
log_level=INFO
verbose_errors=True
```

**Objective Checklist**

- [ ] src/config.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/debug-config.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/debug-config`
2. In the simulator's file editor, set `src/config.py` to exactly:

   ```
   debug=False
   log_level=INFO
   verbose_errors=True
   ```
3. `git add src/config.py`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/config.py` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/debug-config`; `src/config.py` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.1.5 Resolve src/components/Navbar.tsx · Easy

**Variant ID:** `manual-easy-navbar-copy`

**Story**

The front-end team has approved a small rebrand. Sage opens the navigation preview and sees two competing edits to `src/components/Navbar.tsx`: the existing brand name and a new Beta tagline. Git pauses when you merge `feature/navbar-rebrand` into `main`.

“Keep MyApp as the brand and show Beta beneath it,” Sage says. You are on `main`, and both branches exist locally. The preview cannot proceed until the merge is finished.

**Starting point:** You are on `main`; available local branches: `main`, `feature/navbar-rebrand`; the next merge will report a conflict.

**Real-World Context**

A navigation conflict can combine a stable product name with a new release tagline. The resolved component must contain the approved values. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/navbar-rebrand` into your current `main` branch. Resolve `src/components/Navbar.tsx` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/components/Navbar.tsx`

```
brand=MyApp
tagline=Beta
```

**Objective Checklist**

- [ ] src/components/Navbar.tsx contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/navbar-rebrand.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/navbar-rebrand`
2. In the simulator's file editor, set `src/components/Navbar.tsx` to exactly:

   ```
   brand=MyApp
   tagline=Beta
   ```
3. `git add src/components/Navbar.tsx`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/components/Navbar.tsx` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/navbar-rebrand`; `src/components/Navbar.tsx` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.1.6 Resolve src/routes.ts · Medium

**Variant ID:** `manual-medium-router`

**Story**

The group's support portal needs a routing update for tonight's integration build.

Finn merges `feature/routes` into `main`, but `src/routes.ts` was edited on both sides, and Git stops. The two of you reviewed both versions and settled on one agreed result, which is written out in your task.

**Starting point:** You are on `main`; available local branches: `main`, `feature/routes`; the next merge will report a conflict.

**Real-World Context**

A routing conflict can remove a working destination if only one side is kept. The agreed routes preserve the home page and add the support page. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/routes` into your current `main` branch. Resolve `src/routes.ts` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/routes.ts`

```
export const routes = ["/", "/support"];
```

**Objective Checklist**

- [ ] src/routes.ts contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/routes.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/routes`
2. In the simulator's file editor, set `src/routes.ts` to exactly:

   ```
   export const routes = ["/", "/support"];
   ```
3. `git add src/routes.ts`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/routes.ts` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/routes`; `src/routes.ts` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.1.7 Resolve src/policy.yml · Medium

**Variant ID:** `manual-medium-policy`

**Story**

Maeve is merging a policy update right before the integration tests. Git stops because both `main` and `feature/policy` changed `src/policy.yml`.

The group has already decided what the final file should say; it's listed in your task. Until the merge is finished, the tests can't run.

**Starting point:** You are on `main`; available local branches: `main`, `feature/policy`; the next merge will report a conflict.

**Real-World Context**

Access rules control who may use protected features. The agreed policy denies access by default and allows the librarian role. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/policy` into your current `main` branch. Resolve `src/policy.yml` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`src/policy.yml`

```
access:
  default: deny
  allow_roles:
    - librarian
```

**Objective Checklist**

- [ ] src/policy.yml contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/policy.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/policy`
2. In the simulator's file editor, set `src/policy.yml` to exactly:

   ```
   access:
     default: deny
     allow_roles:
       - librarian
   ```
3. `git add src/policy.yml`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/policy.yml` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/policy`; `src/policy.yml` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.1.8 Resolve config/gateway.yml · Medium

**Variant ID:** `manual-medium-gateway`

**Story**

Two teammates edited `config/gateway.yml` on different branches, and Sage's attempt to bring `feature/gateway` into `main` stops at that file.

The gateway work is blocking the next integration, and the final contents have been agreed. They're in your task.

**Starting point:** You are on `main`; available local branches: `main`, `feature/gateway`; the next merge will report a conflict.

**Real-World Context**

Timeout and retry settings work together when requests are slow. The agreed configuration keeps a 30-second timeout and three retries. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/gateway` into your current `main` branch. Resolve `config/gateway.yml` in the simulator’s file editor to contain exactly the lines shown below, with no conflict markers. Stage the file and finish the merge.

**Required resolved file content**

`config/gateway.yml`

```
gateway:
  timeout_seconds: 30
  retry_count: 3
```

**Objective Checklist**

- [ ] config/gateway.yml contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/gateway.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/gateway`
2. In the simulator's file editor, set `config/gateway.yml` to exactly:

   ```
   gateway:
     timeout_seconds: 30
     retry_count: 3
   ```
3. `git add config/gateway.yml`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`config/gateway.yml` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/gateway`; `config/gateway.yml` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.1.9 Resolve src/pricing.rb · Hard

**Variant ID:** `manual-hard-pricing`

**Story**

Raven is preparing the pricing release when she finds that `src/pricing.rb` changed on both `main` and `feature/pricing`.

Shipping whichever side Git happens to show first would be a guess. The reviewed result is in your task, and the release is waiting on it.

**Starting point:** You are on `main`; available local branches: `main`, `feature/pricing`; the next merge will report a conflict.

**Real-World Context**

A pricing merge must preserve the agreed calculation. This version applies a 10 percent discount to a base price of 100. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/pricing` into your current `main` branch so that `src/pricing.rb` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required resolved file content**

`src/pricing.rb`

```
BASE_PRICE = 100
DISCOUNT_PERCENT = 10
def final_price
  BASE_PRICE * (100 - DISCOUNT_PERCENT) / 100.0
end
```

**Objective Checklist**

- [ ] src/pricing.rb contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/pricing.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/pricing`
2. In the simulator's file editor, set `src/pricing.rb` to exactly:

   ```
   BASE_PRICE = 100
   DISCOUNT_PERCENT = 10
   def final_price
     BASE_PRICE * (100 - DISCOUNT_PERCENT) / 100.0
   end
   ```
3. `git add src/pricing.rb`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`src/pricing.rb` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/pricing`; `src/pricing.rb` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.1.10 Resolve schema/orders.sql · Hard

**Variant ID:** `manual-hard-schema`

**Story**

The warehouse team is lining up an orders schema change for release, but `main` and `feature/schema` both changed `schema/orders.sql`, so Git can't combine them on its own.

Finn has reviewed both versions and written down the agreed result. It's in your task.

**Starting point:** You are on `main`; available local branches: `main`, `feature/schema`; the next merge will report a conflict.

**Real-World Context**

A schema defines the fields the application can store. This orders table retains a customer name and gives new orders a pending status. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/schema` into your current `main` branch so that `schema/orders.sql` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required resolved file content**

`schema/orders.sql`

```
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
);
```

**Objective Checklist**

- [ ] schema/orders.sql contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/schema.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/schema`
2. In the simulator's file editor, set `schema/orders.sql` to exactly:

   ```
   CREATE TABLE orders (
     id INTEGER PRIMARY KEY,
     customer_name TEXT NOT NULL,
     status TEXT NOT NULL DEFAULT 'pending'
   );
   ```
3. `git add schema/orders.sql`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`schema/orders.sql` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/schema`; `schema/orders.sql` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.1.11 Resolve db/migrations/001_users.sql · Hard

**Variant ID:** `manual-hard-migration`

**Story**

A user database migration is up for release review. Maeve looked at `db/migrations/001_users.sql` and saw different edits on `main` and `feature/migration`.

The merge will pause until someone decides what the file should say. That decision has been made and is recorded in your task.

**Starting point:** You are on `main`; available local branches: `main`, `feature/migration`; the next merge will report a conflict.

**Real-World Context**

A migration changes the database structure. This users table requires an email and display name and prevents duplicate email addresses. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Merge `feature/migration` into your current `main` branch so that `db/migrations/001_users.sql` ends up with exactly the lines shown below, no conflict markers remain, and the merge is complete.

**Required resolved file content**

`db/migrations/001_users.sql`

```
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL
);
```

**Objective Checklist**

- [ ] db/migrations/001_users.sql contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/migration.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/migration`
2. In the simulator's file editor, set `db/migrations/001_users.sql` to exactly:

   ```
   CREATE TABLE users (
     id INTEGER PRIMARY KEY,
     email TEXT NOT NULL UNIQUE,
     display_name TEXT NOT NULL
   );
   ```
3. `git add db/migrations/001_users.sql`
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`db/migrations/001_users.sql` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/migration`; `db/migrations/001_users.sql` equals the required content; no markers anywhere; clean tree.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.1.12 Abort a wrong merge, then resolve the right one · Hard

**Variant ID:** `manual-hard-abort-redo`

**Story**

The support portal’s help center needs a route beside its existing support route. Maeve asks you to merge `feature/help-center` into `main`, but a slip of the keyboard started a merge with `feature/legacy-help` instead, and Git has already stopped with a conflict in `src/routes.ts`. That branch should never reach `main`.

“Back it out cleanly,” Maeve says, “then bring in the right one. Keep both destinations, `/support` and `/help-center`, or one of the portal’s links will break.”

**Starting point:** You are on `main` with a merge of `feature/legacy-help` in progress, stopped on a conflict in `src/routes.ts`; available local branches: `main`, `feature/legacy-help`, `feature/help-center`.

**Real-World Context**

A merge that has stopped on a conflict can be cancelled, which puts the branch back exactly as it was before the merge started. After that, the right branch can be merged and the new conflict resolved. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

**Cancel the unwanted merge so `main` is exactly as it was before it started.** Then merge `feature/help-center` into `main` and resolve `src/routes.ts` to contain exactly the lines shown below, with no conflict markers. Complete the merge.

**Required resolved file content**

`src/routes.ts`

```
route('/support')
route('/help-center')
```

**Objective Checklist**

- [ ] The wrong merge (feature/legacy-help) left nothing behind in main’s history or files.
- [ ] src/routes.ts contains exactly the required lines.
- [ ] No conflict markers remain.
- [ ] main has a merge commit joining feature/help-center.
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge --abort`
2. `git merge feature/help-center`
3. In the simulator's file editor, set `src/routes.ts` to exactly:

   ```
   route('/support')
   route('/help-center')
   ```
4. `git add src/routes.ts`
5. `git commit --no-edit`

**Accepted Alternatives**

- `git reset --merge` or `git reset --hard HEAD` right after the wrong merge are accepted (same end state) but not CAR-accurate; `git merge --abort` is the expected answer.
- Common patterns that apply: P15, P16, P17, P18.

**Not accepted**

- `git checkout --ours <file>` / `git checkout --theirs <file>` are NOT enough here: the agreed result combines both sides, so the learner must edit the file.

**Expected Result**

`feature/legacy-help` never reached `main`. `feature/help-center` is merged, `/support` and `/help-center` are both routed, and the work is recorded on `main`.

**Evaluation**

- No ancestor of HEAD is a commit from `feature/legacy-help`; tip is a 2-parent merge of `feature/help-center`; `src/routes.ts` equals the required content; clean tree.
- Process: the first merge must have been cancelled (no merge commit that includes the legacy branch).
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 3.2.1 Resolve src/cache.py in the merge tool · Easy

**Variant ID:** `mergetool-easy-cache-ttl`

**Story**

Sage is merging `feature/cache-ttl` into `main` before the nightly build. Both branches touched `src/cache.py`: one lengthened how long cached results live, the other made caching switchable. Git stops on the same lines and cannot choose.

“The tool shows you both sides next to each other,” Sage says. “Use it, and keep the longer lifetime together with the switch.” You are on `main`, and the feature branch is available locally.

**Starting point:** You are on `main`; available local branches: `main`, `feature/cache-ttl`; the next merge will report a conflict.

**Real-World Context**

A merge tool shows your version, the incoming version and the result side by side, so you can pick or combine lines without hunting for conflict markers in a text file.

**Your Task**

Merge `feature/cache-ttl` into your current `main` branch. Use the simulator’s merge tool to resolve `src/cache.py` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/cache.py`

```
CACHE_TTL = 300
CACHE_ENABLED = True
```

**Objective Checklist**

- [ ] src/cache.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/cache-ttl.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/cache-ttl`
2. `git mergetool`
3. In the simulator's file editor, set `src/cache.py` to exactly:

   ```
   CACHE_TTL = 300
   CACHE_ENABLED = True
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/cache.py` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/cache-ttl`; `src/cache.py` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.2.2 Resolve src/mailer.py in the merge tool · Easy

**Variant ID:** `mergetool-easy-mail-footer`

**Story**

The library system’s email sender changed in two places at once. One teammate set the sender address, and another added a footer line. Finn tries to merge `feature/mail-footer` into `main` and Git stops in `src/mailer.py`.

“Open the merge tool and keep both settings,” Finn says. You are on `main`, with the feature branch ready locally.

**Starting point:** You are on `main`; available local branches: `main`, `feature/mail-footer`; the next merge will report a conflict.

**Real-World Context**

Settings that sit on neighbouring lines often conflict even when they do not contradict each other. The merge tool lets you keep both.

**Your Task**

Merge `feature/mail-footer` into your current `main` branch. Use the simulator’s merge tool to resolve `src/mailer.py` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/mailer.py`

```
SENDER = "no-reply@library.test"
FOOTER = "Sent by the library system"
```

**Objective Checklist**

- [ ] src/mailer.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/mail-footer.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/mail-footer`
2. `git mergetool`
3. In the simulator's file editor, set `src/mailer.py` to exactly:

   ```
   SENDER = "no-reply@library.test"
   FOOTER = "Sent by the library system"
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/mailer.py` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/mail-footer`; `src/mailer.py` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.2.3 Resolve src/limits.js in the merge tool · Easy

**Variant ID:** `mergetool-easy-upload-limit`

**Story**

The upload page has two pending changes: a smaller file-size limit and a list of accepted file types.

Both landed in `src/limits.js`, so merging `feature/upload-limit` into `main` stops. Raven wants both rules live before the demo and suggests the merge tool, since the two sides are short enough to compare at a glance. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/upload-limit`; the next merge will report a conflict.

**Real-World Context**

When both sides add something useful, the merge tool’s result pane can combine them without losing either.

**Your Task**

Merge `feature/upload-limit` into your current `main` branch. Use the simulator’s merge tool to resolve `src/limits.js` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/limits.js`

```
maxUploadMb: 20
allowedTypes: ['pdf', 'png']
```

**Objective Checklist**

- [ ] src/limits.js contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/upload-limit.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/upload-limit`
2. `git mergetool`
3. In the simulator's file editor, set `src/limits.js` to exactly:

   ```
   maxUploadMb: 20
   allowedTypes: ['pdf', 'png']
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/limits.js` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/upload-limit`; `src/limits.js` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.2.4 Resolve config/app.ini in the merge tool · Easy

**Variant ID:** `mergetool-easy-app-locale`

**Story**

A new regional setup needs the app to use Philippine English and Manila time. Maeve added the locale on one branch while a teammate added the timezone on another, and both edits are in `config/app.ini`. When you merge `feature/app-locale` into `main`, Git stops.

“Compare the two sides in the merge tool before you save anything,” Maeve says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/app-locale`; the next merge will report a conflict.

**Real-World Context**

Configuration files are a common place for conflicts, because many people edit the same short block.

**Your Task**

Merge `feature/app-locale` into your current `main` branch. Use the simulator’s merge tool to resolve `config/app.ini` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`config/app.ini`

```
[app]
locale = en_PH
timezone = Asia/Manila
```

**Objective Checklist**

- [ ] config/app.ini contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/app-locale.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/app-locale`
2. `git mergetool`
3. In the simulator's file editor, set `config/app.ini` to exactly:

   ```
   [app]
   locale = en_PH
   timezone = Asia/Manila
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`config/app.ini` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/app-locale`; `config/app.ini` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.2.5 Resolve src/labels.ts in the merge tool · Easy

**Variant ID:** `mergetool-easy-labels`

**Story**

The mobile app is getting Filipino labels. One teammate rewrote the greeting and another added the farewell, both in `src/labels.ts`. Merging `feature/labels-fil` into `main` stops on those lines. “Both labels ship together,” Finn says, opening the merge tool for you.

You are on `main`, with the feature branch available.

**Starting point:** You are on `main`; available local branches: `main`, `feature/labels-fil`; the next merge will report a conflict.

**Real-World Context**

Text labels are small, but a lost line means a missing word on a real screen. Check the result pane before you save.

**Your Task**

Merge `feature/labels-fil` into your current `main` branch. Use the simulator’s merge tool to resolve `src/labels.ts` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/labels.ts`

```
export const greeting = "Hello";
export const farewell = "Paalam";
```

**Objective Checklist**

- [ ] src/labels.ts contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/labels-fil.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/labels-fil`
2. `git mergetool`
3. In the simulator's file editor, set `src/labels.ts` to exactly:

   ```
   export const greeting = "Hello";
   export const farewell = "Paalam";
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/labels.ts` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/labels-fil`; `src/labels.ts` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 12

---

### 3.2.6 Resolve two checkout files in the merge tool · Medium

**Variant ID:** `mergetool-medium-checkout-copy`

**Story**

The checkout screen and its receipt were reworded by two different teammates at the same time. Merging `feature/checkout-copy` into `main` stops in two files, `src/checkout.js` and `src/receipt.js`, and each needs its own decision.

Sage opens the merge tool and says, “It takes the files one at a time. *Don’t rush the second one.*” You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/checkout-copy`; the next merge will report conflicts in two files.

**Real-World Context**

A merge can conflict in several files. The merge tool walks through them in turn, and each result still has to be checked.

**Your Task**

Merge `feature/checkout-copy` into your current `main` branch. Use the simulator’s merge tool to resolve both files so that each contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/checkout.js`

```
title = "Checkout"
button = "Pay now"
```

`src/receipt.js`

```
header = "Receipt"
footer = "Thank you"
```

**Objective Checklist**

- [ ] src/checkout.js contains exactly the required lines.
- [ ] src/receipt.js contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/checkout-copy.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/checkout-copy`
2. `git mergetool`
3. In the simulator's file editor, set `src/checkout.js` to exactly:

   ```
   title = "Checkout"
   button = "Pay now"
   ```
4. In the simulator's file editor, set `src/receipt.js` to exactly:

   ```
   header = "Receipt"
   footer = "Thank you"
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/checkout.js`, `src/receipt.js` hold the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/checkout-copy`; `src/checkout.js` equals the required content; `src/receipt.js` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.2.7 Resolve rate-limit and CORS settings in the merge tool · Medium

**Variant ID:** `mergetool-medium-api-limits`

**Story**

Two configuration files changed on both sides of a merge: `config/limits.yml`, where the request limits were adjusted, and `config/cors.yml`, where an allowed origin was added. When Finn merges `feature/api-limits` into `main`, Git stops on both.

“Settings files are tiny, but a wrong indent can break the whole service,” he says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/api-limits`; the next merge will report conflicts in two files.

**Real-World Context**

In YAML files, indentation is part of the meaning. The result must keep the spacing exactly as agreed.

**Your Task**

Merge `feature/api-limits` into your current `main` branch. Use the simulator’s merge tool to resolve both files so that each contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`config/limits.yml`

```
limits:
  requests_per_minute: 60
  burst: 10
```

`config/cors.yml`

```
cors:
  origins:
    - https://library.test
```

**Objective Checklist**

- [ ] config/limits.yml contains exactly the required lines.
- [ ] config/cors.yml contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/api-limits.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/api-limits`
2. `git mergetool`
3. In the simulator's file editor, set `config/limits.yml` to exactly:

   ```
   limits:
     requests_per_minute: 60
     burst: 10
   ```
4. In the simulator's file editor, set `config/cors.yml` to exactly:

   ```
   cors:
     origins:
       - https://library.test
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`config/limits.yml`, `config/cors.yml` hold the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/api-limits`; `config/limits.yml` equals the required content; `config/cors.yml` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.2.8 Resolve two schema files in the merge tool · Medium

**Variant ID:** `mergetool-medium-db-names`

**Story**

The database team renamed columns on one branch while another teammate added keys on a second, and both touched `schema/books.sql` and `schema/authors.sql`. Merging `feature/db-rename` into `main` stops on both files. Raven has the agreed result written down and wants it checked carefully, since schema mistakes are expensive to undo.

You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/db-rename`; the next merge will report conflicts in two files.

**Real-World Context**

Schema files define what the application can store. After a merge, the result must be checked as carefully as new code.

**Your Task**

Merge `feature/db-rename` into your current `main` branch. Use the simulator’s merge tool to resolve both files so that each contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`schema/books.sql`

```
CREATE TABLE books (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL
);
```

`schema/authors.sql`

```
CREATE TABLE authors (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
```

**Objective Checklist**

- [ ] schema/books.sql contains exactly the required lines.
- [ ] schema/authors.sql contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/db-rename.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/db-rename`
2. `git mergetool`
3. In the simulator's file editor, set `schema/books.sql` to exactly:

   ```
   CREATE TABLE books (
     id INTEGER PRIMARY KEY,
     title TEXT NOT NULL
   );
   ```
4. In the simulator's file editor, set `schema/authors.sql` to exactly:

   ```
   CREATE TABLE authors (
     id INTEGER PRIMARY KEY,
     name TEXT NOT NULL
   );
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`schema/books.sql`, `schema/authors.sql` hold the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/db-rename`; `schema/books.sql` equals the required content; `schema/authors.sql` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.2.9 Resolve two documentation files in the merge tool · Medium

**Variant ID:** `mergetool-medium-docs-sync`

**Story**

Two writers updated the setup and usage guides at the same time. Merging `feature/docs-sync` into `main` stops in `docs/setup.md` and `docs/usage.md`. Maeve does not want half-merged docs in front of new teammates tomorrow.

“Open the tool, settle both pages, and then we’re done,” she says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/docs-sync`; the next merge will report conflicts in two files.

**Real-World Context**

Documentation conflicts are easy to resolve badly, because a result can look fine while a sentence is missing.

**Your Task**

Merge `feature/docs-sync` into your current `main` branch. Use the simulator’s merge tool to resolve both files so that each contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`docs/setup.md`

```
# Setup
Install Python 3.12.
```

`docs/usage.md`

```
# Usage
Run the app with python main.py.
```

**Objective Checklist**

- [ ] docs/setup.md contains exactly the required lines.
- [ ] docs/usage.md contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/docs-sync.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/docs-sync`
2. `git mergetool`
3. In the simulator's file editor, set `docs/setup.md` to exactly:

   ```
   # Setup
   Install Python 3.12.
   ```
4. In the simulator's file editor, set `docs/usage.md` to exactly:

   ```
   # Usage
   Run the app with python main.py.
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`docs/setup.md`, `docs/usage.md` hold the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/docs-sync`; `docs/setup.md` equals the required content; `docs/usage.md` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 10

---

### 3.2.10 Resolve src/prices.py when no merge tool is set up · Hard

**Variant ID:** `mergetool-hard-choose-tool`

**Story**

A new laptop has just been issued to you, and Git has no merge tool configured on it. The team handbook names `meld` as the standard tool. Merging `feature/pricing-v2` into `main` stops in `src/prices.py`, because the base price and the discount were edited on separate branches.

Sage says, “Git can’t open a tool you haven’t told it about.” You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/pricing-v2`; no merge tool is configured; the next merge will report a conflict.

**Real-World Context**

A merge tool is a separate program. Git has to be told which one to use before it can open it, and that choice is stored in Git’s configuration.

**Your Task**

Merge `feature/pricing-v2` into your current `main` branch. Use the simulator’s merge tool to resolve `src/prices.py` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message. **The team’s tool is `meld`, and it is not configured yet.**

**Required resolved file content**

`src/prices.py`

```
PRICE = 100
DISCOUNT = 10
```

**Objective Checklist**

- [ ] Configure meld as the Git merge tool.
- [ ] src/prices.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/pricing-v2.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git config merge.tool meld`
2. `git merge feature/pricing-v2`
3. `git mergetool`
4. In the simulator's file editor, set `src/prices.py` to exactly:

   ```
   PRICE = 100
   DISCOUNT = 10
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- `git config --global merge.tool meld` is accepted (same effect for this repository).
- `git mergetool --tool=meld` or `git mergetool -t meld` is accepted in place of configuring first (the learner still reaches the same end state), but the checklist item about configuration stays unchecked.
- The configuration step may come before or after `git merge`, but must come before `git mergetool`.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/prices.py` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/pricing-v2`; `src/prices.py` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 3.2.11 Resolve only the conflicted file after a partial merge · Hard

**Variant ID:** `mergetool-hard-one-of-two`

**Story**

Merging `feature/release-notes` into `main` changes two files, but only one of them is in dispute. `docs/CHANGELOG.md` merged on its own, with both new entries, while `src/version.py` was edited on both sides and now needs a decision.

Finn warns you about the common mistake: “Don’t touch the file Git already merged. __Fix only the one it stopped on.__” You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/release-notes`; the next merge will report a conflict in one file.

**Real-World Context**

Git merges whatever it can on its own and stops only on the lines it cannot combine. Files that merged cleanly should be left alone.

**Your Task**

Merge `feature/release-notes` into your current `main` branch. Use the simulator’s merge tool to resolve `src/version.py` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/version.py`

```
VERSION = "2.1.0"
CODENAME = "Lantern"
```

**Objective Checklist**

- [ ] docs/CHANGELOG.md keeps both new entries exactly as Git merged them (it was not edited by hand).
- [ ] src/version.py contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/release-notes.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/release-notes`
2. `git mergetool`
3. In the simulator's file editor, set `src/version.py` to exactly:

   ```
   VERSION = "2.1.0"
   CODENAME = "Lantern"
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- The merge tool is only opened for `src/version.py`; if the learner also opens the changelog, the evaluator checks the file is byte-identical to Git’s automatic result.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/version.py` holds the agreed content, `docs/CHANGELOG.md` still has both entries from the automatic merge, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/release-notes`; `src/version.py` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.2.12 Keep the incoming version of src/i18n.json · Hard

**Variant ID:** `mergetool-hard-take-theirs`

**Story**

The translation team rewrote `src/i18n.json` on `feature/i18n-refresh` from scratch, while someone on `main` made small tweaks to the old file. The reviewers have decided the rewrite wins completely: *nothing from `main`’s tweaks should survive*.

When Raven merges `feature/i18n-refresh` into `main`, Git stops on that file. “The incoming side is the whole answer,” Raven says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/i18n-refresh`; the next merge will report a conflict.

**Real-World Context**

Sometimes the right resolution is to take one side entirely. Git can do this in a single step, and the merge tool can too.

**Your Task**

Merge `feature/i18n-refresh` into your current `main` branch. Use the simulator’s merge tool to resolve `src/i18n.json` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message.

**Required resolved file content**

`src/i18n.json`

```
{
  "greeting": "Kumusta",
  "farewell": "Paalam"
}
```

**Objective Checklist**

- [ ] src/i18n.json contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/i18n-refresh.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git merge feature/i18n-refresh`
2. `git mergetool`
3. In the simulator's file editor, set `src/i18n.json` to exactly:

   ```
   {
     "greeting": "Kumusta",
     "farewell": "Paalam"
   }
   ```
4. `git commit --no-edit`

**Accepted Alternatives**

- `git checkout --theirs src/i18n.json` (also `git checkout feature/i18n-refresh -- src/i18n.json`, `git restore --theirs src/i18n.json`) followed by `git add src/i18n.json` and a commit is accepted and is the shorter route.
- `git merge -X theirs feature/i18n-refresh` is accepted (no conflict arises) and counts as 1 command; the process objective about the merge tool is marked not applicable.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/i18n.json` is exactly the incoming version, nothing of `main`’s tweaks remains, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/i18n-refresh`; `src/i18n.json` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.2.13 Resolve src/auth.js and leave no backup files behind · Hard

**Variant ID:** `mergetool-hard-no-leftovers`

**Story**

Merging `feature/auth-timeout` into `main` stops in `src/auth.js`. Raven has resolved this kind of conflict before and gives you one warning:

“Some merge tools leave a backup copy next to the file, named like the original with `.orig` on the end. If you commit with those lying around, they end up in the history.”

The review tomorrow expects a clean folder and nothing stray in the commit. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`, `feature/auth-timeout`; the next merge will report a conflict. The merge tool saves a `src/auth.js.orig` backup unless told not to.

**Real-World Context**

Some merge tools save a backup of each conflicted file. Backups are clutter: they should not be committed, and they should not be left in the folder either.

**Your Task**

Merge `feature/auth-timeout` into your current `main` branch. Use the simulator’s merge tool to resolve `src/auth.js` so that it contains exactly the lines shown below, with no conflict markers. Complete the merge with the default merge message. **Finish with no leftover backup files in the folder and none in the commit.**

**Required resolved file content**

`src/auth.js`

```
timeout=5000
retry=enabled
```

**Objective Checklist**

- [ ] No src/auth.js.orig (or any other backup file) exists in the folder or in the commit.
- [ ] src/auth.js contains exactly the required lines.
- [ ] No conflict markers remain in any file.
- [ ] Complete the merge: main has a merge commit joining feature/auth-timeout.
- [ ] The merge tool was used to resolve the conflict (process check).
- [ ] main is checked out and the working folder is clean.

**Answer Key**

1. `git config mergetool.keepBackup false`
2. `git merge feature/auth-timeout`
3. `git mergetool`
4. In the simulator's file editor, set `src/auth.js` to exactly:

   ```
   timeout=5000
   retry=enabled
   ```
5. `git commit --no-edit`

**Accepted Alternatives**

- Alternative: run `git mergetool` first, then remove the backup (`rm src/auth.js.orig`, or `git clean -f src/auth.js.orig`) before committing; accepted, not CAR-accurate (an extra command).
- If the backup was committed, the scenario fails the 'none in the commit' objective even when the folder is later cleaned.
- Common patterns that apply: P9, P10, P11, P12, P13.

**Expected Result**

`src/auth.js` holds the agreed content, the conflict is gone, and the finished merge is recorded on `main`.

**Evaluation**

- HEAD on `main`; tip is a 2-parent merge of `feature/auth-timeout`; `src/auth.js` equals the required content; no markers; clean tree.
- Process: `git mergetool` ran during the conflict.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 3.3.1 Cherry-pick c1 onto release-1.0 · Easy

**Variant ID:** `cherry-easy-login-timeout`

**Story**

A login timeout fix has been committed as `c1` on another line of work. Customers still on `release-1.0` need that repair, but the rest of `main` contains features that this release cannot take. Finn says, “We need the one fix, not the whole branch.”

You are already on `release-1.0`. Apply only the changes from `c1` here as a new commit, leaving unrelated work behind.

**Starting point:** You are on `release-1.0`; available local branches: `main`, `release-1.0`.

**Real-World Context**

Cherry-pick copies one commit’s changes onto the current branch as a new commit. It brings a repair to an older release without merging an entire branch.

**Your Task**

Apply only the changes from commit `c1` to your current `release-1.0` branch as a new commit.

**Objective Checklist**

- [ ] Copy c1's changes onto release-1.0.
- [ ] Unrelated commits from the other branch were not copied.
- [ ] release-1.0 is checked out.

**Answer Key**

1. `git cherry-pick c1`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P25.

**Expected Result**

The fix from `c1` now exists as a new commit on `release-1.0`. Nothing else was copied.

**Evaluation**

- `release-1.0` +1 commit whose diff equals c1's diff; the other branch's unrelated commits absent; HEAD on `release-1.0`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 3.3.2 Cherry-pick c1 onto release-1.1 · Easy

**Variant ID:** `cherry-easy-invoice-rounding`

**Story**

Sage finds an invoice rounding bug on the maintained `release-1.1` line. The correction exists in commit `c1` elsewhere, but merging the full development branch would bring changes unrelated to invoicing. “Just bring over the rounding repair,” she says.

You are on `release-1.1`, and the commit is available in the repository. Apply that selected commit to your current branch so the older release gets the fix.

**Starting point:** You are on `release-1.1`; available local branches: `main`, `release-1.1`.

**Real-World Context**

Older supported releases often need a specific bug fix without unrelated development work. A cherry-pick applies just the selected commit.

**Your Task**

Apply only the changes from commit `c1` to your current `release-1.1` branch as a new commit.

**Objective Checklist**

- [ ] Copy c1's changes onto release-1.1.
- [ ] Unrelated commits from the other branch were not copied.
- [ ] release-1.1 is checked out.

**Answer Key**

1. `git cherry-pick c1`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P25.

**Expected Result**

The fix from `c1` now exists as a new commit on `release-1.1`. Nothing else was copied.

**Evaluation**

- `release-1.1` +1 commit whose diff equals c1's diff; the other branch's unrelated commits absent; HEAD on `release-1.1`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 3.3.3 Cherry-pick c1 onto release-2.0 · Easy

**Variant ID:** `cherry-easy-export-null`

**Story**

A report export crashes when a field is empty. Finn points to commit `c1`, which already contains the null check, but `release-2.0` does not have it yet. Other development commits are not part of this patch.

You are on the release branch and have a short window before the next test run. Copy the selected fix onto `release-2.0` as its own new commit.

**Starting point:** You are on `release-2.0`; available local branches: `main`, `release-2.0`.

**Real-World Context**

A release patch can reuse a fix already committed elsewhere. The new release commit has its own identity on the release branch.

**Your Task**

Apply only the changes from commit `c1` to your current `release-2.0` branch as a new commit.

**Objective Checklist**

- [ ] Copy c1's changes onto release-2.0.
- [ ] Unrelated commits from the other branch were not copied.
- [ ] release-2.0 is checked out.

**Answer Key**

1. `git cherry-pick c1`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P25.

**Expected Result**

The fix from `c1` now exists as a new commit on `release-2.0`. Nothing else was copied.

**Evaluation**

- `release-2.0` +1 commit whose diff equals c1's diff; the other branch's unrelated commits absent; HEAD on `release-2.0`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 3.3.4 Cherry-pick c1 onto release-1.2 · Easy

**Variant ID:** `cherry-easy-rate-limit`

**Story**

The API team discovers that older clients can trigger a rate limit error too quickly. Maeve has already reviewed the repair in commit `c1`. The maintained `release-1.2` branch needs that single correction, while the larger development branch still has unfinished work.

You are on `release-1.2`. Apply only `c1` to this branch as a new commit so the patch can ship independently.

**Starting point:** You are on `release-1.2`; available local branches: `main`, `release-1.2`.

**Real-World Context**

Targeted cherry-picks let a team ship a verified rate-limit fix while leaving newer, unfinished development changes behind.

**Your Task**

Apply only the changes from commit `c1` to your current `release-1.2` branch as a new commit.

**Objective Checklist**

- [ ] Copy c1's changes onto release-1.2.
- [ ] Unrelated commits from the other branch were not copied.
- [ ] release-1.2 is checked out.

**Answer Key**

1. `git cherry-pick c1`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P25.

**Expected Result**

The fix from `c1` now exists as a new commit on `release-1.2`. Nothing else was copied.

**Evaluation**

- `release-1.2` +1 commit whose diff equals c1's diff; the other branch's unrelated commits absent; HEAD on `release-1.2`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 3.3.5 Cherry-pick c1 onto release-2.1 · Easy

**Variant ID:** `cherry-easy-null-check`

**Story**

Sage finds a parser crash on an empty value in version 2.1. The correction is already saved in commit `c1` on another branch. “This release needs the guard, not the other features beside it,” she says.

You are on `release-2.1`, with the selected commit available. Apply `c1` to your current branch as a new commit, then keep working on the release from the repaired history.

**Starting point:** You are on `release-2.1`; available local branches: `main`, `release-2.1`.

**Real-World Context**

Copying the selected parser fix keeps the maintained release focused on a single needed correction.

**Your Task**

Apply only the changes from commit `c1` to your current `release-2.1` branch as a new commit.

**Objective Checklist**

- [ ] Copy c1's changes onto release-2.1.
- [ ] Unrelated commits from the other branch were not copied.
- [ ] release-2.1 is checked out.

**Answer Key**

1. `git cherry-pick c1`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P25.

**Expected Result**

The fix from `c1` now exists as a new commit on `release-2.1`. Nothing else was copied.

**Evaluation**

- `release-2.1` +1 commit whose diff equals c1's diff; the other branch's unrelated commits absent; HEAD on `release-2.1`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 3.3.6 Cherry-pick c1 and c2 onto release-1.0 · Medium

**Variant ID:** `cherry-medium-login-timeout`

**Story**

A support engineer asks whether the login timeout fix can reach `release-1.0` today. Raven finds the completed correction in commit `c1`, but it only works together with the test that came right after it, commit `c2`. The surrounding development work is still not ready for that release.

You are already on `release-1.0`. “Take just those two changes, in order, and keep the rest out,” she says.

**Starting point:** You are on `release-1.0`; available local branches: `main`, `release-1.0`. `c1` and `c2` are consecutive commits on `main`.

**Real-World Context**

A commit is a reusable record of a change. Several commits can be copied onto another branch one after another, as long as their order is kept.

**Your Task**

Apply the changes of `c1` and then `c2` to your current `release-1.0` branch as two new commits, keeping their order.

**Leave the rest of `main` behind.**

**Objective Checklist**

- [ ] Copy c1's changes and then c2's changes onto release-1.0, in order.
- [ ] No other commit from main was copied.
- [ ] release-1.0 is checked out.

**Answer Key**

1. `git cherry-pick c1`
2. `git cherry-pick c2`

**Accepted Alternatives**

- `git cherry-pick c1 c2` (one command, same result), `git cherry-pick c1^..c2` (a range).
- `git cherry-pick -x` adds a trailer to each message; accepted.

**Not accepted**

- `git cherry-pick c2` before `c1` is NOT accepted: the order of the new commits must match the originals.

**Expected Result**

`release-1.0` gained two new commits, in the same order as `c1` and `c2`. Nothing else was copied.

**Evaluation**

- `release-1.0` +2 commits whose diffs equal c1 then c2; no other commits; HEAD on `release-1.0`.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 3.3.7 Cherry-pick the newest invoice fix onto release-1.1 · Medium

**Variant ID:** `cherry-medium-invoice-rounding`

**Story**

An accountant spots a one-cent rounding error in invoices generated by `release-1.1`. Finn points to the branch `feature/invoice-rounding`, where the fix is finished as the branch’s newest commit. The release should not inherit the rest of that branch, or every newer feature, just to get that repair.

You are on `release-1.1`.

**Starting point:** You are on `release-1.1`; available local branches: `main`, `release-1.1`, `feature/invoice-rounding`.

**Real-World Context**

A branch name points to its newest commit, so a branch name can stand in for that single commit when copying a change.

**Your Task**

Apply __only__ the newest commit of `feature/invoice-rounding` to your current `release-1.1` branch as a new commit.

**Objective Checklist**

- [ ] Copy only the newest commit of feature/invoice-rounding onto release-1.1.
- [ ] The older commits of feature/invoice-rounding were not copied.
- [ ] release-1.1 is checked out.

**Answer Key**

1. `git cherry-pick feature/invoice-rounding`

**Accepted Alternatives**

- `git cherry-pick <tip-hash>` is accepted if the learner finds the hash with `git log feature/invoice-rounding` (not counted).
- `git cherry-pick feature/invoice-rounding~0` and `feature/invoice-rounding^0` are equivalent and accepted.

**Expected Result**

`release-1.1` gained one new commit with the rounding fix. The rest of `feature/invoice-rounding` stayed behind.

**Evaluation**

- `release-1.1` +1 commit whose diff equals the tip commit of `feature/invoice-rounding`; HEAD on `release-1.1`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 3.3.8 Cherry-pick c1 into the index (no commit) on release-review · Medium

**Variant ID:** `cherry-medium-no-commit`

**Story**

Sage wants to review a report hotfix on `release-review` before any new commit is created. The change already exists in commit `c1`, but the team’s sign-off is still pending.

“Bring the patch into the staging area so we can inspect it first,” she says. You are on `release-review`. Apply the selected commit’s changes without creating a commit; the reviewed changes should remain staged on this branch.

**Starting point:** You are on `release-review`; available local branches: `main`, `release-review`.

**Real-World Context**

The selected changes are applied and staged, but no commit is made yet. This leaves room for a reviewer to inspect them first.

**Your Task**

Apply the changes from `c1` onto `release-review` and leave them staged for review.

**Do not create a commit.**

**Objective Checklist**

- [ ] The changes of c1 are staged on release-review.
- [ ] No new commit was created.
- [ ] release-review is checked out.

**Answer Key**

1. `git cherry-pick --no-commit c1`

**Accepted Alternatives**

- `git cherry-pick -n c1`, `git cherry-pick c1 --no-commit`.

**Expected Result**

The changes of `c1` are staged on `release-review`. History is unchanged.

**Evaluation**

- `release-review` HEAD unchanged; index contains c1's diff; working tree matches index.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 3.3.9 Cherry-pick c1 into the index (no commit) on release-staged · Medium

**Variant ID:** `cherry-medium-staged-review`

**Story**

A cache hotfix is ready in commit `c1`, but Raven’s team requires a final code review on `release-staged`. They want to see exactly what will be committed before adding another history entry.

You are on that release branch with `main` also available. Apply the changes from `c1` into the staging area without committing them. Raven can then review the staged patch before anyone records it.

**Starting point:** You are on `release-staged`; available local branches: `main`, `release-staged`.

**Real-World Context**

Staging a copied patch before committing lets a reviewer inspect exactly what will enter the release history.

**Your Task**

Apply the changes from `c1` onto `release-staged` and leave them staged for review.

**Do not create a commit.**

**Objective Checklist**

- [ ] The changes of c1 are staged on release-staged.
- [ ] No new commit was created.
- [ ] release-staged is checked out.

**Answer Key**

1. `git cherry-pick --no-commit c1`

**Accepted Alternatives**

- `git cherry-pick -n c1`, `git cherry-pick c1 --no-commit`.

**Expected Result**

The changes of `c1` are staged on `release-staged`. History is unchanged.

**Evaluation**

- `release-staged` HEAD unchanged; index contains c1's diff; working tree matches index.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 3.3.10 Cherry-pick c1 onto release-2.0 and resolve the conflict · Hard

**Variant ID:** `cherry-hard-export-conflict`

**Story**

A release test still fails when the export receives an empty field. Sage finds the repair in commit `c1`, but the export code on `release-2.0` has changed since `c1` was written, so Git cannot copy the change cleanly and stops with a conflict in `src/export.py`.

The development branch contains other work that has not cleared release review. You are on `release-2.0`. “One verified patch is all we need,” she says.

**Starting point:** You are on `release-2.0`; available local branches: `main`, `release-2.0`; the next cherry-pick will report a conflict.

**Real-World Context**

Copying a commit can conflict just like a merge, when the code around the change is not the same on the target branch. The copy is paused until you decide what the file should say.

**Your Task**

Apply only the changes of `c1` to `release-2.0` as a new commit. `src/export.py` will conflict: resolve it so it contains exactly the lines shown below, with no conflict markers, and finish the cherry-pick.

**Required resolved file content**

`src/export.py`

```
def export(rows):
    return [r for r in rows if r is not None]
```

**Objective Checklist**

- [ ] src/export.py contains exactly the required lines.
- [ ] No conflict markers remain.
- [ ] release-2.0 has one new commit carrying c1's fix, and no cherry-pick is still in progress.
- [ ] release-2.0 is checked out and the working folder is clean.

**Answer Key**

1. `git cherry-pick c1`
2. In the simulator's file editor, set `src/export.py` to exactly:

   ```
   def export(rows):
       return [r for r in rows if r is not None]
   ```
3. `git add src/export.py`
4. `git cherry-pick --continue`

**Accepted Alternatives**

- `git cherry-pick --continue` may be replaced by `git commit` (accepted; Git completes the pick) or `git commit --no-edit`.
- `git add -A` / `git add .` are accepted (only the conflicted file changed).
- `git cherry-pick -x c1` is accepted.
- Abandoning with `--abort` and starting over is allowed; the evaluator only checks the final state.

**Expected Result**

`c1`'s fix exists on `release-2.0` as one new commit, the conflict is resolved, and nothing else was copied.

**Evaluation**

- `release-2.0` +1 commit; `src/export.py` equals the required content; no CHERRY_PICK_HEAD; clean tree; HEAD on `release-2.0`.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 3.3.11 Cancel a cherry-pick that stopped on a conflict · Hard

**Variant ID:** `cherry-hard-abort-conflict`

**Story**

Raven stops a search hotfix while it is being copied onto `release-abort`. The cherry-pick has stopped on a conflict in `src/search.py`, and a new report shows the patch needs more investigation before anyone should ship it.

“Leave the release exactly as it was before we started,” she says. You are on `release-abort`.

**Starting point:** You are on `release-abort`; available local branches: `main`, `release-abort`; a cherry-pick has stopped with a conflict in `src/search.py` and some changes are staged.

**Real-World Context**

An unfinished cherry-pick can be cancelled, which puts the branch, the staging area and the files back as they were before the copy began.

**Your Task**

Cancel the unfinished cherry-pick so `release-abort` is exactly as it was before the copy started. **Nothing from the patch should remain, staged or in your files.**

**Objective Checklist**

- [ ] No cherry-pick is still in progress.
- [ ] release-abort points to the same commit as before the attempt.
- [ ] Nothing is staged and the working folder is clean (no half-applied patch).
- [ ] release-abort is checked out.

**Answer Key**

1. `git cherry-pick --abort`

**Accepted Alternatives**

- `git reset --merge` is accepted as an equivalent (same end state) but is not the expected answer; `git reset --hard` is accepted only if no other uncommitted work exists.

**Not accepted**

- `git cherry-pick --quit` is NOT accepted: it leaves the staged changes behind.

**Expected Result**

The cherry-pick is cancelled, and `release-abort` is back at its pre-attempt state with a clean folder.

**Evaluation**

- No CHERRY_PICK_HEAD; `release-abort` at the original commit; index and working tree clean.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 3.3.12 Cherry-pick c1 onto release-finalize and record its source · Hard

**Variant ID:** `cherry-hard-trace-source`

**Story**

The queue hotfix has passed its final check, and Finn wants it on `release-finalize`.

The release team keeps an audit trail: every backported fix must say which original commit it came from, so someone can trace it later. The fix exists as commit `c1` on another line of work. You are already on `release-finalize`.

**Starting point:** You are on `release-finalize`; available local branches: `main`, `release-finalize`.

**Real-World Context**

Copying a commit creates a new commit with a different ID, so nothing links it to the original unless you record the link. Teams often note the source commit in the message.

**Your Task**

Apply only `c1` to `release-finalize` as a new commit whose message records which commit it was copied from.

**Objective Checklist**

- [ ] Copy c1's changes onto release-finalize.
- [ ] The new commit’s message says which commit it was copied from (the original commit ID).
- [ ] No unrelated commits were copied.
- [ ] release-finalize is checked out.

**Answer Key**

1. `git cherry-pick -x c1`

**Accepted Alternatives**

- `git cherry-pick c1` followed by `git commit --amend` and typing the same trailer is accepted (2 or more counted commands, not CAR-accurate).
- `git cherry-pick c1` alone fails the 'records its source' objective.

**Expected Result**

`release-finalize` has the fix as a new commit, and its message names the original commit.

**Evaluation**

- `release-finalize` +1 commit whose diff equals c1's; message contains `(cherry picked from commit <c1-id>)`; HEAD on `release-finalize`.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 3.3.13 Cherry-pick c1 onto both release-1.2 and release-1.1 · Hard

**Variant ID:** `cherry-hard-two-releases`

**Story**

A late rate limit issue is holding up two maintained releases, `release-1.2` and `release-1.1`. Sage has verified a fix in commit `c1`, but the surrounding development changes should stay where they are.

Both release branches exist locally, and you are currently on `main`. “Move only the tested patch, to both,” she says.

**Starting point:** You are on `main`; available local branches: `main`, `release-1.1`, `release-1.2`.

**Real-World Context**

One fix often has to be copied to every supported release. Each release gets its own new commit, with its own ID.

**Your Task**

Apply only the changes of `c1` to `release-1.2` and to `release-1.1`, as a new commit on each. Finish on `release-1.1`.

**Objective Checklist**

- [ ] Copy c1's changes onto release-1.2.
- [ ] Copy c1's changes onto release-1.1.
- [ ] main is unchanged.
- [ ] release-1.1 is checked out.

**Answer Key**

1. `git switch release-1.2`
2. `git cherry-pick c1`
3. `git switch release-1.1`
4. `git cherry-pick c1`

**Accepted Alternatives**

- The releases may be done in either order; the final branch must be release-1.1.
- `git checkout release-1.2` is accepted in place of `git switch release-1.2`.

**Expected Result**

Both release branches carry the fix as their own new commit, `main` did not change, and you are on `release-1.1`.

**Evaluation**

- `release-1.2` +1 commit and `release-1.1` +1 commit, each with c1's diff; `main` unchanged; HEAD on `release-1.1`.
- Minimum counted commands: 4 · Maximum counted commands: 8

---

### 4.1.1 Recover an accidental reset · Easy

**Variant ID:** `e1`

**Story**

A hard reset has moved `main` backward, and the commits you finished earlier no longer appear at its tip.

Raven sees the alarm on your face and says, “Git may still remember where we were.” The repository’s recent reflog contains a candidate at `c3`. You are on `main`, which should remain where the reset left it for now.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A hard reset moves a branch pointer and can discard working edits, but a recent committed tip may still be reachable through the reflog. A new branch can preserve it.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e1`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/e1 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/e1 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/e1 c3`

**Accepted Alternatives**

- `git branch recovery/e1 c3` then `git switch recovery/e1` and `git checkout -b recovery/e1 c3` are accepted.
- Common patterns that apply: P26.

**Expected Result**

The lost commit is preserved by `recovery/e1`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/e1` = former tip (c3); `main` unchanged; HEAD on `recovery/e1`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.1.2 Recover after a script reset · Easy

**Variant ID:** `e2`

**Story**

A teammate’s cleanup script runs a hard reset on your project branch. Sage notices that the latest completed commits have disappeared from the visible `main` history.

“Let’s look for the position from before the script ran,” she says. You are on `main`, with no recovery branch yet.

The recent reflog leads to candidate `c3`; check what it contains. Once you confirm it, create `recovery/e2` at that commit and move onto the recovered branch.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

An automated reset can hide commits from ordinary branch history. Checking the reflog and commit contents helps recover the correct point.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e2`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/e2 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/e2 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/e2 c3`

**Accepted Alternatives**

- `git branch recovery/e2 c3` then `git switch recovery/e2` and `git checkout -b recovery/e2 c3` are accepted.
- Common patterns that apply: P26.

**Expected Result**

The lost commit is preserved by `recovery/e2`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/e2` = former tip (c3); `main` unchanged; HEAD on `recovery/e2`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.1.3 Recover after resetting too far · Easy

**Variant ID:** `e3`

**Story**

You meant to remove one bad commit but reset farther back than planned. Finn compares the current `main` with your notes and sees that several good commits have gone missing too.

“Don’t guess at a reset target twice,” he says. You are still on `main`. Use Git’s reflog to locate the former tip at `c3`, inspect that commit, and create `recovery/e3` there. The new branch preserves the lost position without moving `main` again.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Recovering on a new branch preserves the former tip while leaving the reset `main` in place for comparison.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e3`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/e3 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/e3 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/e3 c3`

**Accepted Alternatives**

- `git branch recovery/e3 c3` then `git switch recovery/e3` and `git checkout -b recovery/e3 c3` are accepted.
- Common patterns that apply: P26.

**Expected Result**

The lost commit is preserved by `recovery/e3`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/e3` = former tip (c3); `main` unchanged; HEAD on `recovery/e3`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.1.4 Recover after a merge reset · Easy

**Variant ID:** `e4`

**Story**

A merge attempt leaves the team confused, and you run a hard reset to get a clean working folder. Finn checks the history and realizes the reset went past several useful commits.

“We can recover a pointer before we decide what to merge next,” he says. You are on `main`. Find the lost tip in recent reflog, inspect candidate `c3`, then create and switch to `recovery/e4` at that commit.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The reflog records recent movements of `HEAD` and branches. Inspecting a candidate commit before naming it avoids preserving the wrong position.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e4`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/e4 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/e4 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/e4 c3`

**Accepted Alternatives**

- `git branch recovery/e4 c3` then `git switch recovery/e4` and `git checkout -b recovery/e4 c3` are accepted.
- Common patterns that apply: P26.

**Expected Result**

The lost commit is preserved by `recovery/e4`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/e4` = former tip (c3); `main` unchanged; HEAD on `recovery/e4`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.1.5 Recover a debugging reset · Easy

**Variant ID:** `e5`

**Story**

While debugging a failing test, you run a hard reset and later realize you needed the commits that were at the old tip. Finn asks you to stop making new edits until you have a safe copy of that point.

You are on `main`; the candidate in the reflog is `c3`. Then create `recovery/e5` at the lost tip and switch to it, leaving the reset `main` untouched.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Committed work is often still reachable shortly after a mistaken reset. A recovery branch gives it a stable name.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/e5`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/e5 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/e5 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/e5 c3`

**Accepted Alternatives**

- `git branch recovery/e5 c3` then `git switch recovery/e5` and `git checkout -b recovery/e5 c3` are accepted.
- Common patterns that apply: P26.

**Expected Result**

The lost commit is preserved by `recovery/e5`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/e5` = former tip (c3); `main` unchanged; HEAD on `recovery/e5`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.1.6 Recover an accidental reset · Medium

**Variant ID:** `m1`

**Story**

Sage asks for a feature you committed yesterday, but it is missing from `main` after an accidental hard reset. You remember the work was committed, just not exactly which movement entry points to it.

“Let’s trace the old tip rather than rebuilding it,” Sage says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

The visible log follows the current branch; the reflog can show positions that branch used to occupy.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m1`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/m1 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/m1 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/m1 c3`

**Accepted Alternatives**

- `git branch recovery/m1 c3` then `git switch recovery/m1` (2 commands) and `git checkout -b recovery/m1 c3` are accepted.
- `git switch -c recovery/m1 HEAD@{1}` is accepted when that is the former tip.
- Common patterns that apply: P27.

**Expected Result**

The lost commit is preserved by `recovery/m1`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/m1` = former tip (c3); `main` unchanged; HEAD on `recovery/m1`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.1.7 Recover after a script reset · Medium

**Variant ID:** `m2`

**Story**

Finn is reviewing the build when an automated script unexpectedly resets `main`. The working folder looks clean, which *almost* hides the fact that recent commits are no longer at the branch tip.

“Clean isn’t the same as complete,” he says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A clean working folder does not prove a reset kept every commit. Verify the old tip itself before creating a recovery branch.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m2`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/m2 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/m2 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/m2 c3`

**Accepted Alternatives**

- `git branch recovery/m2 c3` then `git switch recovery/m2` (2 commands) and `git checkout -b recovery/m2 c3` are accepted.
- `git switch -c recovery/m2 HEAD@{1}` is accepted when that is the former tip.
- Common patterns that apply: P27.

**Expected Result**

The lost commit is preserved by `recovery/m2`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/m2` = former tip (c3); `main` unchanged; HEAD on `recovery/m2`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.1.8 Recover after resetting too far · Medium

**Variant ID:** `m3`

**Story**

You wanted to drop a single test commit and used a hard reset, but the branch moved past several other commits as well. Maeve notices the gap during review.

“Before changing anything else, let’s keep a pointer to the old work,” she says. You are on `main`.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

An overly broad reset changes where `main` points. Naming the old commit recovers access without another reset.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m3`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/m3 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/m3 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/m3 c3`

**Accepted Alternatives**

- `git branch recovery/m3 c3` then `git switch recovery/m3` (2 commands) and `git checkout -b recovery/m3 c3` are accepted.
- `git switch -c recovery/m3 HEAD@{1}` is accepted when that is the former tip.
- Common patterns that apply: P27.

**Expected Result**

The lost commit is preserved by `recovery/m3`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/m3` = former tip (c3); `main` unchanged; HEAD on `recovery/m3`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.1.9 Recover after a merge reset · Medium

**Variant ID:** `m4`

**Story**

A confusing merge prompts a hard reset, and the next build reveals that useful commits disappeared with the failed attempt. Finn asks you to find the exact pre-reset tip rather than replaying changes by hand.

You are on `main`. Keep that work on `recovery/m4` and move there for review.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

A separate recovery branch provides a safe place to review the former history before deciding what to merge later.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m4`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/m4 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/m4 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/m4 c3`

**Accepted Alternatives**

- `git branch recovery/m4 c3` then `git switch recovery/m4` (2 commands) and `git checkout -b recovery/m4 c3` are accepted.
- `git switch -c recovery/m4 HEAD@{1}` is accepted when that is the former tip.
- Common patterns that apply: P27.

**Expected Result**

The lost commit is preserved by `recovery/m4`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/m4` = former tip (c3); `main` unchanged; HEAD on `recovery/m4`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.1.10 Recover a debugging reset · Medium

**Variant ID:** `m5`

**Story**

Finn has been helping you debug a tricky test. After a hard reset, the test folder is clean but the last committed work is no longer visible from `main`. “The commits may still be there even if the branch moved,” he says.

You are on `main`. Finish on the recovery branch.

**Starting point:** You are on `main`; available local branches: `main`.

**Real-World Context**

Checking the candidate by inspecting it confirms its contents before treating the reflog entry as the lost tip.

**Your Task**

Recover the commit that was `main`’s tip before the reset onto a new branch named `recovery/m5`, and switch to it. Leave `main` where the reset left it.

**Objective Checklist**

- [ ] Create recovery/m5 pointing at the former tip of main.
- [ ] main still points to its reset position.
- [ ] recovery/m5 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c3`
3. `git switch -c recovery/m5 c3`

**Accepted Alternatives**

- `git branch recovery/m5 c3` then `git switch recovery/m5` (2 commands) and `git checkout -b recovery/m5 c3` are accepted.
- `git switch -c recovery/m5 HEAD@{1}` is accepted when that is the former tip.
- Common patterns that apply: P27.

**Expected Result**

The lost commit is preserved by `recovery/m5`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/m5` = former tip (c3); `main` unchanged; HEAD on `recovery/m5`; clean tree.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.1.11 Recover an accidental reset · Hard

**Variant ID:** `h1`

**Story**

After a hard reset, `main` no longer shows the work you finished this morning, and the ordinary log can't bring it back.

Sage points out that the reflog records every place `main` has been, including positions the log has forgotten. Sage wants the right commit identified and checked before anything gets a name.

**Starting point:** You are on `main`; available local branches: `main`. The reflog includes candidate commits `c3` and `c4` after repeated checkouts and resets. Commit `c3` contains the borrower search fix; `c4` contains an abandoned search experiment. No old position has a branch name. The working tree is clean.

**Real-World Context**

Busy reflogs may contain several movements. Verify the selected commit instead of assuming the first entry is the right one.

**Your Task**

Find the lost work among the old positions in the reflog. Recover the commit containing the borrower search fix on a new branch named `recovery/h1`, then switch to that branch. Reject the candidate containing an abandoned search experiment.

**Leave `main` at its reset position and keep the working tree clean.**

**Objective Checklist**

- [ ] Create recovery/h1 pointing at the commit with the borrower search fix.
- [ ] The other candidate (containing an abandoned search experiment) was not recovered.
- [ ] main still points to its reset position.
- [ ] recovery/h1 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c4`
3. `git show c3`
4. `git switch -c recovery/h1 c3`

**Accepted Alternatives**

- `git branch recovery/h1 c3` followed by `git switch recovery/h1` (2 commands) is accepted; so is `git checkout -b recovery/h1 c3`.
- `git switch -c recovery/h1 HEAD@{n}` is accepted if `HEAD@{n}` is the c3 entry.
- Common patterns that apply: P28.

**Expected Result**

The commit with the right work is preserved by `recovery/h1`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/h1` = the c3 commit (the borrower search fix); `main` unchanged; HEAD on `recovery/h1`; clean tree.
- Process: both candidates were inspected (`git show`) before the branch was created.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 4.1.12 Recover after a script reset · Hard

**Variant ID:** `h2`

**Story**

A cleanup script reset `main` while Finn was collecting changes for review. The reflog now has several entries close together, and it would be easy to pick the wrong one.

"We need the most recent lost tip, not just any old commit," Finn says. `main` is not to move again during the recovery.

**Starting point:** You are on `main`; available local branches: `main`. The reflog includes candidate commits `c3` and `c4` after repeated checkouts and resets. Commit `c3` contains the completed borrowing report; `c4` contains an earlier draft of the report. No old position has a branch name. The working tree is clean.

**Real-World Context**

Recent scripts and manual commands can create confusing movement records. Recover a confirmed commit with a new branch.

**Your Task**

Find the lost work among the old positions in the reflog. Recover the commit containing the completed borrowing report on a new branch named `recovery/h2`, then switch to that branch. Reject the candidate containing an earlier draft of the report.

**Leave `main` at its reset position and keep the working tree clean.**

**Objective Checklist**

- [ ] Create recovery/h2 pointing at the commit with the completed borrowing report.
- [ ] The other candidate (containing an earlier draft of the report) was not recovered.
- [ ] main still points to its reset position.
- [ ] recovery/h2 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c4`
3. `git show c3`
4. `git switch -c recovery/h2 c3`

**Accepted Alternatives**

- `git branch recovery/h2 c3` followed by `git switch recovery/h2` (2 commands) is accepted; so is `git checkout -b recovery/h2 c3`.
- `git switch -c recovery/h2 HEAD@{n}` is accepted if `HEAD@{n}` is the c3 entry.
- Common patterns that apply: P28.

**Expected Result**

The commit with the right work is preserved by `recovery/h2`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/h2` = the c3 commit (the completed borrowing report); `main` unchanged; HEAD on `recovery/h2`; clean tree.
- Process: both candidates were inspected (`git show`) before the branch was created.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 4.1.13 Recover after resetting too far · Hard

**Variant ID:** `h3`

**Story**

Maeve spots a surprising gap in `main` after you reset farther back than you meant to. The reflog shows enough activity that a quick glance could be misleading. She asks you to check the candidates before relying on any of them.

**Starting point:** You are on `main`; available local branches: `main`. The reflog includes candidate commits `c3` and `c4` after repeated checkouts and resets. Commit `c3` contains the validation fix and its passing test; `c4` contains a cleanup that does not include the validation fix. No old position has a branch name. The working tree is clean.

**Real-World Context**

When several earlier positions are visible, inspecting `c3` helps distinguish the desired former tip from an unrelated movement.

**Your Task**

Find the lost work among the old positions in the reflog. Recover the commit containing the validation fix and its passing test on a new branch named `recovery/h3`, then switch to that branch. Reject the candidate containing a cleanup that does not include the validation fix.

**Leave `main` at its reset position and keep the working tree clean.**

**Objective Checklist**

- [ ] Create recovery/h3 pointing at the commit with the validation fix and its passing test.
- [ ] The other candidate (containing a cleanup that does not include the validation fix) was not recovered.
- [ ] main still points to its reset position.
- [ ] recovery/h3 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c4`
3. `git show c3`
4. `git switch -c recovery/h3 c3`

**Accepted Alternatives**

- `git branch recovery/h3 c3` followed by `git switch recovery/h3` (2 commands) is accepted; so is `git checkout -b recovery/h3 c3`.
- `git switch -c recovery/h3 HEAD@{n}` is accepted if `HEAD@{n}` is the c3 entry.
- Common patterns that apply: P28.

**Expected Result**

The commit with the right work is preserved by `recovery/h3`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/h3` = the c3 commit (the validation fix and its passing test); `main` unchanged; HEAD on `recovery/h3`; clean tree.
- Process: both candidates were inspected (`git show`) before the branch was created.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 4.1.14 Recover after a merge reset · Hard

**Variant ID:** `h4`

**Story**

Sage's merge attempt went wrong, so the group backed out with a hard reset, and then discovered the reset had hidden good work too. Several movements happened during the attempt, so choosing the first entry you see would be careless.

"Check the candidate before you restore anything," Sage says.

**Starting point:** You are on `main`; available local branches: `main`. The reflog includes candidate commits `c3` and `c4` after repeated checkouts and resets. Commit `c3` contains the working export before the failed merge; `c4` contains the failed merge result. No old position has a branch name. The working tree is clean.

**Real-World Context**

A merge and reset can create multiple reflog entries. A new pointer at the verified former tip preserves the committed work.

**Your Task**

Find the lost work among the old positions in the reflog. Recover the commit containing the working export before the failed merge on a new branch named `recovery/h4`, then switch to that branch. Reject the candidate containing the failed merge result.

**Leave `main` at its reset position and keep the working tree clean.**

**Objective Checklist**

- [ ] Create recovery/h4 pointing at the commit with the working export before the failed merge.
- [ ] The other candidate (containing the failed merge result) was not recovered.
- [ ] main still points to its reset position.
- [ ] recovery/h4 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c4`
3. `git show c3`
4. `git switch -c recovery/h4 c3`

**Accepted Alternatives**

- `git branch recovery/h4 c3` followed by `git switch recovery/h4` (2 commands) is accepted; so is `git checkout -b recovery/h4 c3`.
- `git switch -c recovery/h4 HEAD@{n}` is accepted if `HEAD@{n}` is the c3 entry.
- Common patterns that apply: P28.

**Expected Result**

The commit with the right work is preserved by `recovery/h4`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/h4` = the c3 commit (the working export before the failed merge); `main` unchanged; HEAD on `recovery/h4`; clean tree.
- Process: both candidates were inspected (`git show`) before the branch was created.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 4.1.15 Recover a debugging reset · Hard

**Variant ID:** `h5`

**Story**

A late debugging session ends with a hard reset, followed by the uncomfortable discovery that the previous tip of `main` has vanished from its visible history. Raven helps you read through the recent reflog entries.

"Let's confirm what's in the commit before we save a branch at it," she says.

**Starting point:** You are on `main`; available local branches: `main`. The reflog includes candidate commits `c3` and `c4` after repeated checkouts and resets. Commit `c3` contains the final login timeout fix; `c4` contains a temporary debugging change. No old position has a branch name. The working tree is clean.

**Real-World Context**

Even a late reset need not require rebuilding committed changes by hand if the former tip remains reachable in the reflog.

**Your Task**

Find the lost work among the old positions in the reflog. Recover the commit containing the final login timeout fix on a new branch named `recovery/h5`, then switch to that branch. Reject the candidate containing a temporary debugging change.

**Leave `main` at its reset position and keep the working tree clean.**

**Objective Checklist**

- [ ] Create recovery/h5 pointing at the commit with the final login timeout fix.
- [ ] The other candidate (containing a temporary debugging change) was not recovered.
- [ ] main still points to its reset position.
- [ ] recovery/h5 is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git show c4`
3. `git show c3`
4. `git switch -c recovery/h5 c3`

**Accepted Alternatives**

- `git branch recovery/h5 c3` followed by `git switch recovery/h5` (2 commands) is accepted; so is `git checkout -b recovery/h5 c3`.
- `git switch -c recovery/h5 HEAD@{n}` is accepted if `HEAD@{n}` is the c3 entry.
- Common patterns that apply: P28.

**Expected Result**

The commit with the right work is preserved by `recovery/h5`, which is now checked out; `main` stays at its reset position.

**Evaluation**

- `recovery/h5` = the c3 commit (the final login timeout fix); `main` unchanged; HEAD on `recovery/h5`; clean tree.
- Process: both candidates were inspected (`git show`) before the branch was created.
- Minimum counted commands: 1 · Maximum counted commands: 8

---

### 4.2.1 Revert c3 safely · Easy

**Variant ID:** `re6`

**Story**

QA catches a risky configuration change only after it has reached the shared `main` branch. Finn checks the history and identifies the published change as `c3`.

Other teammates may already have pulled the branch, so he wants a new correction recorded in history and sent to `origin`. “Let’s undo that one change without making their histories jump backward,” he says.

You are on local `main`. Reverse `c3` with a new commit and publish the updated branch.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Revert adds a new commit that reverses an earlier change. Teammates can receive it by an ordinary push without rewriting shared history.

**Your Task**

Create a new commit on `main` that reverses `c3`, then push the correction to `origin`.

**Objective Checklist**

- [ ] main has one new commit that reverses c3; c3 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c3`
2. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c3` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 4.2.2 Revert c2 safely · Easy

**Variant ID:** `re7`

**Story**

The marketing agency’s homepage looks fine on a laptop but collapses on a phone after a promo banner goes live. Sage traces the banner to published commit `c2`.

The rest of the team is already working from `main`, so she asks for a new rollback commit that everyone can receive normally.

You are on local `main`, with `origin` available. Reverse the effect of `c2`, then publish the correction so the mobile layout is usable again.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

A published branch should keep its history stable for collaborators. Reverting the banner change produces a new correction they can pull.

**Your Task**

Create a new commit on `main` that reverses `c2`, then push the correction to `origin`.

**Objective Checklist**

- [ ] main has one new commit that reverses c2; c2 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c2`
2. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c2` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 4.2.3 Revert c4 safely · Easy

**Variant ID:** `re8`

**Story**

The payment API begins timing out on ordinary slow requests right after a new setting is published. Raven compares the history and points to commit `c4`.

“We need that setting undone, but we still need the later work in the shared branch,” she says.

You are on `main`, and the team remote is available. Create a new commit that reverses `c4`, then push the corrected history so other developers can pick it up.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

A targeted revert backs out the faulty timeout setting while leaving other published commits in place.

**Your Task**

Create a new commit on `main` that reverses `c4`, then push the correction to `origin`.

**Objective Checklist**

- [ ] main has one new commit that reverses c4; c4 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c4`
2. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c4` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 12

---

### 4.2.4 Restore progressive tax withholding · Medium

**Variant ID:** `rm6`

**Story**

Payroll support sends Sage a worrying screenshot: every payslip now withholds a flat 30 percent instead of following the progressive table.

Several useful changes have been published since the faulty tax edit. “Find the one commit responsible, and leave the later work alone,” she says.

You are on `main`, with `origin` available. Inspect the history and candidate `c2`, reverse that change with a new commit, then publish the corrected branch.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Inspecting a candidate before reverting helps confirm which change caused the payroll problem. Later good work can remain in history.

**Your Task**

Inspect the history and commit `c2` to confirm the cause. Revert that commit on `main` and push the new corrective commit to `origin`.

**Objective Checklist**

- [ ] Inspect the history to identify the faulty commit before reverting (command-history check).
- [ ] main has one new commit that reverses c2; c2 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git log --oneline`
2. `git show c2`
3. `git revert c2`
4. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c2` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 4.2.5 Stop the every-minute push notifications · Medium

**Variant ID:** `rm7`

**Story**

A notification test account receives a push alert every minute. Finn opens the recent history: templates, quiet hours, and settings were also added, and those changes should stay. The faulty frequency change is candidate `c2`.

“Let’s inspect it before rolling anything back,” he says.

You are on `main`, with `origin` configured. Check the history and `c2`, make a new commit that reverses its effect, then publish the fix without removing the surrounding work.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

A revert undoes the effect of the selected notification commit rather than removing all the later settings and template changes.

**Your Task**

Inspect the history and commit `c2` to confirm the cause. Revert that commit on `main` and push the new corrective commit to `origin`.

**Objective Checklist**

- [ ] Inspect the history to identify the faulty commit before reverting (command-history check).
- [ ] main has one new commit that reverses c2; c2 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git log --oneline`
2. `git show c2`
3. `git revert c2`
4. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c2` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 4.2.6 Restore relevance ranking in search · Medium

**Variant ID:** `rm8`

**Story**

Search users complain that results now appear by upload date rather than relevance. Finn knows the synonym and pagination updates made afterward are valuable. A quick look at the log points to candidate `c1` for the ranking change.

“Verify that one and undo *only its effect*,” he says.

You are on `main`, with a shared remote available. Inspect the commit, revert it with a new commit, and push the corrected branch while keeping the later improvements.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Reversing one earlier ranking commit preserves subsequent search improvements that did not cause the regression.

**Your Task**

Inspect the history and commit `c1` to confirm the cause. Revert that commit on `main` and push the new corrective commit to `origin`.

**Objective Checklist**

- [ ] Inspect the history to identify the faulty commit before reverting (command-history check).
- [ ] main has one new commit that reverses c1; c1 itself is still in history.
- [ ] Later unrelated work is untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git log --oneline`
2. `git show c1`
3. `git revert c1`
4. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

The change in `c1` is reversed by a new commit on `main`, history was not rewritten, and the correction is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 2 · Maximum counted commands: 10

---

### 4.2.7 Roll back two faulty checkout changes · Hard

**Variant ID:** `rh6`

**Story**

Two checkout changes have created a messy production morning: the beta flow is on for everyone, and coupons are discounted twice. Sage identifies the faulty published commits as `c3` and `c1`; order summary email and checkout metrics must remain.

“Undo the bad effects from newest to oldest, then tell the team when it’s up,” she says. You are on `main`, with `origin` available.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Two faulty commits can be reverted one at a time. A single push afterward publishes both new corrective commits.

**Your Task**

Undo the faulty changes `c3` and `c1` with a separate corrective commit for each, newest first, keeping all unrelated work. Then publish the corrected `main` to `origin` once.

**Objective Checklist**

- [ ] Revert c3 and then c1 on main, each in its own commit, newest first.
- [ ] The unrelated commits between and after them are untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c3`
2. `git revert c1`
3. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

Both faulty changes are reversed by two new commits, the unrelated work remains, and the corrected history is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 4.2.8 Roll back two faulty session changes · Hard

**Variant ID:** `rh7`

**Story**

Security reports two session problems: logins now persist for 30 days, and a 24-hour cache prevents forced logout from taking effect. Maeve traces both problems to published commits `c3` and `c1`.

Between them sits an audit-field change that is useful and has to stay, and teammates may already have pulled all three commits.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Reverting the two session changes leaves the intervening audit commit in shared history.

**Your Task**

Undo the faulty changes `c3` and `c1` with a separate corrective commit for each, newest first, keeping all unrelated work. Then publish the corrected `main` to `origin` once.

**Objective Checklist**

- [ ] Revert c3 and then c1 on main, each in its own commit, newest first.
- [ ] The unrelated commits between and after them are untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c3`
2. `git revert c1`
3. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

Both faulty changes are reversed by two new commits, the unrelated work remains, and the corrected history is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 4.2.9 Roll back two faulty site changes · Hard

**Variant ID:** `rh8`

**Story**

Sage’s site review finds two serious regressions: search engines stopped indexing pages, and analytics began storing full visitor IP addresses. The published changes responsible are `c4` and `c2`; other site work around them should survive.

You are on `main`, with `origin` configured. “Make two targeted corrections, then publish one update,” she says. Reverse `c4` and then `c2` with new commits, and push after both are recorded.

**Starting point:** You are on `main`; available local branches: `main`; `origin` is available and `main` tracks `origin/main`.

**Real-World Context**

Targeted revert commits undo the two harmful site changes without discarding unrelated pages and fixes.

**Your Task**

Undo the faulty changes `c4` and `c2` with a separate corrective commit for each, newest first, keeping all unrelated work. Then publish the corrected `main` to `origin` once.

**Objective Checklist**

- [ ] Revert c4 and then c2 on main, each in its own commit, newest first.
- [ ] The unrelated commits between and after them are untouched.
- [ ] Push the result to origin/main.
- [ ] main is checked out; no revert is unfinished.

**Answer Key**

1. `git revert c4`
2. `git revert c2`
3. `git push`

**Accepted Alternatives**

- Only the common patterns below apply.
- Common patterns that apply: P21, P22, P48.

**Not accepted**

- `git revert -n` for several targets followed by one commit is NOT accepted for Hard (separate reverts required).
- `git reset --hard` + `git push --force` is NOT accepted: it rewrites shared history.

**Expected Result**

Both faulty changes are reversed by two new commits, the unrelated work remains, and the corrected history is on `origin`.

**Evaluation**

- Each target has a revert commit; targets still in history; unrelated commits intact; `origin/main` == `main`; no revert in progress.
- Minimum counted commands: 3 · Maximum counted commands: 8

---

### 4.3.1 Rebase feature/recovery onto main · Easy

**Variant ID:** `be6`

**Story**

Finn is preparing a code freeze when he notices your `feature/recovery` branch split from `main` several commits ago. The team has since added changes to `main`, and your feature commits still sit on the older base.

“Put your work on top of what we have now,” he says.

You are on `feature/recovery`. Rebase it onto current `main`, then inspect the graph to confirm the feature follows the updated base and the working folder is clean.

**Starting point:** You are on `feature/recovery`; available local branches: `main`, `feature/recovery`.

**Real-World Context**

Rebase replays a branch’s commits on a new base, giving a linear feature history. The commit IDs change, so verify the result.

**Your Task**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Objective Checklist**

- [ ] Rebase feature/recovery onto main.
- [ ] No rebase is in progress.
- [ ] feature/recovery is checked out and the working folder is clean.

**Answer Key**

1. `git rebase main`
2. `git log --oneline --graph --all`

**Accepted Alternatives**

- `git rebase main` from the feature branch; `git rebase main feature/recovery` from any branch is accepted if the end state is on feature/recovery.
- Common patterns that apply: P49.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `feature/recovery`; same patches; clean tree; HEAD on `feature/recovery`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.3.2 Rebase feature/search-filters onto main · Easy

**Variant ID:** `be7`

**Story**

You have been building search filters while another teammate refreshed the application shell on `main`. Finn wants the filter branch to begin from that newer foundation before review.

You are on `feature/search-filters`, which has diverged from `main`. “Replay your commits after the shell update so the reviewer sees a clean line,” he says. Rebase onto `main`, then inspect the commit graph to verify the new order and leave no unfinished changes.

**Starting point:** You are on `feature/search-filters`; available local branches: `main`, `feature/search-filters`.

**Real-World Context**

Building filters on the updated `main` gives reviewers a branch based on the latest application shell.

**Your Task**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Objective Checklist**

- [ ] Rebase feature/search-filters onto main.
- [ ] No rebase is in progress.
- [ ] feature/search-filters is checked out and the working folder is clean.

**Answer Key**

1. `git rebase main`
2. `git log --oneline --graph --all`

**Accepted Alternatives**

- `git rebase main` from the feature branch; `git rebase main feature/search-filters` from any branch is accepted if the end state is on feature/search-filters.
- Common patterns that apply: P49.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `feature/search-filters`; same patches; clean tree; HEAD on `feature/search-filters`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.3.3 Rebase feature/cli-flags onto main · Easy

**Variant ID:** `be8`

**Story**

The command-line tool gained two fixes on `main` while you were adding optional flags in `feature/cli-flags`. Finn opens the history and sees parallel lines.

“The flags should sit on top of those fixes,” he says, pointing at the updated `main` branch.

You are already on `feature/cli-flags`. Rebase your branch onto `main` and inspect the graph afterward so the team can confirm the rewritten feature history is linear and complete.

**Starting point:** You are on `feature/cli-flags`; available local branches: `main`, `feature/cli-flags`.

**Real-World Context**

A rebased feature can include newer fixes from `main` beneath its own commits; the graph helps confirm their order.

**Your Task**

Rebase the current feature branch onto `main`, then inspect the complete commit graph to verify the order. Finish with clean working files.

**Objective Checklist**

- [ ] Rebase feature/cli-flags onto main.
- [ ] No rebase is in progress.
- [ ] feature/cli-flags is checked out and the working folder is clean.

**Answer Key**

1. `git rebase main`
2. `git log --oneline --graph --all`

**Accepted Alternatives**

- `git rebase main` from the feature branch; `git rebase main feature/cli-flags` from any branch is accepted if the end state is on feature/cli-flags.
- Common patterns that apply: P49.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `feature/cli-flags`; same patches; clean tree; HEAD on `feature/cli-flags`.
- Minimum counted commands: 1 · Maximum counted commands: 12

---

### 4.3.4 Move fix/footer-typo onto main · Medium

**Variant ID:** `bm6`

**Story**

Sage asks for a typo correction in the site footer. You finish it, then notice you started `fix/footer-typo` from the unapproved `feature/checkout-redesign` branch instead of `main`.

“We can ship the spelling fix without bringing in the redesign,” Sage says.

You are on the typo branch. Inspect the branch graph, then replay only the typo branch’s own commits onto `main`, leaving the checkout redesign behind. Finish on the corrected fix branch.

**Starting point:** You are on `fix/footer-typo`; available local branches: `main`, `feature/checkout-redesign`, `fix/footer-typo`.

**Real-World Context**

Replaying onto a new base can move only commits after an accidental parent branch onto `main`, keeping the unwanted redesign out.

**Your Task**

Inspect the graph, then replay only the commits unique to `fix/footer-typo` after `feature/checkout-redesign` onto `main`. Finish on `fix/footer-typo` with clean working files.

**Objective Checklist**

- [ ] Rebase fix/footer-typo directly onto main, leaving out its parent branch's commits.
- [ ] The unapproved parent branch’s commits are not in fix/footer-typo.
- [ ] No rebase is in progress.
- [ ] fix/footer-typo is checked out and the working folder is clean.

**Answer Key**

1. `git log --oneline --graph --all`
2. `git rebase --onto main feature/checkout-redesign fix/footer-typo`

**Accepted Alternatives**

- `git rebase --onto main <parent-branch>` from the feature branch is accepted (`<br>` argument optional).
- Interactive rebase (`git rebase -i`) is not supported in the simulator.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `fix/footer-typo`; the unwanted parent branch's commits are not; own patches present; clean tree; HEAD on `fix/footer-typo`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.3.5 Move hotfix/login-timeout onto main · Medium

**Variant ID:** `bm7`

**Story**

Finn reviews an urgent login timeout fix and catches a branch mistake: `hotfix/login-timeout` began from `release/2.0-beta`, a version the team is not shipping. The hotfix itself is wanted, but the beta commits are not.

You are on the hotfix branch. “Let’s move just your repair onto `main`,” Finn says.

Inspect the graph to identify the old base, then replay only the hotfix commits onto current `main` and keep the beta work out.

**Starting point:** You are on `hotfix/login-timeout`; available local branches: `main`, `release/2.0-beta`, `hotfix/login-timeout`.

**Real-World Context**

Moving only hotfix-specific commits onto `main` avoids bringing a beta release line into the repair.

**Your Task**

Inspect the graph, then replay only the commits unique to `hotfix/login-timeout` after `release/2.0-beta` onto `main`. Finish on `hotfix/login-timeout` with clean working files.

**Objective Checklist**

- [ ] Rebase hotfix/login-timeout directly onto main, leaving out its parent branch's commits.
- [ ] The unapproved parent branch’s commits are not in hotfix/login-timeout.
- [ ] No rebase is in progress.
- [ ] hotfix/login-timeout is checked out and the working folder is clean.

**Answer Key**

1. `git log --oneline --graph --all`
2. `git rebase --onto main release/2.0-beta hotfix/login-timeout`

**Accepted Alternatives**

- `git rebase --onto main <parent-branch>` from the feature branch is accepted (`<br>` argument optional).
- Interactive rebase (`git rebase -i`) is not supported in the simulator.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `hotfix/login-timeout`; the unwanted parent branch's commits are not; own patches present; clean tree; HEAD on `hotfix/login-timeout`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.3.6 Abandon a rebase that stopped on a conflict · Medium

**Variant ID:** `rebase-medium-abort`

**Story**

Finn starts rebasing `feature/export-pdf` onto `main` so it can ship this week, but Git stops halfway on a conflict in `src/export.py`. The two versions of that file differ in ways nobody on the team understands yet, and Finn would rather have a calm conversation than guess.

“Put the branch back the way it was,” he says. “We'll sort the rebase out tomorrow.” You are in the middle of the unfinished rebase.

**Starting point:** You are in the middle of a rebase of `feature/export-pdf` onto `main`, stopped on a conflict in `src/export.py`; available local branches: `main`, `feature/export-pdf`.

**Real-World Context**

A rebase that has stopped on a conflict can be cancelled. The branch then returns to exactly the commits it had before the rebase began.

**Your Task**

Cancel the unfinished rebase so `feature/export-pdf` is exactly as it was before the rebase started.

**Objective Checklist**

- [ ] No rebase is still in progress.
- [ ] feature/export-pdf has its original commits with their original IDs.
- [ ] The working folder is clean (no conflict markers).
- [ ] feature/export-pdf is checked out.

**Answer Key**

1. `git rebase --abort`

**Accepted Alternatives**

- `git reset --hard ORIG_HEAD` is accepted as an equivalent only if ORIG_HEAD is set (not CAR-accurate).

**Not accepted**

- `git rebase --quit` is NOT accepted: it leaves the half-rewritten branch behind.

**Expected Result**

The rebase is cancelled and `feature/export-pdf` is back to its original commits with a clean folder.

**Evaluation**

- No rebase state; `feature/export-pdf` at its original tip; clean tree; HEAD on `feature/export-pdf`.
- Minimum counted commands: 1 · Maximum counted commands: 10

---

### 4.3.7 Recover the dropped commit on feature/cli-flags · Hard

**Variant ID:** `bh6`

**Story**

Sage reviews `feature/cli-flags` after a teammate’s rebase and cannot find the commit that adds the silent-mode flag. The flag was committed before, so the original position should still appear in Git’s recent reflog.

You are on the feature branch. “I want the whole feature on today’s `main`, with nothing missing,” she says.

**Starting point:** You are on `feature/cli-flags`; available local branches: `main`, `feature/cli-flags`.

**Real-World Context**

A faulty rebase can omit a commit. The reflog may reveal the original tip; finding it and restoring it before rebasing preserves the complete feature.

**Your Task**

Bring the complete feature back, including the commit that went missing, and place the whole branch on top of current `main`. Finish with clean working files.

**Objective Checklist**

- [ ] Rebase feature/cli-flags onto main, recovering the one that went missing in the process.
- [ ] No rebase is in progress.
- [ ] feature/cli-flags is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git reset --hard c4`
3. `git rebase main`

**Accepted Alternatives**

- `git reset --hard <hash>` / `HEAD@{n}` instead of the label are accepted.
- `git branch -f feature/cli-flags <old tip>` from another branch is accepted but not CAR-accurate.
- `git cherry-pick <missing commit>` after rebasing is accepted (same end state); not CAR-accurate.
- `git reflog` / `git log -g` are diagnostics and are not counted.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `feature/cli-flags`; the missing commit's patch is present; clean tree; HEAD on `feature/cli-flags`.
- Process: the reflog was read to find the old tip.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 4.3.8 Recover the dropped commit on hotfix/export-csv · Hard

**Variant ID:** `bh7`

**Story**

The CSV export hotfix has been rebased onto `main`, but Raven notices that its test commit disappeared. The original branch tip is still recoverable in the reflog.

You are on `hotfix/export-csv`, and candidate `c5` contains the complete pre-rebase work. “Let’s get the tests back before we call this ready,” Raven says. The finished hotfix must sit on current `main` with its tests included.

**Starting point:** You are on `hotfix/export-csv`; available local branches: `main`, `hotfix/export-csv`.

**Real-World Context**

Recovering the pre-rebase hotfix tip restores the test commit, then replays the whole branch onto the newer base.

**Your Task**

Bring back the complete hotfix, including its missing test commit, and place the whole branch on top of current `main`. Finish with clean working files.

**Objective Checklist**

- [ ] Rebase hotfix/export-csv onto main, recovering the one that went missing in the process.
- [ ] No rebase is in progress.
- [ ] hotfix/export-csv is checked out and the working folder is clean.

**Answer Key**

1. `git reflog`
2. `git reset --hard c5`
3. `git rebase main`

**Accepted Alternatives**

- `git reset --hard <hash>` / `HEAD@{n}` instead of the label are accepted.
- `git branch -f hotfix/export-csv <old tip>` from another branch is accepted but not CAR-accurate.
- `git cherry-pick <missing commit>` after rebasing is accepted (same end state); not CAR-accurate.
- `git reflog` / `git log -g` are diagnostics and are not counted.

**Expected Result**

The branch contains the intended commits on the correct base, with no unfinished rebase or working changes.

**Evaluation**

- `main` is an ancestor of `hotfix/export-csv`; the missing commit's patch is present; clean tree; HEAD on `hotfix/export-csv`.
- Process: the reflog was read to find the old tip.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

### 4.3.9 Finish a rebase after fixing a conflict · Hard

**Variant ID:** `rebase-hard-continue`

**Story**

Sage rebased `feature/rate-limits` onto `main` so the team could review a straight history, but Git stopped on a conflict in `src/limiter.py`. Main added a limit name, and the feature added a retry count, so both belong in the result.

The rebase is still paused and the branch looks half-built. “Finish the rebase properly,” Sage says. “Don’t leave the branch in this state overnight.”

**Starting point:** You are in the middle of a rebase of `feature/rate-limits` onto `main`, stopped on a conflict in `src/limiter.py`; available local branches: `main`, `feature/rate-limits`.

**Real-World Context**

While a rebase is paused, Git replays your commits one at a time and stops when one of them conflicts. The conflict must be resolved, and the rebase told to carry on, before the branch is whole again. Git marks the disputed lines with `<<<<<<<`, `=======`, and `>>>>>>>` lines; the finished file must contain none of them.

**Your Task**

Resolve `src/limiter.py` so it contains exactly the lines shown below, with no conflict markers, and finish the rebase. The finished branch must sit on top of `main` with all its commits.

**Required resolved file content**

`src/limiter.py`

```
LIMIT_NAME = 'api'
RETRY_COUNT = 3
```

**Objective Checklist**

- [ ] src/limiter.py contains exactly the required lines.
- [ ] No conflict markers remain.
- [ ] No rebase is still in progress.
- [ ] Rebase feature/rate-limits onto main.
- [ ] feature/rate-limits is checked out and the working folder is clean.

**Answer Key**

1. In the simulator's file editor, set `src/limiter.py` to exactly:

   ```
   LIMIT_NAME = 'api'
   RETRY_COUNT = 3
   ```
2. `git add src/limiter.py`
3. `git rebase --continue`

**Accepted Alternatives**

- `git add -A` / `git add .` accepted (only the conflicted file changed).
- `git -c core.editor=true rebase --continue` is not required; the simulator must not open an editor for the unchanged message.
- Starting over with `git rebase --abort` then `git rebase main` is accepted; the evaluator checks the final state only.

**Not accepted**

- `git rebase --skip` is NOT accepted: it drops the conflicting commit and loses work.

**Expected Result**

The rebase is complete, the conflict is resolved, and `feature/rate-limits` sits on `main` with all its commits.

**Evaluation**

- No rebase state; `main` is an ancestor of HEAD; all original feature commits present (by patch); `src/limiter.py` equals required; clean tree.
- Minimum counted commands: 2 · Maximum counted commands: 8

---

