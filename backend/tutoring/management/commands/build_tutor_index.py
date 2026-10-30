"""Build cached public-scenario vectors, never during a learner request."""

import json
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from tutoring.services.provider_transport import ProviderError
from tutoring.services.providers import retry_seconds
from tutoring.services.scenario_recognition import (
    DIMENSIONS,
    MODEL,
    PREPROCESSING,
    corpus_hash,
    documents,
    embed,
)


class Command(BaseCommand):
    help = "Build the AI tutor's semantic index from public fields in both seed banks."

    def add_arguments(self, parser):
        parser.add_argument("--output", default=str(settings.TUTOR_SCENARIO_INDEX_PATH))
        parser.add_argument("--check", action="store_true")

    def handle(self, *args, **options):
        path = Path(options["output"])
        fingerprint = corpus_hash()
        if options["check"]:
            from tutoring.services.scenario_recognition import load_index

            if load_index(str(path), fingerprint) is None:
                raise CommandError(
                    "Tutor semantic index is missing or stale; run build_tutor_index."
                )
            self.stdout.write("Tutor index matches all public scenario fields.")
            return
        rows = documents()
        temporary = path.with_suffix(".building")
        header = {
            "model": MODEL,
            "dimensions": DIMENSIONS,
            "preprocessing": PREPROCESSING,
            "corpus_hash": fingerprint,
        }
        vectors = []
        try:
            previous = json.loads(temporary.read_text(encoding="utf-8"))
            if all(previous.get(key) == value for key, value in header.items()):
                vectors = previous["vectors"]
        except (OSError, ValueError, KeyError):
            pass
        completed = {row["id"] for row in vectors}
        remaining = [row for row in rows if row["id"] not in completed]
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            for offset in range(0, len(remaining), 8):
                batch = remaining[offset : offset + 8]
                for attempt in range(3):
                    try:
                        values = embed(
                            [row["text"] for row in batch], "RETRIEVAL_DOCUMENT", timeout=20
                        )
                        break
                    except ProviderError as exc:
                        delay = retry_seconds(exc.retry_after) if exc.retry_after else 20
                        if exc.status != 429 or attempt == 2 or delay > 60:
                            raise
                        self.stdout.write(
                            f"Embedding quota cooling down for {delay}s; completed {len(vectors)}/{len(rows)}."
                        )
                        self.stdout.flush()
                        time.sleep(delay)
                vectors.extend(
                    {"id": row["id"], "values": [round(value, 9) for value in vector]}
                    for row, vector in zip(batch, values, strict=True)
                )
                temporary.write_text(
                    json.dumps({**header, "vectors": vectors}, separators=(",", ":")),
                    encoding="utf-8",
                )
                self.stdout.write(f"Indexed {len(vectors)}/{len(rows)} public scenarios.")
                self.stdout.flush()
                time.sleep(1)
        except Exception as exc:
            status = getattr(exc, "status", "invalid-response")
            raise CommandError(
                f"Could not build tutor index (status {status}); the existing index was preserved."
            ) from exc
        temporary.write_text(
            json.dumps(
                {
                    "model": MODEL,
                    "dimensions": DIMENSIONS,
                    "preprocessing": PREPROCESSING,
                    "corpus_hash": fingerprint,
                    "vectors": vectors,
                },
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        temporary.replace(path)
        self.stdout.write(f"Indexed {len(rows)} scenarios: {path}")
