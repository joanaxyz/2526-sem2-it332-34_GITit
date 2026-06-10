"""Seed the Git command content library.

The Storey Book renders authored command reference content (overview, syntax,
options, arguments, effects, diagrams). That content is **seeded content** like
the rest of the curriculum — authored here, and (once a storage model exists)
persisted to the database and versioned — rather than baked into the codebase.
``curriculum/command_content.py`` now holds only the builder helpers; its
``GIT_COMMAND_CONTENT_LIBRARY`` is intentionally empty until this seed is wired.

This command is the seed entry point for that content. It is intentionally a
TEMPLATE for now:

  * ``COMMAND_LIBRARY_ENTRIES`` holds one fully-authored example entry. It shows
    every authorable field, including the option/argument sub-sections that drive
    the Storey Book's sub-navigation and an authored ``diagram`` block.
  * ``handle()`` builds each entry through the shared ``_content`` helper (the
    exact builder the book uses) so the template is validated end to end, and
    reports what it would seed.

TODO(seed): once a ``CommandLibraryEntry`` model exists, persist each built entry
with ``update_or_create`` (mirroring ``seed_curriculum_v2``) and point
``command_content_entry_for_command`` at the table instead of the in-module list.

Run with:  python manage.py seed_command_library
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from curriculum.command_content import _content, _diagram

# ── Template ────────────────────────────────────────────────────────────────
# Copy this block once per command and fill it in. Every field maps 1:1 to the
# arguments of ``_content`` in command_content.py.
COMMAND_LIBRARY_ENTRIES: list[dict[str, Any]] = [
    {
        # Stable identifier for the entry (kebab-case). Also the seed lookup key.
        "key": "git-init",
        # Human label shown in the book's command rail.
        "display_name": "git init",
        # The canonical, fully-written form the content is authored against.
        "canonical_command": "git init",
        # Base command used for grouping (defaults from canonical when omitted).
        "base_command": "git init",
        # Other accepted spellings/forms for this command.
        "aliases": ["git init <directory>", "git init -b <branch>", "git init -q"],
        # One-paragraph summary shown at the top of the command.
        "summary": "git init creates Git metadata for a folder so future snapshots can be tracked there.",
        # Free-form tags (diagnostic/action/…); surfaced to the book payload.
        "tags": ["action", "setup"],
        # Authored syntax examples; each becomes a syntax page.
        "syntax": [
            "git init",
            "git init <directory>",
            "git init -b <branch>",
            "git init --quiet",
        ],
        "effects": ["Creates the repository metadata directory for the folder."],
        "boundaries": ["It does not stage or commit any existing project files."],
        "watch_for": "Running it inside a folder that is already a repository.",
        "readiness": ["Confirm you are in the intended folder before initializing."],
        "terminal_output": "Initialized empty Git repository in /path/.git/",
        # ── Sub-navigation: options & arguments ──────────────────────────────
        # Each option/argument becomes its own page AND a sub-nav item in the
        # Storey Book (e.g. git init → -q / --quiet, -b / --initial-branch).
        "options": [
            {
                "token": "-b / --initial-branch",
                "title": "Initial branch name",
                "body": "Names the first branch instead of accepting the default branch name.",
            },
            {
                "token": "-q / --quiet",
                "title": "Quiet init",
                "body": "Suppresses the confirmation message while still creating the repository.",
            },
        ],
        "arguments": [
            {
                "token": "<directory>",
                "title": "Destination directory",
                "body": "Initializes the named folder instead of the current working directory.",
            },
        ],
        # ── Authored diagram (optional) ──────────────────────────────────────
        # Rendered as neon SVG in the book. kind="flow" | "dag".
        "diagram": _diagram(
            kind="flow",
            title="What init sets up",
            caption="git init creates the .git metadata folder; your files stay untracked until you stage and commit them.",
            nodes=[
                {"id": "folder", "label": "Project folder", "accent": "muted"},
                {"id": "repo", "label": ".git metadata", "accent": "cyan"},
            ],
            edges=[{"from": "folder", "to": "repo", "label": "git init"}],
        ),
    },
    # TODO(seed): add the remaining commands registered across the storeys here,
    # one dict per command, following the template above.
]


class Command(BaseCommand):
    help = "Seed the Git command content library (template scaffold)."

    def handle(self, *args: Any, **options: Any) -> None:
        built = 0
        for entry in COMMAND_LIBRARY_ENTRIES:
            content = _content(**entry)
            page_count = len(content["pages"])
            built += 1
            self.stdout.write(
                f"  • {content['key']}: {page_count} pages "
                f"({content['display_name']})"
            )
            # TODO(seed): persist `content` to the CommandLibraryEntry model here.

        self.stdout.write(
            self.style.SUCCESS(
                f"Validated {built} command library entr{'y' if built == 1 else 'ies'}. "
                "Persistence is not wired yet — see the module docstring."
            )
        )
