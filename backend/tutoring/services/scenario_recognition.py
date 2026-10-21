"""Public-field scenario fingerprints. This recognizer never reads answer fields."""

from __future__ import annotations

import hashlib
import json
import math
import re
from functools import cache, lru_cache
from pathlib import Path

from django.conf import settings

from tutoring.services.provider_transport import ProviderError, post_json

BANK_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "seed_data"
PUBLIC_FIELDS = ("label", "story", "starting_point", "task", "real_world_context")
PREPROCESSING = "public-fields-v1"
DIMENSIONS = 768
MODEL = "gemini-embedding-001"


def normalized(text):
    text = re.sub(r"`[^`]+`|https?://\S+", " value ", text.lower())
    return " ".join(re.findall(r"[a-z]+", text))


@cache
def documents():
    rows = []
    for bank in ("scenario_bank", "scenario_bank_waves"):
        source = json.loads((BANK_ROOT / f"{bank}.json").read_text(encoding="utf-8"))
        for case_id, row in source.items():
            fields = {key: str(row.get(key, "")) for key in PUBLIC_FIELDS}
            rows.append(
                {
                    "id": f"{bank}:{case_id}",
                    "text": "\n".join(fields.values()),
                    "task": fields["task"],
                }
            )
    return rows


@cache
def corpus_hash():
    return hashlib.sha256(json.dumps(documents(), sort_keys=True).encode()).hexdigest()


def unit_vector(vector):
    if len(vector) != DIMENSIONS or any(
        not isinstance(value, (int, float)) or not math.isfinite(value) for value in vector
    ):
        raise ValueError("Invalid embedding")
    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        raise ValueError("Empty embedding")
    return [value / norm for value in vector]


def embed(texts, task_type, timeout=3):
    if not settings.GOOGLE_AI_STUDIO_API_KEY:
        raise ProviderError(503)
    response = post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:batchEmbedContents",
        {"x-goog-api-key": settings.GOOGLE_AI_STUDIO_API_KEY},
        {
            "requests": [
                {
                    "model": f"models/{MODEL}",
                    "content": {"parts": [{"text": text}]},
                    "taskType": task_type,
                    "outputDimensionality": DIMENSIONS,
                }
                for text in texts
            ]
        },
        timeout,
    )
    vectors = [unit_vector(row["values"]) for row in response["embeddings"]]
    if len(vectors) != len(texts):
        raise ValueError("Incomplete embeddings")
    return vectors


def load_index(path, fingerprint):
    try:
        stamp = Path(path).stat().st_mtime_ns
    except OSError:
        stamp = 0
    return _load_index(path, fingerprint, stamp)


@lru_cache(maxsize=2)
def _load_index(path, fingerprint, stamp):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if (
            data["corpus_hash"] != fingerprint
            or data["model"] != MODEL
            or data["dimensions"] != DIMENSIONS
            or data["preprocessing"] != PREPROCESSING
        ):
            return None
        rows = data["vectors"]
        if {row["id"] for row in rows} != {row["id"] for row in documents()}:
            return None
        return [unit_vector(row["values"]) for row in rows]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def recognize(message):
    """Unknown retrieval is conservative. It never enables unrestricted output."""
    question = normalized(message)
    words = set(question.split())
    best = 0.0
    for row in documents():
        task = normalized(row["task"])
        if len(task) >= 24 and task in question:
            return "matched"
        task_words = set(task.split())
        if len(words) >= 7 and task_words:
            best = max(best, len(words & task_words) / len(task_words | words))
    if best >= 0.45:
        return "matched"
    vectors = load_index(str(settings.TUTOR_SCENARIO_INDEX_PATH), corpus_hash())
    if vectors is None:
        return "uncertain"
    try:
        query = embed([message], "RETRIEVAL_QUERY")[0]
        score = max(math.sumprod(query, vector) for vector in vectors)
        return "matched" if score >= 0.72 else "uncertain" if score >= 0.55 else "unmatched"
    except (ProviderError, ValueError, KeyError, TypeError):
        return "uncertain"
