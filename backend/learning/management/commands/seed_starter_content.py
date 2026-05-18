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
                "Branching and Navigation",
                "Reason about HEAD, branch pointers, detached states, and safe navigation.",
                False,
            ),
            (
                "collaboration-integration",
                4,
                "Collaboration and Integration",
                "Resolve divergent history, merge conflicts, and branch cleanup without discarding work.",
                False,
            ),
            (
                "undo-recovery",
                5,
                "Undo and Recovery",
                "Recover safely from common repository mistakes without deleting or re-cloning.",
                False,
            ),
        ]
        starter_slugs = [slug for slug, *_ in data]
        with transaction.atomic():
            for index, slug in enumerate(starter_slugs, start=1):
                LearningUnit.objects.filter(slug=slug).update(number=1000 + index)

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
            ("what-head-is", "What HEAD Is", "The current repository position the simulator displays."),
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
                "Command, subcommand, options, arguments, and diagnostics.",
            ),
            (
                "practice-rules",
                "GIT it! Practice Rules",
                "Simulator boundaries, No-Answer Policy, and command-count rules.",
            ),
            (
                "scaffolds-review",
                "Scaffolding, Retry, and Review Mode",
                "How Easy, Medium, Hard, adaptive retry, and Review Mode differ.",
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
                    "overview_html": self._orientation_html(slug, title, subtitle),
                    "interaction_steps": self._orientation_steps(slug),
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
                "Use diagnostic commands to understand commits without spending counted actions.",
                [],
            ),
            (
                "branch-head",
                units["branching-collaboration"],
                "Branch Pointers and HEAD",
                Lesson.LessonKind.CONTENT,
                "How HEAD and branch labels move.",
                [],
            ),
            (
                "detached-head",
                units["branching-collaboration"],
                "Detached HEAD and Safe Navigation",
                Lesson.LessonKind.CONTENT,
                "Understand detached states before making recovery decisions.",
                [],
            ),
            (
                "right-branch",
                units["branching-collaboration"],
                "Moving Work to the Right Branch",
                Lesson.LessonKind.SCENARIO,
                "Recover a local commit made from the wrong repository position.",
                ["wrong-branch-commit"],
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
                "undo-without-panic",
                units["undo-recovery"],
                "Undo Without Panic",
                Lesson.LessonKind.CONTENT,
                "Recovery decisions without deleting, re-cloning, or blindly copying commands.",
                [],
            ),
            (
                "reset-recovery",
                units["undo-recovery"],
                "Recovering After Pointer Movement",
                Lesson.LessonKind.SCENARIO,
                "Repair a local branch pointer move while preserving reachable work.",
                ["accidental-reset-recovery"],
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
                "unit": units["collaboration-integration"],
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
                "unit": units["collaboration-integration"],
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
                "unit": units["collaboration-integration"],
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
                "unit": units["branching-collaboration"],
                "lesson": lessons["right-branch"],
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
            {
                "slug": "accidental-reset-recovery",
                "unit": units["undo-recovery"],
                "lesson": lessons["reset-recovery"],
                "title": "Recover after an accidental local reset",
                "focus": "local reset recovery",
                "narrative": "A local branch pointer moved backward, but a safety reference still points to the work that must be preserved.",
                "task": "Move the active branch pointer back to the preserved work without inventing a new history.",
                "policy": (2, 8, ["git status", "git log --oneline", "git branch -v"]),
                "rule": {
                    "head_branch": "main",
                    "branch_exists": ["safety-copy"],
                    "branches_equal": [["main", "safety-copy"]],
                    "working_tree_clean": True,
                    "staging_empty": True,
                    "conflict_free": True,
                },
                "variants": [
                    self._variant(
                        "a",
                        "Variant A",
                        "reset-a",
                        graph(
                            [commit("c0", "Base"), commit("c1", "Lost local work", ["c0"])],
                            {"main": "c0", "safety-copy": "c1"},
                            "main",
                        ),
                    ),
                    self._variant(
                        "b",
                        "Variant B",
                        "reset-b",
                        graph(
                            [commit("c0", "Base"), commit("c1", "Recovered report", ["c0"])],
                            {"main": "c0", "safety-copy": "c1"},
                            "main",
                        ),
                    ),
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

        if "safety-copy" in branches and head.get("name") == "main":
            branches["main"] = branches["safety-copy"]

        head_target = branches.get(head.get("name"))
        return {"commits": commits, "branches": branches, "head": {**head, "target": head_target}}

    def _orientation_steps(self, slug: str) -> list[str]:
        steps = {
            "three-file-areas": [
                "Locate the working tree: the place where file edits appear before Git records them.",
                "Locate the staging area: the proposed contents of the next commit.",
                "Locate the repository history: committed snapshots connected by parent edges.",
            ],
            "tracked-untracked": [
                "Start with an untracked file that Git can see but does not yet include in history.",
                "Notice how staging changes that file's relationship to the repository.",
                "Connect tracked status to whether future changes can be compared and committed.",
            ],
            "what-head-is": [
                "Find HEAD in the diagram before looking at branch names.",
                "Observe whether HEAD is attached to a branch or points directly to a commit.",
                "Use HEAD to explain where the next commit or branch movement would happen.",
            ],
            "dag-literacy": [
                "Read commits as nodes and parent links as arrows through history.",
                "Identify branch labels and the commit each label currently names.",
                "Compare the graph shape before and after a state change.",
            ],
            "branch-pointers": [
                "Treat a branch as a movable label, not as a separate folder.",
                "Watch the current branch pointer move when a new commit is created.",
                "Distinguish switching branches from changing committed history.",
            ],
            "command-anatomy": [
                "Separate the git command, subcommand, options, and arguments.",
                "Classify inspection commands as diagnostic before changing repository state.",
                "Read command intent without assuming there is only one valid path.",
            ],
            "practice-rules": [
                "Confirm that typed commands are parsed by the simulator, not a real shell.",
                "Use feedback as a consequence summary, not as an answer key.",
                "Track counted action commands separately from diagnostic commands.",
            ],
            "scaffolds-review": [
                "Compare Easy, Medium, and Hard scaffolds before starting a scenario.",
                "Recognize that failed or abandoned retries may use changed variants.",
                "Recognize that Review Mode is playable and logged separately.",
            ],
        }
        return steps[slug]

    def _orientation_html(self, slug: str, title: str, subtitle: str) -> str:
        bodies = {
            "three-file-areas": """
              <p>Git reasoning starts with three areas. The working tree contains file edits.
              The staging area holds the next proposed snapshot. The repository history stores
              completed commits. Scenario practice expects students to name which area changed
              before deciding what to do next.</p>
            """,
            "tracked-untracked": """
              <p>A tracked file already belongs to Git's history. An untracked file exists in
              the working tree but has not yet been included in a commit. This distinction
              explains why status output matters before any state-changing action.</p>
            """,
            "what-head-is": """
              <p>HEAD marks the current repository position. In normal work it is attached to
              a branch, so new commits move that branch pointer. In a detached state, HEAD
              points directly at a commit, which changes how students should reason about safety.</p>
            """,
            "dag-literacy": """
              <p>Git history forms a Directed Acyclic Graph. Commits are nodes, parent
              relationships are edges, and branch labels point to selected commits. GIT it!
              uses the live DAG to make those relationships visible after simulator-processed
              commands.</p>
            """,
            "branch-pointers": """
              <p>Branches are movable pointers. They do not copy the whole project into a
              separate folder. Understanding this prevents destructive workarounds when a
              branch appears to diverge or when work was committed from the wrong position.</p>
            """,
            "command-anatomy": """
              <p>Git commands have a shape: <code>git</code>, a subcommand, optional flags,
              and arguments. GIT it! encourages students to inspect before acting and logs
              diagnostic commands separately from counted action commands.</p>
            """,
            "practice-rules": """
              <p>The terminal in GIT it! is simulated. It never executes shell input, never
              calls the external Git CLI, and never connects to GitHub or another remote. The
              No-Answer Policy also means the system will never reveal a correct command
              sequence.</p>
            """,
            "scaffolds-review": """
              <p>Easy shows the live DAG, expected-state diagram, and contextual feedback.
              Medium keeps the live DAG and expected-state diagram. Hard shows the live DAG
              and narrative context only. Completed difficulties can be replayed in Review
              Mode without altering primary KPI records.</p>
            """,
        }
        return f"""
        <article class="lesson-copy">
          <h1>{title}</h1>
          <p>{subtitle}</p>
          {bodies[slug]}
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
