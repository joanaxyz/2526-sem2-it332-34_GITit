import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from common.constants import (
    COMPLETION_EXPANDED_STATE_BASED,
    COMPLETION_INSPECTION,
    COMPLETION_STATE_BASED,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
)
from evaluation.services import InspectionEvaluator
from learning.models import LearningUnit, Lesson, OrientationProgress
from progress.models import StreakRecord, StudentProgress
from scenarios.command_content import (
    command_content_key_for_command,
    seed_git_command_content_library,
)
from scenarios.models import (
    CommandCountPolicy,
    CompletionRecord,
    DifficultyInstance,
    ScenarioGenerationBlueprint,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
    TargetStateRule,
)
from simulator.services import RepositorySnapshotService, RepositoryStateSimulator

DIFFICULTY_MAP = {
    "Easy": DIFFICULTY_EASY,
    "Medium": DIFFICULTY_MEDIUM,
    "Hard": DIFFICULTY_HARD,
}


def default_successful_attempts_for_difficulty(difficulty: str) -> int:
    return 3 if difficulty == DIFFICULTY_EASY else 2


TOPICS = ("auth", "payment", "search", "export", "profile")
PLACEHOLDER_RE = re.compile(r"<[^>]+>")
TASK_COMMAND_REPLACEMENTS = (
    ("git commit --amend", "the latest snapshot repair"),
    ("git restore --staged", "the unstaging recovery"),
    ("git log --oneline --graph", "history inspection"),
    ("git log --oneline", "history inspection"),
    ("git diff --staged", "staged-difference inspection"),
    ("git remote -v", "remote verification"),
    ("git branch -v", "branch inspection"),
    ("git status", "state inspection"),
    ("git diff", "difference inspection"),
    ("git show", "object inspection"),
    ("git branch", "branch inspection"),
    ("git remote", "remote configuration"),
    ("git switch -c", "new-branch navigation"),
    ("git checkout -b", "new-branch navigation"),
    ("git restore", "working-tree recovery"),
    ("git reset --soft", "soft branch-pointer recovery"),
    ("git clone", "local-copy setup"),
    ("git init", "repository setup"),
    ("git fetch", "remote-tracking update"),
    ("git pull", "upstream update"),
    ("git push", "publish workflow"),
    ("git reset", "branch-pointer recovery"),
    ("git revert", "reversing snapshot"),
    ("git stash", "temporary work save"),
    ("git reflog", "recovery-history inspection"),
    ("git switch", "branch navigation"),
    ("git checkout", "branch navigation"),
    ("git merge", "branch integration"),
    ("git add", "snapshot preparation"),
    ("git commit", "snapshot save"),
)


@dataclass
class UnitSpec:
    slug: str
    number: int
    title: str
    description: str
    is_orientation: bool
    sort_order: int


@dataclass
class LessonSpec:
    unit_slug: str
    slug: str
    kind: str
    title: str
    subtitle: str
    sort_order: int
    visual_html: str = ""
    body_html: str = ""


@dataclass
class DifficultySpec:
    difficulty: str
    required_successful_attempts: int
    narrative: str
    task: str
    policy: tuple[int, int, list[str]]
    target_rule: dict
    variants: list[dict] = field(default_factory=list)
    blueprints: list["VariantTemplateSpec"] = field(default_factory=list)


@dataclass
class ScenarioSpec:
    slug: str
    unit_slug: str
    lesson_slug: str
    title: str
    focus: str
    seeding_status: str
    fields: dict
    difficulties: dict[str, DifficultySpec]


@dataclass
class VariantTemplateSpec:
    slug_template: str
    label_template: str
    structure_signature_template: str
    initial_state_template: dict
    target_rule_template: dict
    solution_commands_template: list[str]
    parameter_pools: dict[str, list[Any]]
    generation_count: int
    expected_observations_template: dict = field(default_factory=dict)
    student_context_template: dict = field(default_factory=dict)


