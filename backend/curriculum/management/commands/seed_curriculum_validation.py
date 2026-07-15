from __future__ import annotations

from django.core.management.base import CommandError

from adventures.models import AdventureLevel, AdventureWave
from challenges.models import ChallengeLevel
from curriculum.models import Chapter, CommandForm, CommandSkill
from curriculum.seed_data.adventure_levels import ADVENTURE_LEVELS
from curriculum.seed_data.adventures import ADVENTURE_SOURCES
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.command_catalog import COMMAND_CATALOG
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from practice.services.visualization import RepositoryVisualizationService
from simulator.services import RepositoryStateSimulator


class SeedCurriculumValidationMixin:
    def _validate_curriculum(self) -> None:
        errors: list[str] = []
        chapters = list(Chapter.objects.filter(is_published=True).order_by("sort_order", "number"))
        # Skills are a global library now; a form carries the chapter it is taught
        # in. Every published chapter must teach at least one command form, and
        # every published skill must be well-formed.
        for chapter in chapters:
            owns_form = CommandForm.objects.filter(chapter=chapter, is_published=True).exists()
            reuses_form = AdventureLevel.objects.filter(
                chapter=chapter,
                is_published=True,
                command_forms__is_published=True,
            ).exists() or ChallengeLevel.objects.filter(
                chapter=chapter,
                is_published=True,
                command_forms__is_published=True,
            ).exists()
            if not owns_form and not reuses_form:
                errors.append(f"{chapter.slug}: missing command forms")
        for skill in CommandSkill.objects.filter(is_published=True).order_by("sort_order", "id"):
            self._validate_command_skill(skill=skill, errors=errors)

        for wave in AdventureWave.objects.filter(
            is_published=True,
            level__is_published=True,
            level__chapter__is_published=True,
        ).order_by(
            "level__chapter__sort_order",
            "level__sort_order",
            "sort_order",
            "id",
        ):
            self._validate_level_variants(level=wave, errors=errors)

        for level in ChallengeLevel.objects.filter(is_published=True).prefetch_related("trials__variants"):
            trials = list(level.trials.filter(is_published=True))
            difficulties = {trial.difficulty for trial in trials}
            if difficulties != {"easy", "medium", "hard"}:
                errors.append(
                    f"{level.slug}: challenge levels must publish Easy, Medium, and Hard"
                )
            for trial in trials:
                self._validate_level_variants(level=trial, errors=errors)


        self._validate_challenge_intro_contract(errors=errors)
        self._validate_seed_adventure_references(errors=errors)

        if errors:
            raise CommandError(
                "Curriculum validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            )
        self.stdout.write(self.style.SUCCESS("Validated curriculum."))

    def _validate_seed_adventure_references(self, *, errors: list[str]) -> None:
        configured = set()
        for chapter_slug, configured_specs in ADVENTURE_SOURCES.items():
            if isinstance(configured_specs, dict):
                configured_specs = [configured_specs]
            for index, configured_spec in enumerate(configured_specs or [{}], start=1):
                suffix = "" if index == 1 else f"-{index}"
                configured.add(
                    configured_spec.get("slug") or f"{chapter_slug}-command-adventure{suffix}"
                )
        for spec in ADVENTURE_LEVELS:
            adventure_slug = spec.get("adventure")
            if adventure_slug and adventure_slug not in configured:
                errors.append(
                    f"{spec['slug']}: references unknown Adventure {adventure_slug!r}"
                )

    def _validate_command_skill(self, *, skill: CommandSkill, errors: list[str]) -> None:
        if not skill.base_command:
            errors.append(f"{skill.slug}: command skill is missing a base command")
        forms = list(skill.command_forms.filter(is_published=True).order_by("sort_order", "id"))
        if not forms:
            errors.append(f"{skill.slug}: command skill has no published forms")

    def _validate_level_variants(self, *, level, errors: list[str]) -> None:
        variants = list(level.variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            errors.append(f"{self._level_name(level)}: published level/trial has no variants")
            return
        for variant in variants:
            self._validate_variant(variant=variant, errors=errors)

    def _validate_challenge_intro_contract(self, *, errors: list[str]) -> None:
        """Challenges must apply, not introduce, Git concepts.

        A Challenge level declares the Adventure levels it depends on through
        ``uses_adventure_levels``. Every listed level must exist, and it must
        belong to the same chapter or an earlier chapter. This keeps Challenge
        scenario quality high without shrinking the curriculum to whatever the
        current command evaluator already supports. The authored evaluation spec
        also carries a curriculum_contract.dag_transition so future engine work
        knows what graph behavior the scenario is teaching.
        """
        module_order = {spec["slug"]: spec["number"] for spec in CHAPTERS}
        usage_to_module = {}
        for skill_spec in COMMAND_CATALOG:
            for form_spec in skill_spec.get("usages", []):
                usage_to_module[f"{skill_spec['slug']}/{form_spec['slug']}"] = skill_spec["module"]
        source_to_module: dict[str, str] = {}
        for module_slug, configured_specs in ADVENTURE_SOURCES.items():
            if isinstance(configured_specs, dict):
                configured_specs = [configured_specs]
            for index, configured_spec in enumerate(configured_specs or [{}], start=1):
                suffix = "" if index == 1 else f"-{index}"
                source_slug = configured_spec.get("slug") or f"{module_slug}-command-adventure{suffix}"
                source_to_module[source_slug] = module_slug

        level_to_module = {
            spec["slug"]: (
                source_to_module.get(spec.get("adventure", ""))
                or usage_to_module.get(spec["usage"])
            )
            for spec in ADVENTURE_LEVELS
        }

        for scenario in CHALLENGES:
            challenge_module = scenario.get("module")
            challenge_order = module_order.get(challenge_module, 1 << 30)
            for level_spec in scenario.get("levels", []):
                difficulty = level_spec.get("difficulty")
                used_levels = list(level_spec.get("uses_adventure_levels") or [])
                if not used_levels:
                    errors.append(
                        f"{scenario.get('slug')}/{difficulty}: missing uses_adventure_levels contract"
                    )
                    continue
                for level_slug in used_levels:
                    level_module = level_to_module.get(level_slug)
                    if not level_module:
                        errors.append(
                            f"{scenario.get('slug')}/{difficulty}: unknown Adventure level dependency {level_slug!r}"
                        )
                        continue
                    if module_order.get(level_module, 1 << 30) > challenge_order:
                        errors.append(
                            f"{scenario.get('slug')}/{difficulty}: uses {level_slug!r} before its Adventure chapter"
                        )

                for variant_spec in level_spec.get("variants", []):
                    initial = variant_spec.get("initial_state_template") or {}
                    remote_fixture = initial.get("remote_fixtures") or {}
                    has_history = bool(initial.get("commits")) or bool(
                        isinstance(remote_fixture, dict) and remote_fixture.get("commits")
                    )
                    target = variant_spec.get("target_state_template") or {}
                    creates_first_history = (
                        challenge_order == 1
                        and bool(target.get("commits"))
                        and any(
                            command.startswith(("git init", "git clone", "git commit"))
                            for command in variant_spec.get("solution_commands_template") or []
                        )
                    )
                    if not has_history and not creates_first_history:
                        errors.append(
                            f"{scenario.get('slug')}/{difficulty}/{variant_spec.get('case_id')}: "
                            "Challenge variants must start from history or create the repository's first history"
                        )
                    eval_spec = variant_spec.get("evaluation_spec_template") or {}
                    contract = eval_spec.get("curriculum_contract") or {}
                    dag_transition = contract.get("dag_transition") or {}
                    if (
                        contract.get("challenge_type") != "scenario_graph_transition"
                        or not dag_transition
                    ):
                        errors.append(
                            f"{scenario.get('slug')}/{difficulty}/{variant_spec.get('case_id')}: "
                            "missing curriculum_contract.dag_transition"
                        )

    def _validate_variant(self, *, variant, errors: list[str]) -> None:
        domain = "challenge" if hasattr(variant, "trial_id") else "adventure"
        label = f"{domain}:{self._level_slug(variant)}/{variant.slug}"
        required_fields = {
            "initial_state": variant.initial_state,
            "target_state": variant.target_state,
            "evaluation_spec": variant.evaluation_spec,
            "solution_commands": variant.solution_commands,
        }
        for field, value in required_fields.items():
            if not value:
                errors.append(f"{label}: missing {field}")

        simulator = RepositoryStateSimulator()
        final_state = simulator.normalize_state(variant.target_state)
        executed_commands = list(variant.solution_commands or [])
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
            errors.append(
                f"{label}: official solution does not satisfy evaluation_spec: {outcome.summary}"
            )

        visualization = RepositoryVisualizationService().snapshot(final_state)
        if visualization.get("schema_version") != 2 or "commit_dag" not in visualization:
            errors.append(f"{label}: repository visualization is missing")

    def _level_slug(self, variant) -> str:
        owner = (
            getattr(variant, "wave", None)
            or getattr(variant, "level", None)
            or getattr(variant, "trial", None)
        )
        return getattr(owner, "slug", "") or str(getattr(owner, "id", ""))

    def _level_name(self, level) -> str:
        if isinstance(level, AdventureWave):
            return f"{level.level.slug}/{level.slug}"
        if isinstance(level, AdventureLevel):
            return level.slug
        return f"{level.challenge_level.slug}/{level.difficulty}"
