"""Compose a Squire's Drill from a level's own authored command forms.

The drill is the missing rung between reading a chapter and typing into a
live terminal: short recall practice on exactly the commands the level will
demand. Nothing here is hand-authored per level - every question is derived
from ``CommandForm.usage_form`` / ``label`` and the level's authored
solution commands, so a level gets a correct drill the moment it is seeded.

The composer is pure and deterministic: it emits option *pools*, never a
shuffled question. The client shuffles, so repeat sessions vary without the
server holding session state.

Distractor policy is the pedagogy. A wrong option is always another real
command form - siblings of the same command first (``git add -A`` against
``git add -p``), then the level's other commands, then the chapter's. That
makes every wrong answer explainable with authored text instead of a
generic "incorrect", and it drills the confusions that actually block
people mid-adventure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from django.db.models import Q

from adventures.models import AdventureLevel
from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM
from curriculum.library_preview import command_preview_syntax_for_command
from curriculum.models import CommandForm

# A multiple-choice question is only fair with real alternatives; below this
# the rung is dropped for that card rather than padded with filler.
MIN_DISTRACTORS = 2
MAX_DISTRACTORS = 3
MAX_BANK_TOKENS = 8
# Two steps is a real question for this audience - "add then commit" is the
# order beginners invert - but past six, ordering chips is a memory test
# rather than a lesson about the shape of the work.
MIN_SEQUENCE_STEPS = 2
MAX_SEQUENCE_STEPS = 6
_TIER_ORDER = {DIFFICULTY_EASY: 0, DIFFICULTY_MEDIUM: 1, DIFFICULTY_HARD: 2}


@dataclass
class DrillCatalog:
    """The published command catalog, read once.

    Composing a drill needs the whole catalog twice - for distractors and
    for resolving authored solutions - and seeding runs it over every
    level. Re-reading a few hundred rows per level is invisible on SQLite
    and costs minutes against a pooled Postgres, so the seeder loads this
    once and threads it through.
    """

    forms: list[CommandForm] = field(default_factory=list)
    by_match_key: dict[str, list[CommandForm]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> DrillCatalog:
        forms = list(
            CommandForm.objects.filter(is_published=True)
            .select_related("command_skill")
            .order_by("command_skill__sort_order", "sort_order", "id")
        )
        by_match_key: dict[str, list[CommandForm]] = {}
        for form in forms:
            by_match_key.setdefault(_match_key(form.usage_form), []).append(form)
        return cls(forms=forms, by_match_key=by_match_key)


def form_key(form: CommandForm) -> str:
    """The catalog usage key ("git-add/patch") - stable across reseeds."""
    return f"{form.command_skill.slug}/{form.slug}"


def token_kind(token: str) -> str:
    if token.startswith("-"):
        return "flag"
    if token.startswith("<"):
        return "placeholder"
    return "word"


def tokenize(usage_form: str) -> list[str]:
    return str(usage_form).split()


_SLOT = "▫"


def _match_key(command: str) -> str:
    """Compare two command shapes the way Git would read them.

    Two vocabularies have to meet here. The command library renders a
    sample message as ``"message"`` and a path as ``<path>``; the catalog
    writes the same slots as ``<message>`` and ``<file>``. The slot *name*
    is documentation, not meaning, so every filled-in value collapses to a
    single placeholder mark and only the literal words and flags - the
    parts that actually change what Git does - are compared.
    """
    text = " ".join(str(command).split())
    text = re.sub(r"<[^>]*>", _SLOT, text)
    text = re.sub(r"\"[^\"]*\"|'[^']*'", _SLOT, text)
    return text.lower()


def _prefix_keys(key: str) -> list[str]:
    """The key, then progressively shorter commands it specialises.

    ``git commit --amend -m <slot>`` is the taught move ``git commit
    --amend`` with a message attached; when the catalog only carries the
    shorter form, that is still the right card to drill. Dropping trailing
    tokens finds it without inventing a form that was never authored.
    """
    tokens = key.split()
    return [" ".join(tokens[:size]) for size in range(len(tokens), 1, -1)]


def _level_waves(level: AdventureLevel) -> list:
    """Published waves, tier order first, then the plain-wave flow.

    Filtered in Python on purpose: both the solution scan and the finale
    picker need this same tree, and querysets built with ``.filter()``
    ignore any prefetch the caller set up. Reading ``.all()`` lets the
    seeder prefetch the whole catalog's waves in a couple of queries
    instead of a handful per level.
    """
    tiers = sorted(
        (tier for tier in level.tiers.all() if tier.is_published),
        key=lambda tier: _TIER_ORDER.get(tier.difficulty, 99),
    )
    waves = [wave for tier in tiers for wave in tier.waves.all() if wave.is_published]
    waves += sorted(
        (wave for wave in level.waves.all() if wave.is_published),
        key=lambda wave: (wave.sort_order, wave.id),
    )
    return waves


def _published_variants(wave) -> list:
    return [variant for variant in wave.variants.all() if variant.is_published]


def _solution_commands(waves: list) -> list[str]:
    """Every authored solution command for the level, in the order taught."""
    commands: list[str] = []
    for wave in waves:
        for variant in _published_variants(wave):
            commands.extend(str(step) for step in variant.solution_commands if str(step).strip())
    return commands


def _forms_from_solutions(
    level: AdventureLevel, catalog: DrillCatalog, waves: list | None = None
) -> list[CommandForm]:
    """Recover a level's taught forms from what its solutions actually type.

    The seeders attach ``command_forms`` to a level and its waves, but that
    wiring is data, and a database seeded before it existed has levels whose
    solutions are full of Git yet whose form list is empty. Rather than
    showing an empty drill on exactly the levels that need one, resolve each
    authored command through the command library's own
    "concrete command -> taught syntax" mapping and look that syntax up in
    the published catalog. Same derivation the legacy seeder does at write
    time, done at read time so the drill cannot be out of step with it.
    """
    commands = _solution_commands(waves if waves is not None else _level_waves(level))
    if not commands:
        return []
    wanted: list[str] = []
    for command in commands:
        key = _match_key(command_preview_syntax_for_command(command))
        if key and key not in wanted:
            wanted.append(key)
    if not wanted:
        return []

    def pick(key: str) -> CommandForm | None:
        candidates = catalog.by_match_key.get(key)
        if not candidates:
            return None
        # Forms owned by this level's own chapter win a tie; otherwise the
        # first catalog entry for that syntax stands in.
        for candidate in candidates:
            if candidate.chapter_id == level.chapter_id:
                return candidate
        return candidates[0]

    resolved: list[CommandForm] = []
    seen: set[int] = set()
    for key in wanted:
        match = next(
            (found for candidate in _prefix_keys(key) if (found := pick(candidate)) is not None),
            None,
        )
        if match is not None and match.id not in seen:
            seen.add(match.id)
            resolved.append(match)
    return resolved


def level_command_forms(
    level: AdventureLevel,
    catalog: DrillCatalog | None = None,
    waves: list | None = None,
) -> list[CommandForm]:
    """Every published form the level teaches, whichever tree holds it.

    A level attaches forms directly, and its waves (single-difficulty flow)
    or tier waves (Easy/Medium/Hard flow) attach them again. Reading all
    three keeps the drill correct for both content shapes without asking
    the caller which one this level uses; when none of them is wired, the
    authored solutions are the fallback source of truth.
    """
    attached = list(
        CommandForm.objects.filter(
            Q(adventure_levels=level)
            | Q(adventure_waves__level=level)
            | Q(adventure_level_tier_waves__tier__adventure_level=level),
            is_published=True,
        )
        .select_related("command_skill")
        .distinct()
    )
    return attached or _forms_from_solutions(level, catalog or DrillCatalog.load(), waves)


def _distractor_pool(forms: list[CommandForm], catalog: DrillCatalog) -> list[CommandForm]:
    if not forms:
        return []
    skill_ids = {form.command_skill_id for form in forms}
    chapter_ids = {form.chapter_id for form in forms if form.chapter_id}
    return [
        form
        for form in catalog.forms
        if form.command_skill_id in skill_ids or (form.chapter_id and form.chapter_id in chapter_ids)
    ]


def _rank(candidate: CommandForm, form: CommandForm, level_form_ids: set[int]) -> int:
    """Lower is a better distractor: the closer the confusion, the more the
    question is worth asking."""
    if candidate.command_skill_id == form.command_skill_id:
        return 0
    if candidate.id in level_form_ids:
        return 1
    return 2


def _ranked_pool(
    form: CommandForm,
    pool: list[CommandForm],
    level_form_ids: set[int],
) -> list[CommandForm]:
    """Every other real form, closest confusion first."""
    return sorted(
        (
            candidate
            for candidate in pool
            if candidate.id != form.id and candidate.usage_form and candidate.label
        ),
        key=lambda candidate: (
            _rank(candidate, form, level_form_ids),
            candidate.command_skill.sort_order,
            candidate.sort_order,
            candidate.id,
        ),
    )


def _distractors(form: CommandForm, ranked: list[CommandForm]) -> list[CommandForm]:
    seen_usage = {form.usage_form}
    seen_label = {form.label}
    chosen: list[CommandForm] = []
    for candidate in ranked:
        if candidate.usage_form in seen_usage or candidate.label in seen_label:
            continue
        seen_usage.add(candidate.usage_form)
        seen_label.add(candidate.label)
        chosen.append(candidate)
        if len(chosen) == MAX_DISTRACTORS:
            break
    return chosen


def _slot_options(
    *,
    index: int,
    answer: str,
    form: CommandForm,
    ranked: list[CommandForm],
) -> list[dict]:
    """Same-slot, same-kind tokens from other real forms.

    Options are collected in two passes, and the first pass wins outright
    whenever it can fill the question: a flag borrowed from a *different*
    command (offering ``--stat`` under ``git add ___``) is eliminated on
    sight and its gloss would explain a flag the learner was never choosing
    between. Only a slot with no sibling answers - typically the subcommand
    in ``git ___`` - widens to the rest of the chapter, which is exactly
    where the wider question is the right one.
    """
    kind = token_kind(answer)
    siblings: list[dict] = []
    others: list[dict] = []
    seen = {answer}
    for candidate in ranked:
        candidate_tokens = tokenize(candidate.usage_form)
        if index >= len(candidate_tokens):
            continue
        token = candidate_tokens[index]
        if token in seen or token_kind(token) != kind:
            continue
        seen.add(token)
        option = {"value": token, "gloss": candidate.label}
        if candidate.command_skill_id == form.command_skill_id:
            siblings.append(option)
        else:
            others.append(option)
    if len(siblings) >= MIN_DISTRACTORS:
        return siblings[:MAX_DISTRACTORS]
    return (siblings + others)[:MAX_DISTRACTORS]


def _blank(tokens: list[str], ranked: list[CommandForm], form: CommandForm) -> dict | None:
    """Pick the one token worth hiding, with same-kind options beside it.

    Blanking is only a question when the alternatives could plausibly sit in
    the same slot, so options are drawn from the same index and the same
    token kind in other real forms. A flag is the most discriminative thing
    to hide, then the subcommand, then a placeholder; ties go to the
    earliest slot, which is the one carrying the most meaning.
    """
    kind_priority = {"flag": 0, "word": 1, "placeholder": 2}
    best: tuple[tuple[int, int], dict] | None = None
    for index in range(1, len(tokens)):
        answer = tokens[index]
        options = _slot_options(index=index, answer=answer, form=form, ranked=ranked)
        if len(options) < MIN_DISTRACTORS:
            continue
        score = (kind_priority[token_kind(answer)], index)
        if best is None or score < best[0]:
            best = (score, {"index": index, "answer": answer, "options": options})
    return best[1] if best else None


def _bank(tokens: list[str], distractors: list[CommandForm]) -> list[str]:
    """The answer's tokens plus a few real decoys, for the assembly rung."""
    bank = list(dict.fromkeys(tokens))
    if len(bank) >= MAX_BANK_TOKENS - 1:
        return bank
    answer_tokens = set(bank)
    decoys: list[str] = []
    for candidate in distractors:
        for token in tokenize(candidate.usage_form):
            if token in answer_tokens or token in decoys or token == "git":
                continue
            decoys.append(token)
    # Flags and words are the confusable decoys; a spare placeholder reads as
    # noise next to a command the learner is assembling.
    decoys.sort(key=lambda token: 0 if token_kind(token) != "placeholder" else 1)
    return bank + decoys[: MAX_BANK_TOKENS - len(bank)]


