from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db import transaction
from django.db.utils import OperationalError

from common.constants import (
    COMPLETION_STATE_BASED,
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
)
from learning.management.commands.seed_module1_scenarios import commit, repo_with_head
from learning.models import LearningUnit, Lesson, OrientationProgress
from scenarios.builders import ScenarioVariantBuildError, StaticCaseMaterializer
from scenarios.command_content import (
    command_content_key_for_command,
    command_preview_section_ids_for_command,
    command_preview_syntax_for_command,
    seed_git_command_content_library,
)
from scenarios.models import (
    CommandCountPolicy,
    CompletionRecord,
    DifficultyInstance,
    ScenarioSession,
    ScenarioSkillFocus,
    ScenarioVariant,
)
from simulator.services import RepositoryStateSimulator, is_diagnostic_command

DIAG_PATTERNS = [
    "git status",
    "git log --oneline --graph --all",
    "git reflog",
    "git show HEAD@{n}",
    "git merge-base <branch1> <branch2>",
    "git rev-list --count <branch1>..<branch2>",
]

MODULE_FOUR_LESSONS = [
    (1, "recovering-from-hard-resets", "Recovering from Hard Resets", "Recover lost work after a destructive reset."),
    (2, "reversing-pushed-commits-safely", "Reversing Pushed Commits Safely", "Use revert to preserve shared history."),
    (3, "completing-rebase-recovery-sequences", "Completing Rebase Recovery Sequences", "Finish a full rebase recovery workflow."),
]


def _debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict[str, Any]) -> None:
    log_path = Path(__file__).resolve().parents[4] / "debug-f8332c.log"
    payload = {
        "sessionId": "f8332c",
        "id": f"log_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}",
        "timestamp": int(time.time() * 1000),
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=True) + "\n")


def template(
    *,
    slug: str,
    signature: str,
    cases: list[dict[str, Any]],
    initial_state: dict[str, Any],
    target_rule: dict[str, Any],
    solution: list[str] | str,
    label: str,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "slug_template": f"{slug}-{{{{case_id}}}}",
        "label_template": label,
        "template_key": signature,
        "structure_key": signature,
        "cases": cases,
        "initial_state_template": initial_state,
        "target_rule_template": target_rule,
        "solution_commands_template": solution,
        "student_context_template": {
            "story": "{{incident}}",
            "required_details": [
                {"label": "Objective", "value": "{{objective}}"},
                {"label": "Expected end state", "value": "{{expected_end_state}}"},
            ],
            "constraints": ["Use safe recovery and history operations."],
        },
    }


def difficulty_spec(
    *,
    policy: tuple[int, int],
    narrative: str,
    task: str,
    templates: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "policy": policy,
        "narrative": narrative,
        "task": task,
        "templates": templates,
        "completion_type": COMPLETION_STATE_BASED,
    }


def scenario_dict(
    *,
    lesson: tuple,
    slug: str,
    title: str,
    focus: str,
    summary: str,
    explanation: str,
    primary: list[str],
    supporting: list[str],
    concepts: list[str],
    difficulties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "lesson": lesson,
        "slug": slug,
        "title": title,
        "focus": focus,
        "summary": summary,
        "explanation": explanation,
        "primary": primary,
        "supporting": supporting,
        "concepts": concepts,
        "kind": ScenarioSkillFocus.SkillFocusType.WORKFLOW_SPECIFIC,
        "difficulties": difficulties,
    }


