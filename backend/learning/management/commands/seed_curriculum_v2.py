from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
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
from scenarios.visualization import RepositoryVisualizationService
from simulator.services import RepositoryStateSimulator


class Command(BaseCommand):
    help = "Seed the v2 command drill and workflow scenario curriculum."

    def add_arguments(self, parser):
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate published curriculum shape, simulator support, and official solutions.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.supported_usage_keys = {spec["usage"] for spec in COMMAND_DRILLS}
        self.published_module_slugs = self._published_module_slugs()
        self._seed_foundations()
        modules = self._seed_modules()
        usages = self._seed_command_topics(modules)
        self._seed_command_drills(usages)
        self._seed_workflows(modules)
        if options.get("validate"):
            self._validate_curriculum()
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
            is_published = spec["slug"] in self.published_module_slugs
            module, _ = LearningModule.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "number": spec["number"],
                    "title": spec["title"],
                    "description": spec["description"],
                    "sort_order": index,
                    "is_published": is_published,
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
            usage_keys = {
                f"{spec['slug']}/{usage_spec['slug']}"
                for usage_spec in spec.get("usages", [])
            }
            topic_is_published = bool(module.is_published and usage_keys.intersection(self.supported_usage_keys))
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
                    "is_published": topic_is_published,
                },
            )
            live_topic_ids.append(topic.id)
            live_usage_ids = []
            for usage_index, usage_spec in enumerate(spec.get("usages", []), start=1):
                usage_key = f"{spec['slug']}/{usage_spec['slug']}"
                usage_is_published = topic_is_published and usage_key in self.supported_usage_keys
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
                        "is_published": usage_is_published,
                    },
                )
                usages[usage_key] = usage
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
                    "is_published": modules[spec["module"]].is_published,
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
                        "is_published": scenario.is_published,
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

    def _published_module_slugs(self) -> set[str]:
        usage_to_module = {}
        for topic in COMMAND_TOPICS:
            for usage in topic.get("usages", []):
                usage_to_module[f"{topic['slug']}/{usage['slug']}"] = topic["module"]
        command_modules = {
            usage_to_module[spec["usage"]]
            for spec in COMMAND_DRILLS
            if spec["usage"] in usage_to_module
        }
        workflow_modules = {
            spec["module"]
            for spec in WORKFLOW_SCENARIOS
            if spec["module"] in command_modules
        }
        return command_modules | workflow_modules

    def _validate_curriculum(self) -> None:
        errors: list[str] = []
        modules = list(LearningModule.objects.filter(is_published=True).order_by("sort_order", "number"))
        for module in modules:
            levels = list(
                CommandTopic.objects.filter(module=module, is_published=True).order_by("sort_order", "id")
            )
            if not levels:
                errors.append(f"{module.slug}: missing command drill adventure levels")
                continue
            for level in levels:
                self._validate_command_level(level=level, errors=errors)

        for scenario in WorkflowScenario.objects.filter(is_published=True):
            levels = list(scenario.levels.filter(is_published=True))
            difficulties = {level.difficulty for level in levels}
            if difficulties != {"easy", "medium", "hard"}:
                errors.append(f"{scenario.slug}: workflow scenarios must publish Easy, Medium, and Hard")
            for level in levels:
                self._validate_problem_variants(problem=level, errors=errors)

        if errors:
            raise CommandError("Curriculum validation failed:\n" + "\n".join(f"- {error}" for error in errors))
        self.stdout.write(self.style.SUCCESS("Validated v2 curriculum."))

    def _validate_command_level(self, *, level: CommandTopic, errors: list[str]) -> None:
        if not level.base_command:
            errors.append(f"{level.slug}: command level is missing a base command")
        usages = list(level.usages.filter(is_published=True).order_by("sort_order", "id"))
        if not usages:
            errors.append(f"{level.slug}: command level has no published usages/options")
            return
        for usage in usages:
            drills = list(usage.drills.filter(is_published=True).order_by("sort_order", "id"))
            if not drills:
                errors.append(f"{level.slug}/{usage.slug}: published usage has no command drills")
                continue
            for drill in drills:
                self._validate_problem_variants(problem=drill, errors=errors)

    def _validate_problem_variants(self, *, problem, errors: list[str]) -> None:
        variants = list(problem.variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            errors.append(f"{self._problem_name(problem)}: published practice item has no variants")
            return
        for variant in variants:
            self._validate_variant(variant=variant, errors=errors)

    def _validate_variant(self, *, variant: ProblemVariant, errors: list[str]) -> None:
        label = f"{variant.practice_kind}:{self._problem_slug(variant)}/{variant.slug}"
        required_fields = {
            "initial_state": variant.initial_state,
            "target_state": variant.target_state,
            "evaluation_spec": variant.evaluation_spec,
            "solution_commands": variant.solution_commands,
            "expected_state_diagram": variant.expected_state_diagram,
        }
        for field, value in required_fields.items():
            if not value:
                errors.append(f"{label}: missing {field}")

        simulator = RepositoryStateSimulator()
        state = simulator.normalize_state(variant.initial_state)
        executed_commands = []
        for command in variant.solution_commands or []:
            result = simulator.process(state, command)
            if not result.processed:
                errors.append(f"{label}: solution command is not supported by the simulator: {command}")
                return
            executed_commands.append(result.normalized_command)
            state = result.state

        final_state = simulator.normalize_state(state)
        try:
            spec = compile_evaluation_spec(variant.evaluation_spec)
        except ValueError as exc:
            errors.append(f"{label}: invalid evaluation_spec: {exc}")
            return
        outcome = EvaluationEngine().evaluate(
            spec=spec,
            next_state=final_state,
            initial_state=variant.initial_state,
            executed_commands=executed_commands,
            next_state_hash=simulator.state_hash_for_normalized(final_state),
            expected_state_hash=simulator.state_hash(variant.target_state),
        )
        if not outcome.target_matched:
            errors.append(f"{label}: official solution does not satisfy evaluation_spec: {outcome.summary}")

        visualization = RepositoryVisualizationService().snapshot(
            final_state,
            target_state=variant.target_state,
        )
        if visualization.get("schema_version") != 2 or not visualization.get("target_state_lens"):
            errors.append(f"{label}: target state visualization is missing")

    def _problem_slug(self, variant: ProblemVariant) -> str:
        if variant.command_drill_id:
            return variant.command_drill.slug
        return f"{variant.workflow_level.scenario.slug}/{variant.workflow_level.difficulty}"

    def _problem_name(self, problem) -> str:
        if isinstance(problem, CommandDrill):
            return problem.slug
        return f"{problem.scenario.slug}/{problem.difficulty}"
