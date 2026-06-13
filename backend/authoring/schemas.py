BOOK_BLOCK_TYPES = {
    "paragraph",
    "bullet_list",
    "list",
    "command",
    "code",
    "callout",
    "warning",
    "terminal_output",
    "diagram",
    "image",
}


def content_levels(definition: dict) -> list[dict]:
    levels = definition.get("levels")
    if isinstance(levels, list):
        return [level for level in levels if isinstance(level, dict)]
    level = definition.get("level")
    return [level] if isinstance(level, dict) else []