class CurriculumMarkdownParser:
    def parse(self, path: Path) -> tuple[list[UnitSpec], list[LessonSpec], list[ScenarioSpec]]:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        units: list[UnitSpec] = []
        lessons: list[LessonSpec] = []
        scenarios: list[ScenarioSpec] = []
        current_unit_slug = ""
        current_lesson_slug = ""

        i = 0
        while i < len(lines):
            line = lines[i]
            module_match = re.match(r"# Module \d+\s+.+", line)
            lesson_match = re.match(r"### Lesson ([0-9.]+):", line)
            scenario_match = re.match(r"#### Scenario [^:]+: ([a-z0-9-]+)", line)

            if module_match:
                attrs, i = self._next_attribute_table(lines, i)
                unit = UnitSpec(
                    slug=str(attrs["slug"]),
                    number=int(attrs["number"]),
                    title=str(attrs["title"]),
                    description=str(attrs["description"]),
                    is_orientation=bool(attrs["is_orientation"]),
                    sort_order=int(attrs["sort_order"]),
                )
                units.append(unit)
                current_unit_slug = unit.slug
                continue

            if lesson_match:
                attrs, table_end = self._next_attribute_table(lines, i)
                visual_html = self._extract_named_html_block(lines, table_end, "Visual")
                body_html = self._extract_named_html_block(lines, table_end, "Body")
                lesson = LessonSpec(
                    unit_slug=current_unit_slug,
                    slug=str(attrs["slug"]),
                    kind=str(attrs["kind"]),
                    title=str(attrs["title"]),
                    subtitle=str(attrs.get("subtitle", "")),
                    sort_order=int(attrs["sort_order"]),
                    visual_html=visual_html,
                    body_html=body_html,
                )
                lessons.append(lesson)
                current_lesson_slug = lesson.slug
                i = table_end
                continue

            if scenario_match:
                scenario, i = self._parse_scenario(lines, i, current_unit_slug, current_lesson_slug)
                scenarios.append(scenario)
                continue

            i += 1

        if not units or not lessons or not scenarios:
            raise CommandError("Curriculum markdown did not contain the expected seed sections.")
        return units, lessons, scenarios

    def _next_attribute_table(self, lines: list[str], start: int) -> tuple[dict, int]:
        i = start
        while i < len(lines) and not lines[i].startswith("| Attribute |"):
            i += 1
        if i >= len(lines):
            raise CommandError(f"Missing attribute table near line {start + 1}.")
        return self._parse_field_table(lines, i)

    def _parse_field_table(self, lines: list[str], start: int) -> tuple[dict, int]:
        values: dict[str, Any] = {}
        i = start + 1
        while i < len(lines) and lines[i].startswith("|"):
            cells = self._cells(lines[i])
            i += 1
            if len(cells) < 2 or cells[0] in {"Attribute", "Field"} or set(cells[0]) <= {"-"}:
                continue
            values[cells[0]] = self._decode_value(cells[1])
        return values, i

    def _parse_scenario(
        self,
        lines: list[str],
        start: int,
        unit_slug: str,
        lesson_slug: str,
    ) -> tuple[ScenarioSpec, int]:
        header = lines[start]
        slug = re.match(r"#### Scenario [^:]+: ([a-z0-9-]+)", header).group(1)
        end = start + 1
        while end < len(lines) and not re.match(r"#{1,4} ", lines[end]):
            end += 1
        block = lines[start:end]

        seeding_status = ""
        primary_focus = ""
        fields: dict[str, Any] = {}
        difficulties: dict[str, DifficultySpec] = {}
        current_difficulty: DifficultySpec | None = None

        for index, line in enumerate(block):
            focus_match = re.match(r"\*\*Primary focus command:\*\* `(.+)`", line)
            if focus_match:
                primary_focus = focus_match.group(1)
            status_match = re.match(r"\*\*Seeding status:\*\* `(.+)`", line)
            if status_match:
                seeding_status = status_match.group(1)
            if line == "**ScenarioSkillFocus fields**":
                table_index = start + index + 2
                fields, _ = self._parse_field_table(lines, table_index)
            diff_match = re.match(r"###### (Easy|Medium|Hard)", line)
            if diff_match:
                difficulty = DIFFICULTY_MAP[diff_match.group(1)]
                current_difficulty = DifficultySpec(
                    difficulty=difficulty,
                    required_successful_attempts=default_successful_attempts_for_difficulty(
                        difficulty
                    ),
                    narrative="",
                    task="",
                    policy=(0, 0, []),
                    target_rule={},
                )
                difficulties[difficulty] = current_difficulty
                continue
            if current_difficulty is None:
                continue
            if line.startswith("- narrative:"):
                current_difficulty.narrative = self._quoted_line_value(line)
            elif line.startswith("- task:"):
                current_difficulty.task = self._quoted_line_value(line)
            elif line.startswith("- policy:"):
                current_difficulty.policy = ast.literal_eval(self._backtick_value(line))
            elif line.startswith("- target_rule:"):
                current_difficulty.target_rule = json.loads(self._backtick_value(line))
            elif line.startswith("| `"):
                cells = self._cells(line)
                if len(cells) >= 4 and cells[0].startswith("`"):
                    current_difficulty.variants.append(
                        {
                            "slug": self._strip_ticks(cells[0]),
                            "label": cells[1],
                            "initial_state": json.loads(self._strip_ticks(cells[2])),
                            "solution_commands": json.loads(self._strip_ticks(cells[3])),
                        }
                    )

        fields.setdefault("slug", slug)
        fields.setdefault("title", self._title_from_slug(slug))
        fields.setdefault("focus", primary_focus)
        fields.setdefault("primary_focus_commands", [primary_focus])
        fields.setdefault("supporting_inspection_commands", [])
        return ScenarioSpec(
            slug=slug,
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title=str(fields["title"]),
            focus=str(fields["focus"]),
            seeding_status=seeding_status,
            fields=fields,
            difficulties=difficulties,
        ), end

    def _extract_named_html_block(self, lines: list[str], start: int, name: str) -> str:
        marker = f"**{name}**"
        i = start
        while i < len(lines) and not re.match(r"### Lesson |#### Scenario |# Module ", lines[i]):
            if lines[i] == marker:
                while i < len(lines) and lines[i] != "```html":
                    i += 1
                if i >= len(lines):
                    return ""
                i += 1
                block: list[str] = []
                while i < len(lines) and lines[i] != "```":
                    block.append(lines[i])
                    i += 1
                return "\n".join(block)
            i += 1
        return ""

    def _cells(self, line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def _decode_value(self, value: str) -> Any:
        value = value.strip()
        if value.startswith("*(empty"):
            return ""
        if value.startswith("`") and value.endswith("`"):
            inner = value[1:-1]
            if inner in {"True", "False"}:
                return inner == "True"
            if re.fullmatch(r"\d+", inner):
                return int(inner)
            if inner.startswith(("[", "{")):
                return json.loads(inner)
            return inner
        return value

    def _quoted_line_value(self, line: str) -> str:
        return line.split(":", 1)[1].strip().strip('"')

    def _backtick_value(self, line: str) -> str:
        match = re.search(r"`(.+)`", line)
        if not match:
            raise CommandError(f"Expected backtick value in: {line}")
        return match.group(1)

    def _strip_ticks(self, value: str) -> str:
        value = value.strip()
        if value.startswith("`") and value.endswith("`"):
            return value[1:-1]
        return value

    def _title_from_slug(self, slug: str) -> str:
        return " ".join(part.capitalize() for part in slug.split("-"))


class DynamicVariantGenerator:
    """Resolve template specs into concrete ScenarioVariant seed payloads."""

    placeholder_re = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")

    def generate(self, template: VariantTemplateSpec) -> list[dict]:
        contexts = self._contexts(template.parameter_pools)
        if not contexts:
            raise CommandError(f"Variant template {template.slug_template} has no parameter cases.")

        variants = []
        for index in range(template.generation_count):
            context = {**contexts[index % len(contexts)], "index": index + 1}
            variants.append(
                {
                    "slug": self._render(template.slug_template, context),
                    "label": self._render(template.label_template, context),
                    "structure_signature": self._render(
                        template.structure_signature_template,
                        context,
                    ),
                    "initial_state": self._render(template.initial_state_template, context),
                    "target_rule": self._render(template.target_rule_template, context),
                    "expected_observations": self._render(
                        template.expected_observations_template,
                        context,
                    ),
                    "solution_commands": self._render(
                        template.solution_commands_template,
                        context,
                    ),
                }
            )
        return variants

    def _contexts(self, pools: dict[str, list[Any]]) -> list[dict]:
        if "cases" in pools:
            return [dict(item) for item in pools["cases"]]

        contexts = [{}]
        for key, values in pools.items():
            contexts = [{**context, key: value} for context in contexts for value in values]
        return contexts

    def _render(self, value: Any, context: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {
                self._render(key, context): self._render(item, context)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._render(item, context) for item in value]
        if not isinstance(value, str):
            return value

        exact = self.placeholder_re.fullmatch(value)
        if exact:
            return context[exact.group(1)]

        def replace(match: re.Match) -> str:
            return str(context[match.group(1)])

        return self.placeholder_re.sub(replace, value)


class ModuleOneSeedBuilder:
    """Build Module 1 from dynamic variant templates based on docs/curriculum.md."""

    diagnostic_commands = [
        "git status",
        "git log",
        "git log --oneline",
        "git remote -v",
        "git diff",
        "git diff --staged",
    ]

    session_counts = {
        1: {DIFFICULTY_EASY: 3, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        2: {DIFFICULTY_EASY: 3, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        3: {DIFFICULTY_EASY: 3, DIFFICULTY_MEDIUM: 3, DIFFICULTY_HARD: 2},
        4: {DIFFICULTY_EASY: 3, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        5: {DIFFICULTY_EASY: 2, DIFFICULTY_MEDIUM: 3, DIFFICULTY_HARD: 2},
        6: {DIFFICULTY_EASY: 2, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        7: {DIFFICULTY_EASY: 2, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        8: {DIFFICULTY_EASY: 2, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 2},
        9: {DIFFICULTY_EASY: 3, DIFFICULTY_MEDIUM: 2, DIFFICULTY_HARD: 3},
    }

    def __init__(self) -> None:
        self.generator = DynamicVariantGenerator()

    def build(self) -> tuple[list[UnitSpec], list[LessonSpec], list[ScenarioSpec]]:
        unit = UnitSpec(
            slug="local-repository-foundations",
            number=1,
            title="Local Repository Foundations",
            description=(
                "Initialize, clone, stage, commit, ignore, amend, clean up, and inspect "
                "local Git repositories through scenario practice."
            ),
            is_orientation=False,
            sort_order=1,
        )
        lessons = self._lessons(unit.slug)
        lesson_map = {lesson.sort_order: lesson.slug for lesson in lessons}
        scenarios = [
            self._init_scenario(unit.slug, lesson_map[1]),
            self._clone_scenario(unit.slug, lesson_map[2]),
            self._stage_commit_scenario(unit.slug, lesson_map[3]),
            self._gitignore_scenario(unit.slug, lesson_map[4]),
            self._partial_staging_scenario(unit.slug, lesson_map[5]),
            self._amend_scenario(unit.slug, lesson_map[6]),
            self._restore_scenario(unit.slug, lesson_map[7]),
            self._read_state_scenario(unit.slug, lesson_map[8]),
            self._review_scenario(unit.slug, lesson_map[9]),
        ]
        return [unit], lessons, scenarios

    def _lessons(self, unit_slug: str) -> list[LessonSpec]:
        lesson_data = [
            (
                "initializing-a-local-repository",
                "Initializing a Local Repository",
                "Create Git metadata in an existing or named project folder.",
            ),
            (
                "cloning-a-remote-repository",
                "Cloning a Remote Repository",
                "Create a local working copy and verify the origin relationship.",
            ),
            (
                "staging-and-committing-basic-workflow",
                "Staging and Committing: The Basic Workflow",
                "Prepare intentional changes and save them with a clear message.",
            ),
            (
                "ignoring-files-with-gitignore",
                "Ignoring Files with .gitignore",
                "Keep generated files, dependency folders, logs, and secrets out of history.",
            ),
            (
                "partial-staging-and-git-add-p",
                "Partial Staging and git add -p",
                "Stage selected hunks so each commit has one clear purpose.",
            ),
            (
                "amending-commits",
                "Amending Commits",
                "Repair the latest commit message or contents before sharing it.",
            ),
            (
                "unstaging-and-discarding-changes",
                "Unstaging and Discarding Changes",
                "Move changes out of the index and safely discard unwanted work.",
            ),
            (
                "reading-repository-status-and-history",
                "Reading Repository Status and History",
                "Inspect status, history, and diffs without changing repository state.",
            ),
            (
                "module-1-review-and-practice",
                "Module 1 Review and Practice",
                "Combine the local workflow skills in larger repository situations.",
            ),
        ]
        return [
            LessonSpec(
                unit_slug=unit_slug,
                slug=slug,
                kind="scenario",
                title=title,
                subtitle=subtitle,
                sort_order=index,
                body_html=self._body_html(title, subtitle),
            )
            for index, (slug, title, subtitle) in enumerate(lesson_data, start=1)
        ]

    def _scenario(
        self,
        *,
        slug: str,
        unit_slug: str,
        lesson_slug: str,
        title: str,
        focus: str,
        summary: str,
        explanation: str,
        primary: list[str],
        supporting: list[str],
        concepts: list[str],
        narrative: str,
        task_prompt: str,
        lesson_number: int,
        difficulty_configs: dict[
            str, tuple[str, str, tuple[int, int, list[str]], VariantTemplateSpec]
        ],
    ) -> ScenarioSpec:
        difficulties = {}
        for difficulty, (diff_narrative, task, policy, template) in difficulty_configs.items():
            variants = self.generator.generate(template)
            difficulties[difficulty] = DifficultySpec(
                difficulty=difficulty,
                required_successful_attempts=self.session_counts[lesson_number][difficulty],
                narrative=diff_narrative,
                task=task,
                policy=policy,
                target_rule=template.target_rule_template,
                variants=variants,
                blueprints=[template],
            )

        fields = {
            "title": title,
            "focus": focus,
            "summary": summary,
            "short_explanation": explanation,
            "skill_focus_type": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
            "primary_focus_commands": primary,
            "supporting_inspection_commands": supporting,
            "safe_demo_commands": supporting[:3],
            "demo_repository_state": difficulties[DIFFICULTY_EASY].variants[0]["initial_state"],
            "related_git_concepts": concepts,
            "narrative": narrative,
            "task_prompt": task_prompt,
        }
        return ScenarioSpec(
            slug=slug,
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title=title,
            focus=focus,
            seeding_status="ready",
            fields=fields,
            difficulties=difficulties,
        )

    def _init_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "docs-portal",
                "files": {"README.md": "untracked", "docs/intro.md": "untracked"},
            },
            {
                "project": "api-starter",
                "files": {"README.md": "untracked", "api/routes.py": "untracked"},
            },
            {
                "project": "cli-tool",
                "files": {"README.md": "untracked", "git_it_cli.py": "untracked"},
            },
            {
                "project": "profile-site",
                "files": {"README.md": "untracked", "site/index.html": "untracked"},
            },
        ]
        template = self._state_template(
            slug="init-{{project}}-{{index}}",
            label="{{project}} starter files",
            signature="init/{{project}}/{{index}}",
            cases=cases,
            initial_state={
                **self._empty_uninitialized_state(),
                "working_tree": "{{files}}",
            },
            target_rule={
                "repository_initialized": True,
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "min_commits_on_branch": {"main": 1},
                "required_commands": ["git init", "git add", "git commit"],
            },
            commands=["git init", "git add .", 'git commit -m "Create starter snapshot"'],
            count=3,
        )
        return self._scenario(
            slug="initialize-project-and-first-commit",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Initialize and save the first snapshot",
            focus="git init",
            summary="Turn a folder into a repository and commit the starter files.",
            explanation="Initialization creates the .git metadata; the first commit gives the repository a clean starting point.",
            primary=["git init"],
            supporting=["git status", "git log --oneline"],
            concepts=["working tree", "staging area", "first commit"],
            narrative="A starter folder exists, but Git is not tracking it yet.",
            task_prompt="Initialize the folder, prepare the starter files, and save the first snapshot.",
            lesson_number=1,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "The starter files are visible. Create the repository and save them.",
                    "Initialize the project, prepare every starter file, and save the first snapshot.",
                    (3, 5, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "The files sit at different depths. Create one clean initial snapshot.",
                    "Initialize the project and save the starter files in one snapshot.",
                    (3, 5, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="init/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use the repository state alone to create the first clean commit.",
                    "Initialize the project and save a clean first snapshot.",
                    (3, 4, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="init/hard/{{project}}/{{index}}"
                    ),
                ),
            },
        )

    def _clone_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "docs-portal",
                "url": "https://example.test/docs-portal.git",
                "folder": "docs-portal",
                "remote_commit": "r10",
            },
            {
                "project": "api-starter",
                "url": "git@example.test:training/api-starter.git",
                "folder": "api-starter",
                "remote_commit": "r11",
            },
            {
                "project": "cli-tool",
                "url": "https://example.test/tools/cli-tool.git",
                "folder": "cli-lab",
                "remote_commit": "r12",
            },
            {
                "project": "profile-site",
                "url": "git@example.test:training/profile-site.git",
                "folder": "profile-site",
                "remote_commit": "r13",
            },
        ]
        template = self._state_template(
            slug="clone-{{project}}-{{index}}",
            label="{{project}} remote",
            signature="clone/{{project}}/{{folder}}/{{index}}",
            cases=cases,
            initial_state={
                **self._empty_uninitialized_state(),
                "remote_branches": {"origin/main": "{{remote_commit}}"},
            },
            target_rule={
                "repository_initialized": True,
                "head_branch": "main",
                "remote_exists": ["origin"],
                "remote_url_matches": {"origin": "{{url}}"},
                "upstream_tracking": {"main": "origin/main"},
                "branches_equal": [["main", "origin/main"]],
                "required_commands": ["git clone"],
            },
            commands=["git clone {{url}} {{folder}}"],
            count=3,
        )
        return self._scenario(
            slug="clone-project-and-inspect",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Clone and verify a remote project",
            focus="git clone",
            summary="Create a local working copy and confirm origin is configured.",
            explanation="Cloning copies history, checks out the default branch, and records the remote as origin.",
            primary=["git clone"],
            supporting=["git remote -v", "git log --oneline"],
            concepts=["origin", "remote branch", "working copy"],
            narrative="A teammate published a starter repository and you need a local copy.",
            task_prompt="Create a local working copy from the provided remote and verify origin.",
            lesson_number=2,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "The remote URL and destination are provided.",
                    "Create the local working copy, then inspect the configured remote.",
                    (1, 4, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "The destination folder name differs from the remote project name.",
                    "Create the local working copy in the requested folder.",
                    (1, 3, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="clone/medium/{{project}}/{{folder}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use the provided remote details with no extra setup.",
                    "Create the local working copy from the remote.",
                    (1, 2, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="clone/hard/{{project}}/{{folder}}/{{index}}"
                    ),
                ),
            },
        )

    def _stage_commit_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "form-flow",
                "files": {"src/form.js": "modified"},
                "message": "Update form validation",
            },
            {
                "project": "copy-pass",
                "files": {"README.md": "modified"},
                "message": "Clarify setup notes",
            },
            {
                "project": "asset-cleanup",
                "files": {"src/app.js": "modified", "styles/site.css": "modified"},
                "message": "Refresh app styling",
            },
            {
                "project": "api-route",
                "files": {"api/routes.py": "modified"},
                "message": "Add route handling",
            },
        ]
        template = self._state_template(
            slug="commit-{{project}}-{{index}}",
            label="{{project}} working changes",
            signature="commit/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state("c0", "{{files}}", {}),
            target_rule={
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "latest_commit": {"branch": "main", "message_contains": ["{{message}}"]},
                "required_commands": ["git add", "git commit"],
            },
            commands=["git add .", 'git commit -m "{{message}}"'],
            count=3,
        )
        return self._scenario(
            slug="form-clean-commit",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Stage and commit a clean change",
            focus="git commit",
            summary="Prepare working changes and save them with a descriptive message.",
            explanation="The basic workflow is deliberate: stage the next snapshot, then commit that staged state.",
            primary=["git commit"],
            supporting=["git status", "git diff", "git diff --staged"],
            concepts=["staging area", "commit message", "clean working tree"],
            narrative="A small local change is ready to become a proper commit.",
            task_prompt="Prepare the intended changes and save a clear snapshot.",
            lesson_number=3,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "One or two files need to be saved as a clean snapshot.",
                    "Prepare the changes and save them with a descriptive message.",
                    (2, 5, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "Use the status and diff views to decide what belongs in the snapshot.",
                    "Prepare the intended files and save the snapshot.",
                    (2, 5, self.diagnostic_commands),
                    self._copy_template(
                        template, count=3, signature="commit/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Only the repository state view is available.",
                    "Prepare and save the intended change.",
                    (2, 4, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="commit/hard/{{project}}/{{index}}"
                    ),
                ),
            },
        )

    def _gitignore_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "node-app",
                "files": {
                    ".gitignore": "untracked",
                    "node_modules/pkg.js": "ignored",
                    "dist/app.js": "ignored",
                },
                "message": "Add Node ignore rules",
            },
            {
                "project": "python-api",
                "files": {
                    ".gitignore": "untracked",
                    "__pycache__/app.pyc": "ignored",
                    ".env": "ignored",
                },
                "message": "Add Python ignore rules",
            },
            {
                "project": "java-service",
                "files": {
                    ".gitignore": "untracked",
                    "target/classes/App.class": "ignored",
                    "app.log": "ignored",
                },
                "message": "Add Java ignore rules",
            },
        ]
        template = self._state_template(
            slug="ignore-{{project}}-{{index}}",
            label="{{project}} generated files",
            signature="ignore/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state("c0", "{{files}}", {}),
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": "{{ignored_paths}}",
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": [".gitignore"],
                    "excludes_paths": "{{ignored_paths}}",
                    "message_contains": ["{{message}}"],
                },
                "required_commands": ["git add", "git commit"],
            },
            commands=["git add .gitignore", 'git commit -m "{{message}}"'],
            count=3,
        )
        return self._scenario(
            slug="configure-gitignore-rules",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Create and commit ignore rules",
            focus="git add .gitignore",
            summary="Commit ignore rules while keeping generated files out of history.",
            explanation=".gitignore is tracked like any other file, while matching generated files remain outside commits.",
            primary=["git add"],
            supporting=["git status"],
            concepts=["ignore patterns", "untracked files", "tracked ignore rules"],
            narrative="Generated files are present locally and should not enter Git history.",
            task_prompt="Prepare and save the ignore rules without saving generated files.",
            lesson_number=4,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "The ignore file is ready and generated files are present.",
                    "Save only the ignore rules.",
                    (2, 4, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "The project type changes which generated files should stay out.",
                    "Save the ignore rules and leave generated files out of history.",
                    (2, 4, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="ignore/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use the state view to identify the one file that belongs in history.",
                    "Save the ignore rules without saving ignored artifacts.",
                    (2, 3, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="ignore/hard/{{project}}/{{index}}"
                    ),
                ),
            },
        )

    def _partial_staging_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "auth",
                "file": "src/auth.py",
                "other_file": "notes/auth-notes.md",
                "message": "Isolate auth validation",
            },
            {
                "project": "search",
                "file": "src/search.py",
                "other_file": "notes/search-notes.md",
                "message": "Isolate search ranking",
            },
            {
                "project": "billing",
                "file": "src/billing.py",
                "other_file": "notes/billing-notes.md",
                "message": "Isolate billing totals",
            },
        ]
        template = self._state_template(
            slug="partial-{{project}}-{{index}}",
            label="{{project}} mixed hunks",
            signature="partial/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state(
                "c0",
                {"{{file}}": "modified", "{{other_file}}": "modified"},
                {},
                extra={"partial_hunks": {"{{file}}": ["target-hunk", "leftover-hunk"]}},
            ),
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": ["{{file}}", "{{other_file}}"],
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": ["{{file}}"],
                    "excludes_paths": ["{{other_file}}"],
                    "message_contains": ["{{message}}"],
                },
                "required_commands": ["git add -p", "git commit"],
            },
            commands=["git add -p {{file}}", 'git commit -m "{{message}}"'],
            count=2,
        )
        return self._scenario(
            slug="stage-selected-changes",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Stage selected hunks for a focused commit",
            focus="git add -p",
            summary="Use partial staging to commit one logical change while leaving other work untouched.",
            explanation="Partial staging lets one file carry both staged and unstaged work until the focused commit is saved.",
            primary=["git add -p"],
            supporting=["git diff", "git diff --staged", "git status"],
            concepts=["hunks", "partial staging", "focused commits"],
            narrative="A file contains mixed-purpose edits and only one hunk belongs in the next commit.",
            task_prompt="Prepare only the requested hunk and save a focused snapshot.",
            lesson_number=5,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "The target file is identified for you.",
                    "Stage only the requested hunk and save it.",
                    (2, 5, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "Use the diff views to verify the staged hunk before saving.",
                    "Stage only the intended hunk and save it.",
                    (2, 5, self.diagnostic_commands),
                    self._copy_template(
                        template, count=3, signature="partial/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use the state view to avoid committing unrelated edits.",
                    "Save only the selected hunk.",
                    (2, 4, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="partial/hard/{{project}}/{{index}}"
                    ),
                ),
            },
        )

    def _amend_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        message_cases = [
            {"project": "login-copy", "message": "Clarify login copy"},
            {"project": "settings-docs", "message": "Clarify settings docs"},
        ]
        content_cases = [
            {"project": "profile", "file": "src/profile.py", "message": "Polish profile update"},
            {"project": "export", "file": "src/export.py", "message": "Polish export update"},
        ]
        easy_template = self._state_template(
            slug="amend-message-{{project}}-{{index}}",
            label="{{project}} message repair",
            signature="amend/message/{{project}}/{{index}}",
            cases=message_cases,
            initial_state=self._repo_state("c1", {}, {}),
            target_rule={
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "latest_commit": {"branch": "main", "message_contains": ["{{message}}"]},
                "required_commands": ["git commit --amend"],
            },
            commands=['git commit --amend -m "{{message}}"'],
            count=2,
        )
        content_template = self._state_template(
            slug="amend-content-{{project}}-{{index}}",
            label="{{project}} content repair",
            signature="amend/content/{{project}}/{{index}}",
            cases=content_cases,
            initial_state=self._repo_state("c1", {"{{file}}": "modified"}, {}),
            target_rule={
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "latest_commit": {"branch": "main", "contains_paths": ["{{file}}"]},
                "required_commands": ["git add", "git commit --amend"],
            },
            commands=["git add {{file}}", "git commit --amend --no-edit"],
            count=2,
        )
        hard_template = self._copy_template(
            content_template,
            slug="amend-hard-{{project}}-{{index}}",
            signature="amend/hard/{{project}}/{{index}}",
            commands=["git add {{file}}", 'git commit --amend -m "{{message}}"'],
            target_rule={
                "head_branch": "main",
                "working_tree_clean": True,
                "staging_empty": True,
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": ["{{file}}"],
                    "message_contains": ["{{message}}"],
                },
                "required_commands": ["git add", "git commit --amend"],
            },
        )
        return self._scenario(
            slug="amend-latest-commit",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Amend the latest commit",
            focus="git commit --amend",
            summary="Repair the latest local commit before it is shared.",
            explanation="Amending rewrites the most recent local commit so the message or contents better match the intended snapshot.",
            primary=["git commit --amend"],
            supporting=["git status", "git log --oneline", "git diff --staged"],
            concepts=["commit amendment", "message repair", "content repair"],
            narrative="The latest commit needs a final local correction before anyone else sees it.",
            task_prompt="Repair the latest snapshot without creating an extra commit.",
            lesson_number=6,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "Only the commit message needs repair.",
                    "Amend the latest snapshot with the corrected message.",
                    (1, 3, self.diagnostic_commands),
                    easy_template,
                ),
                DIFFICULTY_MEDIUM: (
                    "A missing file change belongs in the latest commit.",
                    "Prepare the missing change and amend the latest snapshot.",
                    (2, 4, self.diagnostic_commands),
                    content_template,
                ),
                DIFFICULTY_HARD: (
                    "Repair both the staged content and message on the latest commit.",
                    "Amend the latest snapshot with the corrected content and message.",
                    (2, 4, self.diagnostic_commands),
                    hard_template,
                ),
            },
        )

    def _restore_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {"project": "cleanup", "keep_file": "src/app.py", "discard_file": "debug.log"},
            {"project": "docs", "keep_file": "docs/guide.md", "discard_file": "tmp/scratch.txt"},
            {"project": "styles", "keep_file": "styles/site.css", "discard_file": "dist/site.css"},
        ]
        template = self._state_template(
            slug="restore-{{project}}-{{index}}",
            label="{{project}} staged and unstaged mix",
            signature="restore/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state(
                "c0",
                {"{{discard_file}}": "modified"},
                {"{{keep_file}}": "modified"},
            ),
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": ["{{keep_file}}"],
                "working_tree_absent": ["{{discard_file}}"],
                "required_commands": ["git restore --staged", "git restore"],
            },
            commands=["git restore --staged {{keep_file}}", "git restore {{discard_file}}"],
            count=2,
        )
        restore_dot_template = self._copy_template(
            template,
            slug="restore-dot-{{project}}-{{index}}",
            signature="restore/staged-dot/{{project}}/{{index}}",
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": ["{{keep_file}}"],
                "working_tree_absent": ["{{discard_file}}"],
                "required_commands": ["git restore --staged", "git restore"],
            },
            commands=["git restore --staged .", "git restore {{discard_file}}"],
        )
        return self._scenario(
            slug="unstage-and-discard-changes",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Unstage and discard safely",
            focus="git restore",
            summary="Move wanted changes out of staging and remove unwanted working-tree edits.",
            explanation="Unstaging keeps work in the working tree; restoring a path discards the local edit for that path.",
            primary=["git restore"],
            supporting=["git status", "git diff", "git diff --staged"],
            concepts=["unstaging", "working tree", "discarding changes"],
            narrative="Some changes were staged too early and another local edit should be discarded.",
            task_prompt="Keep the intended work, unstage it, and discard the unwanted edit.",
            lesson_number=7,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "The staged file should be kept but not staged; the scratch file should go away.",
                    "Unstage the kept file and discard the unwanted file.",
                    (2, 4, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "Use restore to separate kept work from discarded work.",
                    "Unstage the kept file and discard the unwanted edit.",
                    (2, 4, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="restore/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use the broad staged-restore form, then discard the unwanted edit.",
                    "Unstage the kept file and discard the unwanted edit.",
                    (2, 4, self.diagnostic_commands),
                    restore_dot_template,
                ),
            },
        )

    def _read_state_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "status",
                "command": "git status",
                "must": ["staged_paths", "unstaged_paths", "untracked_paths"],
            },
            {
                "project": "history",
                "command": "git log --oneline",
                "must": ["commit_history", "latest_commit"],
            },
            {
                "project": "staged-diff",
                "command": "git diff --staged",
                "must": ["staged_diff_paths"],
            },
        ]
        template = self._state_template(
            slug="read-{{project}}-{{index}}",
            label="{{project}} repository reading",
            signature="read/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state(
                "c2",
                {"src/app.py": "modified", "notes/todo.md": "untracked"},
                {"README.md": "modified"},
            ),
            target_rule={
                "completion_type": COMPLETION_INSPECTION,
                "repository_state_unchanged": True,
                "required_commands": ["{{command}}"],
                "must_identify": "{{must}}",
            },
            commands=["{{command}}"],
            count=2,
        )
        return self._scenario(
            slug="read-repository-state",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Read status, history, and diffs",
            focus="git status",
            summary="Use diagnostic commands to identify repository state without changing it.",
            explanation="Inspection commands are non-counted because they help students reason before acting.",
            primary=["git status"],
            supporting=["git status", "git log --oneline", "git diff", "git diff --staged"],
            concepts=["status output", "commit history", "diff views"],
            narrative="The repository already has mixed state; the goal is to read it accurately.",
            task_prompt="Inspect the repository state without changing files, staging, or history.",
            lesson_number=8,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "Use the named diagnostic command to inspect the repository.",
                    "Inspect the repository without changing it.",
                    (0, 3, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "Choose the diagnostic view that answers the question.",
                    "Inspect the repository without changing it.",
                    (0, 3, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="read/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Use only diagnostic commands and preserve the repository state.",
                    "Inspect the repository without changing it.",
                    (0, 2, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="read/hard/{{project}}/{{index}}"
                    ),
                ),
            },
        )

    def _review_scenario(self, unit_slug: str, lesson_slug: str) -> ScenarioSpec:
        cases = [
            {
                "project": "release-notes",
                "commit_file": "docs/release.md",
                "keep_file": "notes/draft.md",
                "message": "Prepare release notes",
            },
            {
                "project": "profile-polish",
                "commit_file": "src/profile.py",
                "keep_file": "notes/profile-plan.md",
                "message": "Polish profile flow",
            },
            {
                "project": "build-cleanup",
                "commit_file": "build/config.yml",
                "keep_file": "notes/build-plan.md",
                "message": "Clean build config",
            },
        ]
        template = self._state_template(
            slug="review-{{project}}-{{index}}",
            label="{{project}} local workflow",
            signature="review/{{project}}/{{index}}",
            cases=cases,
            initial_state=self._repo_state(
                "c0",
                {
                    "{{commit_file}}": "modified",
                    ".gitignore": "untracked",
                    "{{keep_file}}": "modified",
                    "tmp/output.log": "ignored",
                },
                {},
            ),
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": ["{{keep_file}}", "tmp/output.log"],
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": ["{{commit_file}}", ".gitignore"],
                    "excludes_paths": ["{{keep_file}}", "tmp/output.log"],
                    "message_contains": ["{{message}}"],
                },
                "required_commands": ["git add", "git commit"],
            },
            commands=[
                "git add .gitignore",
                "git add {{commit_file}}",
                'git commit -m "{{message}}"',
            ],
            count=3,
        )
        hard_template = self._copy_template(
            template,
            count=3,
            signature="review/hard/{{project}}/{{index}}",
            initial_state=self._repo_state(
                "c1",
                {
                    "{{commit_file}}": "modified",
                    "{{keep_file}}": "modified",
                    "tmp/output.log": "ignored",
                },
                {},
            ),
            target_rule={
                "head_branch": "main",
                "staging_empty": True,
                "working_tree_contains": ["{{keep_file}}", "tmp/output.log"],
                "latest_commit": {
                    "branch": "main",
                    "contains_paths": ["{{commit_file}}"],
                    "excludes_paths": ["{{keep_file}}", "tmp/output.log"],
                    "message_contains": ["{{message}}"],
                },
                "required_commands": ["git add -p", "git commit --amend"],
            },
            commands=["git add -p {{commit_file}}", 'git commit --amend -m "{{message}}"'],
        )
        return self._scenario(
            slug="integrate-local-workflow",
            unit_slug=unit_slug,
            lesson_slug=lesson_slug,
            title="Complete a local repository workflow",
            focus="local Git workflow",
            summary="Combine ignore rules, selective staging, clean commits, and state reading.",
            explanation="The review scenario asks students to reason across the full local workflow, not just recall one command.",
            primary=["git commit"],
            supporting=["git status", "git diff", "git diff --staged", "git log --oneline"],
            concepts=["workflow integration", "clean commits", "state reasoning"],
            narrative="A local repository has useful work, ignored artifacts, and unrelated notes in progress.",
            task_prompt="Save the intended local work while leaving unrelated and ignored files out of the snapshot.",
            lesson_number=9,
            difficulty_configs={
                DIFFICULTY_EASY: (
                    "Use the visible file groups to save only the release-ready work.",
                    "Save the intended local work and leave unrelated files out.",
                    (3, 6, self.diagnostic_commands),
                    template,
                ),
                DIFFICULTY_MEDIUM: (
                    "Use status and diff views to confirm the snapshot scope.",
                    "Save the intended local work and leave unrelated files out.",
                    (3, 5, self.diagnostic_commands),
                    self._copy_template(
                        template, count=2, signature="review/medium/{{project}}/{{index}}"
                    ),
                ),
                DIFFICULTY_HARD: (
                    "Repair the latest local snapshot with only the selected work.",
                    "Amend the latest snapshot with the intended local work.",
                    (2, 5, self.diagnostic_commands),
                    hard_template,
                ),
            },
        )

    def _state_template(
        self,
        *,
        slug: str,
        label: str,
        signature: str,
        cases: list[dict],
        initial_state: dict,
        target_rule: dict,
        commands: list[str],
        count: int,
    ) -> VariantTemplateSpec:
        return VariantTemplateSpec(
            slug_template=slug,
            label_template=label,
            structure_signature_template=signature,
            initial_state_template=initial_state,
            target_rule_template=target_rule,
            solution_commands_template=commands,
            parameter_pools={"cases": [self._augment_case(case) for case in cases]},
            generation_count=count,
            student_context_template=self._student_context_template(),
        )

    def _copy_template(self, template: VariantTemplateSpec, **overrides) -> VariantTemplateSpec:
        return VariantTemplateSpec(
            slug_template=overrides.get("slug", template.slug_template),
            label_template=overrides.get("label", template.label_template),
            structure_signature_template=overrides.get(
                "signature",
                template.structure_signature_template,
            ),
            initial_state_template=overrides.get("initial_state", template.initial_state_template),
            target_rule_template=overrides.get("target_rule", template.target_rule_template),
            solution_commands_template=overrides.get(
                "commands", template.solution_commands_template
            ),
            parameter_pools=overrides.get("parameter_pools", template.parameter_pools),
            generation_count=overrides.get("count", template.generation_count),
            expected_observations_template=template.expected_observations_template,
            student_context_template=overrides.get(
                "student_context_template",
                template.student_context_template,
            ),
        )

    def _student_context_template(self) -> dict:
        return {
            "story": "You are working on {{project}}. Reach the requested repository outcome cleanly.",
            "current_state": [
                "Use the live repository state and terminal output to confirm the current branch, staged paths, and working-tree changes.",
            ],
            "provided_values": [],
            "requirements": [
                "Use the required details below as the exact target values for this attempt.",
                "Do not use the context as a command sequence; decide the Git steps from the repository state.",
            ],
            "warnings": [],
            "success_checklist": [],
            "inspection_suggestions": [
                "You may inspect the repository state before deciding what to do.",
            ],
        }

    def _augment_case(self, case: dict) -> dict:
        files = case.get("files") or {}
        ignored_paths = [path for path, state in files.items() if str(state).lower() == "ignored"]
        return {**case, "ignored_paths": ignored_paths}

    def _empty_uninitialized_state(self) -> dict:
        return {
            "repository_initialized": False,
            "commits": [],
            "branches": {"main": None},
            "head": {"type": "none", "name": None},
            "working_tree": {},
            "staging": {},
            "conflicts": [],
        }

    def _repo_state(
        self,
        head_commit: str,
        working_tree: dict | str,
        staging: dict | str,
        *,
        extra: dict | None = None,
    ) -> dict:
        commits = [{"id": "c0", "message": "Initial project", "parents": [], "files": {}}]
        if head_commit != "c0":
            commits.append(
                {
                    "id": head_commit,
                    "message": "Draft local update",
                    "parents": ["c0"],
                    "files": {"README.md": "modified"},
                }
            )
        state = {
            "repository_initialized": True,
            "commits": commits,
            "branches": {"main": head_commit},
            "head": {"type": "branch", "name": "main"},
            "working_tree": working_tree,
            "staging": staging,
            "conflicts": [],
        }
        if extra:
            state.update(extra)
        return state

    def _body_html(self, title: str, subtitle: str) -> str:
        return f"""
        <section class="lesson-panel">
          <h2>{title}</h2>
          <p>{subtitle}</p>
          <p>Practice below rotates project names, file structures, and repository states so the command pattern has to be understood instead of memorized.</p>
        </section>
        """