def hard_reset_case(case_id: str, *, depth: int, suffix: str) -> dict[str, Any]:
    incident_variants = [
        (
            "During a release dry-run, you reset main while cleaning up local commits and lost the feature tip just before handoff."
        ),
        (
            "While preparing a hotfix branch, you used a hard reset on main and erased the latest validated commit from visible history."
        ),
        (
            "In a handover crunch, you rewound main to inspect an older state and accidentally dropped the newest feature checkpoint."
        ),
        (
            "During an incident triage, you forcefully moved HEAD to an earlier commit and now need to recover the missing release tip."
        ),
        (
            "While reconciling branch history after QA feedback, you reset too far back and lost the commit the team still needs."
        ),
    ]
    try:
        case_number = int(case_id.split("-")[-1][1:]) - 1
    except (ValueError, IndexError):
        case_number = 0
    incident_blurb = incident_variants[case_number % len(incident_variants)]
    commits = [
        commit("c0", f"Baseline {suffix}", {"README.md": f"base-{suffix}"}),
        commit("c1", f"Feature A {suffix}", {"README.md": f"a-{suffix}"}, ["c0"]),
        commit("c2", f"Feature B {suffix}", {"README.md": f"b-{suffix}"}, ["c1"]),
        commit("c3", f"Feature C {suffix}", {"README.md": f"c-{suffix}"}, ["c2"]),
    ]
    state = repo_with_head(commits=commits, head="c3", branch="main")
    simulator = RepositoryStateSimulator()
    reset_target = f"HEAD~{depth}"
    reset_state = simulator.process(state, f"git reset --hard {reset_target}").state
    expected = {"recovery_branch": f"recovery-{case_id}", "recovery_target": "c3"}
    return {
        "case_id": case_id,
        "incident": (
            "You are a release engineer in a software company. "
            f"{incident_blurb} The destructive reset landed on {reset_target}."
        ),
        "objective": "Recover the lost work from history evidence without rewriting shared history.",
        "expected_end_state": (
            f"Create branch {expected['recovery_branch']} at the recovered lost tip commit (c3)."
        ),
        "initial_state": reset_state,
        **expected,
    }


def revert_case(case_id: str, *, bad_commit: str, suffix: str) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit("c0", f"Baseline {suffix}", {"README.md": "v1"}),
            commit("c1", f"Stable update {suffix}", {"README.md": "v2"}, ["c0"]),
            commit("c2", f"Bad pushed change {suffix}", {"README.md": f"bad-{suffix}"}, ["c1"]),
            commit("c3", f"Follow-up change {suffix}", {"README.md": f"follow-{suffix}"}, ["c2"]),
        ],
        head="c3",
        branch="main",
        remotes={"origin": f"https://example.test/{suffix}.git"},
        remote_branches={"origin/main": "c3"},
        upstream_tracking={"main": "origin/main"},
    )
    return {
        "case_id": case_id,
        "incident": (
            "You are a backend developer in a software company. A risky configuration change "
            "was already pushed to main before QA flagged it as breaking production behavior."
        ),
        "objective": "Undo the bad change safely by appending corrective history and synchronizing remote.",
        "expected_end_state": "A new rollback commit is appended on main and origin/main matches the local tip.",
        "initial_state": state,
        "bad_commit": bad_commit,
    }


def rebase_case(case_id: str, *, suffix: str, interactive: bool = False) -> dict[str, Any]:
    state = repo_with_head(
        commits=[
            commit("c0", f"Base {suffix}", {"src/app.ts": "base"}),
            commit("c1", f"Main update {suffix}", {"src/app.ts": "main-v1"}, ["c0"]),
            commit("c2", f"Feature update {suffix}", {"src/app.ts": "feature-v1"}, ["c0"]),
            commit("c3", f"Feature follow-up {suffix}", {"src/app.ts": "feature-v2"}, ["c2"]),
        ],
        head="c3",
        branch="feature/recovery",
    )
    state["branches"]["main"] = "c1"
    return {
        "case_id": case_id,
        "incident": (
            "You are a feature owner in a software company. Your branch diverged while main moved, "
            "and a teammate needs a clean history before code freeze."
        ),
        "objective": "Recover the branch by replaying feature work onto the latest main and validating history integrity.",
        "expected_end_state": "feature/recovery points to a clean rebased commit chain with no in-progress state.",
        "initial_state": state,
        "rebase_target": "main",
        "interactive": interactive,
    }


