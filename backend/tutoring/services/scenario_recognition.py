"""Public-field scenario retrieval. This recognizer never reads answer fields.

Recognition decides whether a conversation is about a seeded scenario, so the
tutor teaches it instead of solving it. It returns the matched case IDs; the
answer guard looks up those cases' answer fields on its own.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

from django.conf import settings
from django.core.cache import cache as shared_cache

from tutoring.services.provider_transport import ProviderError, post_json

BANK_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "seed_data"
BANKS = ("scenario_bank", "scenario_bank_extension")
PUBLIC_FIELDS = ("label", "story", "starting_point", "task", "real_world_context")
PREPROCESSING = "public-fields-v1"
DIMENSIONS = 768
MODEL = "gemini-embedding-001"
MATCHED, UNCERTAIN, UNMATCHED = "matched", "uncertain", "unmatched"
_RANK = {UNMATCHED: 0, UNCERTAIN: 1, MATCHED: 2}
CANDIDATES = 3
RECOGNITION_TTL = 86400
# Cosine similarity to the nearest scenario. General Git questions score up to
# about 0.74 against this index while tasks retold in a learner's own words score
# from about 0.76, so a confident match starts above the general questions.
MATCH_SCORE = 0.75
UNCERTAIN_SCORE = 0.55


@dataclass(frozen=True)
class Recognition:
    status: str
    case_ids: tuple[str, ...] = ()

    @property
    def related(self):
        return self.status != UNMATCHED


def normalized(text):
    text = re.sub(r"`[^`]+`|https?://\S+", " value ", text.lower())
    return " ".join(re.findall(r"[a-z]+", text))


@cache
def documents():
    rows = []
    for bank in BANKS:
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
    """``[(case_id, vector)]`` when the index matches the public corpus, else None."""
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
        return [(row["id"], unit_vector(row["values"])) for row in rows]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _lexical(message):
    """Exact or near-verbatim task text: a pasted scenario needs no embedding."""
    question = normalized(message)
    words = set(question.split())
    scores, verbatim = [], []
    for row in documents():
        task = normalized(row["task"])
        if len(task) >= 24 and task in question:
            # Variants can share wording; guard every scenario the text could be.
            verbatim.append(row["id"])
            continue
        task_words = set(task.split())
        if len(words) >= 7 and task_words:
            scores.append((len(words & task_words) / len(task_words | words), row["id"]))
    if verbatim:
        return Recognition(MATCHED, tuple(verbatim)), []
    scores.sort(reverse=True)
    if scores and scores[0][0] >= 0.45:
        return Recognition(MATCHED, (scores[0][1],)), scores
    return None, scores


def _semantic(vector, index):
    scores = sorted(
        ((math.sumprod(vector, values), case_id) for case_id, values in index), reverse=True
    )
    top = scores[0][0] if scores else 0.0
    if top >= MATCH_SCORE:
        return Recognition(
            MATCHED,
            tuple(case_id for score, case_id in scores[:CANDIDATES] if score >= MATCH_SCORE),
        )
    if top >= UNCERTAIN_SCORE:
        return Recognition(UNCERTAIN, tuple(case_id for _, case_id in scores[:CANDIDATES]))
    return Recognition(UNMATCHED)


def _fallback(scores):
    """Retrieval is unavailable: stay protective, guarding the nearest tasks by wording."""
    return Recognition(UNCERTAIN, tuple(case_id for _, case_id in scores[:CANDIDATES]))


def _memo(text):
    return "tutor:recognition:" + hashlib.sha256(f"{corpus_hash()}:{text}".encode()).hexdigest()


def recognize_all(texts):
    """One recognition per text. Unknown retrieval is protective, never permissive."""
    results = {}
    settled = {}
    pending = []
    for text in dict.fromkeys(texts):
        cached = shared_cache.get(_memo(text))
        if isinstance(cached, list) and len(cached) == 2:
            results[text] = Recognition(cached[0], tuple(cached[1]))
            continue
        found, scores = _lexical(text)
        if found:
            results[text] = settled[text] = found
        else:
            pending.append((text, scores))
    if pending:
        index = load_index(str(settings.TUTOR_SCENARIO_INDEX_PATH), corpus_hash())
        vectors = None
        if index is not None:
            try:
                vectors = embed([text for text, _ in pending], "RETRIEVAL_QUERY")
            except (ProviderError, ValueError, KeyError, TypeError):
                vectors = None
        for position, (text, scores) in enumerate(pending):
            if vectors is None:
                # Not memoized: a later turn retries real retrieval for this text.
                results[text] = _fallback(scores)
            else:
                results[text] = settled[text] = _semantic(vectors[position], index)
    for text, result in settled.items():
        shared_cache.set(_memo(text), [result.status, list(result.case_ids)], RECOGNITION_TTL)
    return [results[text] for text in texts]


def recognize(message):
    return recognize_all([message])[0]


def recognize_conversation(texts):
    """A conversation that has touched a scenario stays protected for its later turns."""
    status, case_ids = UNMATCHED, []
    for result in recognize_all([text for text in texts if text.strip()]):
        if _RANK[result.status] > _RANK[status]:
            status = result.status
        case_ids.extend(case_id for case_id in result.case_ids if case_id not in case_ids)
    return Recognition(status, tuple(case_ids))