def _card(form: CommandForm, pool: list[CommandForm], level_form_ids: set[int]) -> dict:
    tokens = tokenize(form.usage_form)
    ranked = _ranked_pool(form, pool, level_form_ids)
    distractors = _distractors(form, ranked)
    enough = len(distractors) >= MIN_DISTRACTORS
    return {
        "key": form_key(form),
        "command": form.usage_form,
        "intent": form.label,
        "base_command": form.command_skill.base_command,
        "summary": form.summary or form.command_skill.summary,
        "tokens": tokens,
        # Wrong options only - the client inserts the answer and shuffles, so
        # a question can never render without its correct choice.
        "command_choices": (
            [{"value": item.usage_form, "gloss": item.label} for item in distractors]
            if enough
            else []
        ),
        "intent_choices": (
            [{"value": item.label, "gloss": item.usage_form} for item in distractors]
            if enough
            else []
        ),
        "blank": _blank(tokens, ranked, form),
        "bank": _bank(tokens, distractors),
    }


def _sequence(level: AdventureLevel, waves: list) -> dict | None:
    """One authored solution, as the "order the moves" finale.

    Deliberately taken from the Easy tier when there is one: Easy is already
    the scaffolded rung, so rehearsing its shape is the scaffold the drill
    exists to provide, not a leaked answer - Medium and Hard draw different
    variants.
    """
    for wave in waves:
        candidates = []
        for variant in _published_variants(wave):
            steps = [str(step).strip() for step in variant.solution_commands if str(step).strip()]
            if not MIN_SEQUENCE_STEPS <= len(steps) <= MAX_SEQUENCE_STEPS:
                continue
            # A repeated command would render as two identical chips: the
            # learner cannot tell them apart and neither slot can be marked
            # wrong fairly. Skip the variant rather than ship an unwinnable
            # question.
            if len(set(steps)) != len(steps):
                continue
            candidates.append((len(steps), variant.id, variant, steps))
        if not candidates:
            continue
        # Shortest qualifying variant: the cleanest statement of the shape,
        # and the least likely to carry incidental diagnostic steps.
        _, _, variant, steps = min(candidates, key=lambda item: (item[0], item[1]))
        return {
            "label": variant.label or wave.title or level.title,
            "task": wave.task,
            "steps": steps,
        }
    return None


def compose_level_drill(level: AdventureLevel, catalog: DrillCatalog | None = None) -> dict:
    """The drill content for one level: one card per command form it teaches,
    plus the ordering finale. No player state - see ``drills.selectors``.

    Pass a shared ``catalog`` when composing many levels; it is loaded on
    demand otherwise so single-level callers stay simple.
    """
    catalog = catalog or DrillCatalog.load()
    # The wave tree answers two questions - which commands the solutions
    # type, and which run makes the ordering finale - so it is walked once.
    waves = _level_waves(level)
    forms = level_command_forms(level, catalog, waves)
    pool = _distractor_pool(forms, catalog)
    level_form_ids = {form.id for form in forms}
    return {
        "cards": [_card(form, pool, level_form_ids) for form in forms],
        "sequence": _sequence(level, waves),
    }
