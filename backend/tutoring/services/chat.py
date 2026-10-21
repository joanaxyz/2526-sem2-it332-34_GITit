"""Tutor orchestration. Eligibility and rendering remain independent of the model."""

import re

from django.core import signing
from django.shortcuts import get_object_or_404

from adventures.models import AdventureLevelTierRun
from common.exceptions import BadRequest
from tutoring.services.introductions import HELP_SALT
from tutoring.services.provider_transport import in_background
from tutoring.services.providers import select_blocks
from tutoring.services.scenario_recognition import recognize
from tutoring.services.teaching import NEUTRAL, catalog, form_blocks, option_blocks, topic_choices

_EXPLAIN = re.compile(
    r"\b(what (?:is|are|does|do)|why|explain|understand|meaning|mean|difference|clarify|"
    r"clarification|how does|tell me about|more detail|simpler|again)\b",
    re.I,
)
_SOLVE = re.compile(
    r"\b(answer|solution|correct|right command|which command|what command|next (?:step|move)|"
    r"solve|complete (?:this|the task)|step.by.step|should i|is this right|answer.key|"
    r"ignore (?:all|previous)|system prompt)\b",
    re.I,
)
_FOLLOWUP = re.compile(r"^(?:more|why|simpler|again|explain further|more detail)[.!?\s]*$", re.I)
_ALIASES = {
    "working-tree": ("working tree", "working directory"),
    "staging-area": ("staging", "staged", "index"),
    "head": ("head",),
    "placeholders": ("placeholder", "angle bracket"),
    "repository": ("repository", "repositories", "repo"),
    "branch": ("branch", "branches"),
    "commit": ("commit", "commits"),
    "remote": ("remote",),
    "conflict": ("conflict",),
    "stash": ("stash",),
    "tag": ("tag",),
    "config": ("configuration",),
    "commands": ("command", "commands"),
}


def guide_usage(player, context):
    if context["surface"] != "command_guide":
        return None
    # Validate ownership without invoking the solution planner or reading a trajectory.
    get_object_or_404(AdventureLevelTierRun.objects.only("pk"), pk=context["run_id"], player=player)
    try:
        # Generic teaching stays valid on replay; current authentication and run
        # ownership are checked above. This token cannot execute or complete a run.
        data = signing.loads(context["guide_token"], salt=HELP_SALT)
    except (signing.BadSignature, KeyError):
        raise BadRequest("This guide has expired. Refresh the workspace to reopen it.") from None
    if (
        data.get("player") != player.pk
        or data.get("run") != context["run_id"]
        or data.get("key") != context["teaching_key"]
    ):
        raise BadRequest("This guide is no longer available. Reopen the command guide.")
    return data["usage"]


def eligible_blocks(message, usage=None):
    """Only explicitly requested concepts/forms or the already displayed guide."""
    if _SOLVE.search(message):
        return []
    if usage:
        return form_blocks(usage)
    if not _EXPLAIN.search(message):
        return []
    blocks = catalog()
    families = [
        block
        for block in blocks.values()
        if block.id.startswith("command:")
        and re.search(rf"\bgit\s+{re.escape(block.family)}\b", message, re.I)
    ]
    if families:
        result = list(families)
        # Bare family questions get a neutral overview, never a model-chosen variant.
        if len(families) == 1:
            flags = set(re.findall(r"(?<!\w)--?[a-zA-Z][a-zA-Z-]*", message))
            result.extend(option_blocks(families[0].family, flags))
            forms = [
                block
                for block in blocks.values()
                if block.usage
                and block.family == families[0].family
                and set(re.findall(r"(?<!\w)--?[a-zA-Z][a-zA-Z-]*", block.usage)) == flags
            ]
            if flags and len(forms) == 1:
                result.extend(forms)
        result.append(blocks["concept:placeholders"])
        return result[:12]
    result = []
    for key, names in _ALIASES.items():
        if any(re.search(rf"\b{re.escape(name)}\b", message, re.I) for name in names):
            result.append(blocks[f"concept:{key}"])
            if f"detail:{key}" in blocks:
                result.append(blocks[f"detail:{key}"])
    return result[:10]


def chat(player, message, context, history=()):
    usage = guide_usage(player, context)
    # Recognition only labels the reply, so its embedding call overlaps selection.
    recognition = in_background(recognize, message)
    followup = bool(_FOLLOWUP.fullmatch(message.strip()))
    learning_question = message
    if followup and history and not usage:
        learning_question = next(
            (
                question
                for question in reversed(history)
                if not _FOLLOWUP.fullmatch(question.strip())
            ),
            message,
        )
    blocks = eligible_blocks(learning_question, usage)
    if not blocks:
        return {
            "reply": NEUTRAL,
            "sources": [],
            "suggested_topics": topic_choices(),
            "response_kind": "concept_redirect",
            "scenario_related": recognition.result() != "unmatched",
        }
    # Earlier questions only disambiguate follow-ups. Standalone questions stay
    # history-free, so repeated ones (topic chips) reuse cached selections.
    selected = select_blocks(message, blocks, history if followup else ())
    if selected is None:
        # Static material is useful even while every provider is limited.
        selected = [block.id for block in blocks if not block.usage][:2]
        note = "AI is temporarily unavailable. You can still review this guide material.\n\n"
        kind = "unavailable"
    else:
        note, kind = "", "explanation"
    allowed = {block.id: block for block in blocks}
    chosen = [allowed[block_id] for block_id in selected]
    return {
        "reply": note + "\n\n".join(block.text for block in chosen),
        "sources": [block.source() for block in chosen],
        "suggested_topics": topic_choices(),
        "response_kind": kind,
        "scenario_related": recognition.result() != "unmatched",
    }
