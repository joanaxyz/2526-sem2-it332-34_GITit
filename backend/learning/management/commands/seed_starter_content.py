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
from learning.models import LearningUnit, Lesson
from scenarios.models import (
    CommandCountPolicy,
    DifficultyInstance,
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
    narrative: str
    task: str
    policy: tuple[int, int, list[str]]
    target_rule: dict
    variants: list[dict] = field(default_factory=list)


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


class Command(BaseCommand):
    help = "Seed the GIT it! curriculum from docs/GIT_it_Curriculum.md."

    def handle(self, *args, **options):
        curriculum_path = settings.BASE_DIR.parent / "docs" / "GIT_it_Curriculum.md"
        if not curriculum_path.exists():
            raise CommandError(f"Curriculum markdown not found at {curriculum_path}.")

        units, lessons, scenarios = CurriculumMarkdownParser().parse(curriculum_path)
        with transaction.atomic():
            unit_map = self._seed_units(units)
            lesson_map = self._seed_lessons(lessons, unit_map)
            self._seed_scenarios(scenarios, unit_map, lesson_map)
        self.stdout.write(self.style.SUCCESS("Seeded GIT it! curriculum content."))

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
        DifficultyInstance.objects.filter(scenario__in=retired_scenarios).update(
            is_published=False
        )
        ScenarioVariant.objects.filter(scenario__in=retired_scenarios).update(
            is_published=False
        )
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

                variant_payloads = []
                for variant in config.variants:
                    initial_state = simulator.normalize_state(variant["initial_state"])
                    solution_commands = list(variant["solution_commands"])
                    target_rule = self._resolve_rule(
                        config.target_rule,
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
                            "structure_signature": variant["slug"],
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
                        "rule": self._difficulty_rule_for_storage(config.target_rule, variant_payloads),
                        "target_state_hash": simulator.state_hash(first_target_state),
                    },
                )

                current_variant_slugs = []
                for payload in variant_payloads:
                    current_variant_slugs.append(payload["slug"])
                    ScenarioVariant.objects.update_or_create(
                        scenario=scenario,
                        difficulty_instance=diff,
                        slug=payload["slug"],
                        defaults=payload,
                    )
                ScenarioVariant.objects.filter(difficulty_instance=diff).exclude(
                    slug__in=current_variant_slugs
                ).update(is_published=False)

    def _scenario_defaults(self, spec: ScenarioSpec) -> dict:
        primary_focus_commands = spec.fields.get("primary_focus_commands") or [spec.focus]
        if len(primary_focus_commands) != 1:
            raise CommandError(
                f"Scenario {spec.slug} must have exactly one primary focus command."
            )
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
            "related_git_concepts": spec.fields.get("related_git_concepts", []),
            "narrative": spec.fields.get("narrative", ""),
            "task_prompt": self._student_task_prompt(spec.fields.get("task_prompt", "")),
        }

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
        prompt = re.sub(r"\b[Ss]oft reset\b", "Move the branch pointer while keeping changes staged", prompt)
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
            remote_matches.setdefault("origin", self._remote_url(initial_state, solution_commands, "app"))
            augmented["remote_url_matches"] = remote_matches

        if any(command.startswith("git commit") for command in solution_commands):
            latest_commit = self._head_commit(target_state)
            changed_paths = sorted((latest_commit or {}).get("files", {}))
            if changed_paths:
                latest_rule = dict(augmented.get("latest_commit", {}))
                latest_rule.setdefault("branch", self._head_branch(target_state) or "main")
                latest_rule["contains_paths"] = sorted(
                    set(latest_rule.get("contains_paths", [])) | set(changed_paths)
                )
                excluded_paths = sorted(set(initial_state.get("working_tree", {})) - set(changed_paths))
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
        return next((commit for commit in state.get("commits", []) if commit["id"] == commit_id), None)

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
            "checks": {
                key: observations[key]
                for key in must_identify
                if key in observations
            },
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

    def _topic_for(self, variant_slug: str, initial_state: dict, solution_commands: list[str]) -> str:
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
        practice_heading = "Practice connection" if kind == Lesson.LessonKind.SCENARIO else "Where you will use this"
        practice_text = (
            "After reading, use the scenarios listed below this lesson to choose a practice topic "
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