def module_four_scenarios() -> list[dict[str, Any]]:
    hard_easy = [hard_reset_case(f"4-1-e{i}", depth=1, suffix=f"e{i}") for i in range(1, 6)]
    hard_medium = [hard_reset_case(f"4-1-m{i}", depth=2, suffix=f"m{i}") for i in range(1, 6)]
    hard_hard = [hard_reset_case(f"4-1-h{i}", depth=3, suffix=f"h{i}") for i in range(1, 6)]

    revert_easy = [revert_case(f"4-2-e{i}", bad_commit="c3", suffix=f"re{i}") for i in range(1, 6)]
    revert_medium = [revert_case(f"4-2-m{i}", bad_commit="c2", suffix=f"rm{i}") for i in range(1, 6)]
    revert_hard = [revert_case(f"4-2-h{i}", bad_commit="c2", suffix=f"rh{i}") for i in range(1, 6)]

    rebase_easy = [rebase_case(f"4-3-e{i}", suffix=f"be{i}") for i in range(1, 6)]
    rebase_medium = [rebase_case(f"4-3-m{i}", suffix=f"bm{i}", interactive=True) for i in range(1, 6)]
    rebase_hard = [rebase_case(f"4-3-h{i}", suffix=f"bh{i}", interactive=(i % 2 == 0)) for i in range(1, 6)]

    hard_reset_target = {}
    revert_target = {
        "head_branch": "main",
        "working_tree_clean": True,
        "staging_empty": True,
        "conflict_free": True,
        "required_commands": ["git revert", "git push"],
        "rules": [
            {"type": "new_revert_commit_exists"},
            {"type": "revert_preserves_history", "commit": "{{bad_commit}}", "branch": "main"},
            {"type": "push_moved_remote_to_local_tip", "branch": "main", "remote_branch": "origin/main"},
        ],
    }
    rebase_target = {}

    return [
        scenario_dict(
            lesson=MODULE_FOUR_LESSONS[0],
            slug="recover-from-hard-reset-incident",
            title="Recover from a hard reset incident",
            focus="hard reset recovery",
            summary=(
                "You are an on-call release engineer who accidentally dropped recent work with a hard reset "
                "and must reconstruct the lost tip from repository history."
            ),
            explanation=(
                "Each variant frames a workplace incident where you investigate history clues and safely restore work "
                "onto a dedicated recovery branch."
            ),
            primary=["git reflog", "git show", "git switch", "git reset --hard"],
            supporting=["git log --oneline --graph --all", "git status"],
            concepts=["reflog", "head movement", "safe branch restore"],
            difficulties={
                DIFFICULTY_EASY: difficulty_spec(
                    policy=(2, 6),
                    narrative=(
                        "You are a junior engineer handling a low-pressure rollback incident after a shallow mistaken reset."
                    ),
                    task="Find the most recent lost tip and restore it to the requested recovery branch.",
                    templates=[
                        template(
                            slug="recover-hard-reset",
                            signature="module4.hard-reset.easy",
                            cases=hard_easy,
                            initial_state="{{initial_state}}",
                            target_rule=hard_reset_target,
                            solution=[
                                "git reflog",
                                "git reset --hard HEAD",
                                "git show {{recovery_target}}",
                                "git switch -c {{recovery_branch}} {{recovery_target}}",
                            ],
                            label="Recover {{recovery_branch}}",
                        )
                    ],
                ),
                DIFFICULTY_MEDIUM: difficulty_spec(
                    policy=(2, 7),
                    narrative=(
                        "You are the sprint lead responding to a deeper mistaken reset with limited guidance from teammates."
                    ),
                    task="Trace the correct history entry and restore the branch to the requested recovery point.",
                    templates=[
                        template(
                            slug="recover-hard-reset",
                            signature="module4.hard-reset.medium",
                            cases=hard_medium,
                            initial_state="{{initial_state}}",
                            target_rule=hard_reset_target,
                            solution=[
                                "git reflog",
                                "git reset --hard HEAD",
                                "git show {{recovery_target}}",
                                "git switch -c {{recovery_branch}} {{recovery_target}}",
                            ],
                            label="Recover {{recovery_branch}}",
                        )
                    ],
                ),
                DIFFICULTY_HARD: difficulty_spec(
                    policy=(2, 8),
                    narrative=(
                        "You are the incident commander recovering critical work from a noisy reset trail under release pressure."
                    ),
                    task="Disambiguate noisy history evidence and recover exactly the requested lost tip branch.",
                    templates=[
                        template(
                            slug="recover-hard-reset",
                            signature="module4.hard-reset.hard",
                            cases=hard_hard,
                            initial_state="{{initial_state}}",
                            target_rule=hard_reset_target,
                            solution=[
                                "git reflog",
                                "git reset --hard HEAD",
                                "git show {{recovery_target}}",
                                "git switch -c {{recovery_branch}} {{recovery_target}}",
                            ],
                            label="Recover {{recovery_branch}}",
                        )
                    ],
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_FOUR_LESSONS[1],
            slug="reverse-pushed-commit-safely",
            title="Reverse a pushed commit safely",
            focus="shared-history-safe reversal",
            summary=(
                "You are shipping on a shared main branch, and a production-risk commit is already published to origin."
            ),
            explanation=(
                "Variants simulate team-facing rollback incidents where you must correct shared history safely "
                "without destructive rewrites."
            ),
            primary=["git revert", "git push"],
            supporting=["git status", "git log --oneline --graph --all"],
            concepts=["shared history", "revert", "remote synchronization"],
            difficulties={
                DIFFICULTY_EASY: difficulty_spec(
                    policy=(2, 4),
                    narrative=(
                        "You are a developer handling a straightforward rollback request right after a bad push."
                    ),
                    task="Append the rollback commit for the target change and ensure remote main is updated.",
                    templates=[
                        template(
                            slug="revert-pushed",
                            signature="module4.revert.easy",
                            cases=revert_easy,
                            initial_state="{{initial_state}}",
                            target_rule=revert_target,
                            solution=["git revert {{bad_commit}}", "git push"],
                            label="Revert {{bad_commit}} safely",
                        )
                    ],
                ),
                DIFFICULTY_MEDIUM: difficulty_spec(
                    policy=(2, 5),
                    narrative=(
                        "You are supporting QA during regression triage, and the bad change is buried in published history."
                    ),
                    task="Identify the correct published change to roll back and synchronize the shared branch.",
                    templates=[
                        template(
                            slug="revert-pushed",
                            signature="module4.revert.medium",
                            cases=revert_medium,
                            initial_state="{{initial_state}}",
                            target_rule=revert_target,
                            solution=["git revert {{bad_commit}} --no-edit", "git push"],
                            label="Revert {{bad_commit}} with --no-edit",
                        )
                    ],
                ),
                DIFFICULTY_HARD: difficulty_spec(
                    policy=(2, 6),
                    narrative=(
                        "You are the release owner during a high-stakes deploy window with strict rollback constraints."
                    ),
                    task="Execute the required rollback while preserving shared history integrity across local and remote.",
                    templates=[
                        template(
                            slug="revert-pushed",
                            signature="module4.revert.hard",
                            cases=revert_hard,
                            initial_state="{{initial_state}}",
                            target_rule=revert_target,
                            solution=["git revert {{bad_commit}}", "git push -u origin main"],
                            label="Rollback {{bad_commit}}",
                        )
                    ],
                ),
            },
        ),
        scenario_dict(
            lesson=MODULE_FOUR_LESSONS[2],
            slug="complete-rebase-recovery-sequence",
            title="Complete a rebase recovery sequence",
            focus="rebase recovery",
            summary=(
                "You are a feature lead preparing a branch for merge after timeline pressure caused history divergence."
            ),
            explanation=(
                "Variants place you in realistic pre-release cleanup stories where you recover branch history "
                "and prove the final graph is healthy."
            ),
            primary=["git rebase", "git status", "git log --oneline --graph --all"],
            supporting=["git merge-base", "git rev-list --count"],
            concepts=["rebase", "history rewrite", "integrity checks"],
            difficulties={
                DIFFICULTY_EASY: difficulty_spec(
                    policy=(1, 5),
                    narrative=(
                        "You are finishing a normal sprint task where your feature branch simply drifted from main."
                    ),
                    task="Recover the branch onto the current main line and confirm the repository is clean.",
                    templates=[
                        template(
                            slug="rebase-recovery",
                            signature="module4.rebase.easy",
                            cases=rebase_easy,
                            initial_state="{{initial_state}}",
                            target_rule=rebase_target,
                            solution=[
                                "git status",
                                "git rebase {{rebase_target}}",
                                "git log --oneline --graph --all",
                            ],
                            label="Rebase {{case_id}}",
                        )
                    ],
                ),
                DIFFICULTY_MEDIUM: difficulty_spec(
                    policy=(1, 6),
                    narrative=(
                        "You are coordinating with reviewers who need a refined commit sequence before acceptance."
                    ),
                    task="Run an interactive recovery flow and verify no incomplete rebase state remains.",
                    templates=[
                        template(
                            slug="rebase-recovery",
                            signature="module4.rebase.medium",
                            cases=rebase_medium,
                            initial_state="{{initial_state}}",
                            target_rule=rebase_target,
                            solution=[
                                "git status",
                                "git merge-base main feature/recovery",
                                "git rebase -i {{rebase_target}}",
                                "git rev-list --count main..feature/recovery",
                                "git log --oneline --graph --all",
                            ],
                            label="Interactive rebase {{case_id}}",
                        )
                    ],
                ),
                DIFFICULTY_HARD: difficulty_spec(
                    policy=(1, 7),
                    narrative=(
                        "You are driving final release cleanup, and branch integrity checks are stricter than usual."
                    ),
                    task="Complete the full recovery sequence and validate branch integrity with all required checks.",
                    templates=[
                        template(
                            slug="rebase-recovery",
                            signature="module4.rebase.hard",
                            cases=rebase_hard,
                            initial_state="{{initial_state}}",
                            target_rule=rebase_target,
                            solution=[
                                "git status",
                                "git rebase {{rebase_target}}",
                                "git merge-base main feature/recovery",
                                "git rev-list --count main..feature/recovery",
                                "git log --oneline --graph --all",
                            ],
                            label="Capstone rebase {{case_id}}",
                        )
                    ],
                ),
            },
        ),
    ]


class Command(BaseCommand):
    help = "Seed Module 4 advanced recovery and history scenario skill focuses and variants."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")
        parser.add_argument("--confirm", action="store_true")
        parser.add_argument("--validate-build", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H1",
            location="seed_module4_scenarios.py:handle",
            message="seed command entered",
            data={"options_keys": sorted(options.keys()), "reset": bool(options.get("reset"))},
        )
        # endregion
        self._ensure_lesson_kind_default()

        if options["reset"]:
            self._reset_module_four(confirm=options["confirm"])

        seed_git_command_content_library()
        unit, _ = LearningUnit.objects.update_or_create(
            slug="advanced-recovery-history",
            defaults={
                "number": 4,
                "title": "Advanced Recovery and History",
                "description": "Practice hard reset recovery, safe pushed commit reversal, and rebase recovery sequences.",
                "is_orientation": False,
                "is_published": True,
                "sort_order": 4,
            },
        )

        lesson_by_order: dict[int, Lesson] = {}
        for order, slug, title, subtitle in MODULE_FOUR_LESSONS:
            lesson, _ = Lesson.objects.update_or_create(
                unit=unit,
                slug=slug,
                defaults={
                    "title": title,
                    "subtitle": subtitle,
                    "content_html": self._anchor_html(title, subtitle),
                    "scoped_css": "",
                    "interaction_steps": [],
                    "is_published": True,
                    "sort_order": order,
                },
            )
            lesson_by_order[order] = lesson

        specs = module_four_scenarios()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).exclude(
            slug__in=[spec["slug"] for spec in specs]
        ).update(is_published=False)

        for spec in specs:
            lesson_order = spec["lesson"][0]
            scenario, _ = ScenarioSkillFocus.objects.update_or_create(
                learning_unit=unit,
                slug=spec["slug"],
                defaults={
                    "lesson": lesson_by_order[lesson_order],
                    "title": spec["title"],
                    "focus": spec["focus"],
                    "summary": spec["summary"],
                    "short_explanation": spec["explanation"],
                    "skill_focus_type": spec["kind"],
                    "primary_focus_commands": spec["primary"],
                    "supporting_diagnostic_commands": spec["supporting"],
                    "safe_demo_commands": self._demo_commands(spec),
                    "demo_repository_state": self._demo_state(spec),
                    "demo_dag_config": {"requires_dag": True},
                    "demo_explanation_steps": [],
                    "command_preview_config": self._command_preview_config(spec),
                    "related_git_concepts": spec["concepts"],
                    "narrative": spec["summary"],
                    "task_prompt": "Start an authored practice variant and reach the requested repository outcome.",
                    "is_published": True,
                    "sort_order": lesson_order,
                },
            )
            for difficulty, dspec in spec["difficulties"].items():
                difficulty_instance, _ = DifficultyInstance.objects.update_or_create(
                    scenario=scenario,
                    difficulty=difficulty,
                    defaults={
                        "completion_type": dspec["completion_type"],
                        "required_successful_attempts": 2 if difficulty == DIFFICULTY_EASY else 1,
                        "narrative": dspec["narrative"],
                        "task_prompt": dspec["task"],
                        "is_published": True,
                    },
                )
                min_count, max_count = dspec["policy"]
                CommandCountPolicy.objects.update_or_create(
                    difficulty_instance=difficulty_instance,
                    defaults={
                        "min_counted_commands": min_count,
                        "max_counted_commands": max_count,
                        "non_counted_patterns": DIAG_PATTERNS,
                    },
                )
                variants = self._render_variants(difficulty_instance=difficulty_instance, dspec=dspec)
                active_semantic_keys = []
                for variant in variants:
                    active_semantic_keys.append(variant.semantic_key)
                    ScenarioVariant.objects.update_or_create(
                        difficulty_instance=difficulty_instance,
                        semantic_key=variant.semantic_key,
                        defaults={
                            "scenario": scenario,
                            "slug": variant.slug,
                            "label": variant.label,
                            "structure_signature": variant.structure_signature,
                            "initial_state": variant.initial_state,
                            "target_rule": variant.target_rule,
                            "target_state": variant.target_state,
                            "expected_state_diagram": variant.expected_state_diagram,
                            "solution_commands": variant.solution_commands,
                            "case_id": variant.case_id,
                            "parameter_context": variant.parameter_context,
                            "student_context": variant.student_context,
                            "is_published": True,
                        },
                    )
                ScenarioVariant.objects.filter(difficulty_instance=difficulty_instance).exclude(
                    semantic_key__in=active_semantic_keys
                ).update(is_published=False)

        self.stdout.write(self.style.SUCCESS("Seeded Module 4 authored scenario variants."))
        if options["validate_build"]:
            self.stdout.write(self.style.SUCCESS("All Module 4 authored variants are valid."))

    def _render_variants(self, *, difficulty_instance: DifficultyInstance, dspec: dict[str, Any]) -> list[ScenarioVariant]:
        materializer = StaticCaseMaterializer()
        variants = []
        for authored_template in dspec["templates"]:
            for index, case in enumerate(authored_template["cases"], start=1):
                try:
                    variants.append(
                        materializer.materialize_variant(
                            difficulty_instance=difficulty_instance,
                            template=authored_template,
                            case=case,
                            index=index,
                        )
                    )
                except (KeyError, ScenarioVariantBuildError) as exc:
                    raise CommandError(
                        f"{difficulty_instance.scenario.slug}/{difficulty_instance.difficulty}/"
                        f"{authored_template['slug']}/{case.get('case_id')}: {exc}"
                    ) from exc
        if not variants:
            raise CommandError(f"{difficulty_instance.scenario.slug}/{difficulty_instance.difficulty}: no variants")
        return variants

    def _reset_module_four(self, *, confirm: bool):
        if not settings.DEBUG:
            raise CommandError("--reset is only available when DEBUG=True.")
        if not confirm:
            raise CommandError("Pass --confirm with --reset to clear Module 4 seeded data.")
        unit = LearningUnit.objects.filter(slug="advanced-recovery-history").first()
        if not unit:
            return
        CompletionRecord.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSession.objects.filter(learning_unit=unit).delete()
        ScenarioVariant.objects.filter(scenario__learning_unit=unit).delete()
        DifficultyInstance.objects.filter(scenario__learning_unit=unit).delete()
        ScenarioSkillFocus.objects.filter(learning_unit=unit).delete()
        OrientationProgress.objects.filter(lesson__unit=unit).delete()
        unit.lessons.all().delete()
        unit.delete()

    def _ensure_lesson_kind_default(self) -> None:
        model_field_names = {field.name for field in Lesson._meta.get_fields() if hasattr(field, "name")}
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H2",
            location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
            message="entered ensure_lesson_kind_default",
            data={"has_model_kind": "kind" in model_field_names, "db_vendor": connection.vendor},
        )
        # endregion
        if "kind" in model_field_names:
            return
        if connection.vendor != "postgresql":
            return
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'learning_lesson'
                  AND column_name = 'kind'
                """
            )
            if cursor.fetchone() is None:
                # region agent log
                _debug_log(
                    run_id="pre-fix",
                    hypothesis_id="H3",
                    location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                    message="kind column absent in physical table",
                    data={"table": "learning_lesson"},
                )
                # endregion
                return
            cursor.execute("SHOW statement_timeout")
            timeout_value = cursor.fetchone()
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H4",
                location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                message="about to alter lesson.kind default",
                data={"statement_timeout": timeout_value[0] if timeout_value else None},
            )
            # endregion
            cursor.execute(
                """
                SELECT column_default
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'learning_lesson'
                  AND column_name = 'kind'
                """
            )
            default_row = cursor.fetchone()
            current_default = default_row[0] if default_row else None
            # region agent log
            _debug_log(
                run_id="post-fix",
                hypothesis_id="H6",
                location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                message="observed current lesson.kind default",
                data={"current_default": current_default},
            )
            # endregion
            if current_default and "scenario" in current_default:
                # region agent log
                _debug_log(
                    run_id="post-fix",
                    hypothesis_id="H6",
                    location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                    message="skipping alter; default already scenario",
                    data={"current_default": current_default},
                )
                # endregion
                return
            try:
                cursor.execute("ALTER TABLE learning_lesson ALTER COLUMN kind SET DEFAULT 'scenario'")
            except OperationalError as exc:
                # region agent log
                _debug_log(
                    run_id="post-fix",
                    hypothesis_id="H7",
                    location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                    message="alter default failed; continuing seed",
                    data={"error": str(exc)},
                )
                # endregion
                return
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H5",
                location="seed_module4_scenarios.py:_ensure_lesson_kind_default",
                message="alter default succeeded",
                data={"table": "learning_lesson", "column": "kind", "default": "scenario"},
            )
            # endregion

    def _anchor_html(self, title: str, subtitle: str) -> str:
        return f"""
