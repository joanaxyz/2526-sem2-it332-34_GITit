import hashlib
import json

from django.core import signing

from common.exceptions import BadRequest, Conflict
from simulator.services import RepositoryStateSimulator
from tutoring.models import PendingCommandIntroduction, PlayerCommandIntroduction

SALT = "tutoring.command-introduction.v1"


def context_hash(run):
    return hashlib.sha256(json.dumps(binding(run), sort_keys=True).encode()).hexdigest()


def binding(run):
    return {
        "player": run.player_id, "run": run.pk, "variant": run.selected_variant_id,
        "revision": run.total_attempts,
        "state": RepositoryStateSimulator().state_hash(run.repository_state),
        "objective": run.selected_variant.evaluation_spec,
    }


def issue_token(run, teaching_key, phase):
    return signing.dumps({**binding(run), "key": teaching_key, "phase": phase}, salt=SALT)


def validate_token(run, token, phase):
    try:
        data = signing.loads(token, salt=SALT, max_age=3600)
    except signing.BadSignature as exc:
        raise BadRequest("This introduction has expired. Refresh the workspace to continue.") from exc
    if data.get("phase") != phase:
        raise BadRequest("Read the command feedback before completing this introduction.")
    if any(
        data.get(key) != value for key, value in binding(run).items()
    ):
        raise Conflict("The repository has changed. Review the refreshed introduction.")
    return data["key"]


def complete_introduction(run, token):
    key = validate_token(run, token, "feedback")
    if not (PendingCommandIntroduction.objects.filter(run=run, teaching_key=key).exists()
            or PlayerCommandIntroduction.objects.filter(player_id=run.player_id, teaching_key=key).exists()):
        raise BadRequest("There is no command introduction to complete.")
    PlayerCommandIntroduction.objects.get_or_create(player_id=run.player_id, teaching_key=key)
    PendingCommandIntroduction.objects.filter(run=run, teaching_key=key).delete()
