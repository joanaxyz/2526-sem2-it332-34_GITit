"""Shop catalog. Companions are the only thing the shop sells.

Stories are not purchasable: they are gated by prerequisite mastery alone
(see ``curriculum.selectors.stories.story_locked``).
"""

from __future__ import annotations

KIND_COMPANION = "companion"
SHOP_KINDS = (KIND_COMPANION,)

# No companion is free - every player must buy their first one.
COMPANIONS: dict[str, dict] = {
    "blue": {"label": "Blue", "price": 150},
    "white": {"label": "White", "price": 150},
    "black": {"label": "Black", "price": 150},
}


def catalog(kind: str) -> dict[str, dict]:
    if kind == KIND_COMPANION:
        return COMPANIONS
    return {}


def get(kind: str, slug: str) -> dict | None:
    return catalog(kind).get(slug)


def listings() -> list[dict]:
    return [
        {
            "kind": kind,
            "slug": slug,
            "label": meta["label"],
            "price": meta["price"],
        }
        for kind in SHOP_KINDS
        for slug, meta in catalog(kind).items()
    ]
