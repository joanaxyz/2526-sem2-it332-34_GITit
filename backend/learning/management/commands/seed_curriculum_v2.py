from django.core.management.base import BaseCommand
from django.db import transaction

from learning.curriculum_v2.command_topics import COMMAND_TOPICS
from learning.curriculum_v2.drills import COMMAND_DRILLS
from learning.curriculum_v2.foundations import FOUNDATIONS
from learning.curriculum_v2.modules import MODULES
from learning.curriculum_v2.workflows import WORKFLOW_SCENARIOS
from learning.models import FoundationTopic, LearningModule
from scenarios.builders import StaticProblemVariantBuilder
from scenarios.models import (
    CommandDrill,
    CommandTopic,
    CommandUsage,
    ProblemVariant,
    WorkflowScenario,
    WorkflowScenarioLevel,
)


class Command(BaseCommand):
    help = "Seed the v2 command drill and workflow scenario curriculum."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_foundations()
        modules = self._seed_modules()
        usages = self._seed_command_topics(modules)
        self._seed_command_drills(usages)
        self._seed_workflows(modules)
        self.stdout.write(self.style.SUCCESS("Seeded v2 curriculum."))

    def _seed_foundations(self) -> None:
        live_slugs = []
        for index, spec in enumerate(FOUNDATIONS, start=1):
            live_slugs.append(spec["slug"])
            FoundationTopic.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "body": spec["body"],
                    "icon": spec.get("icon", ""),
                    "cards": spec.get("cards", []),
                    "sort_order": index,
                    "is_published": True,
                },
            )
        FoundationTopic.objects.exclude(slug__in=live_slugs).update(is_published=False)

    def _seed_modules(self) -> dict[str, LearningModule]:
        modules = {}
        live_slugs = []
        for index, spec in enumerate(MODULES, start=1):
            live_slugs.append(spec["slug"])
            module, _ = LearningModule.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "number": spec["number"],
                    "title": spec["title"],
                    "description": spec["description"],
                    "sort_order": index,
                    "is_published": True,
                },
            )
            modules[spec["slug"]] = module
        LearningModule.objects.exclude(slug__in=live_slugs).update(is_published=False)
        return modules

    def _seed_command_topics(self, modules: dict[str, LearningModule]) -> dict[str, CommandUsage]:
        usages = {}
        live_topic_ids = []
        for topic_index, spec in enumerate(COMMAND_TOPICS, start=1):
            module = modules[spec["module"]]
            topic, _ = CommandTopic.objects.update_or_create(
                module=module,
                slug=spec["slug"],
                defaults={
                    "base_command": spec["base_command"],
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "mental_model": spec.get("mental_model", {}),
                    "command_preview": self._preview(spec["title"], spec["summary"]),
                    "sort_order": topic_index,
                    "is_published": True,
                },
            )
            live_topic_ids.append(topic.id)
            live_usage_ids = []
            for usage_index, usage_spec in enumerate(spec.get("usages", []), start=1):
                usage, _ = CommandUsage.objects.update_or_create(
                    topic=topic,
                    slug=usage_spec["slug"],
                    defaults={
                        "usage_form": usage_spec["usage_form"],
                        "label": usage_spec["label"],
                        "summary": usage_spec.get("summary", ""),
                        "command_preview": self._preview(
                            usage_spec["usage_form"],
                            usage_spec.get("summary") or spec["summary"],
                            syntax=usage_spec["usage_form"],
                        ),
                        "sort_order": usage_index,
                        "is_published": True,
                    },
                )
                usages[f"{spec['slug']}/{usage_spec['slug']}"] = usage
                live_usage_ids.append(usage.id)
            CommandUsage.objects.filter(topic=topic).exclude(id__in=live_usage_ids).update(
                is_published=False
            )
        CommandTopic.objects.exclude(id__in=live_topic_ids).update(is_published=False)
        return usages

    def _seed_command_drills(self, usages: dict[str, CommandUsage]) -> None:
        builder = StaticProblemVariantBuilder()
        live_drill_ids = []
        for index, spec in enumerate(COMMAND_DRILLS, start=1):
            usage = usages[spec["usage"]]
            drill, _ = CommandDrill.objects.update_or_create(
                usage=usage,
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "required_successful_attempts": spec["required_successful_attempts"],
                    "min_counted_commands": spec["min_counted_commands"],
                    "max_counted_commands": spec["max_counted_commands"],
                    "student_context": spec["student_context"],
                    "sort_order": index,
                    "is_published": True,
                },
            )
            live_drill_ids.append(drill.id)
            self._sync_variants(problem=drill, variant_specs=spec["variants"], builder=builder)
        CommandDrill.objects.exclude(id__in=live_drill_ids).update(is_published=False)

    def _seed_workflows(self, modules: dict[str, LearningModule]) -> None:
        builder = StaticProblemVariantBuilder()
        live_scenario_ids = []
        for index, spec in enumerate(WORKFLOW_SCENARIOS, start=1):
            scenario, _ = WorkflowScenario.objects.update_or_create(
                module=modules[spec["module"]],
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "narrative": spec["narrative"],
                    "command_topics": spec.get("command_topics", []),
                    "sort_order": index,
                    "is_published": True,
                },
            )
            live_scenario_ids.append(scenario.id)
            live_level_ids = []
            for level_spec in spec.get("levels", []):
                level, _ = WorkflowScenarioLevel.objects.update_or_create(
                    scenario=scenario,
                    difficulty=level_spec["difficulty"],
                    defaults={
                        "narrative": level_spec["narrative"],
                        "task_prompt": level_spec["task_prompt"],
                        "required_successful_attempts": level_spec["required_successful_attempts"],
                        "min_counted_commands": level_spec["min_counted_commands"],
                        "max_counted_commands": level_spec["max_counted_commands"],
                        "student_context": level_spec["student_context"],
                        "is_published": True,
                    },
                )
                live_level_ids.append(level.id)
                self._sync_variants(
                    problem=level,
                    variant_specs=level_spec["variants"],
                    builder=builder,
                )
            WorkflowScenarioLevel.objects.filter(scenario=scenario).exclude(id__in=live_level_ids).update(
                is_published=False
            )
        WorkflowScenario.objects.exclude(id__in=live_scenario_ids).update(is_published=False)

    def _sync_variants(self, *, problem, variant_specs: list[dict], builder: StaticProblemVariantBuilder) -> None:
        live_ids = []
        for index, variant_spec in enumerate(variant_specs, start=1):
            case = {"case_id": variant_spec["case_id"]}
            variant = builder.build(problem=problem, template=variant_spec, case=case, index=index)
            filters = {"semantic_key": variant.semantic_key}
            if isinstance(problem, CommandDrill):
                filters["command_drill"] = problem
            else:
                filters["workflow_level"] = problem
            saved, _ = ProblemVariant.objects.update_or_create(
                **filters,
                defaults={
                    "slug": variant.slug,
                    "label": variant.label,
                    "structure_signature": variant.structure_signature,
                    "initial_state": variant.initial_state,
                    "evaluation_spec": variant.evaluation_spec,
                    "target_state": variant.target_state,
                    "expected_state_diagram": variant.expected_state_diagram,
                    "solution_commands": variant.solution_commands,
                    "case_id": variant.case_id,
                    "parameter_context": variant.parameter_context,
                    "student_context": variant.student_context,
                    "is_published": True,
                },
            )
            live_ids.append(saved.id)
        if isinstance(problem, CommandDrill):
            ProblemVariant.objects.filter(command_drill=problem).exclude(id__in=live_ids).update(
                is_published=False
            )
        else:
            ProblemVariant.objects.filter(workflow_level=problem).exclude(id__in=live_ids).update(
                is_published=False
            )

    def _preview(self, title: str, summary: str, *, syntax: str | None = None) -> dict:
        syntax_examples = [syntax] if syntax else []
        return {
            "schema_version": 2,
            "title": title,
            "summary": summary,
            "syntax_examples": syntax_examples,
        }
