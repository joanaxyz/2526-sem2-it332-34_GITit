"""Tips: short notes beside the workspace, apart from the command guide.

A tip explains a technique (how a command's operands are written, see
``techniques.py``) or a concept (an idea the move touches, see ``concepts.py``).
Neither belongs to the scenario that teaches a command, so a tip comes with its
move wherever and whenever that move comes up; the client may put it away for
the rest of a run.
"""

from __future__ import annotations

from dataclasses import dataclass

from tutoring.services.concepts import CONCEPTS, concept_key
from tutoring.services.teaching import safe_usage
from tutoring.services.techniques import Technique


@dataclass(frozen=True)
class Tip:
    key: str
    kind: str
    title: str
    text: str
    # A technique's generic syntax; concepts have none.
    syntax: str | None = None

    def payload(self) -> dict:
        return {
            "key": self.key,
            "kind": self.kind,
            "title": self.title,
            "text": self.text,
            "syntax": self.syntax,
        }


def concept_tip(key: str) -> Tip:
    title, text = CONCEPTS[key]
    return Tip(concept_key(key), "concept", title, text)


def technique_tip(technique: Technique, family: str) -> Tip:
    return Tip(
        technique.teaching_key,
        "technique",
        technique.title,
        technique.summary,
        safe_usage(technique.syntax(family)),
    )
