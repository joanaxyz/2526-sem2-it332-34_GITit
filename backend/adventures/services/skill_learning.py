"""Persist skill discovery from verified command use, independently of clears."""

from django.db.models import Exists, OuterRef
from django.utils import timezone

from adventures.models import SkillMastery
from curriculum.models import CommandForm, CommandSkill
from curriculum.selectors.command_skills import learned_command_skills
from tutoring.services.forms import command_family, command_matches_form


def learn_from_command(*, player, result) -> list[dict]:
    """Return only skills discovered by this successful, verified command.

    Call inside the command submission transaction. Learning records the forms
    actually exercised; completion still owns solve counts and mastery.
    """
    if not result.processed or result.exit_code != 0:
        return []
    family = command_family(result.normalized_command)
    if family is None:
        return []
    forms = [
        form
        for form in CommandForm.objects.filter(
            is_published=True,
            is_playable=True,
            command_skill__is_published=True,
            command_skill__base_command=f"git {family}",
        ).annotate(
            # Repeat use is the common case; one read answers it.
            already_learned=Exists(
                SkillMastery.objects.filter(
                    player=player, command_form=OuterRef("pk"), learned_at__isnull=False
                )
            )
        )
        # A catalog's one-or-more operand form also covers one path. The tutor's
        # stricter multi-operand lesson detector is not the skill unlock rule.
        if command_matches_form(result.normalized_command, form.usage_form)
    ]
    if all(form.already_learned for form in forms):
        return []

    skill_ids = {form.command_skill_id for form in forms}
    # Different run rows can introduce different forms of the same skill at
    # once. Serialize first discovery on the catalog rows so only one command
    # emits the celebration; ordinary repeat use takes the fast path above.
    list(CommandSkill.objects.select_for_update().filter(id__in=skill_ids).order_by("id"))
    previously_learned = set(
        SkillMastery.objects.filter(
            player=player,
            command_form__command_skill_id__in=skill_ids,
            learned_at__isnull=False,
        ).values_list("command_form__command_skill_id", flat=True)
    )
    learned_at = timezone.now()
    for form in forms:
        row, _ = SkillMastery.objects.get_or_create(player=player, command_form=form)
        if row.learned_at is None:
            row.learned_at = learned_at
            row.save(update_fields=["learned_at", "updated_at"])

    newly_learned = skill_ids - previously_learned
    if not newly_learned:
        return []
    return [
        skill for skill in learned_command_skills(player=player) if skill["id"] in newly_learned
    ]
