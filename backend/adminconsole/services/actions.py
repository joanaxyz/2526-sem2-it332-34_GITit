from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import ValidationError

from adminconsole.models import AdminActionLog


def record_admin_action(
    *,
    actor,
    action: str,
    target=None,
    target_type: str | None = None,
    target_id: str | int | None = None,
    target_label: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
    metadata: dict | None = None,
    request_id: str = "",
) -> AdminActionLog:
    if target is not None:
        target_type = target_type or f"{target._meta.app_label}.{target._meta.model_name}"
        target_id = target.pk if target_id is None else target_id
        target_label = str(target) if target_label is None else target_label
    if not target_type:
        raise ValueError("target_type is required for an admin action log.")
    return AdminActionLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id="" if target_id is None else str(target_id),
        target_label=(target_label or "")[:255],
        before=before or {},
        after=after or {},
        metadata=metadata or {},
        request_id=request_id,
    )


class AdminUserActionService:
    @transaction.atomic
    def set_staff(self, *, actor, target, value: bool):
        if actor.pk == target.pk and not value:
            raise ValidationError({"value": "You cannot revoke your own admin access."})
        before = {"is_staff": target.is_staff}
        if target.is_staff == value:
            return target
        target.is_staff = value
        target.save(update_fields=["is_staff"])
        record_admin_action(
            actor=actor,
            action="user.set_staff",
            target=target,
            before=before,
            after={"is_staff": target.is_staff},
        )
        return target

    @transaction.atomic
    def set_active(self, *, actor, target, value: bool):
        if actor.pk == target.pk and not value:
            raise ValidationError({"value": "You cannot disable your own account."})
        before = {"is_active": target.is_active}
        if target.is_active == value:
            return target
        target.is_active = value
        target.save(update_fields=["is_active"])
        record_admin_action(
            actor=actor,
            action="user.set_active",
            target=target,
            before=before,
            after={"is_active": target.is_active},
        )
        return target


@transaction.atomic
def unpublish_moderation_content(*, actor, content):
    before = {"visibility": content.visibility, "status": content.status}
    content.visibility = "private"
    content.status = "draft"
    content.save(update_fields=["visibility", "status", "updated_at"])
    record_admin_action(
        actor=actor,
        action="moderation.unpublish",
        target=content,
        before=before,
        after={"visibility": content.visibility, "status": content.status},
    )
    return content


@transaction.atomic
def update_feature_flag(*, actor, key: str, enabled: bool):
    from adminconsole.flags import SUPPORTED_FLAGS
    from adminconsole.models import FeatureFlag

    spec = SUPPORTED_FLAGS[key]
    flag, _created = FeatureFlag.objects.get_or_create(
        key=key,
        defaults={
            "label": spec["label"],
            "description": spec["description"],
            "enabled": spec["default"],
        },
    )
    before = {"enabled": flag.enabled}
    flag.label = spec["label"]
    flag.description = spec["description"]
    flag.enabled = enabled
    flag.save(update_fields=["label", "description", "enabled", "updated_at"])
    record_admin_action(
        actor=actor,
        action="feature_flag.update",
        target=flag,
        before=before,
        after={"enabled": flag.enabled},
    )
    return flag
