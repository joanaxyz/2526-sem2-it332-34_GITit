"""Seed the Git command library.

The Storey Book renders authored command reference content (overview, syntax,
options, arguments, effects, diagrams). Entries are authored in
``curriculum/library.py`` (``LIBRARY_ENTRIES``) using the same builder helpers
the book uses, built through ``_content`` here, and persisted to the
``LibraryEntry`` model. ``storey_book`` resolves each registered command to its
seeded entry; commands without one fall back to a synthesized summary page.

Run with:  python manage.py seed_command_library
"""

from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from curriculum.library import LIBRARY_ENTRIES, _content
from curriculum.models import LibraryEntry


class Command(BaseCommand):
    help = "Seed the Git command library (LibraryEntry rows for the Storey Book)."

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        live_ids = []
        for spec in LIBRARY_ENTRIES:
            content = _content(**spec)
            entry, _ = LibraryEntry.objects.update_or_create(
                command_key=content["key"],
                defaults={
                    "title": content["display_name"],
                    "summary": content["summary"],
                    "tags": content["tags"],
                    "pages": content["pages"],
                    "is_published": True,
                },
            )
            live_ids.append(entry.id)
            self.stdout.write(
                f"  • {content['key']}: {len(content['pages'])} pages ({content['display_name']})"
            )
        LibraryEntry.objects.exclude(id__in=live_ids).update(is_published=False)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(live_ids)} command library entr{'y' if len(live_ids) == 1 else 'ies'}."
            )
        )
