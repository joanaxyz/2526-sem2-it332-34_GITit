"""Code-defined GitCoin pack catalog."""

from __future__ import annotations

# slug -> {label, coins, price_cents}. price_cents is USD cents (Stripe's unit).
PACKS: dict[str, dict] = {
    "starter": {"label": "Starter Pouch", "coins": 150, "price_cents": 99},
    "adventurer": {"label": "Adventurer's Purse", "coins": 500, "price_cents": 299},
    "hero": {"label": "Hero's Coffer", "coins": 1200, "price_cents": 599},
}


def get(slug: str) -> dict | None:
    return PACKS.get(slug)


def listings() -> list[dict]:
    return [{"slug": slug, **meta} for slug, meta in PACKS.items()]
