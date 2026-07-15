"""Read-model builders for content definitions and feature flags."""

from __future__ import annotations


def content_payload(content) -> dict:
    return {
        "id": content.id,
        "kind": content.kind,
        "slug": content.slug,
        "title": content.title,
        "status": content.status,
        "visibility": content.visibility,
        "updated_at": content.updated_at,
    }


def flag_payload(flag) -> dict:
    return {
        "key": flag.key,
        "label": flag.label,
        "description": flag.description,
        "enabled": flag.enabled,
    }
