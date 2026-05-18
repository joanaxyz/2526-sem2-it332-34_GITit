from django.core.management.base import BaseCommand

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from learning.models import LearningUnit, Lesson
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
    ScenarioSkillFocus,
    ScenarioVariant,
    TargetStateRule,
)
from simulator.services import RepositoryStateSimulator


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
                "Repository State Foundations",
                "Read working tree, staging area, commits, and status before changing state.",
                False,
            ),
            (
                "branching-collaboration",
                3,
                "Branching and Collaboration",
                "Reason about HEAD, branch pointers, divergent history, merges, and cleanup.",
                False,
            ),
            (
                "undo-recovery",
                4,
                "Undo and Recovery",
                "Recover safely from common repository mistakes without deleting or re-cloning.",
                False,
            ),
        ]
        units = {}
        for index, (slug, number, title, description, is_orientation) in enumerate(data, start=1):
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
            ("mental-model", "Git as Repository State", "Commits, references, and safe practice boundaries."),
            ("command-anatomy", "Command Anatomy", "How Git commands are structured without memorizing answers."),
            ("dag-literacy", "Reading the DAG", "Commits, parent edges, branch labels, and HEAD."),
            ("working-tree", "Working Tree and Staging Area", "Before a commit exists, state can still matter."),
            ("branch-pointers", "Branch Pointers", "Branches are movable labels, not folders."),
            ("merge-thinking", "Merge Thinking", "Collaboration changes repository topology."),
            ("feedback-policy", "Feedback and No-Answer Policy", "Consequences are explained without command solutions."),
            ("practice-flow", "Practice Flow", "Difficulty scaffolding, command limits, retry variants, and Review Mode."),
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
                    "overview_html": self._orientation_html(title, subtitle),
                    "interaction_steps": [
                        "Start with the repository state you can observe.",
                        "Identify which pointer, file area, or graph relationship changed.",
                        "Connect the consequence to the concept before moving on.",
                    ],
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
                "branch-head",
                units["branching-collaboration"],
                "Branch Pointers and Detached HEAD",
                Lesson.LessonKind.CONTENT,
                "How HEAD and branch labels move.",
                [],
            ),
            (
                "divergence-merge",
                units["branching-collaboration"],
                "Divergent Branches and Merge Recovery",
                Lesson.LessonKind.SCENARIO,
                "Resolve collaboration states without discarding team work.",
                ["divergent-branches", "merge-conflict", "branch-cleanup"],
            ),
            (
                "undo-without-panic",
                units["undo-recovery"],
                "Undo Without Panic",
                Lesson.LessonKind.SCENARIO,
                "Recovery decisions without deleting or re-cloning.",
                ["wrong-branch-commit"],
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
                    "overview_html": self._lesson_html(title, subtitle, kind == Lesson.LessonKind.SCENARIO),
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
                "narrative": "A starter project has untracked files that must become one clean initial commit on main.",
                "task": "Reach a clean repository state with the starter work captured on main.",
                "policy": (3, 9, ["git status", "git log --oneline"]),
                "rule": {
                    "head_branch": "main",
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                    "min_commits_on_branch": {"main": 1},
                },
                "variants": [
                    self._variant("a", "Variant A", "first-a", graph([], {"main": None}, "main", working_tree={"README.md": "untracked", "app.py": "untracked"})),
                    self._variant("b", "Variant B", "first-b", graph([], {"main": None}, "main", working_tree={"index.html": "untracked", "styles.css": "untracked", "tests.py": "untracked"})),
                ],
            },
            {
                "slug": "partial-staging",
                "unit": units["repository-state"],
                "lesson": lessons["first-commit"],
                "title": "Stage selected changes",
                "focus": "partial staging",
                "narrative": "A teammate asked you to commit configuration changes while leaving draft work visible but uncommitted.",
                "task": "Create an intentional commit while keeping repository state understandable.",
                "policy": (4, 10, ["git status", "git diff"]),
                "rule": {
                    "head_branch": "main",
                    "staging_empty": True,
                    "conflict_free": True,
                    "min_commits_on_branch": {"main": 2},
                },
                "variants": [
                    self._variant("a", "Variant A", "stage-a", graph([commit("c0", "Base")], {"main": "c0"}, "main", working_tree={"config.yml": "modified", "draft.md": "modified"})),
                    self._variant("b", "Variant B", "stage-b", graph([commit("c0", "Base")], {"main": "c0"}, "main", working_tree={"settings.json": "modified", "notes.txt": "modified"})),
                ],
            },
            {
                "slug": "divergent-branches",
                "unit": units["branching-collaboration"],
                "lesson": lessons["divergence-merge"],
                "title": "Resolve divergent branches after team edits",
                "focus": "merge/rebase recovery",
                "narrative": "A teammate updated main while your feature branch also moved forward. Preserve both lines of work.",
                "task": "Reach an integrated clean state without discarding either side of the history.",
                "policy": (4, 12, ["git status", "git log --oneline", "git branch -v"]),
                "rule": {
                    "head_branch": "main",
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                    "min_commits_on_branch": {"main": 3},
                },
                "variants": [
                    self._variant("a", "Variant A", "diverge-a", graph([commit("c0", "Base"), commit("c1", "Team update", ["c0"]), commit("c2", "Feature work", ["c0"])], {"main": "c1", "feature/login": "c2"}, "main")),
                    self._variant("b", "Variant B", "diverge-b", graph([commit("c0", "Base"), commit("c1", "Main patch", ["c0"]), commit("c2", "Profile work", ["c0"])], {"main": "c1", "feature/profile": "c2"}, "main")),
                ],
            },
            {
                "slug": "merge-conflict",
                "unit": units["branching-collaboration"],
                "lesson": lessons["divergence-merge"],
                "title": "Finish a merge after conflict markers appear",
                "focus": "merge conflict resolution",
                "narrative": "A merge stopped because one file contains conflict markers. Finish the repository state safely.",
                "task": "Resolve the conflict state and complete the merge without exposing command answers.",
                "policy": (5, 12, ["git status", "git diff"]),
                "rule": {
                    "head_branch": "main",
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                    "min_commits_on_branch": {"main": 3},
                },
                "variants": [
                    self._variant("a", "Variant A", "conflict-a", graph([commit("c0", "Base"), commit("c1", "Main edit", ["c0"]), commit("c2", "Feature edit", ["c0"])], {"main": "c1", "feature/forms": "c2"}, "main", merge_parent="c2", conflicts=["forms.py"], working_tree={"forms.py": "conflict"})),
                    self._variant("b", "Variant B", "conflict-b", graph([commit("c0", "Base"), commit("c1", "Main copy", ["c0"]), commit("c2", "Feature copy", ["c0"])], {"main": "c1", "feature/copy": "c2"}, "main", merge_parent="c2", conflicts=["copy.md"], working_tree={"copy.md": "conflict"})),
                ],
            },
            {
                "slug": "branch-cleanup",
                "unit": units["branching-collaboration"],
                "lesson": lessons["divergence-merge"],
                "title": "Clean up a merged feature branch",
                "focus": "branch cleanup",
                "narrative": "A completed branch has already been merged and should be removed without changing main history.",
                "task": "Leave the repository on main with the stale feature branch removed.",
                "policy": (2, 7, ["git branch", "git log --oneline"]),
                "rule": {
                    "head_branch": "main",
                    "branch_absent": ["old-feature"],
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                },
                "variants": [
                    self._variant("a", "Variant A", "cleanup-a", graph([commit("c0", "Base"), commit("c1", "Merged feature", ["c0"])], {"main": "c1", "old-feature": "c1"}, "main")),
                    self._variant("b", "Variant B", "cleanup-b", graph([commit("c0", "Base"), commit("c1", "Merged topic", ["c0"])], {"main": "c1", "old-feature": "c1"}, "main")),
                ],
            },
            {
                "slug": "wrong-branch-commit",
                "unit": units["undo-recovery"],
                "lesson": lessons["undo-without-panic"],
                "title": "Move a commit made on the wrong branch",
                "focus": "wrong-branch commit recovery",
                "narrative": "Feature work was committed while main was checked out. Recover it onto the appropriate branch.",
                "task": "Place the work on the feature branch and leave the repository ready for continued practice.",
                "policy": (4, 12, ["git status", "git log --oneline", "git branch -v"]),
                "rule": {
                    "head_branch": "feature/recovery",
                    "branch_exists": ["feature/recovery"],
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                    "min_commits_on_branch": {"feature/recovery": 2},
                },
                "variants": [
                    self._variant("a", "Variant A", "wrong-a", graph([commit("c0", "Base"), commit("c1", "Feature work", ["c0"])], {"main": "c1", "feature/recovery": "c0"}, "main")),
                    self._variant("b", "Variant B", "wrong-b", graph([commit("c0", "Base"), commit("c1", "Report work", ["c0"])], {"main": "c1", "feature/recovery": "c0"}, "main")),
                ],
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
                    "narrative": item["narrative"],
                    "task_prompt": item["task"],
                    "sort_order": index,
                    "is_published": True,
                },
            )
            for difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD):
                diff, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "narrative": item["narrative"],
                        "is_published": True,
                    },
                )
                minimum, maximum, diagnostics = item["policy"]
                multiplier = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: -1, DIFFICULTY_HARD: -2}[difficulty]
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={
                        "min_counted_commands": max(1, minimum + multiplier),
                        "max_counted_commands": maximum,
                        "non_counted_patterns": diagnostics,
                    },
                )
                target_hash = RepositoryStateSimulator().state_hash(item["variants"][0]["target_state"])
                TargetStateRule.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={"rule": item["rule"], "target_state_hash": target_hash},
                )

            for variant_data in item["variants"]:
                ScenarioVariant.objects.update_or_create(
                    scenario=scenario,
                    slug=variant_data["slug"],
                    defaults=variant_data,
                )

    def _variant(self, slug: str, label: str, signature: str, initial_state: dict) -> dict:
        target_state = self._expected_state_from_initial(initial_state)
        return {
            "slug": slug,
            "label": label,
            "structure_signature": signature,
            "initial_state": initial_state,
            "target_state": target_state,
            "expected_state_diagram": target_state,
            "is_published": True,
        }

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
            commits.append({"id": new_id, "message": "Intentional repository update", "parents": parents})
            branches[head_name] = new_id

        if "old-feature" in branches:
            branches.pop("old-feature", None)

        if "feature/recovery" in branches:
            head = {"type": "branch", "name": "feature/recovery"}
            if branches["feature/recovery"] == "c0" and len(commits) > 1:
                new_id = f"c{len(commits)}"
                commits.append({"id": new_id, "message": "Recovered feature work", "parents": ["c0"]})
                branches["feature/recovery"] = new_id

        head_target = branches.get(head.get("name"))
        return {"commits": commits, "branches": branches, "head": {**head, "target": head_target}}

    def _orientation_html(self, title: str, subtitle: str) -> str:
        return f"""
        <article class="lesson-copy">
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <p>Use this walkthrough to connect Git vocabulary with repository state before entering scenario practice.</p>
          <div class="callout">Orientation lessons are concept-only. They do not ask for commands and do not generate scenario KPI logs.</div>
        </article>
        """

    def _lesson_html(self, title: str, subtitle: str, scenario_bearing: bool) -> str:
        practice = (
            "<p>After reading, open View Scenarios to select a skill focus and difficulty level.</p>"
            if scenario_bearing
            else "<p>This lesson prepares later practice and has no attached scenario.</p>"
        )
        return f"""
        <article class="lesson-copy">
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <p>Focus on the repository state, the visible branch pointers, HEAD, staging area, and working tree consequences.</p>
          {practice}
          <pre><code>git status
git log --oneline --graph</code></pre>
        </article>
        """
