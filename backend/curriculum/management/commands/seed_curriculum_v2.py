from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from adventures.models import AdventureQuest, AdventureVariant, CommandAdventure
from challenges.models import Challenge, ChallengeQuest, ChallengeVariant
from curriculum.curriculum_v2.adventures import COMMAND_DRILL_ADVENTURES
from curriculum.curriculum_v2.command_topics import COMMAND_TOPICS
from curriculum.curriculum_v2.drills import COMMAND_DRILLS
from curriculum.curriculum_v2.foundations import FOUNDATIONS
from curriculum.curriculum_v2.modules import MODULES
from curriculum.curriculum_v2.workflows import WORKFLOW_SCENARIOS
from curriculum.models import (
    CommandForm,
    CommandSkill,
    ConceptPage,
    Storey,
    default_chest_rewards,
)
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from practice.builders import StaticQuestVariantBuilder
from practice.visualization import RepositoryVisualizationService
from simulator.services import RepositoryStateSimulator


def _find_prerequisite_cycle(graph: dict[int, list[int]]) -> list[int] | None:
    """Return one cycle (as a node path) in the prerequisite graph, or None."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    stack: list[int] = []

    def visit(node: int) -> list[int] | None:
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, ()):
            if color.get(nxt, WHITE) == GRAY:
                return stack[stack.index(nxt):] + [nxt]
            if color.get(nxt, WHITE) == WHITE:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for node in graph:
        if color[node] == WHITE:
            found = visit(node)
            if found:
                return found
    return None


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
        # Seed-spec dict keys ("module", "usage", "levels", ...) are the frozen
        # authoring format of curriculum_v2; only the ORM names are normalized.
        self.supported_form_keys = {spec["usage"] for spec in COMMAND_DRILLS}
        self.published_storey_slugs = self._published_storey_slugs()
        self._seed_foundations()
        storeys = self._seed_storeys()
        forms = self._seed_command_skills(storeys)
        self._seed_adventure_quests(forms)
        self._seed_command_adventures(storeys)
        self._seed_challenges(storeys)
        if options.get("validate"):
            self._validate_curriculum()
        self.stdout.write(self.style.SUCCESS("Seeded v2 curriculum."))

    def _seed_foundations(self) -> None:
        live_slugs = []
        for index, spec in enumerate(FOUNDATIONS, start=1):
            live_slugs.append(spec["slug"])
            ConceptPage.objects.update_or_create(
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
        ConceptPage.objects.exclude(slug__in=live_slugs).update(is_published=False)

    def _seed_storeys(self) -> dict[str, Storey]:
        storeys = {}
        live_slugs = []
        for index, spec in enumerate(MODULES, start=1):
            live_slugs.append(spec["slug"])
            is_published = spec["slug"] in self.published_storey_slugs
            storey, _ = Storey.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "number": spec["number"],
                    "title": spec["title"],
                    "description": spec["description"],
                    "sort_order": index,
                    "is_published": is_published,
                    "chest_rewards": spec.get("chest_rewards", default_chest_rewards()),
                },
            )
            storeys[spec["slug"]] = storey
        Storey.objects.exclude(slug__in=live_slugs).update(is_published=False)
        return storeys

    def _seed_command_adventures(self, storeys: dict[str, Storey]) -> None:
        """One CommandAdventure per Storey that has published adventure quests."""
        live_ids = []
        for index, (slug, storey) in enumerate(storeys.items(), start=1):
            has_quests = AdventureQuest.objects.filter(
                command_form__command_skill__storey=storey, is_published=True
            ).exists()
            if not has_quests:
                continue
            configured = COMMAND_DRILL_ADVENTURES.get(slug, {})
            adventure, _ = CommandAdventure.objects.update_or_create(
                storey=storey,
                defaults={
                    "slug": f"{slug}-command-adventure",
                    "title": configured.get("title") or f"{storey.title} Adventure",
                    "description": configured.get("description") or storey.description,
                    "sort_order": index,
                    "is_published": storey.is_published,
                },
            )
            live_ids.append(adventure.id)
        CommandAdventure.objects.exclude(id__in=live_ids).update(is_published=False)

    def _seed_command_skills(self, storeys: dict[str, Storey]) -> dict[str, CommandForm]:
        forms = {}
        live_skill_ids = []
        for skill_index, spec in enumerate(COMMAND_TOPICS, start=1):
            storey = storeys[spec["module"]]
            form_keys = {
                f"{spec['slug']}/{form_spec['slug']}"
                for form_spec in spec.get("usages", [])
            }
            skill_is_published = bool(storey.is_published and form_keys.intersection(self.supported_form_keys))
            skill, _ = CommandSkill.objects.update_or_create(
                storey=storey,
                slug=spec["slug"],
                defaults={
                    "base_command": spec["base_command"],
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "mental_model": spec.get("mental_model", {}),
                    "command_preview": self._preview(spec["title"], spec["summary"]),
                    "sort_order": skill_index,
                    "is_published": skill_is_published,
                },
            )
            live_skill_ids.append(skill.id)
            live_form_ids = []
            for form_index, form_spec in enumerate(spec.get("usages", []), start=1):
                form_key = f"{spec['slug']}/{form_spec['slug']}"
                form_is_published = skill_is_published and form_key in self.supported_form_keys
                form, _ = CommandForm.objects.update_or_create(
                    command_skill=skill,
                    slug=form_spec["slug"],
                    defaults={
                        "usage_form": form_spec["usage_form"],
                        "label": form_spec["label"],
                        "summary": form_spec.get("summary", ""),
                        "command_preview": self._preview(
                            form_spec["usage_form"],
                            form_spec.get("summary") or spec["summary"],
                            syntax=form_spec["usage_form"],
                        ),
                        "sort_order": form_index,
                        "is_published": form_is_published,
                    },
                )
                forms[form_key] = form
                live_form_ids.append(form.id)
            CommandForm.objects.filter(command_skill=skill).exclude(id__in=live_form_ids).update(
                is_published=False
            )
        CommandSkill.objects.exclude(id__in=live_skill_ids).update(is_published=False)
        return forms

    def _seed_adventure_quests(self, forms: dict[str, CommandForm]) -> None:
        builder = StaticQuestVariantBuilder()
        live_quest_ids = []
        quests_by_slug: dict[str, AdventureQuest] = {}
        for index, spec in enumerate(COMMAND_DRILLS, start=1):
            form = forms[spec["usage"]]
            quest, _ = AdventureQuest.objects.update_or_create(
                command_form=form,
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "required_successful_attempts": spec["required_successful_attempts"],
                    "min_counted_commands": spec["min_counted_commands"],
                    "max_counted_commands": spec["max_counted_commands"],
                    "scenario_context": spec["scenario_context"],
                    "objective_checks": spec.get("objective_checks", []),
                    "sort_order": index,
                    "is_published": True,
                },
            )
            live_quest_ids.append(quest.id)
            quests_by_slug[spec["slug"]] = quest
            self._sync_variants(quest=quest, variant_specs=spec["variants"], builder=builder)
        # Second pass: wire the explicit prerequisite graph now that every quest
        # exists. Prerequisites are authored as a list of quest slugs.
        for spec in COMMAND_DRILLS:
            quest = quests_by_slug[spec["slug"]]
            try:
                prereqs = [quests_by_slug[slug] for slug in spec.get("prerequisites", [])]
            except KeyError as missing:
                raise CommandError(
                    f"Adventure quest {spec['slug']!r} lists unknown prerequisite {missing}."
                )
            quest.prerequisites.set(prereqs)
        AdventureQuest.objects.exclude(id__in=live_quest_ids).update(is_published=False)

    def _seed_challenges(self, storeys: dict[str, Storey]) -> None:
        builder = StaticQuestVariantBuilder()
        live_challenge_ids = []
        for index, spec in enumerate(WORKFLOW_SCENARIOS, start=1):
            challenge, _ = Challenge.objects.update_or_create(
                storey=storeys[spec["module"]],
                slug=spec["slug"],
                defaults={
                    "title": spec["title"],
                    "summary": spec["summary"],
                    "narrative": spec["narrative"],
                    "sort_order": index,
                    "is_published": storeys[spec["module"]].is_published,
                },
            )
            live_challenge_ids.append(challenge.id)
            live_quest_ids = []
            for quest_spec in spec.get("levels", []):
                quest, _ = ChallengeQuest.objects.update_or_create(
                    challenge=challenge,
                    difficulty=quest_spec["difficulty"],
                    defaults={
                        "required_successful_attempts": quest_spec["required_successful_attempts"],
                        "min_counted_commands": quest_spec["min_counted_commands"],
                        "max_counted_commands": quest_spec["max_counted_commands"],
                        "scenario_context": quest_spec["scenario_context"],
                        "is_published": challenge.is_published,
                    },
                )
                live_quest_ids.append(quest.id)
                self._sync_variants(
                    quest=quest,
                    variant_specs=quest_spec["variants"],
                    builder=builder,
                )
            ChallengeQuest.objects.filter(challenge=challenge).exclude(id__in=live_quest_ids).update(
                is_published=False
            )
        Challenge.objects.exclude(id__in=live_challenge_ids).update(is_published=False)

    def _sync_variants(self, *, quest, variant_specs: list[dict], builder: StaticQuestVariantBuilder) -> None:
        live_ids = []
        for index, variant_spec in enumerate(variant_specs, start=1):
            case = {"case_id": variant_spec["case_id"]}
            variant = builder.build(quest=quest, template=variant_spec, case=case, index=index)
            filters = {"semantic_key": variant.semantic_key}
            if isinstance(quest, AdventureQuest):
                variant_model = AdventureVariant
                filters["adventure_quest"] = quest
            else:
                variant_model = ChallengeVariant
                filters["challenge_quest"] = quest
            saved, _ = variant_model.objects.update_or_create(
                **filters,
                defaults={
                    "slug": variant.slug,
                    "label": variant.label,
                    "initial_state": variant.initial_state,
                    "evaluation_spec": variant.evaluation_spec,
                    "target_state": variant.target_state,
                    "solution_commands": variant.solution_commands,
                    "case_id": variant.case_id,
                    "parameter_context": variant.parameter_context,
                    "scenario_context": variant.scenario_context,
                    "hint_set": variant.hint_set,
                    "scaffold_policy": variant.scaffold_policy,
                    # Command budget lives on the parent quest, not the
                    # variant — all variants of a quest share the same budget.
                    "is_published": True,
                },
            )
            live_ids.append(saved.id)
        if isinstance(quest, AdventureQuest):
            AdventureVariant.objects.filter(adventure_quest=quest).exclude(id__in=live_ids).update(
                is_published=False
            )
        else:
            ChallengeVariant.objects.filter(challenge_quest=quest).exclude(id__in=live_ids).update(
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

    def _published_storey_slugs(self) -> set[str]:
        form_to_storey = {}
        for skill_spec in COMMAND_TOPICS:
            for form_spec in skill_spec.get("usages", []):
                form_to_storey[f"{skill_spec['slug']}/{form_spec['slug']}"] = skill_spec["module"]
        command_storeys = {
            form_to_storey[spec["usage"]]
            for spec in COMMAND_DRILLS
            if spec["usage"] in form_to_storey
        }
        challenge_storeys = {
            spec["module"]
            for spec in WORKFLOW_SCENARIOS
            if spec["module"] in command_storeys
        }
        return command_storeys | challenge_storeys

    def _validate_curriculum(self) -> None:
        errors: list[str] = []
        storeys = list(Storey.objects.filter(is_published=True).order_by("sort_order", "number"))
        for storey in storeys:
            skills = list(
                CommandSkill.objects.filter(storey=storey, is_published=True).order_by("sort_order", "id")
            )
            if not skills:
                errors.append(f"{storey.slug}: missing command skills")
                continue
            for skill in skills:
                self._validate_command_skill(skill=skill, errors=errors)

        for challenge in Challenge.objects.filter(is_published=True):
            quests = list(challenge.challenge_quests.filter(is_published=True))
            difficulties = {quest.difficulty for quest in quests}
            if difficulties != {"easy", "medium", "hard"}:
                errors.append(f"{challenge.slug}: challenges must publish Easy, Medium, and Hard")
            for quest in quests:
                self._validate_quest_variants(quest=quest, errors=errors)

        self._validate_prerequisites(errors=errors)

        if errors:
            raise CommandError("Curriculum validation failed:\n" + "\n".join(f"- {error}" for error in errors))
        self.stdout.write(self.style.SUCCESS("Validated v2 curriculum."))

    def _validate_prerequisites(self, *, errors: list[str]) -> None:
        """Adventure prerequisite graph must be a DAG, and every prerequisite must
        be published, in the same adventure, and precede its dependent in order."""
        ordered = list(
            AdventureQuest.objects.filter(is_published=True)
            .order_by("command_form__command_skill__sort_order", "command_form__sort_order", "sort_order", "id")
            .prefetch_related("prerequisites")
            .select_related("command_form__command_skill")
        )
        position = {quest.id: index for index, quest in enumerate(ordered)}
        graph: dict[int, list[int]] = {}
        for quest in ordered:
            prereqs = list(quest.prerequisites.all())
            graph[quest.id] = [pre.id for pre in prereqs]
            for pre in prereqs:
                if not pre.is_published:
                    errors.append(f"{quest.slug}: prerequisite {pre.slug} is not published")
                elif pre.command_form.command_skill.storey_id != quest.command_form.command_skill.storey_id:
                    errors.append(f"{quest.slug}: prerequisite {pre.slug} is in a different adventure")
                elif position.get(pre.id, 1 << 30) >= position[quest.id]:
                    errors.append(f"{quest.slug}: prerequisite {pre.slug} must precede it in sort order")
        cycle = _find_prerequisite_cycle(graph)
        if cycle:
            slugs = {q.id: q.slug for q in ordered}
            errors.append("prerequisite graph has a cycle: " + " -> ".join(slugs[i] for i in cycle))

    def _validate_command_skill(self, *, skill: CommandSkill, errors: list[str]) -> None:
        if not skill.base_command:
            errors.append(f"{skill.slug}: command skill is missing a base command")
        forms = list(skill.command_forms.filter(is_published=True).order_by("sort_order", "id"))
        if not forms:
            errors.append(f"{skill.slug}: command skill has no published forms")
            return
        for form in forms:
            quests = list(form.adventure_quests.filter(is_published=True).order_by("sort_order", "id"))
            if not quests:
                errors.append(f"{skill.slug}/{form.slug}: published form has no adventure quests")
                continue
            for quest in quests:
                self._validate_quest_variants(quest=quest, errors=errors)

    def _validate_quest_variants(self, *, quest, errors: list[str]) -> None:
        if isinstance(quest, AdventureQuest):
            variants = list(quest.adventure_variants.filter(is_published=True).order_by("semantic_key", "id"))
        else:
            variants = list(quest.challenge_variants.filter(is_published=True).order_by("semantic_key", "id"))
        if not variants:
            errors.append(f"{self._quest_name(quest)}: published practice item has no variants")
            return
        # Mastery reviews must vary the scenario: a quest needs at least as many
        # variants as the masteries it demands, or repeated reviews show the same
        # screen. Warn (not error) so under-authored content still seeds + runs.
        if isinstance(quest, AdventureQuest) and len(variants) < quest.required_successful_attempts:
            self.stdout.write(
                self.style.WARNING(
                    f"{self._quest_name(quest)}: {len(variants)} variant(s) for "
                    f"{quest.required_successful_attempts} required masteries; "
                    "reviews will repeat scenarios until more variants are authored."
                )
            )
        for variant in variants:
            self._validate_variant(variant=variant, errors=errors)

    def _validate_variant(self, *, variant, errors: list[str]) -> None:
        domain = "command_adventure" if hasattr(variant, "adventure_quest_id") else "challenge"
        label = f"{domain}:{self._quest_slug(variant)}/{variant.slug}"
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

        visualization = RepositoryVisualizationService().snapshot(final_state)
        if visualization.get("schema_version") != 2 or "commit_dag" not in visualization:
            errors.append(f"{label}: repository visualization is missing")

    def _quest_slug(self, variant) -> str:
        if getattr(variant, "adventure_quest_id", None):
            return variant.adventure_quest.slug
        quest = variant.challenge_quest
        return f"{quest.challenge.slug}/{quest.difficulty}"

    def _quest_name(self, quest) -> str:
        if isinstance(quest, AdventureQuest):
            return quest.slug
        return f"{quest.challenge.slug}/{quest.difficulty}"
