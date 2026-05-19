from django.core.management.base import BaseCommand
from django.db import transaction

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from learning.models import LearningUnit, Lesson
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    ScenarioSkillFocus,
    ScenarioVariant,
    TargetStateRule,
)
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator


def commit(commit_id: str, message: str, parents: list[str] | None = None) -> dict:
    return {"id": commit_id, "message": message, "parents": parents or []}


def graph(commits, branches, head_branch, **extra) -> dict:
    state = {
        "commits": commits,
        "branches": branches,
        "head": {"type": "branch", "name": head_branch},
        "working_tree": {},
        "staging": {},
        "conflicts": [],
    }
    state.update(extra)
    return state


class Command(BaseCommand):
    help = "Seed the current-release static GIT it! starter content library."

    def handle(self, *args, **options):
        units = self._units()
        lessons = self._lessons(units)
        self._scenarios(units, lessons)
        self.stdout.write(self.style.SUCCESS("Seeded GIT it! starter content."))

    def _units(self) -> dict[str, LearningUnit]:
        data = [
            (
                "orientation",
                1,
                "Orientation",
                "Foundational Git mental models, DAG literacy, command anatomy, and platform conventions.",
                True,
            ),
            (
                "repository-state",
                2,
                "Repository State and Commit Formation",
                "Read working tree, staging area, commits, status, and history before forming intentional commits.",
                False,
            ),
            (
                "branching-navigation",
                3,
                "Branching and Navigation",
                "Reason about HEAD, branch pointers, detached states, and safe navigation.",
                False,
            ),
            (
                "local-undo-recovery",
                4,
                "Local Undo and Recovery",
                "Recover safely from local repository mistakes without deleting, re-cloning, or losing reachable work.",
                False,
            ),
            (
                "collaboration-integration",
                5,
                "Collaboration and Integration",
                "Integrate divergent branches, resolve conflicts, and clean up finished work.",
                False,
            ),
            (
                "team-workflow-capstone",
                6,
                "Integrated Team Workflow Capstone",
                "Combine repository reading, branching, recovery, integration, and cleanup in realistic team flows.",
                False,
            ),
        ]
        retired_slugs = ["branching-collaboration", "undo-recovery"]
        starter_slugs = [slug for slug, *_ in data] + retired_slugs
        with transaction.atomic():
            for index, slug in enumerate(starter_slugs, start=1):
                LearningUnit.objects.filter(slug=slug).update(number=1000 + index)
            LearningUnit.objects.filter(slug__in=retired_slugs).update(is_published=False)

            units = {}
            for index, (slug, number, title, description, is_orientation) in enumerate(
                data, start=1
            ):
                unit, _ = LearningUnit.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "number": number,
                        "title": title,
                        "description": description,
                        "is_orientation": is_orientation,
                        "sort_order": index,
                        "is_published": True,
                    },
                )
                units[slug] = unit
        return units

    def _lessons(self, units: dict[str, LearningUnit]) -> dict[str, Lesson]:
        orientation_titles = [
            (
                "three-file-areas",
                "The Three File Areas",
                "Working tree, staging area, and repository.",
            ),
            (
                "tracked-untracked",
                "Tracked vs. Untracked Files",
                "Why Git notices some paths and ignores others until they are staged.",
            ),
            (
                "what-head-is",
                "What HEAD Is",
                "The current repository position the simulator displays.",
            ),
            (
                "dag-literacy",
                "Commits, Parents, and DAG Literacy",
                "Reading commits, parent edges, branch labels, and HEAD.",
            ),
            (
                "branch-pointers",
                "Branches as Movable Pointers",
                "Branches are labels that move with commits, not folders.",
            ),
            (
                "command-anatomy",
                "Git Command Anatomy",
                "How to read a command before trusting it.",
            ),
            (
                "practice-rules",
                "GIT it! Practice Rules",
                "Safe simulator rules, feedback, and action limits.",
            ),
            (
                "scaffolds-review",
                "Scaffolding, Retry, and Review Mode",
                "How support changes from Easy to Hard.",
            ),
        ]
        lessons: dict[str, Lesson] = {}
        for index, (slug, title, subtitle) in enumerate(orientation_titles, start=1):
            lesson, _ = Lesson.objects.update_or_create(
                unit=units["orientation"],
                slug=slug,
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "kind": Lesson.LessonKind.ORIENTATION,
                    "content_html": self._orientation_html(slug, title, subtitle),
                    "scoped_css": self._lesson_css(slug, orientation=True),
                    "interaction_steps": [],
                    "sort_order": index,
                    "is_published": True,
                },
            )
            lessons[slug] = lesson

        content_rows = [
            (
                "status-reading",
                units["repository-state"],
                "Reading Git Status",
                Lesson.LessonKind.CONTENT,
                "Interpreting status output before changing repository state.",
                [],
            ),
            (
                "first-commit",
                units["repository-state"],
                "First Commits and Staging Decisions",
                Lesson.LessonKind.SCENARIO,
                "Move from working tree changes to intentional commits.",
                ["first-clean-commit", "partial-staging"],
            ),
            (
                "history-inspection",
                units["repository-state"],
                "Inspecting History Without Changing State",
                Lesson.LessonKind.CONTENT,
                "Use inspection commands to understand commits before changing state.",
                [],
            ),
            (
                "branch-head",
                units["branching-navigation"],
                "Branch Pointers and HEAD",
                Lesson.LessonKind.CONTENT,
                "How HEAD and branch labels move.",
                [],
            ),
            (
                "detached-head",
                units["branching-navigation"],
                "Detached HEAD and Safe Navigation",
                Lesson.LessonKind.CONTENT,
                "Understand detached states before making recovery decisions.",
                [],
            ),
            (
                "right-branch",
                units["branching-navigation"],
                "Moving Work to the Right Branch",
                Lesson.LessonKind.SCENARIO,
                "Recover a local commit made from the wrong repository position.",
                ["wrong-branch-commit", "detached-work-rescue"],
            ),
            (
                "undo-without-panic",
                units["local-undo-recovery"],
                "Undo Without Panic",
                Lesson.LessonKind.CONTENT,
                "Choose a local recovery move by naming what should be preserved.",
                [],
            ),
            (
                "reset-recovery",
                units["local-undo-recovery"],
                "Recovering After Pointer Movement",
                Lesson.LessonKind.SCENARIO,
                "Repair local branch pointer moves while preserving reachable work.",
                ["accidental-reset-recovery"],
            ),
            (
                "divergence-merge",
                units["collaboration-integration"],
                "Divergent Branches and Merge Recovery",
                Lesson.LessonKind.SCENARIO,
                "Resolve collaboration states without discarding team work.",
                ["divergent-branches", "merge-conflict", "branch-cleanup"],
            ),
            (
                "conflict-state",
                units["collaboration-integration"],
                "Understanding Merge Conflict State",
                Lesson.LessonKind.CONTENT,
                "Read conflict state as a repository condition, not as a reason to re-clone.",
                [],
            ),
            (
                "team-flow-capstone",
                units["team-workflow-capstone"],
                "Release Workflow Capstone",
                Lesson.LessonKind.SCENARIO,
                "Combine inspection, integration, and cleanup in one coherent team workflow.",
                ["release-integration-capstone"],
            ),
        ]
        for index, (slug, unit, title, kind, subtitle, _) in enumerate(content_rows, start=1):
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit,
                slug=slug,
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "kind": kind,
                    "content_html": self._lesson_html(
                        slug,
                        title,
                        subtitle,
                        kind == Lesson.LessonKind.SCENARIO,
                    ),
                    "scoped_css": self._lesson_css(slug, orientation=False),
                    "interaction_steps": [],
                    "sort_order": index,
                    "is_published": True,
                },
            )
            lessons[slug] = lesson
        return lessons

    def _scenarios(self, units: dict[str, LearningUnit], lessons: dict[str, Lesson]) -> None:
        scenario_data = [
            {
                "slug": "first-clean-commit",
                "unit": units["repository-state"],
                "lesson": lessons["first-commit"],
                "title": "Create a first clean commit",
                "focus": "first commit",
                "narrative": "A starter project needs its first intentional snapshot on main.",
                "task": "Capture the starter work in history and leave the repository clean on main.",
                "difficulties": {
                    DIFFICULTY_EASY: self._difficulty(
                        "A new repository has visible untracked starter files. Decide what belongs in the first commit.",
                        "Create one clean starter commit on main. The exact commit message is not graded, but it should describe the starter work.",
                        (2, 8, ["git status", "git log --oneline"]),
                        {
                            "head_branch": "main",
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 1},
                        },
                        [
                            self._variant(
                                "starter-readme-app",
                                "README and app entry",
                                "first-easy-readme-app",
                                graph(
                                    [],
                                    {"main": None},
                                    "main",
                                    working_tree={"README.md": "untracked", "app.py": "untracked"},
                                ),
                                ["git add .", 'git commit -m "starter snapshot"'],
                            ),
                            self._variant(
                                "starter-web-files",
                                "Static web starter",
                                "first-easy-web-three-files",
                                graph(
                                    [],
                                    {"main": None},
                                    "main",
                                    working_tree={
                                        "index.html": "untracked",
                                        "styles.css": "untracked",
                                        "tests.py": "untracked",
                                    },
                                ),
                                ["git add .", 'git commit -m "starter snapshot"'],
                            ),
                        ],
                    ),
                    DIFFICULTY_MEDIUM: self._difficulty(
                        "The repository already has a baseline commit. New starter changes should become the next snapshot.",
                        "Create the next clean commit on main after inspecting the existing history. The exact commit message is not graded.",
                        (2, 7, ["git status", "git log --oneline", "git diff"]),
                        {
                            "head_branch": "main",
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 2},
                        },
                        [
                            self._variant(
                                "baseline-cli",
                                "CLI starter update",
                                "first-medium-baseline-cli",
                                graph(
                                    [commit("c0", "Project scaffold")],
                                    {"main": "c0"},
                                    "main",
                                    working_tree={"cli.py": "modified", "README.md": "modified"},
                                ),
                                ["git add .", 'git commit -m "starter update"'],
                            ),
                            self._variant(
                                "baseline-api",
                                "API starter update",
                                "first-medium-baseline-api",
                                graph(
                                    [commit("c0", "Project scaffold")],
                                    {"main": "c0", "docs/reference": "c0"},
                                    "main",
                                    working_tree={"api.py": "modified", "README.md": "modified"},
                                ),
                                ["git add .", 'git commit -m "starter update"'],
                            ),
                        ],
                    ),
                    DIFFICULTY_HARD: self._difficulty(
                        "A slightly busier local repository has starter changes and an extra branch label. The target is still main.",
                        "Commit the ready starter changes on main and leave no staged or working tree changes behind. The exact commit message is not graded.",
                        (2, 6, ["git status", "git log --oneline", "git branch -v"]),
                        {
                            "head_branch": "main",
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 2},
                        },
                        [
                            self._variant(
                                "hard-ui-starter",
                                "UI starter with side branch",
                                "first-hard-ui-side-branch",
                                graph(
                                    [commit("c0", "Project scaffold")],
                                    {"main": "c0", "spike/theme": "c0"},
                                    "main",
                                    working_tree={
                                        "src/App.tsx": "modified",
                                        "src/styles.css": "modified",
                                    },
                                ),
                                ["git add .", 'git commit -m "starter ui"'],
                            ),
                            self._variant(
                                "hard-service-starter",
                                "Service starter with side branch",
                                "first-hard-service-side-branch",
                                graph(
                                    [commit("c0", "Project scaffold")],
                                    {"main": "c0", "spike/schema": "c0"},
                                    "main",
                                    working_tree={
                                        "service.py": "modified",
                                        "schema.sql": "modified",
                                    },
                                ),
                                ["git add .", 'git commit -m "starter service"'],
                            ),
                        ],
                    ),
                },
            },
            {
                "slug": "partial-staging",
                "unit": units["repository-state"],
                "lesson": lessons["first-commit"],
                "title": "Stage selected changes",
                "focus": "partial staging",
                "narrative": "Only some working tree changes belong in the next commit; draft work must remain visible but uncommitted.",
                "task": "Create an intentional commit that includes only the requested files and leaves draft work out of history.",
                "difficulties": {
                    DIFFICULTY_EASY: self._difficulty(
                        "Configuration and draft notes changed together. The config change is ready; the draft note is not.",
                        "Commit only config.yml on main. The commit message must mention config. Leave draft.md in the working tree.",
                        (2, 8, ["git status", "git diff"]),
                        {
                            "head_branch": "main",
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 2},
                            "working_tree_contains": ["draft.md"],
                            "latest_commit": {
                                "branch": "main",
                                "contains_paths": ["config.yml"],
                                "excludes_paths": ["draft.md"],
                                "message_contains": ["config"],
                            },
                        },
                        [
                            self._variant(
                                "config-plus-draft",
                                "Config and draft note",
                                "stage-easy-config-draft",
                                graph(
                                    [commit("c0", "Base")],
                                    {"main": "c0"},
                                    "main",
                                    working_tree={"config.yml": "modified", "draft.md": "modified"},
                                ),
                                ["git add config.yml", 'git commit -m "config baseline"'],
                            ),
                            self._variant(
                                "config-plus-draft-with-docs",
                                "Config, draft, and docs branch",
                                "stage-easy-config-draft-docs-branch",
                                graph(
                                    [commit("c0", "Base")],
                                    {"main": "c0", "docs/reference": "c0"},
                                    "main",
                                    working_tree={"config.yml": "modified", "draft.md": "modified"},
                                ),
                                ["git add config.yml", 'git commit -m "config baseline"'],
                            ),
                        ],
                    ),
                    DIFFICULTY_MEDIUM: self._difficulty(
                        "Settings are ready for review, but local notes are still personal scratch work.",
                        "Commit only settings.json on main. The commit message must mention settings. Leave notes.txt uncommitted.",
                        (2, 7, ["git status", "git diff", "git log --oneline"]),
                        {
                            "head_branch": "main",
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 2},
                            "working_tree_contains": ["notes.txt"],
                            "latest_commit": {
                                "branch": "main",
                                "contains_paths": ["settings.json"],
                                "excludes_paths": ["notes.txt"],
                                "message_contains": ["settings"],
                            },
                        },
                        [
                            self._variant(
                                "settings-plus-notes",
                                "Settings and notes",
                                "stage-medium-settings-notes",
                                graph(
                                    [commit("c0", "Base")],
                                    {"main": "c0"},
                                    "main",
                                    working_tree={
                                        "settings.json": "modified",
                                        "notes.txt": "modified",
                                    },
                                ),
                                ["git add settings.json", 'git commit -m "settings update"'],
                            ),
                            self._variant(
                                "settings-plus-notes-with-release",
                                "Settings with release branch nearby",
                                "stage-medium-settings-notes-release-branch",
                                graph(
                                    [commit("c0", "Base"), commit("c1", "Release prep", ["c0"])],
                                    {"main": "c0", "release/checklist": "c1"},
                                    "main",
                                    working_tree={
                                        "settings.json": "modified",
                                        "notes.txt": "modified",
                                    },
                                ),
                                ["git add settings.json", 'git commit -m "settings update"'],
                            ),
                        ],
                    ),
                    DIFFICULTY_HARD: self._difficulty(
                        "A focused code fix and experimental notes are mixed in the same working tree.",
                        "Commit only src/auth.py on main. The commit message must mention auth. Leave experiment.md uncommitted.",
                        (2, 6, ["git status", "git diff", "git branch -v"]),
                        {
                            "head_branch": "main",
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"main": 2},
                            "working_tree_contains": ["experiment.md"],
                            "latest_commit": {
                                "branch": "main",
                                "contains_paths": ["src/auth.py"],
                                "excludes_paths": ["experiment.md"],
                                "message_contains": ["auth"],
                            },
                        },
                        [
                            self._variant(
                                "auth-plus-experiment",
                                "Auth fix and experiment note",
                                "stage-hard-auth-experiment",
                                graph(
                                    [commit("c0", "Base")],
                                    {"main": "c0", "spike/oauth": "c0"},
                                    "main",
                                    working_tree={
                                        "src/auth.py": "modified",
                                        "experiment.md": "modified",
                                    },
                                ),
                                ["git add src/auth.py", 'git commit -m "auth guard"'],
                            ),
                            self._variant(
                                "auth-plus-experiment-after-patch",
                                "Auth fix after prior patch",
                                "stage-hard-auth-experiment-prior-patch",
                                graph(
                                    [commit("c0", "Base"), commit("c1", "Hotfix", ["c0"])],
                                    {"main": "c1", "spike/oauth": "c0"},
                                    "main",
                                    working_tree={
                                        "src/auth.py": "modified",
                                        "experiment.md": "modified",
                                    },
                                ),
                                ["git add src/auth.py", 'git commit -m "auth guard"'],
                            ),
                        ],
                    ),
                },
            },
            {
                "slug": "wrong-branch-commit",
                "unit": units["branching-navigation"],
                "lesson": lessons["right-branch"],
                "title": "Move a commit made on the wrong branch",
                "focus": "wrong-branch commit recovery",
                "narrative": "Feature work was committed while main was checked out. Preserve the work, but put it on the intended branch.",
                "task": "Move the work to feature/recovery, restore main to the base commit, and finish on feature/recovery.",
                "difficulties": {
                    DIFFICULTY_EASY: self._difficulty(
                        "One feature commit is sitting on main even though feature/recovery already points at the base.",
                        "Place that work on feature/recovery, move main back to c0, and finish on feature/recovery.",
                        (5, 12, ["git status", "git log --oneline", "git branch -v"]),
                        {
                            "head_branch": "feature/recovery",
                            "branch_exists": ["feature/recovery"],
                            "branch_points_to": {"main": "c0"},
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"feature/recovery": 2},
                        },
                        [
                            self._variant(
                                "login-commit-on-main",
                                "Login work on main",
                                "wrong-easy-login-main",
                                graph(
                                    [commit("c0", "Base"), commit("c1", "Login work", ["c0"])],
                                    {"main": "c1", "feature/recovery": "c0"},
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c1",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                            self._variant(
                                "report-commit-on-main",
                                "Report work on main",
                                "wrong-easy-report-main",
                                graph(
                                    [commit("c0", "Base"), commit("c1", "Report work", ["c0"])],
                                    {
                                        "main": "c1",
                                        "feature/recovery": "c0",
                                        "docs/reference": "c0",
                                    },
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c1",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                        ],
                    ),
                    DIFFICULTY_MEDIUM: self._difficulty(
                        "Main has advanced twice; only the latest feature-shaped commit belongs on feature/recovery.",
                        "Copy c2 to feature/recovery, move main back to c1, and finish on feature/recovery.",
                        (5, 11, ["git status", "git log --oneline", "git branch -v"]),
                        {
                            "head_branch": "feature/recovery",
                            "branch_exists": ["feature/recovery"],
                            "branch_points_to": {"main": "c1"},
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"feature/recovery": 3},
                        },
                        [
                            self._variant(
                                "feature-after-main-patch",
                                "Feature work after main patch",
                                "wrong-medium-after-main-patch",
                                graph(
                                    [
                                        commit("c0", "Base"),
                                        commit("c1", "Main patch", ["c0"]),
                                        commit("c2", "Feature work", ["c1"]),
                                    ],
                                    {"main": "c2", "feature/recovery": "c1"},
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c2",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                            self._variant(
                                "feature-after-release-note",
                                "Feature work after release note",
                                "wrong-medium-after-release-note",
                                graph(
                                    [
                                        commit("c0", "Base"),
                                        commit("c1", "Release note", ["c0"]),
                                        commit("c2", "Feature work", ["c1"]),
                                    ],
                                    {
                                        "main": "c2",
                                        "feature/recovery": "c1",
                                        "release/checklist": "c1",
                                    },
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c2",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                        ],
                    ),
                    DIFFICULTY_HARD: self._difficulty(
                        "The graph includes an extra branch label. The latest main commit still belongs on feature/recovery.",
                        "Move c2 to feature/recovery, restore main to c1, and leave the worktree clean on feature/recovery.",
                        (5, 10, ["git status", "git log --oneline", "git branch -v", "git show"]),
                        {
                            "head_branch": "feature/recovery",
                            "branch_exists": ["feature/recovery"],
                            "branch_points_to": {"main": "c1"},
                            "working_tree_clean": True,
                            "staging_empty": True,
                            "conflict_free": True,
                            "min_commits_on_branch": {"feature/recovery": 3},
                        },
                        [
                            self._variant(
                                "hard-feature-with-spike",
                                "Feature work with nearby spike",
                                "wrong-hard-feature-spike",
                                graph(
                                    [
                                        commit("c0", "Base"),
                                        commit("c1", "Main patch", ["c0"]),
                                        commit("c2", "Feature work", ["c1"]),
                                    ],
                                    {"main": "c2", "feature/recovery": "c1", "spike/ui": "c0"},
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c2",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                            self._variant(
                                "hard-feature-with-hotfix",
                                "Feature work with hotfix label",
                                "wrong-hard-feature-hotfix",
                                graph(
                                    [
                                        commit("c0", "Base"),
                                        commit("c1", "Main patch", ["c0"]),
                                        commit("c2", "Feature work", ["c1"]),
                                    ],
                                    {"main": "c2", "feature/recovery": "c1", "hotfix/trace": "c1"},
                                    "main",
                                ),
                                [
                                    "git switch feature/recovery",
                                    "git cherry-pick c2",
                                    "git switch main",
                                    "git reset HEAD~1",
                                    "git switch feature/recovery",
                                ],
                            ),
                        ],
                    ),
                },
            },
            {
                "slug": "detached-work-rescue",
                "unit": units["branching-navigation"],
                "lesson": lessons["right-branch"],
                "title": "Rescue work from detached HEAD",
                "focus": "detached HEAD rescue",
                "narrative": "Work began while HEAD was detached. The safe outcome is to attach the work to a named branch.",
                "task": "Create feature/rescue from the detached position, commit the visible work, and finish on that branch.",
                "difficulties": {
                    DIFFICULTY_EASY: self._detached_rescue_difficulty(
                        "A detached checkout has one working tree change that should be kept.",
                        "Create feature/rescue, commit the work there, and leave the repository clean on feature/rescue. The exact commit message is not graded.",
                        "rescue-easy",
                    ),
                    DIFFICULTY_MEDIUM: self._detached_rescue_difficulty(
                        "The detached checkout is one commit behind main, but the current work still needs a branch name.",
                        "Create feature/rescue from the detached commit, commit the work, and finish on feature/rescue. The exact commit message is not graded.",
                        "rescue-medium",
                        base_commits=[commit("c0", "Base"), commit("c1", "Main progress", ["c0"])],
                        branches={"main": "c1"},
                        detached_at="c0",
                    ),
                    DIFFICULTY_HARD: self._detached_rescue_difficulty(
                        "A detached state includes an unrelated branch label. Rescue only the current detached work.",
                        "Attach the detached work to feature/rescue, commit it, and keep the repository clean. The exact commit message is not graded.",
                        "rescue-hard",
                        base_commits=[commit("c0", "Base"), commit("c1", "Main progress", ["c0"])],
                        branches={"main": "c1", "spike/archive": "c0"},
                        detached_at="c0",
                    ),
                },
            },
            {
                "slug": "accidental-reset-recovery",
                "unit": units["local-undo-recovery"],
                "lesson": lessons["reset-recovery"],
                "title": "Recover after an accidental local reset",
                "focus": "local reset recovery",
                "narrative": "A local branch pointer moved backward, but a safety reference still points to the work that must be preserved.",
                "task": "Move the active branch pointer back to the preserved work without inventing a new history.",
                "difficulties": {
                    DIFFICULTY_EASY: self._reset_recovery_difficulty(
                        "Main moved back one commit. safety-copy still points to the lost local work.",
                        "Move main back to safety-copy and finish with a clean repository on main.",
                        "reset-easy",
                    ),
                    DIFFICULTY_MEDIUM: self._reset_recovery_difficulty(
                        "Main moved back while an extra branch label remained in the graph. safety-copy is the preserved target.",
                        "Restore main to safety-copy, keep safety-copy available, and leave the worktree clean.",
                        "reset-medium",
                        extra_branches={"review/base": "c0"},
                    ),
                    DIFFICULTY_HARD: self._reset_recovery_difficulty(
                        "The preserved work is reachable, but the graph has more nearby labels than the easy case.",
                        "Use the safety reference to restore main without creating a replacement commit.",
                        "reset-hard",
                        extra_branches={"review/base": "c0", "spike/old": "c1"},
                    ),
                },
            },
            {
                "slug": "divergent-branches",
                "unit": units["collaboration-integration"],
                "lesson": lessons["divergence-merge"],
                "title": "Resolve divergent branches after team edits",
                "focus": "merge integration",
                "narrative": "Main and a feature branch both moved forward. Preserve both lines of work in an integrated main history.",
                "task": "Integrate the source branch into main and leave the repository clean.",
                "difficulties": {
                    DIFFICULTY_EASY: self._merge_difficulty(
                        "Main has one team update and the source branch has one feature commit.",
                        "Integrate the feature branch into main. Stay on main with a clean worktree.",
                        "diverge-easy",
                        "feature/login",
                    ),
                    DIFFICULTY_MEDIUM: self._merge_difficulty(
                        "Main and the source branch diverged from the same base while another branch label is nearby.",
                        "Inspect the branches, integrate the source branch into main, and keep the result clean.",
                        "diverge-medium",
                        "feature/profile",
                        extra_branches={"release/checklist": "c1"},
                    ),
                    DIFFICULTY_HARD: self._merge_difficulty(
                        "The graph has multiple labels, but only the source branch needs to be integrated into main.",
                        "Integrate the source branch into main without discarding either side of history.",
                        "diverge-hard",
                        "feature/billing",
                        extra_branches={"spike/routing": "c0", "release/checklist": "c1"},
                    ),
                },
            },
            {
                "slug": "merge-conflict",
                "unit": units["collaboration-integration"],
                "lesson": lessons["divergence-merge"],
                "title": "Finish a merge after conflict markers appear",
                "focus": "merge conflict resolution",
                "narrative": "A merge stopped because a file still has conflict markers. The repository is mid-merge, not broken.",
                "task": "Mark the conflict file resolved, complete the merge commit, and leave main clean.",
                "difficulties": {
                    DIFFICULTY_EASY: self._conflict_difficulty(
                        "The merge is already stopped on main with one conflicted file.",
                        "Resolve forms.py in the simulator, complete the merge commit, and leave main clean. The exact merge commit message is not graded.",
                        "conflict-easy",
                        "forms.py",
                        "feature/forms",
                    ),
                    DIFFICULTY_MEDIUM: self._conflict_difficulty(
                        "One conflict remains after merging a copy branch into main.",
                        "Resolve copy.md, finish the merge commit, and keep the repository clean on main. The exact merge commit message is not graded.",
                        "conflict-medium",
                        "copy.md",
                        "feature/copy",
                        extra_branches={"review/text": "c0"},
                    ),
                    DIFFICULTY_HARD: self._conflict_difficulty(
                        "The graph has extra labels, but the active state is still one unfinished merge on main.",
                        "Resolve view.tsx, complete the merge commit, and leave no conflict or staged state behind. The exact merge commit message is not graded.",
                        "conflict-hard",
                        "view.tsx",
                        "feature/view",
                        extra_branches={"spike/layout": "c0", "release/checklist": "c1"},
                    ),
                },
            },
            {
                "slug": "branch-cleanup",
                "unit": units["collaboration-integration"],
                "lesson": lessons["divergence-merge"],
                "title": "Clean up a merged feature branch",
                "focus": "branch cleanup",
                "narrative": "A completed branch has already been merged and should be removed without changing main history.",
                "task": "Leave the repository on main with old-feature removed and the working tree clean.",
                "difficulties": {
                    DIFFICULTY_EASY: self._cleanup_difficulty(
                        "old-feature points to the same commit as main, so it is safe to remove.",
                        "Delete old-feature while staying on main.",
                        "cleanup-easy",
                    ),
                    DIFFICULTY_MEDIUM: self._cleanup_difficulty(
                        "A stale merged branch and an active review branch are both visible. Only old-feature is stale.",
                        "Delete old-feature, keep the other branch labels intact, and stay on main.",
                        "cleanup-medium",
                        extra_branches={"review/copy": "c0"},
                    ),
                    DIFFICULTY_HARD: self._cleanup_difficulty(
                        "Multiple labels share history. Remove only the stale merged branch named old-feature.",
                        "Leave main clean with old-feature absent and the rest of the graph preserved.",
                        "cleanup-hard",
                        extra_branches={"review/copy": "c0", "release/checklist": "c1"},
                    ),
                },
            },
            {
                "slug": "release-integration-capstone",
                "unit": units["team-workflow-capstone"],
                "lesson": lessons["team-flow-capstone"],
                "title": "Finish a release integration workflow",
                "focus": "integrated team workflow",
                "narrative": "A release branch is ready to integrate, and an old feature branch should be cleaned up afterward.",
                "task": "Integrate release/topic into main, delete old-feature, and leave the repository clean on main.",
                "difficulties": {
                    DIFFICULTY_EASY: self._capstone_difficulty(
                        "The graph has one release branch to integrate and one stale branch to remove.",
                        "Merge release/topic into main, delete old-feature, and stay clean on main.",
                        "capstone-easy",
                    ),
                    DIFFICULTY_MEDIUM: self._capstone_difficulty(
                        "There is an additional review branch nearby. It is not the integration target.",
                        "Integrate release/topic into main, remove old-feature only, and leave the rest intact.",
                        "capstone-medium",
                        extra_branches={"review/docs": "c0"},
                    ),
                    DIFFICULTY_HARD: self._capstone_difficulty(
                        "The final scenario combines branch reading, integration, and cleanup with several nearby labels.",
                        "Finish on main with release/topic integrated, old-feature removed, and no working tree changes.",
                        "capstone-hard",
                        extra_branches={"review/docs": "c0", "spike/perf": "c1"},
                    ),
                },
            },
        ]

        for index, item in enumerate(scenario_data, start=1):
            scenario, _ = ScenarioSkillFocus.objects.update_or_create(
                learning_unit=item["unit"],
                slug=item["slug"],
                defaults={
                    "lesson": item["lesson"],
                    "title": item["title"],
                    "focus": item["focus"],
                    **self._skill_focus_preview(item["slug"]),
                    "narrative": "",
                    "task_prompt": "",
                    "sort_order": index,
                    "is_published": True,
                },
            )
            for difficulty, config in item["difficulties"].items():
                diff, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "narrative": config["narrative"],
                        "task_prompt": config["task"],
                        "is_published": True,
                    },
                )
                minimum, maximum, diagnostics = config["policy"]
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={
                        "min_counted_commands": minimum,
                        "max_counted_commands": maximum,
                        "non_counted_patterns": diagnostics,
                    },
                )
                target_hash = RepositoryStateSimulator().state_hash(
                    config["variants"][0]["target_state"]
                )
                TargetStateRule.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={"rule": config["rule"], "target_state_hash": target_hash},
                )
                current_variant_slugs = []
                for variant_data in config["variants"]:
                    current_variant_slugs.append(variant_data["slug"])
                    ScenarioVariant.objects.update_or_create(
                        scenario=scenario,
                        difficulty_instance=diff,
                        slug=variant_data["slug"],
                        defaults=variant_data,
                    )
                ScenarioVariant.objects.filter(difficulty_instance=diff).exclude(
                    slug__in=current_variant_slugs
                ).update(is_published=False)

    def _skill_focus_preview(self, slug: str) -> dict:
        previews = {
            "first-clean-commit": {
                "title": "Clean Commit Formation",
                "focus": "git status, git add, git commit",
                "summary": "Read file state, stage intentional work, and form a clean snapshot.",
                "short_explanation": "A clean commit is a three-step habit: (1) inspect state, (2) stage intentionally, (3) commit the staged snapshot. The goal is to understand what you are about to change before you change it.",
                "skill_focus_type": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
                "primary_focus_commands": ["git status", "git add", "git commit"],
                "supporting_inspection_commands": [
                    "git log --oneline",
                    "git diff",
                    "git diff --staged",
                ],
                "safe_demo_commands": [
                    "git status",
                    "git diff",
                    "git add demo-notes.md",
                    "git diff --staged",
                    'git commit -m "demo snapshot"',
                ],
                "demo_repository_state": self._demo_snapshot(
                    graph(
                        [],
                        {"demo-main": None},
                        "demo-main",
                        working_tree={"demo-notes.md": "untracked"},
                    )
                ),
                "demo_explanation_steps": [
                    self._demo_step(
                        "git status",
                        "git status helps you name what changed. Here the demo file is in the working tree and not staged yet.",
                        graph(
                            [],
                            {"demo-main": None},
                            "demo-main",
                            working_tree={"demo-notes.md": "untracked"},
                        ),
                    ),
                    self._demo_step(
                        "git diff",
                        "git diff inspects working tree changes that are not staged yet. It is safe inspection: it does not change state.",
                        graph(
                            [],
                            {"demo-main": None},
                            "demo-main",
                            working_tree={"demo-notes.md": "untracked"},
                        ),
                    ),
                    self._demo_step(
                        "git add demo-notes.md",
                        "git add stages only the selected path. The staged snapshot is what the next commit will capture.",
                        graph(
                            [],
                            {"demo-main": None},
                            "demo-main",
                            staging={"demo-notes.md": "added"},
                        ),
                    ),
                    self._demo_step(
                        "git diff --staged",
                        "git diff --staged inspects what is currently staged. Use it to verify what would go into a commit before committing.",
                        graph(
                            [],
                            {"demo-main": None},
                            "demo-main",
                            staging={"demo-notes.md": "added"},
                        ),
                    ),
                    self._demo_step(
                        'git commit -m "demo snapshot"',
                        'git commit creates a new snapshot from staged content. The -m flag sets a message inline (the message is descriptive, not a "solution").',
                        graph(
                            [commit("d1", "Demo snapshot")],
                            {"demo-main": "d1"},
                            "demo-main",
                        ),
                    ),
                ],
                "related_git_concepts": ["working tree", "staging area", "commit history"],
            },
            "partial-staging": {
                "title": "Staging Selected Changes",
                "focus": "git add",
                "summary": "Move selected working tree changes into the staging area before committing.",
                "short_explanation": "Staging is a deliberate boundary: only what you stage can enter the next commit. Selective staging helps you keep messy draft work visible without accidentally committing it.",
                "skill_focus_type": ScenarioSkillFocus.SkillFocusType.COMMAND_SPECIFIC,
                "primary_focus_commands": ["git add"],
                "supporting_inspection_commands": [
                    "git status",
                    "git diff",
                    "git diff --staged",
                    "git restore --staged",
                ],
                "safe_demo_commands": [
                    "git status",
                    "git diff",
                    "git add demo-config.yml",
                    "git diff --staged",
                    "git restore --staged demo-config.yml",
                ],
                "demo_repository_state": self._demo_snapshot(
                    graph(
                        [commit("d0", "Demo base")],
                        {"demo-main": "d0"},
                        "demo-main",
                        working_tree={
                            "demo-config.yml": "modified",
                            "demo-draft.md": "modified",
                        },
                    )
                ),
                "demo_explanation_steps": [
                    self._demo_step(
                        "git status",
                        "git status shows two modified demo files. The key question is: which one belongs in the next commit candidate?",
                        graph(
                            [commit("d0", "Demo base")],
                            {"demo-main": "d0"},
                            "demo-main",
                            working_tree={
                                "demo-config.yml": "modified",
                                "demo-draft.md": "modified",
                            },
                        ),
                    ),
                    self._demo_step(
                        "git diff",
                        "git diff helps you inspect working tree changes before staging. It is read-only inspection.",
                        graph(
                            [commit("d0", "Demo base")],
                            {"demo-main": "d0"},
                            "demo-main",
                            working_tree={
                                "demo-config.yml": "modified",
                                "demo-draft.md": "modified",
                            },
                        ),
                    ),
                    self._demo_step(
                        "git add demo-config.yml",
                        "Only demo-config.yml moves into the staging area; the draft file remains unstaged.",
                        graph(
                            [commit("d0", "Demo base")],
                            {"demo-main": "d0"},
                            "demo-main",
                            working_tree={"demo-draft.md": "modified"},
                            staging={"demo-config.yml": "modified"},
                        ),
                    ),
                    self._demo_step(
                        "git diff --staged",
                        "git diff --staged confirms what is currently staged. Use it to verify your staging scope before committing.",
                        graph(
                            [commit("d0", "Demo base")],
                            {"demo-main": "d0"},
                            "demo-main",
                            working_tree={"demo-draft.md": "modified"},
                            staging={"demo-config.yml": "modified"},
                        ),
                    ),
                    self._demo_step(
                        "git restore --staged demo-config.yml",
                        "git restore --staged moves a path back out of staging. This can be used to correct an accidental stage without changing commit history.",
                        graph(
                            [commit("d0", "Demo base")],
                            {"demo-main": "d0"},
                            "demo-main",
                            working_tree={
                                "demo-config.yml": "modified",
                                "demo-draft.md": "modified",
                            },
                        ),
                    ),
                ],
                "related_git_concepts": ["working tree", "staging area", "selected changes"],
            },
            "wrong-branch-commit": self._head_pointer_preview(
                title="Branch Pointers and HEAD",
                summary="Reason about the current branch before moving or preserving work.",
            ),
            "detached-work-rescue": {
                **self._head_pointer_preview(
                    title="Detached HEAD Rescue",
                    summary="Recognize when HEAD points at a commit instead of a branch.",
                ),
                "focus": "git switch -c",
                "primary_focus_commands": ["git switch -c"],
                "supporting_inspection_commands": ["git status", "git branch", "git log --oneline --graph"],
                "short_explanation": "A detached HEAD means the current position is a commit rather than a branch label. Creating a branch can give that position a stable name without exposing any real scenario state.",
            },
            "accidental-reset-recovery": {
                "title": "Branch Pointer Recovery",
                "focus": "branch pointer recovery workflow",
                "summary": "Inspect reachable commits before deciding how a moved branch pointer should recover.",
                "short_explanation": "Pointer recovery starts by reading the graph: branch labels can move, but reachable commits may still be visible through another safe reference.",
                "skill_focus_type": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
                "primary_focus_commands": ["git reset"],
                "supporting_inspection_commands": [
                    "git status",
                    "git branch",
                    "git log --oneline --graph",
                ],
                "safe_demo_commands": [
                    "git branch",
                    "git log --oneline --graph",
                    "git reset --hard demo-safe",
                ],
                "demo_repository_state": self._demo_snapshot(
                    graph(
                        [commit("d0", "Demo base"), commit("d1", "Demo saved work", ["d0"])],
                        {"demo-main": "d0", "demo-safe": "d1"},
                        "demo-main",
                    )
                ),
                "demo_explanation_steps": [
                    self._demo_step(
                        "git branch",
                        "The demo branch list shows labels that point at reachable commits.",
                        graph(
                            [commit("d0", "Demo base"), commit("d1", "Demo saved work", ["d0"])],
                            {"demo-main": "d0", "demo-safe": "d1"},
                            "demo-main",
                        ),
                    ),
                    self._demo_step(
                        "git log --oneline --graph",
                        "The demo graph makes the saved work visible before any pointer movement.",
                        graph(
                            [commit("d0", "Demo base"), commit("d1", "Demo saved work", ["d0"])],
                            {"demo-main": "d0", "demo-safe": "d1"},
                            "demo-main",
                        ),
                    ),
                    self._demo_step(
                        "git reset --hard demo-safe",
                        "The current demo branch pointer moves to the demo-safe commit and the working tree is clean.",
                        graph(
                            [commit("d0", "Demo base"), commit("d1", "Demo saved work", ["d0"])],
                            {"demo-main": "d1", "demo-safe": "d1"},
                            "demo-main",
                        ),
                    ),
                ],
                "related_git_concepts": ["branch pointers", "reachable commits", "HEAD"],
            },
            "divergent-branches": self._merge_preview(
                title="Divergent Branches and Merge Recovery",
                summary="Inspect diverged histories and safely bring work together.",
            ),
            "merge-conflict": {
                "title": "Merge Conflict State",
                "focus": "merge conflict resolution workflow",
                "summary": "Read a paused merge as repository state that can be completed safely.",
                "short_explanation": "A merge conflict means Git paused integration until the conflicted content is resolved and the merge can be completed.",
                "skill_focus_type": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
                "primary_focus_commands": ["git status", "git add", "git commit"],
                "supporting_inspection_commands": ["git status", "git log --oneline --graph"],
                "safe_demo_commands": [
                    "git status",
                    "git add demo-conflict.txt",
                    'git commit -m "demo merge"',
                ],
                "demo_repository_state": self._demo_snapshot(
                    graph(
                        [
                            commit("d0", "Demo base"),
                            commit("d1", "Demo main edit", ["d0"]),
                            commit("d2", "Demo team edit", ["d0"]),
                        ],
                        {"demo-main": "d1", "demo-topic": "d2"},
                        "demo-main",
                        merge_parent="d2",
                        conflicts=["demo-conflict.txt"],
                    )
                ),
                "demo_explanation_steps": [
                    self._demo_step(
                        "git status",
                        "The demo status explains that the repository is paused during a merge with one conflicted file.",
                        graph(
                            [
                                commit("d0", "Demo base"),
                                commit("d1", "Demo main edit", ["d0"]),
                                commit("d2", "Demo team edit", ["d0"]),
                            ],
                            {"demo-main": "d1", "demo-topic": "d2"},
                            "demo-main",
                            merge_parent="d2",
                            conflicts=["demo-conflict.txt"],
                        ),
                    ),
                    self._demo_step(
                        "git add demo-conflict.txt",
                        "The demo file is marked resolved and moves to the staging area; no real scenario file is involved.",
                        graph(
                            [
                                commit("d0", "Demo base"),
                                commit("d1", "Demo main edit", ["d0"]),
                                commit("d2", "Demo team edit", ["d0"]),
                            ],
                            {"demo-main": "d1", "demo-topic": "d2"},
                            "demo-main",
                            merge_parent="d2",
                            staging={"demo-conflict.txt": "resolved"},
                        ),
                    ),
                    self._demo_step(
                        'git commit -m "demo merge"',
                        "The demo merge completes with a merge commit that has both demo parents.",
                        graph(
                            [
                                commit("d0", "Demo base"),
                                commit("d1", "Demo main edit", ["d0"]),
                                commit("d2", "Demo team edit", ["d0"]),
                                commit("d3", "Demo merge", ["d1", "d2"]),
                            ],
                            {"demo-main": "d3", "demo-topic": "d2"},
                            "demo-main",
                        ),
                    ),
                ],
                "related_git_concepts": ["merge state", "conflicts", "staging area"],
            },
            "branch-cleanup": {
                "title": "Branch Cleanup",
                "focus": "git branch -d",
                "summary": "Remove an already-finished branch label without changing commit history.",
                "short_explanation": "Deleting a branch removes a label. It does not delete commits that are still reachable from another branch.",
                "skill_focus_type": ScenarioSkillFocus.SkillFocusType.COMMAND_SPECIFIC,
                "primary_focus_commands": ["git branch -d"],
                "supporting_inspection_commands": ["git branch", "git log --oneline --graph"],
                "safe_demo_commands": [
                    "git branch",
                    "git branch -d demo-old",
                ],
                "demo_repository_state": self._demo_snapshot(
                    graph(
                        [commit("d0", "Demo base"), commit("d1", "Demo merged work", ["d0"])],
                        {"demo-main": "d1", "demo-old": "d1"},
                        "demo-main",
                    )
                ),
                "demo_explanation_steps": [
                    self._demo_step(
                        "git branch",
                        "The demo branch list shows demo-old pointing at the same commit as demo-main.",
                        graph(
                            [commit("d0", "Demo base"), commit("d1", "Demo merged work", ["d0"])],
                            {"demo-main": "d1", "demo-old": "d1"},
                            "demo-main",
                        ),
                    ),
                    self._demo_step(
                        "git branch -d demo-old",
                        "The demo-old branch label is removed while the commit history stays in place.",
                        graph(
                            [commit("d0", "Demo base"), commit("d1", "Demo merged work", ["d0"])],
                            {"demo-main": "d1"},
                            "demo-main",
                        ),
                    ),
                ],
                "related_git_concepts": ["branch labels", "reachable commits", "cleanup"],
            },
            "release-integration-capstone": {
                **self._merge_preview(
                    title="Integrated Merge and Cleanup Workflow",
                    summary="Combine inspection, integration, and branch cleanup in a safe workflow.",
                ),
                "focus": "integration cleanup workflow",
                "primary_focus_commands": ["git merge", "git branch -d"],
                "safe_demo_commands": [
                    "git branch",
                    "git merge demo-topic",
                    "git branch -d demo-old",
                ],
                "related_git_concepts": ["divergence", "merge commits", "branch cleanup"],
            },
        }
        return {
            "demo_dag_config": {"mode": "preview_only", "layout": "compact"},
            **previews[slug],
        }

    def _head_pointer_preview(self, *, title: str, summary: str) -> dict:
        return {
            "title": title,
            "focus": "git branch, git switch",
            "summary": summary,
            "short_explanation": "HEAD marks the current checkout. Switching branches changes which branch HEAD refers to without changing the commit graph by itself.",
            "skill_focus_type": ScenarioSkillFocus.SkillFocusType.CONCEPT_SPECIFIC,
            "primary_focus_commands": ["git branch", "git switch"],
            "supporting_inspection_commands": ["git status", "git log --oneline --graph"],
            "safe_demo_commands": [
                "git branch",
                "git switch demo-feature",
            ],
            "demo_repository_state": self._demo_snapshot(
                graph(
                    [commit("d0", "Demo base"), commit("d1", "Demo feature", ["d0"])],
                    {"demo-main": "d0", "demo-feature": "d1"},
                    "demo-main",
                )
            ),
            "demo_explanation_steps": [
                self._demo_step(
                    "git branch",
                    "The demo branch list shows which branch HEAD currently refers to.",
                    graph(
                        [commit("d0", "Demo base"), commit("d1", "Demo feature", ["d0"])],
                        {"demo-main": "d0", "demo-feature": "d1"},
                        "demo-main",
                    ),
                ),
                self._demo_step(
                    "git switch demo-feature",
                    "HEAD moved to the demo-feature branch. The branch pointer stayed in place because no new commit was created.",
                    graph(
                        [commit("d0", "Demo base"), commit("d1", "Demo feature", ["d0"])],
                        {"demo-main": "d0", "demo-feature": "d1"},
                        "demo-feature",
                    ),
                ),
            ],
            "related_git_concepts": ["HEAD", "branch pointers", "checkout state"],
        }

    def _merge_preview(self, *, title: str, summary: str) -> dict:
        return {
            "title": title,
            "focus": "merge recovery workflow",
            "summary": summary,
            "short_explanation": "A merge attempts to bring changes from another branch into the current branch while preserving the visible history of both sides.",
            "skill_focus_type": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
            "primary_focus_commands": ["git merge"],
            "supporting_inspection_commands": [
                "git status",
                "git branch",
                "git log --oneline --graph",
            ],
            "safe_demo_commands": [
                "git branch",
                "git log --oneline --graph",
                "git merge demo-topic",
            ],
            "demo_repository_state": self._demo_snapshot(
                graph(
                    [
                        commit("d0", "Demo base"),
                        commit("d1", "Demo main edit", ["d0"]),
                        commit("d2", "Demo topic edit", ["d0"]),
                    ],
                    {"demo-main": "d1", "demo-topic": "d2"},
                    "demo-main",
                )
            ),
            "demo_explanation_steps": [
                self._demo_step(
                    "git branch",
                    "The demo branch list shows the current branch and the branch that can be inspected.",
                    graph(
                        [
                            commit("d0", "Demo base"),
                            commit("d1", "Demo main edit", ["d0"]),
                            commit("d2", "Demo topic edit", ["d0"]),
                        ],
                        {"demo-main": "d1", "demo-topic": "d2"},
                        "demo-main",
                    ),
                ),
                self._demo_step(
                    "git log --oneline --graph",
                    "The demo graph shows two branch pointers that diverged from the same base commit.",
                    graph(
                        [
                            commit("d0", "Demo base"),
                            commit("d1", "Demo main edit", ["d0"]),
                            commit("d2", "Demo topic edit", ["d0"]),
                        ],
                        {"demo-main": "d1", "demo-topic": "d2"},
                        "demo-main",
                    ),
                ),
                self._demo_step(
                    "git merge demo-topic",
                    "The demo merge creates a new merge commit on the current branch and preserves both parent commits.",
                    graph(
                        [
                            commit("d0", "Demo base"),
                            commit("d1", "Demo main edit", ["d0"]),
                            commit("d2", "Demo topic edit", ["d0"]),
                            commit("d3", "Demo merge", ["d1", "d2"]),
                        ],
                        {"demo-main": "d3", "demo-topic": "d2"},
                        "demo-main",
                    ),
                ),
            ],
            "related_git_concepts": ["divergence", "merge commits", "branch pointers"],
        }

    def _demo_step(self, command: str, explanation: str, state: dict) -> dict:
        return {
            "command": command,
            "explanation": explanation,
            "repository_state": self._demo_snapshot(state),
        }

    def _demo_snapshot(self, state: dict) -> dict:
        return RepositorySnapshotService().snapshot(state)

    def _difficulty(
        self,
        narrative: str,
        task: str,
        policy: tuple[int, int, list[str]],
        rule: dict,
        variants: list[dict],
    ) -> dict:
        return {
            "narrative": narrative,
            "task": task,
            "policy": policy,
            "rule": rule,
            "variants": variants,
        }

    def _variant(
        self,
        slug: str,
        label: str,
        signature: str,
        initial_state: dict,
        solution_commands: list[str] | None = None,
    ) -> dict:
        target_state = (
            self._target_state_from_solution(initial_state, solution_commands)
            if solution_commands
            else self._expected_state_from_initial(initial_state)
        )
        return {
            "slug": slug,
            "label": label,
            "structure_signature": signature,
            "initial_state": initial_state,
            "target_state": target_state,
            "expected_state_diagram": RepositorySnapshotService().snapshot(target_state),
            "is_published": True,
        }

    def _target_state_from_solution(self, initial_state: dict, commands: list[str]) -> dict:
        simulator = RepositoryStateSimulator()
        state = simulator.clone_state(initial_state)
        for command in commands:
            result = simulator.process(state, command)
            if not result.processed:
                raise ValueError(f"Seed solution command failed for {command!r}: {result.output}")
            state = result.state
        return state

    def _detached_rescue_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        base_commits: list[dict] | None = None,
        branches: dict | None = None,
        detached_at: str = "c0",
    ) -> dict:
        commits = base_commits or [commit("c0", "Base")]
        branch_map = branches or {"main": "c0"}
        diagnostics = ["git status", "git log --oneline", "git branch -v"]
        return self._difficulty(
            narrative,
            task,
            (3, 9, diagnostics),
            {
                "head_branch": "feature/rescue",
                "branch_exists": ["feature/rescue"],
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
                "min_commits_on_branch": {"feature/rescue": 2},
            },
            [
                self._variant(
                    f"{prefix}-notes",
                    "Detached notes work",
                    f"{prefix}-notes-detached",
                    graph(
                        commits,
                        branch_map,
                        "main",
                        head={"type": "detached", "target": detached_at},
                        working_tree={"notes.md": "modified"},
                    ),
                    ["git switch -c feature/rescue", "git add .", 'git commit -m "rescue notes"'],
                ),
                self._variant(
                    f"{prefix}-patch",
                    "Detached patch work",
                    f"{prefix}-patch-detached",
                    graph(
                        commits,
                        {**branch_map, "archive/base": detached_at},
                        "main",
                        head={"type": "detached", "target": detached_at},
                        working_tree={"patch.txt": "modified"},
                    ),
                    ["git switch -c feature/rescue", "git add .", 'git commit -m "rescue patch"'],
                ),
            ],
        )

    def _reset_recovery_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        extra_branches: dict | None = None,
    ) -> dict:
        branches = {"main": "c0", "safety-copy": "c1", **(extra_branches or {})}
        diagnostics = ["git status", "git log --oneline", "git branch -v"]
        return self._difficulty(
            narrative,
            task,
            (1, 7, diagnostics),
            {
                "head_branch": "main",
                "branch_exists": ["safety-copy"],
                "branches_equal": [["main", "safety-copy"]],
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
            },
            [
                self._variant(
                    f"{prefix}-local-work",
                    "Safety copy holds local work",
                    f"{prefix}-local-work",
                    graph(
                        [commit("c0", "Base"), commit("c1", "Lost local work", ["c0"])],
                        branches,
                        "main",
                    ),
                    ["git reset safety-copy"],
                ),
                self._variant(
                    f"{prefix}-report-work",
                    "Safety copy holds report work",
                    f"{prefix}-report-work",
                    graph(
                        [commit("c0", "Base"), commit("c1", "Recovered report", ["c0"])],
                        branches,
                        "main",
                    ),
                    ["git reset safety-copy"],
                ),
            ],
        )

    def _merge_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        source_branch: str,
        extra_branches: dict | None = None,
    ) -> dict:
        diagnostics = ["git status", "git log --oneline", "git branch -v"]
        return self._difficulty(
            narrative,
            task,
            (1, 8, diagnostics),
            {
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
                "min_commits_on_branch": {"main": 3},
            },
            [
                self._variant(
                    f"{prefix}-feature-a",
                    "Diverged feature branch",
                    f"{prefix}-feature-a",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Team update", ["c0"]),
                            commit("c2", "Feature work", ["c0"]),
                        ],
                        {"main": "c1", source_branch: "c2", **(extra_branches or {})},
                        "main",
                    ),
                    [f"git merge {source_branch}"],
                ),
                self._variant(
                    f"{prefix}-feature-b",
                    "Diverged feature branch with docs base",
                    f"{prefix}-feature-b",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Main patch", ["c0"]),
                            commit("c2", "Feature polish", ["c0"]),
                        ],
                        {
                            "main": "c1",
                            source_branch: "c2",
                            "docs/reference": "c0",
                            **(extra_branches or {}),
                        },
                        "main",
                    ),
                    [f"git merge {source_branch}"],
                ),
            ],
        )

    def _conflict_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        conflict_file: str,
        source_branch: str,
        extra_branches: dict | None = None,
    ) -> dict:
        diagnostics = ["git status", "git diff", "git log --oneline", "git branch -v"]
        return self._difficulty(
            narrative,
            task,
            (2, 9, diagnostics),
            {
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
                "min_commits_on_branch": {"main": 3},
            },
            [
                self._variant(
                    f"{prefix}-active-conflict",
                    "Active conflict state",
                    f"{prefix}-active-conflict",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Main edit", ["c0"]),
                            commit("c2", "Feature edit", ["c0"]),
                        ],
                        {"main": "c1", source_branch: "c2", **(extra_branches or {})},
                        "main",
                        merge_parent="c2",
                        conflicts=[conflict_file],
                        working_tree={conflict_file: "conflict"},
                    ),
                    [f"git add {conflict_file}", 'git commit -m "resolved integration"'],
                ),
                self._variant(
                    f"{prefix}-active-conflict-review",
                    "Active conflict with review label",
                    f"{prefix}-active-conflict-review",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Main copy", ["c0"]),
                            commit("c2", "Feature copy", ["c0"]),
                        ],
                        {
                            "main": "c1",
                            source_branch: "c2",
                            "review/base": "c0",
                            **(extra_branches or {}),
                        },
                        "main",
                        merge_parent="c2",
                        conflicts=[conflict_file],
                        working_tree={conflict_file: "conflict"},
                    ),
                    [f"git add {conflict_file}", 'git commit -m "resolved integration"'],
                ),
            ],
        )

    def _cleanup_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        extra_branches: dict | None = None,
    ) -> dict:
        diagnostics = ["git status", "git branch", "git log --oneline"]
        return self._difficulty(
            narrative,
            task,
            (1, 5, diagnostics),
            {
                "head_branch": "main",
                "branch_absent": ["old-feature"],
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
            },
            [
                self._variant(
                    f"{prefix}-merged-feature",
                    "Merged branch shares main tip",
                    f"{prefix}-merged-feature",
                    graph(
                        [commit("c0", "Base"), commit("c1", "Merged feature", ["c0"])],
                        {"main": "c1", "old-feature": "c1", **(extra_branches or {})},
                        "main",
                    ),
                    ["git branch -d old-feature"],
                ),
                self._variant(
                    f"{prefix}-merged-topic",
                    "Merged topic branch shares main tip",
                    f"{prefix}-merged-topic",
                    graph(
                        [commit("c0", "Base"), commit("c1", "Merged topic", ["c0"])],
                        {
                            "main": "c1",
                            "old-feature": "c1",
                            "docs/reference": "c0",
                            **(extra_branches or {}),
                        },
                        "main",
                    ),
                    ["git branch -d old-feature"],
                ),
            ],
        )

    def _capstone_difficulty(
        self,
        narrative: str,
        task: str,
        prefix: str,
        extra_branches: dict | None = None,
    ) -> dict:
        diagnostics = ["git status", "git log --oneline", "git branch -v", "git diff"]
        return self._difficulty(
            narrative,
            task,
            (2, 9, diagnostics),
            {
                "head_branch": "main",
                "branch_absent": ["old-feature"],
                "working_tree_clean": True,
                "staging_empty": True,
                "conflict_free": True,
                "min_commits_on_branch": {"main": 3},
            },
            [
                self._variant(
                    f"{prefix}-release-a",
                    "Release branch and stale feature",
                    f"{prefix}-release-a",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Main readiness", ["c0"]),
                            commit("c2", "Release topic", ["c0"]),
                        ],
                        {
                            "main": "c1",
                            "release/topic": "c2",
                            "old-feature": "c1",
                            **(extra_branches or {}),
                        },
                        "main",
                    ),
                    ["git merge release/topic", "git branch -d old-feature"],
                ),
                self._variant(
                    f"{prefix}-release-b",
                    "Release branch after docs update",
                    f"{prefix}-release-b",
                    graph(
                        [
                            commit("c0", "Base"),
                            commit("c1", "Main readiness", ["c0"]),
                            commit("c2", "Release topic", ["c0"]),
                        ],
                        {
                            "main": "c1",
                            "release/topic": "c2",
                            "old-feature": "c1",
                            "docs/reference": "c0",
                            **(extra_branches or {}),
                        },
                        "main",
                    ),
                    ["git merge release/topic", "git branch -d old-feature"],
                ),
            ],
        )

    def _expected_state_from_initial(self, initial_state: dict) -> dict:
        commits = [dict(item) for item in initial_state.get("commits", [])]
        branches = dict(initial_state.get("branches", {}))
        head = dict(initial_state.get("head", {}))
        head_name = head.get("name")
        head_target = branches.get(head_name)

        if initial_state.get("merge_parent"):
            new_id = f"c{len(commits)}"
            commits.append(
                {
                    "id": new_id,
                    "message": "Resolved integration",
                    "parents": [head_target, initial_state["merge_parent"]],
                }
            )
            branches[head_name] = new_id
        elif initial_state.get("working_tree"):
            new_id = f"c{len(commits)}"
            parents = [head_target] if head_target else []
            commits.append(
                {"id": new_id, "message": "Intentional repository update", "parents": parents}
            )
            branches[head_name] = new_id

        if "old-feature" in branches:
            branches.pop("old-feature", None)

        if "feature/recovery" in branches:
            head = {"type": "branch", "name": "feature/recovery"}
            if branches["feature/recovery"] == "c0" and len(commits) > 1:
                new_id = f"c{len(commits)}"
                commits.append(
                    {"id": new_id, "message": "Recovered feature work", "parents": ["c0"]}
                )
                branches["feature/recovery"] = new_id

        if "safety-copy" in branches and head.get("name") == "main":
            branches["main"] = branches["safety-copy"]

        head_target = branches.get(head.get("name"))
        return {"commits": commits, "branches": branches, "head": {**head, "target": head_target}}

    def _lesson_visual(self, slug: str) -> str:
        visuals = {
            "three-file-areas": """
              <section class="lesson-visual">
                <div class="visual-label">Repository map</div>
                <div class="area-row">
                  <div class="area-card"><span>Working tree</span><strong>edited files</strong><small>Where files change first</small></div>
                  <span class="diagram-arrow">-&gt;</span>
                  <div class="area-card accent"><span>Staging area</span><strong>chosen snapshot</strong><small>What the next commit will record</small></div>
                  <span class="diagram-arrow">-&gt;</span>
                  <div class="area-card"><span>Repository</span><strong>commit history</strong><small>Saved snapshots on branches</small></div>
                </div>
              </section>
            """,
            "tracked-untracked": """
              <section class="lesson-visual">
                <div class="visual-label">Status split</div>
                <div class="status-columns">
                  <div class="state-card accent"><strong>Tracked</strong><span>Git can compare this path against history.</span><code>app.py modified</code></div>
                  <div class="state-card"><strong>Untracked</strong><span>The file exists, but Git has not been asked to remember it.</span><code>notes.md untracked</code></div>
                  <div class="state-card"><strong>Staged</strong><span>This path is already selected for the next snapshot.</span><code>config.yml staged</code></div>
                </div>
              </section>
            """,
            "what-head-is": """
              <section class="lesson-visual">
                <div class="visual-label">HEAD as current position</div>
                <div class="commit-row">
                  <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="diagram-line"></span><span class="commit-node active">c2</span>
                </div>
                <div class="label-row"><span class="branch-tag">main</span><span class="head-tag">HEAD -&gt; main</span></div>
              </section>
            """,
            "dag-literacy": """
              <section class="lesson-visual">
                <div class="visual-label">Divergence and merge shape</div>
                <div class="graph-stack">
                  <div class="commit-row"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="diagram-line fork"></span><span class="commit-node">c3</span></div>
                  <div class="commit-row offset"><span class="commit-node branch">c2</span><span class="diagram-line merge"></span><span class="commit-node active">c4</span></div>
                </div>
                <div class="label-row"><span class="branch-tag">feature</span><span class="branch-tag">main</span><span class="head-tag">merge commit has two parents</span></div>
              </section>
            """,
            "branch-pointers": """
              <section class="lesson-visual">
                <div class="visual-label">Branches are labels</div>
                <div class="commit-row">
                  <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span><span class="diagram-line"></span><span class="commit-node ghost">next</span>
                </div>
                <div class="label-row"><span class="branch-tag">main points at c1</span><span class="head-tag">new commit moves the label</span></div>
              </section>
            """,
            "command-anatomy": """
              <section class="lesson-visual">
                <div class="visual-label">Read the command shape</div>
                <div class="command-parse">
                  <span><strong>git</strong><small>program</small></span>
                  <span><strong>commit</strong><small>action</small></span>
                  <span><strong>-m</strong><small>option</small></span>
                  <span><strong>"update config"</strong><small>message</small></span>
                </div>
              </section>
            """,
            "practice-rules": """
              <section class="lesson-visual">
                <div class="visual-label">Practice loop</div>
                <div class="workflow-strip">
                  <span>Inspect</span><span>Explain state</span><span>Act</span><span>Read feedback</span><span>Retry if needed</span>
                </div>
              </section>
            """,
            "scaffolds-review": """
              <section class="lesson-visual">
                <div class="visual-label">Support fades by level</div>
                <div class="level-ladder">
                  <div><strong>Easy</strong><span>DAG, target picture, feedback, action budget</span></div>
                  <div><strong>Medium</strong><span>DAG and target picture</span></div>
                  <div><strong>Hard</strong><span>DAG and story context</span></div>
                </div>
              </section>
            """,
            "status-reading": """
              <section class="lesson-visual">
                <div class="visual-label">Status tells you where to look</div>
                <div class="status-columns">
                  <div class="state-card"><strong>On branch</strong><span>Where HEAD is attached</span><code>main</code></div>
                  <div class="state-card accent"><strong>Staged</strong><span>Ready for commit</span><code>config.yml</code></div>
                  <div class="state-card"><strong>Not staged</strong><span>Changed but not selected</span><code>draft.md</code></div>
                </div>
              </section>
            """,
            "first-commit": """
              <section class="lesson-visual">
                <div class="visual-label">Commit formation</div>
                <div class="area-row">
                  <div class="area-card"><span>Working tree</span><strong>README.md, app.py</strong></div>
                  <span class="diagram-arrow">-&gt;</span>
                  <div class="area-card accent"><span>Staging</span><strong>selected files</strong></div>
                  <span class="diagram-arrow">-&gt;</span>
                  <div class="area-card"><span>main</span><strong>c1 starter snapshot</strong></div>
                </div>
              </section>
            """,
            "history-inspection": """
              <section class="lesson-visual">
                <div class="visual-label">History answers what already happened</div>
                <div class="commit-row">
                  <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="diagram-line"></span><span class="commit-node active">c2</span>
                </div>
                <div class="label-row"><span class="branch-tag">main</span><span class="branch-tag">feature starts at c1</span><span class="head-tag">read before changing</span></div>
              </section>
            """,
            "branch-head": """
              <section class="lesson-visual split-visual">
                <div class="visual-label">Attached vs detached</div>
                <div class="state-card accent"><strong>Attached</strong><span>HEAD -&gt; main -&gt; c2</span><small>New commits move main.</small></div>
                <div class="state-card"><strong>Detached</strong><span>HEAD -&gt; c1</span><small>New work needs a branch name.</small></div>
              </section>
            """,
            "detached-head": """
              <section class="lesson-visual">
                <div class="visual-label">Make detached work reachable</div>
                <div class="commit-row">
                  <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span><span class="diagram-arrow">-&gt;</span><span class="branch-tag">feature/rescue</span>
                </div>
                <div class="label-row"><span class="head-tag">Give useful work a name before moving on</span></div>
              </section>
            """,
            "right-branch": """
              <section class="lesson-visual">
                <div class="visual-label">Wrong branch recovery shape</div>
                <div class="graph-stack">
                  <div class="commit-row"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node active">c1</span><span class="branch-tag danger">main has feature work</span></div>
                  <div class="commit-row offset"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node target">c1 copy</span><span class="branch-tag">feature/recovery</span></div>
                </div>
              </section>
            """,
            "undo-without-panic": """
              <section class="lesson-visual">
                <div class="visual-label">Recovery decision</div>
                <div class="workflow-strip">
                  <span>What changed?</span><span>What must survive?</span><span>Where should HEAD finish?</span>
                </div>
              </section>
            """,
            "reset-recovery": """
              <section class="lesson-visual">
                <div class="visual-label">Restore the branch pointer</div>
                <div class="commit-row">
                  <span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node target">c1</span><span class="branch-tag">safety-copy</span><span class="diagram-arrow">-&gt;</span><span class="head-tag">main should point here again</span>
                </div>
              </section>
            """,
            "divergence-merge": """
              <section class="lesson-visual">
                <div class="visual-label">Integrate both lines of work</div>
                <div class="graph-stack">
                  <div class="commit-row"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node">c1</span><span class="branch-tag">main</span></div>
                  <div class="commit-row offset"><span class="commit-node">c0</span><span class="diagram-line"></span><span class="commit-node branch">c2</span><span class="diagram-line merge"></span><span class="commit-node active">c3</span></div>
                </div>
                <div class="label-row"><span class="head-tag">target: main reaches both histories</span></div>
              </section>
            """,
            "conflict-state": """
              <section class="lesson-visual">
                <div class="visual-label">Conflict state is a paused merge</div>
                <div class="status-columns">
                  <div class="state-card danger"><strong>Conflict</strong><span>forms.py needs a resolved version</span></div>
                  <div class="state-card accent"><strong>Stage resolved file</strong><span>Tell Git the conflict is handled</span></div>
                  <div class="state-card"><strong>Finish merge</strong><span>Record both parents in history</span></div>
                </div>
              </section>
            """,
            "team-flow-capstone": """
              <section class="lesson-visual">
                <div class="visual-label">Capstone workflow</div>
                <div class="workflow-strip">
                  <span>Read graph</span><span>Integrate release</span><span>Remove stale branch</span><span>Verify clean state</span>
                </div>
              </section>
            """,
        }
        return visuals.get(slug, "")

    def _orientation_html(self, slug: str, title: str, subtitle: str) -> str:
        bodies = {
            "three-file-areas": """
              <section class="lesson-grid">
                <div class="lesson-panel">
                  <h2>The three-area map</h2>
                  <p>Git becomes much less mysterious when every change is placed into one of three areas. The working tree is the file system you are editing right now. The staging area is a proposed snapshot that says what the next commit should contain. The repository history is the chain of commits Git has already recorded.</p>
                  <p>Many beginner mistakes happen because those areas are mixed together in the student's head. A file can be edited but not staged. A file can be staged even while newer unstaged edits exist in the working tree. A clean working tree means the working tree and staging area have no pending differences relative to the current commit.</p>
                </div>
                <div class="state-strip">
                  <span>Working tree</span>
                  <span>Staging area</span>
                  <span>Repository history</span>
                </div>
              </section>
              <section class="lesson-panel">
                <h2>How to read the simulator</h2>
                <p>The DAG shows committed history: commit nodes, parent links, branch labels, and HEAD. It does not show every file detail by itself, so the lesson pairs graph reading with status language. When a scenario asks for a clean repository, it is asking for both the staging area and the working tree to be settled.</p>
                <p>Before using a state-changing command, ask two questions: where is the change now, and where should it move next? If the change is only in the working tree, staging may be appropriate. If the change is staged, a commit may be appropriate. If it is already committed on the wrong branch, the problem is no longer about files alone; it is about pointers and reachability.</p>
              </section>
              <pre><code>git status
# Read the branch, staged paths, unstaged paths, and untracked paths before acting.</code></pre>
            """,
            "tracked-untracked": """
              <section class="lesson-grid">
                <div class="lesson-panel">
                  <h2>Tracked is a relationship, not a folder</h2>
                  <p>A tracked file is a path Git already knows from a previous commit or from the staging area. Git can compare it against history, show whether it changed, and include it in a future commit. An untracked file exists in the working tree, but Git has not been told to include it in history yet.</p>
                  <p>That distinction matters because untracked files can be easy to overlook. A student may commit a bug fix and accidentally leave a new required file outside history. The reverse can also happen: a scratch file becomes tracked because everything was staged without checking scope.</p>
                </div>
                <div class="lesson-panel accent-panel">
                  <h2>Status vocabulary</h2>
                  <p>Status output is not just noise. It tells whether a path is untracked, modified but unstaged, staged for commit, or clean. Each label describes the relationship between the working tree, the staging area, and the current commit.</p>
                </div>
              </section>
              <section class="lesson-panel">
                <h2>Why selected staging exists</h2>
                <p>Real team work often mixes ready changes with messy notes. The platform's partial-staging scenarios are built around this habit: inspect first, move only the intended paths into the staged snapshot, and leave draft work visible but uncommitted. The goal is not to memorize a command. The goal is to preserve the meaning of the next commit.</p>
              </section>
              <pre><code>git status
git diff
# Inspect before deciding which paths belong in the next snapshot.</code></pre>
            """,
            "what-head-is": """
              <section class="lesson-grid">
                <div class="lesson-panel">
                  <h2>HEAD answers "where am I?"</h2>
                  <p>HEAD is Git's name for the current position. Most of the time HEAD is attached to a branch, which means it points to a branch label and that branch label points to a commit. When you create a new commit in this attached state, the branch label moves forward to the new commit.</p>
                  <p>When HEAD is detached, it points directly to a commit instead of a branch label. This is not automatically dangerous, but it changes the safety question. New work created from a detached position needs a branch name if you want it to remain easy to find.</p>
                </div>
                <div class="state-strip vertical">
                  <span>HEAD -> main -> c3</span>
                  <span>HEAD -> c3</span>
                </div>
              </section>
              <section class="lesson-panel">
                <h2>What HEAD predicts</h2>
                <p>Before committing, switching, merging, or recovering, identify HEAD. It predicts which branch will move, which branch will receive a merge, and where a new commit would appear. In wrong-branch scenarios, the files may look correct while HEAD reveals that the commit is about to land on the wrong branch.</p>
                <p>The live DAG makes HEAD visible so students can reason from the current state instead of relying on memory. When the scenario changes variants, branch names and nearby commits may differ, but HEAD still gives the same kind of information.</p>
              </section>
            """,
            "dag-literacy": """
              <section class="lesson-panel">
                <h2>Commits are nodes, parents are evidence</h2>
                <p>Git history is a directed acyclic graph. Each commit is a node. Parent links explain where that commit came from. A normal commit usually has one parent. A merge commit has more than one parent because it records the act of joining histories.</p>
                <p>The graph is acyclic because history does not loop backward into itself. A later commit can point to earlier parents, but an earlier commit never points forward to a future child. This one idea makes branch divergence, merging, and recovery much easier to reason about.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel">
                  <h2>Labels are movable</h2>
                  <p>Branch names are labels pointing at commits. The commit does not contain the branch. The branch label simply names the current tip of a line of work.</p>
                </div>
                <div class="lesson-panel">
                  <h2>Read the shape</h2>
                  <p>A straight line suggests one path of history. A split suggests divergence. A merge commit with two parents suggests integration. A stale branch label may point to work that is already reachable from another branch.</p>
                </div>
              </section>
              <pre><code>git log --oneline --graph
git branch -v
# Pair text history with the live DAG to explain the repository shape.</code></pre>
            """,
            "branch-pointers": """
              <section class="lesson-grid">
                <div class="lesson-panel">
                  <h2>A branch is a label that moves</h2>
                  <p>A branch is not a folder, not a copy of the project, and not a separate database. It is a movable label pointing to a commit. When HEAD is attached to that branch and a new commit is created, the branch label advances to the new commit.</p>
                  <p>This explains why a wrong-branch commit is recoverable. The work exists as a commit. The task is to move or recreate the intended pointer relationship without throwing away reachable work.</p>
                </div>
                <div class="lesson-panel accent-panel">
                  <h2>Switching is not copying</h2>
                  <p>Switching branches changes which branch HEAD is attached to and updates the working tree to match. It does not duplicate history. It changes the active viewpoint.</p>
                </div>
              </section>
              <section class="lesson-panel">
                <h2>Pointer thinking prevents panic</h2>
                <p>Many destructive Git habits come from imagining branches as folders. If a branch is a folder, divergence feels like conflicting folders. If a branch is a pointer, divergence is just two labels naming different commits. That mental model makes recovery commands feel like pointer operations rather than emergency rituals.</p>
              </section>
            """,
            "command-anatomy": """
              <section class="lesson-panel">
                <h2>Commands have grammar</h2>
                <p>A Git command has parts: the program name <code>git</code>, a subcommand such as <code>status</code> or <code>commit</code>, optional flags, and arguments such as paths or branch names. Reading the grammar helps students understand intent before executing a command copied from a search result or AI tool.</p>
                <p>In GIT it!, commands are parsed by the simulator. Supported commands change the simulated repository state. Unsupported commands are rejected safely. No typed command runs in a real shell, and no command reaches a real repository.</p>
              </section>
              <section class="lesson-grid">
                <div class="command-slab"><code>git status</code><span>inspection: read state</span></div>
                <div class="command-slab"><code>git add &lt;path&gt;</code><span>action: propose content for commit</span></div>
                <div class="command-slab"><code>git branch -v</code><span>inspection: read labels</span></div>
              </section>
              <section class="lesson-panel">
                <h2>Inspect before action</h2>
                <p>Inspection commands are not wasted effort. The practice counter treats common read-only checks as free because good Git work starts by learning the state. Action commands should follow an explanation, not replace it.</p>
              </section>
            """,
            "practice-rules": """
              <section class="lesson-panel">
                <h2>A safe terminal with real consequences</h2>
                <p>The practice terminal is simulated. It does not execute operating-system commands, call the external Git CLI, connect to GitHub, or touch a student's real files. Within the simulator, however, commands still have consequences: branches move, commits appear, conflicts can exist, and the working tree can become clean or remain messy.</p>
                <p>This design gives students room to make mistakes without harming a real project. It also means every session can be logged consistently for completion, retry, command count, and state-transition analysis.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel">
                  <h2>Feedback is not an answer key</h2>
                  <p>The system explains what changed in the repository. It does not hand over a command script to copy.</p>
                </div>
                <div class="lesson-panel">
                  <h2>Action budget</h2>
                  <p>Each practice level has a limit for state-changing actions. Common read-only inspection commands stay available so you can reason before acting.</p>
                </div>
              </section>
              <section class="lesson-panel">
                <h2>How to practice well</h2>
                <p>Read the narrative, inspect the starting state, name the target state in your own words, then act. If an attempt fails or is abandoned, retry is part of the learning loop. The retry may use a changed variant so the student practices the concept, not a memorized surface pattern.</p>
              </section>
            """,
            "scaffolds-review": """
              <section class="lesson-panel">
                <h2>Scaffolding fades on purpose</h2>
                <p>Easy, Medium, and Hard are not just labels. They change the amount of support available while preserving the same core Git concept. Easy includes the live DAG, expected-state diagram, contextual feedback, and command counter. Medium removes contextual feedback but keeps the expected-state diagram. Hard keeps the live DAG and narrative context, asking the student to infer more independently.</p>
                <p>Easy is open first. Medium opens after Easy for the same practice topic, and Hard opens after Medium. The goal is to let support fade as the same Git idea becomes more familiar.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel">
                  <h2>Adaptive retry</h2>
                  <p>After a failed or abandoned attempt, retry can serve a changed version of the same level. The Git idea stays stable while branch names, file names, or graph shape may change.</p>
                </div>
                <div class="lesson-panel">
                  <h2>Review Mode</h2>
                  <p>After completing a difficulty instance, students can replay it in Review Mode. Review sessions are logged separately and do not overwrite the primary completion record.</p>
                </div>
              </section>
            """,
        }
        return f"""
        <article class="lesson-copy lesson-page lesson-page--{slug}">
          <section class="lesson-hero">
            <div class="lesson-kicker">Foundation lesson</div>
            <h1>{title}</h1>
            <p class="lesson-lede">{subtitle}</p>
            <div class="lesson-meta">
              <span>Git mental model</span>
              <span>Visual guide</span>
              <span>Mark read anytime</span>
            </div>
          </section>
          {self._lesson_visual(slug)}
          {bodies[slug]}
          <section class="lesson-panel remember-panel">
            <h2>What to carry forward</h2>
            <ul>
              <li>Explain the repository state before choosing a command.</li>
              <li>Use the live DAG and status language together; neither tells the whole story alone.</li>
              <li>Keep these foundations nearby while you practice harder repository states.</li>
            </ul>
          </section>
        </article>
        """

    def _lesson_html(self, slug: str, title: str, subtitle: str, scenario_bearing: bool) -> str:
        bodies = {
            "status-reading": """
              <section class="lesson-panel">
                <h2>Status is a state report</h2>
                <p><code>git status</code> is the fastest way to separate facts before acting. It tells the current branch, whether the working tree is clean, which paths are staged, which paths are modified but unstaged, which paths are untracked, and whether a merge or conflict state is in progress.</p>
                <p>Students often skip status because they are hunting for the next command. In this platform, status is part of the command plan. The status report lets the student decide whether the next action should move content into staging, create a commit, resolve a conflict, switch context, or stop because the repository is already in the target state.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Branch line</h2><p>Names the branch HEAD is attached to, or hints that HEAD is detached.</p></div>
                <div class="lesson-panel accent-panel"><h2>Path groups</h2><p>Separate staged, unstaged, untracked, and conflicted paths so scope mistakes become visible.</p></div>
                <div class="lesson-panel accent-panel"><h2>Clean state</h2><p>Means there is no staged or unstaged work pending against the current commit.</p></div>
              </section>
              <pre><code>git status
git diff
git diff --staged</code></pre>
              <section class="lesson-panel">
                <h2>How this appears in scenarios</h2>
                <p>In first-commit tasks, status tells whether files are still untracked or have been staged. In partial-staging tasks, status prevents draft work from being swept into a commit. In conflict tasks, status tells which paths still require resolution. The same habit scales across units: inspect the state, name the mismatch, then choose the smallest action that moves the repository toward the target.</p>
              </section>
            """,
            "first-commit": """
              <section class="lesson-panel">
                <h2>A commit is a chosen snapshot</h2>
                <p>A commit is not simply "saving the project." It is a deliberate snapshot with a branch destination, a content scope, and a message that communicates intent. The staging area is what makes that choice explicit. If the staging area contains everything, the next commit contains everything. If it contains one path, the next commit records one path.</p>
                <p>The first-commit scenarios begin with a simple question: what should become part of history now? Easy starts from an empty history and visible starter files. Medium adds an existing baseline commit. Hard adds nearby branch labels and expects the student to keep the focus on the branch and the intended snapshot.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Scope</h2><p>Which files belong in the next commit, and which should stay out?</p></div>
                <div class="lesson-panel accent-panel"><h2>Target branch</h2><p>Which branch should receive the new commit when HEAD is attached?</p></div>
                <div class="lesson-panel accent-panel"><h2>Message intent</h2><p>Does the message communicate the work without requiring an exact hidden phrase?</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Partial staging is professional hygiene</h2>
                <p>Real work rarely arrives perfectly separated. A configuration fix can sit beside draft notes. A UI update can sit beside experimental tests. The platform's partial-staging evaluator can check whether the latest commit contains the requested paths, excludes draft paths, and leaves intentionally uncommitted work visible in the working tree.</p>
                <p>That means "commit everything" is not a universal answer. A good commit has a boundary. The lesson goal is for students to explain that boundary before they type an action command.</p>
              </section>
            """,
            "history-inspection": """
              <section class="lesson-panel">
                <h2>History inspection answers "how did we get here?"</h2>
                <p>Status tells what is pending now. History inspection tells what has already happened. <code>git log --oneline</code> shows recent commits and messages. <code>git log --oneline --graph</code> adds topology. <code>git branch -v</code> shows branch labels and the commit each label currently names.</p>
                <p>In recovery and collaboration scenarios, this context prevents unnecessary damage. If a commit is already reachable from a safety branch, the task may be to move a branch pointer. If two branches diverged, the task may be to integrate rather than replace. If a branch label is stale after integration, the task may be cleanup, not another merge.</p>
              </section>
              <section class="lesson-grid">
                <div class="command-slab"><code>git log --oneline</code><span>recent commits and messages</span></div>
                <div class="command-slab"><code>git log --oneline --graph</code><span>topology and parent shape</span></div>
                <div class="command-slab"><code>git branch -v</code><span>branch labels and their tips</span></div>
              </section>
              <section class="lesson-panel">
                <h2>Inspection commands are part of mastery</h2>
                <p>The simulator treats common inspection commands as free because careful state reading matters. Efficient Git work is not blind command minimalism. It is choosing state-changing commands after enough inspection to be confident.</p>
              </section>
            """,
            "branch-head": """
              <section class="lesson-panel">
                <h2>Two pointers matter most</h2>
                <p>To reason about branch work, read HEAD and the branch labels separately. HEAD tells where the working context is. A branch label tells which commit that branch currently names. When HEAD is attached to a branch, new commits move that branch label. When HEAD is detached, new commits are not attached to a branch unless the student creates or moves a label intentionally.</p>
                <p>This is why a branch task can be wrong even when file contents look correct. If the commit lands on the wrong branch, the repository state does not match the team workflow. The correct outcome depends on both content and pointer placement.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Attached HEAD</h2><p>HEAD names a branch. Commits advance that branch.</p></div>
                <div class="lesson-panel accent-panel"><h2>Detached HEAD</h2><p>HEAD names a commit directly. New work needs a branch label to stay easy to reach.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Navigation is a state change</h2>
                <p>Switching branches changes the active context and may change the working tree. The safe habit is to inspect first, switch only when the target branch is known, and check the resulting state before creating commits or integrating history.</p>
              </section>
            """,
            "detached-head": """
              <section class="lesson-panel">
                <h2>Detached HEAD is a viewpoint</h2>
                <p>A detached HEAD state means HEAD points directly to a commit instead of pointing through a branch label. This often happens when inspecting an old commit, testing a historical state, or checking out a specific commit hash. It is not automatically a disaster. The risk begins when new work is created and no branch label is attached to it.</p>
                <p>The rescue mindset is simple: keep the work reachable. If the work is a commit, identify which commit contains it and which branch should point to it. If the work is still in the working tree, identify the branch that should receive it before making a snapshot.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>What to inspect</h2><p>HEAD position, recent commits, branch labels, and working tree changes.</p></div>
                <div class="lesson-panel accent-panel"><h2>What to preserve</h2><p>The commit or file changes that represent the useful work.</p></div>
                <div class="lesson-panel accent-panel"><h2>Where to finish</h2><p>The intended branch named by the scenario narrative.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Changed variants, same invariant</h2>
                <p>Different variants may use different branch names, file names, and nearby history. The invariant stays the same: useful work should end reachable from the intended branch, and the repository should finish in a clean, understandable state.</p>
              </section>
            """,
            "right-branch": """
              <section class="lesson-panel">
                <h2>Wrong branch is a pointer problem</h2>
                <p>Committing on the wrong branch feels dramatic because the work is real and the branch is wrong. The key is to separate those facts. If the work exists as a commit, it is reachable somewhere in the graph. If the target branch should contain that work, the task is to place the work on the intended branch and leave unrelated labels in a sensible state.</p>
                <p>The evaluator looks at repository state: which branch points to which commit, where HEAD finishes, whether the working tree is clean, and whether the staged snapshot is empty. It does not require one memorized rescue path as long as the final state satisfies the authored target.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Preserve</h2><p>Identify the work that must not be lost.</p></div>
                <div class="lesson-panel accent-panel"><h2>Relocate</h2><p>Make the intended branch contain the work.</p></div>
                <div class="lesson-panel accent-panel"><h2>Stabilize</h2><p>Finish with a clean working tree and clear HEAD position.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Why this belongs before collaboration</h2>
                <p>Team workflows punish pointer confusion. A developer who understands where their work landed is less likely to overwrite a teammate, force a rewrite without understanding it, or delete and re-clone when the graph looks unfamiliar.</p>
              </section>
            """,
            "undo-without-panic": """
              <section class="lesson-panel">
                <h2>Undo begins with a preservation question</h2>
                <p>Before choosing an undo operation, name what must remain reachable. Is the last commit wrong but the file edits should remain? Is the branch pointer wrong but another label still points to the desired work? Is the working tree dirty but the history is correct? Different states require different recovery strategies.</p>
                <p>The platform's undo lessons avoid treating recovery as a magic incantation. Students learn to read the graph, identify safety references, and decide whether the intended outcome is a clean working tree, a restored branch pointer, or preserved draft work.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Reachable</h2><p>A commit can be found by following a branch, tag-like safety label, HEAD, or parent chain.</p></div>
                <div class="lesson-panel accent-panel"><h2>Uncommitted</h2><p>Working tree and staged changes are not protected by commit history.</p></div>
                <div class="lesson-panel accent-panel"><h2>Recoverable</h2><p>A state is recoverable when the important work still has a path back to it.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Good recovery is conservative</h2>
                <p>The safest recovery move is the one that changes only the thing that is wrong. If the branch pointer moved backward, restore the pointer. If the working tree contains unrelated draft work, avoid sweeping it into a commit just to make the screen look clean.</p>
              </section>
            """,
            "reset-recovery": """
              <section class="lesson-panel">
                <h2>Pointer movement can be repaired</h2>
                <p>Reset-style mistakes are frightening because a branch label may no longer point to the commit students expected. The first recovery question is not "what command fixes this?" but "where is the desired commit still reachable?" In the seeded scenarios, a safety reference keeps the work visible so students can reason from graph evidence.</p>
                <p>The target state usually asks for the main branch to point again at the preserved work, with HEAD on main and no staged or working tree leftovers. Creating a substitute commit is not the same as restoring the intended branch pointer, because the graph shape and commit identity matter.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Find the safe tip</h2><p>Use labels and history to identify the commit that still contains the work.</p></div>
                <div class="lesson-panel accent-panel"><h2>Restore the branch</h2><p>The branch that moved should name the preserved commit again.</p></div>
                <div class="lesson-panel accent-panel"><h2>Verify cleanly</h2><p>Check HEAD, branch pointers, staging, and working tree state.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Why variants matter here</h2>
                <p>Recovery memorization is brittle. A changed variant may use a different safety label or nearby distractor branch, but the reasoning process stays the same: identify preserved work, move the correct pointer, and verify the final repository state.</p>
              </section>
            """,
            "divergence-merge": """
              <section class="lesson-panel">
                <h2>Divergence is not failure</h2>
                <p>Divergence means two lines of work have moved from a shared ancestor. One branch may contain teammate work while another contains feature work. The task is to identify the integration target, understand what each branch contributes, and create a final state where the required work is reachable from the correct branch.</p>
                <p>In the MVP simulator, remote pushing is not executed. Collaboration scenarios end when the local repository is ready for the next team step: integrated where required, conflict-free, clean, and positioned on the expected branch.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Divergent branches</h2><p>Two labels name commits that do not include each other's newest work.</p></div>
                <div class="lesson-panel accent-panel"><h2>Merge state</h2><p>Git may create a merge commit or pause for conflict resolution.</p></div>
                <div class="lesson-panel accent-panel"><h2>Cleanup</h2><p>Stale labels should be removed only after their work is reachable from the integration branch.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Conflict is an unfinished operation</h2>
                <p>A conflict does not mean the repository is ruined. It means Git paused because it needs a resolved file state before it can complete the merge. The student should identify conflicted paths, resolve and stage them, then finish the integration in a clean state.</p>
              </section>
            """,
            "conflict-state": """
              <section class="lesson-panel">
                <h2>A conflict is structured information</h2>
                <p>When a merge conflict appears, the repository enters an unfinished merge state. Git knows the current branch, the branch being merged, the files that could not be combined automatically, and the parent relationship that will exist once the merge is completed. This is information, not chaos.</p>
                <p>The simulator represents conflict state with conflict paths, merge context, working tree changes, and staging state. A complete resolution requires the conflicted content to become resolved, staged, and committed into the integration branch.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Read</h2><p>Inspect which files are conflicted and which branch is receiving the merge.</p></div>
                <div class="lesson-panel accent-panel"><h2>Resolve</h2><p>Produce the intended file state rather than choosing a side blindly.</p></div>
                <div class="lesson-panel accent-panel"><h2>Complete</h2><p>Stage the resolved file and finish the merge so the graph records integration.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>Why "pick one side" is dangerous</h2>
                <p>The preliminary survey showed that students often resolve conflicts by discarding a teammate's code. This lesson pushes against that habit. The target is not to silence Git; the target is to preserve the correct combined work and leave a history that explains the integration.</p>
              </section>
            """,
            "team-flow-capstone": """
              <section class="lesson-panel">
                <h2>The capstone is a workflow, not a new trick</h2>
                <p>The release workflow capstone combines the habits built across the earlier units: inspect status, read the graph, identify the integration target, preserve reachable work, integrate a ready branch, clean up only stale labels, and verify that the repository finishes cleanly.</p>
                <p>Easy keeps the graph compact so the workflow is visible. Medium adds distractor branches. Hard adds multiple nearby labels and expects the student to separate relevant state from noise. The scenario still evaluates repository state, not one prescribed command sequence.</p>
              </section>
              <section class="lesson-grid">
                <div class="lesson-panel accent-panel"><h2>Inspect</h2><p>Use status, log, and branch labels to map the current repository.</p></div>
                <div class="lesson-panel accent-panel"><h2>Integrate</h2><p>Move the release work into the intended branch without discarding history.</p></div>
                <div class="lesson-panel accent-panel"><h2>Clean up</h2><p>Remove only labels that are truly stale after integration.</p></div>
              </section>
              <section class="lesson-panel">
                <h2>How to know you are done</h2>
                <p>The final state should answer four questions: is HEAD on the intended branch, is the required work reachable there, are stale labels removed only when safe, and are the staging area and working tree clean? If those answers are yes, the workflow is complete.</p>
              </section>
            """,
        }
        practice = (
            "<p>After reading, use the scenarios listed below this lesson to choose a practice topic and difficulty. Each level has its own situation, action budget, and retry version, so use this page to understand the problem shape before you start.</p>"
            if scenario_bearing
            else "<p>Use this page as a field guide. The same idea returns in later practice, where you will read the repository state and decide what to change.</p>"
        )
        return f"""
        <article class="lesson-copy lesson-page lesson-page--{slug}">
          <section class="lesson-hero">
            <div class="lesson-kicker">{'Practice lesson' if scenario_bearing else 'Foundation lesson'}</div>
            <h1>{title}</h1>
            <p class="lesson-lede">{subtitle}</p>
            <div class="lesson-meta">
              <span>Scrollable lesson</span>
              <span>State-first reasoning</span>
              <span>{'Includes practice' if scenario_bearing else 'Visual guide'}</span>
            </div>
          </section>
          {self._lesson_visual(slug)}
          {bodies[slug]}
          <section class="lesson-panel practice-panel">
            <h2>{'Practice connection' if scenario_bearing else 'Where you will use this'}</h2>
            {practice}
          </section>
        </article>
        """

    def _lesson_css(self, slug: str, *, orientation: bool) -> str:
        palette = {
            "three-file-areas": ("#14b8a6", "#f59e0b"),
            "tracked-untracked": ("#22c55e", "#38bdf8"),
            "what-head-is": ("#f97316", "#22d3ee"),
            "dag-literacy": ("#38bdf8", "#a3e635"),
            "branch-pointers": ("#06b6d4", "#facc15"),
            "command-anatomy": ("#eab308", "#2dd4bf"),
            "practice-rules": ("#10b981", "#60a5fa"),
            "scaffolds-review": ("#8b5cf6", "#14b8a6"),
            "status-reading": ("#14b8a6", "#f59e0b"),
            "first-commit": ("#22c55e", "#38bdf8"),
            "history-inspection": ("#38bdf8", "#facc15"),
            "branch-head": ("#06b6d4", "#f97316"),
            "detached-head": ("#f97316", "#60a5fa"),
            "right-branch": ("#10b981", "#f59e0b"),
            "undo-without-panic": ("#eab308", "#22d3ee"),
            "reset-recovery": ("#f59e0b", "#14b8a6"),
            "divergence-merge": ("#0ea5e9", "#84cc16"),
            "conflict-state": ("#ef4444", "#22c55e"),
            "team-flow-capstone": ("#8b5cf6", "#f59e0b"),
        }
        accent, accent_2 = palette[slug]
        density = "1.35rem" if orientation else "1.2rem"
        return f"""
        .lesson-page--{slug} {{
          --lesson-accent: {accent};
          --lesson-accent-2: {accent_2};
          display: block;
        }}
        .lesson-page--{slug} .lesson-hero {{
          border: 1px solid color-mix(in srgb, var(--lesson-accent) 34%, hsl(var(--border)));
          border-radius: 8px;
          background:
            linear-gradient(135deg, color-mix(in srgb, var(--lesson-accent) 18%, transparent), transparent 45%),
            linear-gradient(90deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
          margin-bottom: 1.25rem;
          padding: clamp(1.25rem, 4vw, 2.5rem);
        }}
        .lesson-page--{slug} .lesson-kicker {{
          color: var(--lesson-accent);
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-size: 0.72rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          margin-bottom: 0.8rem;
          text-transform: uppercase;
        }}
        .lesson-page--{slug} .lesson-lede {{
          color: hsl(var(--foreground));
          font-size: {density};
          max-width: 54rem;
        }}
        .lesson-page--{slug} .lesson-meta {{
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-top: 1.25rem;
        }}
        .lesson-page--{slug} .lesson-meta span {{
          border: 1px solid color-mix(in srgb, var(--lesson-accent) 30%, hsl(var(--border)));
          border-radius: 6px;
          color: hsl(var(--foreground));
          font-size: 0.78rem;
          font-weight: 700;
          padding: 0.35rem 0.55rem;
        }}
        .lesson-page--{slug} .lesson-visual {{
          border: 1px solid color-mix(in srgb, var(--lesson-accent) 38%, hsl(var(--border)));
          border-radius: 8px;
          background:
            linear-gradient(135deg, color-mix(in srgb, var(--lesson-accent) 14%, transparent), transparent 55%),
            rgba(255,255,255,0.03);
          margin: 0 0 1.25rem;
          overflow: hidden;
          padding: clamp(1rem, 3vw, 1.4rem);
        }}
        .lesson-page--{slug} .visual-label {{
          color: var(--lesson-accent);
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-size: 0.72rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          margin-bottom: 0.85rem;
          text-transform: uppercase;
        }}
        .lesson-page--{slug} .area-row,
        .lesson-page--{slug} .commit-row,
        .lesson-page--{slug} .label-row,
        .lesson-page--{slug} .workflow-strip,
        .lesson-page--{slug} .command-parse {{
          align-items: center;
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
        }}
        .lesson-page--{slug} .status-columns,
        .lesson-page--{slug} .level-ladder,
        .lesson-page--{slug} .split-visual {{
          display: grid;
          gap: 0.75rem;
          grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
        }}
        .lesson-page--{slug} .split-visual .visual-label {{
          grid-column: 1 / -1;
        }}
        .lesson-page--{slug} .area-card,
        .lesson-page--{slug} .state-card,
        .lesson-page--{slug} .level-ladder div,
        .lesson-page--{slug} .command-parse span {{
          border: 1px solid color-mix(in srgb, var(--lesson-accent) 22%, hsl(var(--border)));
          border-radius: 8px;
          background: rgba(0,0,0,0.2);
          min-width: 9rem;
          padding: 0.85rem;
        }}
        .lesson-page--{slug} .area-card.accent,
        .lesson-page--{slug} .state-card.accent {{
          border-color: color-mix(in srgb, var(--lesson-accent-2) 45%, hsl(var(--border)));
          background: color-mix(in srgb, var(--lesson-accent-2) 12%, transparent);
        }}
        .lesson-page--{slug} .state-card.danger,
        .lesson-page--{slug} .branch-tag.danger {{
          border-color: rgba(248, 113, 113, 0.55);
          color: rgb(252, 165, 165);
        }}
        .lesson-page--{slug} .area-card span,
        .lesson-page--{slug} .state-card span,
        .lesson-page--{slug} .level-ladder span,
        .lesson-page--{slug} .command-parse small,
        .lesson-page--{slug} .area-card small,
        .lesson-page--{slug} .state-card small {{
          color: hsl(var(--muted-foreground));
          display: block;
          font-size: 0.78rem;
          line-height: 1.45;
          margin-top: 0.35rem;
        }}
        .lesson-page--{slug} .area-card strong,
        .lesson-page--{slug} .state-card strong,
        .lesson-page--{slug} .level-ladder strong,
        .lesson-page--{slug} .command-parse strong {{
          color: hsl(var(--foreground));
          display: block;
          font-size: 0.95rem;
          line-height: 1.25;
        }}
        .lesson-page--{slug} .state-card code {{
          color: var(--lesson-accent-2);
          display: inline-block;
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-size: 0.75rem;
          margin-top: 0.55rem;
        }}
        .lesson-page--{slug} .commit-node,
        .lesson-page--{slug} .branch-tag,
        .lesson-page--{slug} .head-tag,
        .lesson-page--{slug} .workflow-strip span {{
          border: 1px solid color-mix(in srgb, var(--lesson-accent) 32%, hsl(var(--border)));
          border-radius: 999px;
          background: rgba(0,0,0,0.24);
          color: hsl(var(--foreground));
          display: inline-flex;
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-size: 0.78rem;
          font-weight: 800;
          line-height: 1;
          padding: 0.6rem 0.75rem;
          white-space: nowrap;
        }}
        .lesson-page--{slug} .commit-node.active,
        .lesson-page--{slug} .commit-node.target,
        .lesson-page--{slug} .head-tag {{
          border-color: color-mix(in srgb, var(--lesson-accent-2) 48%, hsl(var(--border)));
          background: color-mix(in srgb, var(--lesson-accent-2) 12%, transparent);
        }}
        .lesson-page--{slug} .commit-node.branch {{
          border-color: color-mix(in srgb, var(--lesson-accent) 48%, hsl(var(--border)));
        }}
        .lesson-page--{slug} .commit-node.ghost {{
          border-style: dashed;
          color: hsl(var(--muted-foreground));
        }}
        .lesson-page--{slug} .diagram-arrow,
        .lesson-page--{slug} .diagram-line {{
          color: var(--lesson-accent);
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-weight: 800;
        }}
        .lesson-page--{slug} .diagram-line {{
          background: color-mix(in srgb, var(--lesson-accent) 70%, hsl(var(--border)));
          display: inline-block;
          height: 2px;
          min-width: 2.5rem;
        }}
        .lesson-page--{slug} .diagram-line.fork,
        .lesson-page--{slug} .diagram-line.merge {{
          background: color-mix(in srgb, var(--lesson-accent-2) 70%, hsl(var(--border)));
        }}
        .lesson-page--{slug} .graph-stack {{
          display: grid;
          gap: 0.8rem;
        }}
        .lesson-page--{slug} .commit-row.offset {{
          margin-left: clamp(1rem, 8vw, 5rem);
        }}
        .lesson-page--{slug} .lesson-panel,
        .lesson-page--{slug} .command-slab,
        .lesson-page--{slug} .state-strip {{
          border: 1px solid hsl(var(--border));
          border-radius: 8px;
          background: rgba(255,255,255,0.035);
          margin: 1rem 0;
          padding: 1rem;
        }}
        .lesson-page--{slug} .lesson-grid {{
          display: grid;
          gap: 1rem;
          grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
          margin: 1rem 0;
        }}
        .lesson-page--{slug} .lesson-grid > .lesson-panel,
        .lesson-page--{slug} .lesson-grid > .command-slab,
        .lesson-page--{slug} .lesson-grid > .state-strip {{
          margin: 0;
        }}
        .lesson-page--{slug} .accent-panel {{
          border-color: color-mix(in srgb, var(--lesson-accent) 34%, hsl(var(--border)));
          background: color-mix(in srgb, var(--lesson-accent) 10%, transparent);
        }}
        .lesson-page--{slug} .state-strip {{
          align-content: center;
          display: grid;
          gap: 0.65rem;
        }}
        .lesson-page--{slug} .state-strip span {{
          border-left: 3px solid var(--lesson-accent);
          background: rgba(0,0,0,0.18);
          border-radius: 6px;
          color: hsl(var(--foreground));
          font-weight: 800;
          padding: 0.75rem;
        }}
        .lesson-page--{slug} .state-strip.vertical span:nth-child(even),
        .lesson-page--{slug} .state-strip span:nth-child(even) {{
          border-left-color: var(--lesson-accent-2);
        }}
        .lesson-page--{slug} .command-slab {{
          display: flex;
          flex-direction: column;
          gap: 0.45rem;
        }}
        .lesson-page--{slug} .command-slab code {{
          color: var(--lesson-accent-2);
          font-family: 'JetBrains Mono', ui-monospace, monospace;
          font-weight: 700;
        }}
        .lesson-page--{slug} .command-slab span {{
          color: hsl(var(--muted-foreground));
          font-size: 0.88rem;
        }}
        .lesson-page--{slug} .remember-panel ul {{
          color: hsl(var(--muted-foreground));
          line-height: 1.7;
          margin: 0.5rem 0 0;
          padding-left: 1.1rem;
        }}
        .lesson-page--{slug} .practice-panel {{
          border-color: color-mix(in srgb, var(--lesson-accent-2) 34%, hsl(var(--border)));
          background: color-mix(in srgb, var(--lesson-accent-2) 8%, transparent);
        }}
        .lesson-page--{slug} h2 {{
          color: hsl(var(--foreground));
        }}
        .lesson-page--{slug} pre {{
          border-color: color-mix(in srgb, var(--lesson-accent) 34%, hsl(var(--border)));
        }}
        @media (max-width: 760px) {{
          .lesson-page--{slug} .lesson-grid {{
            grid-template-columns: 1fr;
          }}
          .lesson-page--{slug} .commit-row.offset {{
            margin-left: 0;
          }}
          .lesson-page--{slug} .diagram-line {{
            min-width: 1.25rem;
          }}
          .lesson-page--{slug} .lesson-meta span {{
            width: 100%;
          }}
        }}
        """
