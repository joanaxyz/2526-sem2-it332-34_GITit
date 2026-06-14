from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.utils.text import slugify

from authoring.models import ContentDefinition, ContentKind, PublishedContentRuntime
from authoring.schemas import content_levels
from challenges.models import Challenge, ChallengeLevel, ChallengeVariant
from command_adventures.models import AdventureLevel, AdventureVariant, CommandAdventure
from curriculum.models import (
    TOME_PLACEMENTS,
    CommandForm,
    CommandSkill,
    Storey,
    Tome,
    default_chest_rewards,
)
from simulator.services import RepositoryStateSimulator

HIDDEN_STOREY_NUMBER_BASE = 900_000
# Storey-grouped content shares one runtime storey, numbered in a distinct range
# from the per-content (storeyless/legacy) hidden storeys above.
GROUPED_STOREY_NUMBER_BASE = 800_000


class ContentRuntimeCompiler:
    def __init__(self) -> None:
        self.simulator = RepositoryStateSimulator()

    @transaction.atomic
    def compile(self, *, content: ContentDefinition) -> PublishedContentRuntime:
        signature = self._signature(content.definition)
        runtime = getattr(content, "runtime", None)
        if runtime and runtime.definition_signature == signature:
            return runtime
        storey = self._runtime_storey(content)
        command_adventure = challenge = tome = None
        if content.kind == ContentKind.ADVENTURE:
            command_adventure = self._compile_adventure(content, storey)
        elif content.kind == ContentKind.CHALLENGE:
            challenge = self._compile_challenge(content, storey)
        elif content.kind == ContentKind.TOME:
            tome = self._compile_tome(content, storey)
        runtime, _created = PublishedContentRuntime.objects.update_or_create(
            content_definition=content,
            defaults={
                "storey": storey,
                "command_adventure": command_adventure,
                "challenge": challenge,
                "tome": tome,
                "definition_signature": signature,
            },
        )
        return runtime

    def _runtime_storey(self, content: ContentDefinition) -> Storey:
        # Content authored INTO a storey shares one runtime storey carrying the
        # storey's settings (reward checkpoints + rosters). Storeyless/legacy
        # content keeps a per-content hidden storey reading from its definition.
        if content.storey_id is not None:
            storey = content.storey
            number = GROUPED_STOREY_NUMBER_BASE + storey.id
            slug = f"ugc-storey-{storey.id}"
            chest_rewards = storey.chest_rewards or default_chest_rewards()
            mob_roster = storey.mob_roster or []
            boss_roster = storey.boss_roster or []
            title = storey.title
            description = storey.summary
        else:
            definition = content.definition or {}
            number = HIDDEN_STOREY_NUMBER_BASE + content.id
            slug = f"ugc-{content.kind}-{content.id}"
            chest_rewards = definition.get("chest_rewards")
            if not isinstance(chest_rewards, list) or not chest_rewards:
                chest_rewards = default_chest_rewards()
            mob_roster = definition.get("mob_roster") if isinstance(definition.get("mob_roster"), list) else []
            boss_roster = definition.get("boss_roster") if isinstance(definition.get("boss_roster"), list) else []
            title = content.title
            description = content.summary
        # GitCoin progress chests are reserved for admin-authored / official
        # towers. Player-authored custom towers never grant coins, no matter
        # what reward checkpoints were entered — strip them at compile time so
        # the runtime storey drops nothing.
        if not self._author_grants_coins(content):
            chest_rewards = []
        return Storey.objects.update_or_create(
            slug=slug,
            defaults={
                "number": number,
                "title": title,
                "description": description,
                "is_published": False,
                "sort_order": number,
                "chest_rewards": chest_rewards,
                "mob_roster": mob_roster,
                "boss_roster": boss_roster,
            },
        )[0]

    @staticmethod
    def _author_grants_coins(content: ContentDefinition) -> bool:
        """Only admin authors (staff/superuser), or unowned/system content,
        produce coin-bearing storeys. Regular players' custom towers do not."""
        owner = content.storey.owner if content.storey_id else content.owner
        if owner is None:
            return True
        return bool(owner.is_staff or owner.is_superuser)

    def _compile_adventure(self, content: ContentDefinition, storey: Storey) -> CommandAdventure:
        definition = content.definition or {}
        adventure_defaults = {
            "storey": storey,
            "title": content.title,
            "description": content.summary,
            "is_published": True,
            "sort_order": 0,
            "source_content_definition": content,
        }
        # Authored mastery threshold that unlocks the storey's Challenge — the
        # storey's value wins, falling back to a per-content definition value.
        pass_bar = content.storey.pass_bar_fraction if content.storey_id else definition.get("pass_bar_fraction")
        if isinstance(pass_bar, (int, float)) and 0 < float(pass_bar) <= 1:
            adventure_defaults["pass_bar_fraction"] = float(pass_bar)
        adventure, _created = CommandAdventure.objects.update_or_create(
            slug=f"ugc-adventure-{content.id}",
            defaults=adventure_defaults,
        )
        levels = content_levels(content.definition)
        base_command = content.command_family or str(content.definition.get("base_command") or "git")
        skill = CommandSkill.objects.update_or_create(
            storey=storey,
            slug=slugify(base_command) or "git",
            defaults={
                "base_command": base_command,
                "title": content.title,
                "summary": content.summary,
                "is_published": True,
                "sort_order": 0,
            },
        )[0]
        form = CommandForm.objects.update_or_create(
            command_skill=skill,
            slug="authored",
            defaults={
                "usage_form": base_command,
                "label": content.title,
                "summary": content.summary,
                "is_published": True,
                "sort_order": 0,
            },
        )[0]
        self._replace_adventure_levels(form=form, levels=levels)
        return adventure

    def _replace_adventure_levels(self, *, form: CommandForm, levels: list[dict[str, Any]]) -> None:
        AdventureLevel.objects.filter(command_form=form).delete()
        for index, authored in enumerate(levels):
            budget = authored.get("command_budget") or {}
            level = AdventureLevel.objects.create(
                command_form=form,
                slug=authored["slug"],
                title=authored["title"],
                required_successful_attempts=int(authored.get("required_successful_attempts") or 1),
                min_counted_commands=int(budget.get("min_counted_commands") or authored.get("min_counted_commands") or 1),
                max_counted_commands=int(budget.get("max_counted_commands") or authored.get("max_counted_commands") or 8),
                evaluation_spec=authored.get("evaluation_spec") or {"completion_policy": {"mode": "state_hash"}},
                scenario_context=authored.get("scenario_context") or {},
                objective_checks=authored.get("objective_checks") or [],
                encounter_spec=authored.get("encounter_spec") or [],
                is_published=True,
                sort_order=index,
            )
            self._create_adventure_variant(level=level, authored=authored, index=index)

    def _create_adventure_variant(self, *, level: AdventureLevel, authored: dict[str, Any], index: int) -> AdventureVariant:
        initial_state = self.simulator.normalize_state(authored.get("initial_state") or {})
        solution_commands = list(authored.get("solution_commands") or [])
        target_state = self._target_state(initial_state, solution_commands)
        return AdventureVariant.objects.create(
            adventure_level=level,
            slug=authored.get("variant_slug") or authored["slug"],
            label=authored.get("variant_label") or "Authored",
            initial_state=initial_state,
            evaluation_spec=level.evaluation_spec,
            target_state=target_state,
            solution_commands=solution_commands,
            case_id=authored.get("case_id") or f"{level.slug}-{index}",
            semantic_key=self._semantic_key(level.slug, authored),
            parameter_context=authored.get("parameter_context") or {},
            scenario_context=authored.get("scenario_context") or {},
            hint_set=authored.get("hint_set") or [],
            scaffold_policy=authored.get("scaffold_policy") or {},
            is_published=True,
        )

    def _compile_challenge(self, content: ContentDefinition, storey: Storey) -> Challenge:
        challenge, _created = Challenge.objects.update_or_create(
            storey=storey,
            slug=f"ugc-challenge-{content.id}",
            defaults={
                "title": content.title,
                "summary": content.summary,
                "narrative": content.definition.get("narrative", content.summary),
                "is_published": True,
                "sort_order": 0,
                "source_content_definition": content,
            },
        )
        ChallengeLevel.objects.filter(challenge=challenge).delete()
        for index, authored in enumerate(content_levels(content.definition)):
            budget = authored.get("command_budget") or {}
            level = ChallengeLevel.objects.create(
                challenge=challenge,
                difficulty=authored.get("difficulty") or content.difficulty or "easy",
                required_successful_attempts=int(authored.get("required_successful_attempts") or 1),
                min_counted_commands=int(budget.get("min_counted_commands") or authored.get("min_counted_commands") or 1),
                max_counted_commands=int(budget.get("max_counted_commands") or authored.get("max_counted_commands") or 8),
                evaluation_spec=authored.get("evaluation_spec") or {"completion_policy": {"mode": "state_hash"}},
                scenario_context=authored.get("scenario_context") or {},
                boss_spec=authored.get("boss_spec") or {},
                is_published=True,
            )
            self._create_challenge_variant(level=level, authored=authored, index=index)
        return challenge

    def _create_challenge_variant(self, *, level: ChallengeLevel, authored: dict[str, Any], index: int) -> ChallengeVariant:
        initial_state = self.simulator.normalize_state(authored.get("initial_state") or {})
        solution_commands = list(authored.get("solution_commands") or [])
        target_state = self._target_state(initial_state, solution_commands)
        return ChallengeVariant.objects.create(
            challenge_level=level,
            slug=authored.get("variant_slug") or authored["slug"],
            label=authored.get("variant_label") or "Authored",
            initial_state=initial_state,
            evaluation_spec=level.evaluation_spec,
            target_state=target_state,
            solution_commands=solution_commands,
            case_id=authored.get("case_id") or f"{level.challenge.slug}-{index}",
            semantic_key=self._semantic_key(level.challenge.slug, authored),
            parameter_context=authored.get("parameter_context") or {},
            scenario_context=authored.get("scenario_context") or {},
            hint_set=authored.get("hint_set") or [],
            scaffold_policy=authored.get("scaffold_policy") or {},
            command_budget={
                "min_counted_commands": level.min_counted_commands,
                "max_counted_commands": level.max_counted_commands,
            },
            is_published=True,
        )

    def _compile_tome(self, content: ContentDefinition, storey: Storey) -> Tome:
        definition = content.definition or {}
        placement = definition.get("placement")
        valid_placements = {value for value, _label in TOME_PLACEMENTS}
        if placement not in valid_placements:
            placement = "above_adventure"
        return Tome.objects.update_or_create(
            storey=storey,
            slug=f"ugc-tome-{content.id}",
            defaults={
                "title": content.title,
                "summary": content.summary,
                "pages": definition.get("pages") or [],
                "placement": placement,
                "is_published": True,
                "sort_order": 0,
                "source_content_definition": content,
            },
        )[0]

    def _target_state(self, initial_state: dict, solution_commands: list[str]) -> dict:
        state = self.simulator.normalize_state(initial_state)
        for command in solution_commands:
            state = self.simulator.normalize_state(self.simulator.process(state, command).state)
        return state

    def _signature(self, definition: dict) -> str:
        return hashlib.sha256(
            json.dumps(definition, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()

    def _semantic_key(self, slug: str, authored: dict[str, Any]) -> str:
        return hashlib.sha256(
            json.dumps({"slug": slug, "authored": authored}, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:40]
