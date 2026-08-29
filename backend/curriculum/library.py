from __future__ import annotations

from curriculum.library_catalog import _catalog_library_entries
from curriculum.library_commands import (
    COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS,
    _bullets,
    _callout,
    _commands,
    _diagram,
    _paragraph,
    _terminal,
    _warning,
    base_command_for_command,
    command_syntax_section_id,
    library_key_for_command,
)
from curriculum.library_data import authored_library_entries
from curriculum.library_payloads import _content, lesson_pages, pages_from_command_sections
from curriculum.library_preview import (
    command_preview_section_ids_for_command,
    command_preview_syntax_for_command,
)
from curriculum.library_preview_outputs import _sample_output_for_syntax, _syntax_title
from curriculum.library_section_builders import (
    _generic_syntax_section,
    _rich_syntax_section,
    _sections,
    _semantic_item_sections,
)
from curriculum.library_sections import (
    _clean_items,
    _placeholder_note,
    _section,
    _state_language,
    _syntax_explanation,
    _syntax_how_to_read,
    _syntax_when_to_use,
    _verification_items,
)

# Authored entries are seed content; generated command-catalog entries fill gaps.
LIBRARY_ENTRIES = authored_library_entries(_diagram)
LIBRARY_ENTRIES.extend(_catalog_library_entries(LIBRARY_ENTRIES))

# Compatibility facade for authored seed modules and selector/test consumers.
# Keep this export list explicit so linting can distinguish public re-exports
# from accidental unused imports.
__all__ = [
    "COMMAND_KEY_ALWAYS_INCLUDED_SECTION_IDS",
    "LIBRARY_ENTRIES",
    "_bullets",
    "_callout",
    "_clean_items",
    "_commands",
    "_content",
    "_diagram",
    "_generic_syntax_section",
    "_paragraph",
    "_placeholder_note",
    "_rich_syntax_section",
    "_sample_output_for_syntax",
    "_section",
    "_sections",
    "_semantic_item_sections",
    "_state_language",
    "_syntax_explanation",
    "_syntax_how_to_read",
    "_syntax_title",
    "_syntax_when_to_use",
    "_terminal",
    "_verification_items",
    "_warning",
    "base_command_for_command",
    "command_preview_section_ids_for_command",
    "command_preview_syntax_for_command",
    "command_syntax_section_id",
    "lesson_pages",
    "library_key_for_command",
    "pages_from_command_sections",
]