class Command(BaseCommand):
    help = "Seed the compact GIT it! Module 1 curriculum content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Clear local seeded content and scenario progress before seeding.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required with --reset to confirm local development data deletion.",
        )

    def handle(self, *args, **options):
        curriculum_path = settings.BASE_DIR.parent / "docs" / "GIT_it_Curriculum.md"
        if curriculum_path.exists():
            units, lessons, scenarios = CurriculumMarkdownParser().parse(curriculum_path)
        else:
            units, lessons, scenarios = ModuleOneSeedBuilder().build()
        with transaction.atomic():
            if options["reset"]:
                self._reset_seeded_content(confirm=options["confirm"])
            seed_git_command_content_library()
            unit_map = self._seed_units(units)
            lesson_map = self._seed_lessons(lessons, unit_map)
            self._seed_scenarios(scenarios, unit_map, lesson_map)
        self.stdout.write(self.style.SUCCESS("Seeded GIT it! curriculum content."))

    def _reset_seeded_content(self, *, confirm: bool) -> None:
        if not settings.DEBUG:
            raise CommandError("--reset is only available when DEBUG=True.")
        if not confirm:
            raise CommandError("Pass --confirm with --reset to clear local seeded data.")

        CompletionRecord.objects.all().delete()
        ScenarioSession.objects.all().delete()
        OrientationProgress.objects.all().delete()
        LearningUnit.objects.all().delete()
        StudentProgress.objects.update(
            first_scenario_started_at=None,
            orientation_complete_at_first_start=False,
        )
        StreakRecord.objects.update(
            current_streak=0,
            longest_streak=0,
            last_completed_on=None,
        )

    def _seed_units(self, specs: list[UnitSpec]) -> dict[str, LearningUnit]:
        active_slugs = [spec.slug for spec in specs]
        retired_units = LearningUnit.objects.exclude(slug__in=active_slugs).order_by("id")
        for index, unit in enumerate(retired_units, start=1000):
            update_fields = []
            if unit.number != index:
                unit.number = index
                update_fields.append("number")
            if unit.is_published:
                unit.is_published = False
                update_fields.append("is_published")
            if update_fields:
                unit.save(update_fields=update_fields)

        unit_map: dict[str, LearningUnit] = {}
        for spec in specs:
            unit, _ = LearningUnit.objects.update_or_create(
                slug=spec.slug,
                defaults={
                    "number": spec.number,
                    "title": spec.title,
                    "description": spec.description,
                    "is_orientation": spec.is_orientation,
                    "sort_order": spec.sort_order,
                    "is_published": True,
                },
            )
            unit_map[spec.slug] = unit
        return unit_map

    def _seed_lessons(
        self,
        specs: list[LessonSpec],
        unit_map: dict[str, LearningUnit],
    ) -> dict[str, Lesson]:
        Lesson.objects.exclude(slug__in=[spec.slug for spec in specs]).update(is_published=False)
        lesson_map: dict[str, Lesson] = {}
        for spec in specs:
            kind = self._lesson_kind(spec.kind)
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit_map[spec.unit_slug],
                slug=spec.slug,
                defaults={
                    "title": spec.title,
                    "subtitle": spec.subtitle,
                    "kind": kind,
                    "content_html": self._lesson_html(spec, kind),
                    "scoped_css": self._lesson_css(spec.slug),
                    "interaction_steps": [],
                    "sort_order": spec.sort_order,
                    "is_published": True,
                },
            )
            lesson_map[spec.slug] = lesson
        return lesson_map

    def _seed_scenarios(
        self,
        specs: list[ScenarioSpec],
        unit_map: dict[str, LearningUnit],
        lesson_map: dict[str, Lesson],
    ) -> None:
        active_slugs = [spec.slug for spec in specs]
        retired_scenarios = ScenarioSkillFocus.objects.exclude(slug__in=active_slugs)
        retired_scenarios.update(is_published=False)
        DifficultyInstance.objects.filter(scenario__in=retired_scenarios).update(is_published=False)
        ScenarioGenerationBlueprint.objects.filter(
            difficulty_instance__scenario__in=retired_scenarios
        ).update(is_published=False)
        ScenarioVariant.objects.filter(scenario__in=retired_scenarios).update(is_published=False)
        simulator = RepositoryStateSimulator()
        snapshotter = RepositorySnapshotService()
        inspector = InspectionEvaluator()

        for sort_order, spec in enumerate(specs, start=1):
            fields = self._scenario_defaults(spec)
            scenario, _ = ScenarioSkillFocus.objects.update_or_create(
                learning_unit=unit_map[spec.unit_slug],
                slug=spec.slug,
                defaults={
                    **fields,
                    "lesson": lesson_map[spec.lesson_slug],
                    "sort_order": sort_order,
                    "is_published": True,
                },
            )
            for difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD):
                config = spec.difficulties[difficulty]
                completion_type = self._completion_type(spec, config.target_rule)
                diff, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "completion_type": completion_type,
                        "required_successful_attempts": config.required_successful_attempts,
                        "narrative": config.narrative,
                        "task_prompt": self._student_task_prompt(config.task),
                        "is_published": True,
                    },
                )
                minimum, maximum, diagnostics = config.policy
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={
                        "min_counted_commands": minimum,
                        "max_counted_commands": maximum,
                        "non_counted_patterns": diagnostics,
                    },
                )

                current_blueprint_slugs = []
                for blueprint_index, template in enumerate(config.blueprints, start=1):
                    blueprint_slug = f"{scenario.slug}-{difficulty}-{blueprint_index}"
                    current_blueprint_slugs.append(blueprint_slug)
                    ScenarioGenerationBlueprint.objects.update_or_create(
                        difficulty_instance=diff,
                        slug=blueprint_slug,
                        defaults={
                            "slug_template": template.slug_template,
                            "label_template": template.label_template,
                            "blueprint_signature": f"{scenario.slug}/{difficulty}",
                            "subtemplate_signature": template.structure_signature_template,
                            "parameter_pools": template.parameter_pools,
                            "initial_state_template": template.initial_state_template,
                            "target_rule_template": template.target_rule_template,
                            "solution_commands_template": template.solution_commands_template,
                            "expected_observations_template": template.expected_observations_template,
                            "student_context_template": template.student_context_template,
                            "generation_count": template.generation_count,
                            "max_combinations": template.generation_count,
                            "sort_order": blueprint_index,
                            "is_published": True,
                        },
                    )
                ScenarioGenerationBlueprint.objects.filter(difficulty_instance=diff).exclude(
                    slug__in=current_blueprint_slugs
                ).update(is_published=False)

                variant_payloads = []
                for variant in config.variants:
                    initial_state = simulator.normalize_state(variant["initial_state"])
                    solution_commands = list(variant["solution_commands"])
                    raw_target_rule = variant.get("target_rule", config.target_rule)
                    target_rule = self._resolve_rule(
                        raw_target_rule,
                        variant_slug=variant["slug"],
                        initial_state=initial_state,
                        solution_commands=solution_commands,
                    )
                    target_state = self._target_state_from_solution(
                        simulator,
                        initial_state,
                        solution_commands,
                    )
                    target_rule = self._augment_target_rule(
                        target_rule,
                        spec=spec,
                        initial_state=initial_state,
                        solution_commands=solution_commands,
                        target_state=target_state,
                        completion_type=completion_type,
                    )
                    expected_observations = (
                        self._expected_observations(
                            inspector,
                            initial_state=initial_state,
                            target_rule=target_rule,
                        )
                        if completion_type == COMPLETION_INSPECTION
                        else {}
                    )
                    self._assert_no_variant_placeholders(
                        variant["slug"],
                        {
                            "target_rule": target_rule,
                            "expected_observations": expected_observations,
                            "solution_commands": solution_commands,
                        },
                    )
                    variant_payloads.append(
                        {
                            "slug": variant["slug"],
                            "label": variant["label"][:80],
                            "structure_signature": variant.get(
                                "structure_signature",
                                variant["slug"],
                            )[:120],
                            "initial_state": initial_state,
                            "target_rule": target_rule,
                            "target_state": target_state,
                            "expected_state_diagram": snapshotter.snapshot(target_state),
                            "expected_observations": expected_observations,
                            "solution_commands": solution_commands,
                            "is_published": True,
                        }
                    )

                first_target_state = variant_payloads[0]["target_state"]
                TargetStateRule.objects.update_or_create(
                    difficulty_instance=diff,
                    defaults={
                        "rule": self._difficulty_rule_for_storage(
                            config.target_rule, variant_payloads
                        ),
                        "target_state_hash": simulator.state_hash(first_target_state),
                    },
                )

                ScenarioVariant.objects.filter(
                    difficulty_instance=diff,
                    is_generated=False,
                ).update(is_published=False)

    def _scenario_defaults(self, spec: ScenarioSpec) -> dict:
        primary_focus_commands = spec.fields.get("primary_focus_commands") or [spec.focus]
        if len(primary_focus_commands) != 1:
            raise CommandError(f"Scenario {spec.slug} must have exactly one primary focus command.")
        return {
            "lesson": None,
            "title": spec.title,
            "focus": spec.focus,
            "summary": spec.fields.get("summary", ""),
            "short_explanation": spec.fields.get("short_explanation", ""),
            "skill_focus_type": spec.fields.get(
                "skill_focus_type", ScenarioSkillFocus.SkillFocusType.COMMAND_SPECIFIC
            ),
            "primary_focus_commands": primary_focus_commands,
            "supporting_inspection_commands": spec.fields.get("supporting_inspection_commands", []),
            "safe_demo_commands": spec.fields.get("safe_demo_commands", []),
            "demo_repository_state": RepositoryStateSimulator().normalize_state(
                spec.fields.get("demo_repository_state", {})
            )
            if spec.fields.get("demo_repository_state")
            else {},
            "demo_dag_config": spec.fields.get("demo_dag_config", {}),
            "demo_explanation_steps": spec.fields.get("demo_explanation_steps", []),
            "command_preview_config": spec.fields.get("command_preview_config")
            or self._command_preview_config(spec),
            "related_git_concepts": spec.fields.get("related_git_concepts", []),
            "narrative": spec.fields.get("narrative", ""),
            "task_prompt": self._student_task_prompt(spec.fields.get("task_prompt", "")),
        }

    def _command_preview_config(self, spec: ScenarioSpec) -> dict:
        commands = self._preview_commands_for_spec(spec)
        if not commands:
            return {}
        preview_commands = self._preview_commands_from_focus(spec, fallback_commands=commands)
        return {
            "schema_version": 2,
            "title": f"{spec.focus} command preview",
            "intro": spec.fields.get("short_explanation", ""),
            "purpose": spec.fields.get("summary", ""),
            "focus_label": spec.focus,
            "command_title": spec.title,
            "command_refs": [
                {
                    "id": command_content_key_for_command(command),
                    "key": command_content_key_for_command(command),
                    "command": command,
                }
                for command in preview_commands
            ],
            "supported_demo_commands": spec.fields.get("safe_demo_commands", commands),
            "demo_repository_state": spec.fields.get("demo_repository_state", {}),
            "demo_dag_config": spec.fields.get("demo_dag_config", {}),
            "custom_pages": [
                {
                    "id": "scenario-context",
                    "title": "Scenario context",
                    "blocks": [
                        {
                            "type": "paragraph",
                            "body": spec.fields.get("short_explanation", ""),
                        },
                        {
                            "type": "callout",
                            "title": "Practice purpose",
                            "body": spec.fields.get("summary", ""),
                        },
                    ],
                }
            ],
        }

    def _preview_commands_from_focus(
        self,
        spec: ScenarioSpec,
        *,
        fallback_commands: list[str],
    ) -> list[str]:
        commands = [
            *list(spec.fields.get("primary_focus_commands", [])),
            *list(spec.fields.get("supporting_inspection_commands", [])),
        ] or fallback_commands
        seen_keys = set()
        unique = []
        for command in commands:
            key = command_content_key_for_command(command)
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            unique.append(command)
        return unique

    def _preview_commands_for_spec(self, spec: ScenarioSpec) -> list[str]:
        commands = [
            *list(spec.fields.get("safe_demo_commands", [])),
            *list(spec.fields.get("primary_focus_commands", [])),
            *list(spec.fields.get("supporting_inspection_commands", [])),
        ]
        seen = set()
        unique = []
        for command in commands:
            normalized = " ".join(str(command).split()).lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique.append(command)
        return unique

    def _student_task_prompt(self, task: str) -> str:
        prompt = task
        for command, replacement in TASK_COMMAND_REPLACEMENTS:
            prompt = re.sub(re.escape(command), replacement, prompt, flags=re.IGNORECASE)
        prompt = re.sub(r"\b[Cc]lone\b", "Create a local working copy", prompt)
        prompt = re.sub(r"\b[Pp]ush\b", "Publish", prompt)
        prompt = re.sub(r"\b[Ff]etch\b", "Update remote-tracking information", prompt)
        prompt = re.sub(r"\b[Pp]ull\b", "Update from upstream", prompt)
        prompt = re.sub(r"\b[Mm]erge\b", "Integrate", prompt)
        prompt = re.sub(r"\b[Ss]witch\b", "Move", prompt)
        prompt = re.sub(
            r"\b[Ss]oft reset\b", "Move the branch pointer while keeping changes staged", prompt
        )
        prompt = re.sub(r"\b[Rr]eset\b", "Move the branch pointer", prompt)
        prompt = re.sub(r"\b[Ss]tage only\b", "Prepare only", prompt)
        prompt = re.sub(r"\b[Ss]tage\b", "Prepare", prompt)
        prompt = re.sub(r"\b[Cc]reate the first commit\b", "save the first snapshot", prompt)
        prompt = re.sub(r"\b[Cc]reate a commit\b", "save a snapshot", prompt)
        prompt = re.sub(r"\b[Cc]ommitted\b", "saved", prompt)
        prompt = re.sub(r"\b[Cc]ommit\b", "snapshot", prompt)
        prompt = re.sub(
            r"\bgit\s+(?!repository\b)[a-z-]+(?:\s+--?[a-z-]+)*",
            "the appropriate command",
            prompt,
            flags=re.IGNORECASE,
        )
        prompt = re.sub(r"\s+", " ", prompt).strip()
        return prompt

    def _augment_target_rule(
        self,
        target_rule: dict,
        *,
        spec: ScenarioSpec,
        initial_state: dict,
        solution_commands: list[str],
        target_state: dict,
        completion_type: str,
    ) -> dict:
        if completion_type == COMPLETION_INSPECTION:
            return target_rule

        augmented = dict(target_rule)
        required = list(augmented.get("required_commands", []))
        for command in spec.fields.get("primary_focus_commands") or [spec.focus]:
            if command and command not in required:
                required.append(command)
        if required:
            augmented["required_commands"] = required

        primary_commands = set(spec.fields.get("primary_focus_commands") or [spec.focus])
        if primary_commands & {"git clone", "git remote"}:
            remote_matches = dict(augmented.get("remote_url_matches", {}))
            remote_matches.setdefault(
                "origin", self._remote_url(initial_state, solution_commands, "app")
            )
            augmented["remote_url_matches"] = remote_matches

        if any(command.startswith("git commit") for command in solution_commands):
            latest_commit = self._head_commit(target_state)
            changed_paths = sorted(
                (latest_commit or {}).get("changes") or (latest_commit or {}).get("files", {})
            )
            if changed_paths:
                latest_rule = dict(augmented.get("latest_commit", {}))
                latest_rule.setdefault("branch", self._head_branch(target_state) or "main")
                latest_rule["contains_paths"] = sorted(
                    set(latest_rule.get("contains_paths", [])) | set(changed_paths)
                )
                excluded_paths = sorted(
                    set(initial_state.get("working_tree", {})) - set(changed_paths)
                )
                if excluded_paths:
                    latest_rule["excludes_paths"] = sorted(
                        set(latest_rule.get("excludes_paths", [])) | set(excluded_paths)
                    )
                augmented["latest_commit"] = latest_rule

        return augmented

    def _completion_type(self, spec: ScenarioSpec, target_rule: dict) -> str:
        if target_rule.get("completion_type") == COMPLETION_INSPECTION:
            return COMPLETION_INSPECTION
        if spec.seeding_status == "requires_simulator_expansion":
            return COMPLETION_EXPANDED_STATE_BASED
        return COMPLETION_STATE_BASED

    def _target_state_from_solution(
        self,
        simulator: RepositoryStateSimulator,
        initial_state: dict,
        commands: list[str],
    ) -> dict:
        state = simulator.clone_state(initial_state)
        for command in commands:
            result = simulator.process(state, command)
            if not result.processed:
                raise CommandError(f"Could not seed solution command {command!r}: {result.output}")
            state = result.state
        return state

    def _head_branch(self, state: dict) -> str | None:
        head = state.get("head", {})
        return head.get("name") if head.get("type") == "branch" else None

    def _head_commit(self, state: dict) -> dict | None:
        head = state.get("head", {})
        commit_id = (
            state.get("branches", {}).get(head.get("name"))
            if head.get("type") == "branch"
            else head.get("target")
        )
        if not commit_id:
            return None
        return next(
            (commit for commit in state.get("commits", []) if commit["id"] == commit_id), None
        )

    def _expected_observations(
        self,
        inspector: InspectionEvaluator,
        *,
        initial_state: dict,
        target_rule: dict,
    ) -> dict:
        observations = inspector.observations_for(initial_state)
        must_identify = target_rule.get("must_identify", [])
        return {
            "required_commands": target_rule.get("required_commands", []),
            "repository_state_unchanged": target_rule.get("repository_state_unchanged", True),
            "checks": {key: observations[key] for key in must_identify if key in observations},
        }

    def _difficulty_rule_for_storage(self, raw_rule: dict, variants: list[dict]) -> dict:
        if not self._has_placeholder(raw_rule):
            return raw_rule
        return {
            "variant_specific": True,
            "completion_type": raw_rule.get("completion_type", COMPLETION_STATE_BASED),
            "variant_rule_count": len(variants),
        }

    def _resolve_rule(
        self,
        rule: dict,
        *,
        variant_slug: str,
        initial_state: dict,
        solution_commands: list[str],
    ) -> dict:
        context = self._placeholder_context(variant_slug, initial_state, solution_commands)
        return self._resolve_placeholders(rule, context)

    def _placeholder_context(
        self,
        variant_slug: str,
        initial_state: dict,
        solution_commands: list[str],
    ) -> dict:
        topic = self._topic_for(variant_slug, initial_state, solution_commands)
        add_paths = self._added_paths(solution_commands)
        working_paths = list(initial_state.get("working_tree", {}).keys())
        staging_paths = list(initial_state.get("staging", {}).keys())
        topic_file = self._topic_file(topic, working_paths + staging_paths)
        ready_file = add_paths[0] if add_paths else topic_file
        draft_file = next((path for path in working_paths if path != ready_file), "draft.md")
        kept_file = next(
            (path for path in working_paths if path not in {"scratch.md", "wip.md"}),
            topic_file,
        )
        url = self._remote_url(initial_state, solution_commands, topic)
        return {
            "<topic>": topic,
            "<ready-file>": ready_file,
            "<draft-file>": draft_file,
            "<kept-file>": kept_file,
            "<topic-file>": topic_file,
            "<changed-file>": topic_file,
            "<file-a>": "README.md",
            "<file-b>": topic_file,
            "<changed-files>": ["README.md", topic_file],
            "<url>": url,
        }

    def _resolve_placeholders(self, value: Any, context: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            resolved = {}
            for key, item in value.items():
                resolved_key = self._resolve_placeholders(key, context)
                resolved[resolved_key] = self._resolve_placeholders(item, context)
            return resolved
        if isinstance(value, list):
            resolved_list = []
            for item in value:
                resolved = self._resolve_placeholders(item, context)
                if isinstance(item, str) and item in context and isinstance(resolved, list):
                    resolved_list.extend(resolved)
                else:
                    resolved_list.append(resolved)
            return resolved_list
        if isinstance(value, str):
            if value in context:
                return context[value]
            resolved = value
            for placeholder, replacement in context.items():
                if isinstance(replacement, list):
                    continue
                resolved = resolved.replace(placeholder, str(replacement))
            return resolved
        return value

    def _topic_for(
        self, variant_slug: str, initial_state: dict, solution_commands: list[str]
    ) -> str:
        joined = " ".join(
            [
                variant_slug,
                json.dumps(initial_state.get("branches", {})),
                json.dumps(initial_state.get("remote_branches", {})),
                " ".join(solution_commands),
            ]
        )
        return next((topic for topic in TOPICS if topic in joined), TOPICS[0])

    def _topic_file(self, topic: str, paths: list[str]) -> str:
        return next((path for path in paths if path.startswith(f"{topic}.")), f"{topic}.py")

    def _added_paths(self, solution_commands: list[str]) -> list[str]:
        paths: list[str] = []
        for command in solution_commands:
            parts = command.split()
            if len(parts) >= 3 and parts[0:2] == ["git", "add"] and parts[2] not in {".", "-A"}:
                paths.extend(parts[2:])
        return paths

    def _remote_url(self, initial_state: dict, solution_commands: list[str], topic: str) -> str:
        for command in solution_commands:
            if command.startswith("git remote add origin "):
                return command.rsplit(" ", 1)[-1]
            if command.startswith("git clone "):
                parts = command.split()
                if len(parts) >= 3:
                    return parts[2]
        return initial_state.get("remotes", {}).get("origin", f"https://example.test/{topic}.git")

    def _has_placeholder(self, value: Any) -> bool:
        return bool(PLACEHOLDER_RE.search(json.dumps(value)))

    def _assert_no_variant_placeholders(self, slug: str, payload: dict) -> None:
        if self._has_placeholder(payload):
            raise CommandError(f"Variant {slug} still contains unresolved target placeholders.")

    def _lesson_kind(self, raw_kind: str) -> str:
        if raw_kind == "orientation":
            return Lesson.LessonKind.ORIENTATION
        if raw_kind == "scenario":
            return Lesson.LessonKind.SCENARIO
        return Lesson.LessonKind.CONTENT

    def _lesson_html(self, spec: LessonSpec, kind: str) -> str:
        kicker = "Practice lesson" if kind == Lesson.LessonKind.SCENARIO else "Foundation lesson"
        meta_last = "Includes practice" if kind == Lesson.LessonKind.SCENARIO else "Visual guide"
        practice_heading = (
            "Practice connection"
            if kind == Lesson.LessonKind.SCENARIO
            else "Where you will use this"
        )
        practice_text = (
            "After reading, use the scenarios listed below this lesson to choose a lesson scenario "
            "and difficulty. Each level has its own situation, action budget, and retry version."
            if kind == Lesson.LessonKind.SCENARIO
            else "Use this page as a field guide. The same idea returns in later practice."
        )
        return f"""
        <article class="lesson-copy lesson-page lesson-page--{spec.slug}">
          <section class="lesson-hero">
            <div class="lesson-kicker">{kicker}</div>
            <h1>{spec.title}</h1>
            <p class="lesson-lede">{spec.subtitle}</p>
            <div class="lesson-meta">
              <span>Scrollable lesson</span>
              <span>State-first reasoning</span>
              <span>{meta_last}</span>
            </div>
          </section>
          {spec.visual_html}
          {spec.body_html}
          <section class="lesson-panel practice-panel">
            <h2>{practice_heading}</h2>
            <p>{practice_text}</p>
          </section>
        </article>
        """

    def _lesson_css(self, slug: str) -> str:
        return f"""
        .lesson-page--{slug} {{
          display: block;
        }}
        .lesson-page--{slug} .lesson-panel,
        .lesson-page--{slug} .lesson-visual,
        .lesson-page--{slug} .lesson-hero {{
          border-radius: 8px;
        }}
        """