<section class=\"internal-scenario-anchor\">
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <p>Internal scenario anchor for Module 4 advanced recovery practice.</p>
</section>
""".strip()

    def _demo_state(self, spec: dict[str, Any]) -> dict[str, Any]:
        return spec["difficulties"][DIFFICULTY_EASY]["templates"][0]["cases"][0]["initial_state"]

    def _demo_commands(self, spec: dict[str, Any]) -> list[str]:
        focus = spec["focus"]
        commands = {
            "hard reset recovery": [
                "git reflog",
                "git show HEAD@{1}",
                "git switch -c recovery-example HEAD@{1}",
                "git log --oneline --graph --all",
            ],
            "shared-history-safe reversal": [
                "git revert c2",
                "git push",
                "git status",
                "git log --oneline --graph --all",
            ],
            "rebase recovery": [
                "git status",
                "git rebase main",
                "git merge-base main feature/recovery",
                "git rev-list --count main..feature/recovery",
                "git log --oneline --graph --all",
            ],
        }.get(focus, [])
        return commands

    def _command_preview_config(self, spec: dict[str, Any]) -> dict[str, Any]:
        commands = self._demo_commands(spec)
        diagnostic = bool(commands) and all(is_diagnostic_command(command) for command in commands)
        return {
            "schema_version": 2,
            "title": f"{spec['focus']} command preview",
            "intro": spec["explanation"],
            "purpose": "Understand expected command phases before starting the scenario.",
            "focus_label": spec["focus"],
            "command_title": spec["title"],
            "command_refs": self._preview_command_refs(commands),
            "supported_demo_commands": commands,
            "demo_repository_state": self._demo_state(spec),
            "demo_dag_config": {"requiresDag": True, "previewModalEnabled": True},
            "diagnostic": diagnostic,
            "counted": not diagnostic,
        }

    def _preview_command_refs(self, commands: list[str]) -> list[dict[str, Any]]:
        refs = []
        seen = set()
        for command in commands:
            if not command.startswith("git "):
                continue
            syntax = command_preview_syntax_for_command(command)
            key = command_content_key_for_command(syntax or command)
            identity = (key, syntax)
            if identity in seen:
                continue
            seen.add(identity)
            refs.append(
                {
                    "id": f"{key}-{len(refs) + 1}",
                    "key": key,
                    "command": syntax or command,
                    "include_section_ids": command_preview_section_ids_for_command(syntax or command),
                }
            )
        return refs
