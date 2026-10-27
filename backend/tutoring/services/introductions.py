import hashlib
import json

from django.core import signing

from common.exceptions import BadRequest, Conflict
from simulator.services import RepositoryStateSimulator
from tutoring.models import PendingCommandIntroduction, PlayerCommandIntroduction
from tutoring.services.teaching import guide_key

SALT = "tutoring.command-introduction.v2"
HELP_SALT = "tutoring.guide-help.v1"


def issue_help_token(run, teaching_key, usage_form):
    return signing.dumps(
        {
            "player": run.player_id,
            "run": run.pk,
            "key": guide_key(teaching_key),
            "usage": usage_form,
        },
        salt=HELP_SALT,
    )


def context_hash(run):
    return hashlib.sha256(json.dumps(binding(run), sort_keys=True).encode()).hexdigest()


def binding(run):
    return {
        "player": run.player_id,
        "run": run.pk,
        "variant": run.selected_variant_id,
        "revision": run.total_attempts,
        "state": RepositoryStateSimulator().state_hash(run.repository_state),
        "objective": run.selected_variant.evaluation_spec,
    }


def issue_token(run, teaching_key, phase):
    return signing.dumps(
        {
            "player": run.player_id,
            "run": run.pk,
            "context": context_hash(run),
            "key": guide_key(teaching_key),
            "phase": phase,
        },
        salt=SALT,
    )


def validate_token(run, token, phase):
    try:
        data = signing.loads(token, salt=SALT, max_age=3600)
    except signing.BadSignature as exc:
        raise BadRequest(
            "This introduction has expired. Refresh the workspace to continue."
        ) from exc
    if data.get("phase") != phase:
        raise BadRequest("Read the command feedback before completing this introduction.")
    if (
        data.get("player") != run.player_id
        or data.get("run") != run.pk
        or data.get("context") != context_hash(run)
    ):
        raise Conflict("The repository has changed. Review the refreshed introduction.")
    return data["key"]


def complete_introduction(run, token):
    key = validate_token(run, token, "feedback")
    pending = PendingCommandIntroduction.objects.filter(run=run).first()
    # Private lesson identities remain stable for mastery and introduction history.
    if pending and guide_key(pending.teaching_key) == key:
        key = pending.teaching_key
    elif key.startswith("guide:"):
        key = next(
            (
                value
                for value in PlayerCommandIntroduction.objects.filter(
                    player_id=run.player_id
                ).values_list("teaching_key", flat=True)
                if guide_key(value) == key
            ),
            "",
        )
    if not (
        PendingCommandIntroduction.objects.filter(run=run, teaching_key=key).exists()
        or PlayerCommandIntroduction.objects.filter(
            player_id=run.player_id, teaching_key=key
        ).exists()
    ):
        raise BadRequest("There is no command introduction to complete.")
    PlayerCommandIntroduction.objects.get_or_create(player_id=run.player_id, teaching_key=key)
    PendingCommandIntroduction.objects.filter(run=run, teaching_key=key).delete()
