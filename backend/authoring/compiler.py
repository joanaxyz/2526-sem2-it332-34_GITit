from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import transaction
from django.utils.text import slugify

from adventures.models import AdventureLevel, AdventureVariant, CommandAdventure
from authoring.models import ContentDefinition, ContentKind, PublishedContentRuntime
from authoring.schemas import content_levels
from challenges.models import Challenge, ChallengeLevel, ChallengeVariant
from curriculum.models import CommandForm, CommandSkill, Storey, Tome
from simulator.services import RepositoryStateSimulator

HIDDEN_STOREY_NUMBER_BASE = 900_000


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
        number = HIDDEN_STOREY_NUMBER_BASE + content.id
        slug = f"ugc-{content.kind}-{content.id}"
        return Storey.objects.update_or_create(
            slug=slug,
            defaults={
                "number": number,
                "title": content.title,
                "description": content.summary,
                "is_published": False,
                "sort_order": number,
                "chest_rewards": [],
            },
        )[0]

    def _compile_adventure(self, content: ContentDefinition, storey: Storey) -> CommandAdventure:
        adventure, _created = CommandAdventure.objects.update_or_create(
            slug=f"ugc-adventure-{content.id}",
            defaults={
                "storey": storey,
                "title": content.title,
                "description": content.summary,
                "is_published": True,
                "sort_order": 0,
                "source_content_definition": content,
            },
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
        return Tome.objects.update_or_create(
            storey=storey,
            slug=f"ugc-tome-{content.id}",
            defaults={
                "title": content.title,
                "summary": content.summary,
                "pages": content.definition.get("pages") or [],
                "placement": "above_adventure",
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
