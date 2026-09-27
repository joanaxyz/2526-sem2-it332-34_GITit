"""The one owner of the fading-scaffold ladder.

Support fades with tier difficulty, and the ladder is a constant here - never
authored per variant and never re-derived in a payload or command processor.
The live DAG is always available; the target diagram goes first, then the
per-command contextual feedback.
"""

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM

SCAFFOLDING_LADDER = {
    DIFFICULTY_EASY: {
        "live_dag": True,
        "expected_state": True,
        "contextual_feedback": True,
    },
    DIFFICULTY_MEDIUM: {
        "live_dag": True,
        "expected_state": False,
        "contextual_feedback": True,
    },
    DIFFICULTY_HARD: {
        "live_dag": True,
        "expected_state": False,
        "contextual_feedback": False,
    },
}

# Guided adventure runs walk waves instead of difficulty tiers, so they sit
# outside the ladder: a live DAG plus the objective checklist, nothing that
# fades.
GUIDED_SUPPORTS = {
    "live_dag": True,
    "expected_state": False,
    "contextual_feedback": False,
}


class ScaffoldingService:
    def supports_for(self, difficulty: str) -> dict:
        """Support flags for a tier. Unknown difficulty gets the least support."""
        return dict(SCAFFOLDING_LADDER.get(difficulty, SCAFFOLDING_LADDER[DIFFICULTY_HARD]))

    def guided_supports(self) -> dict:
        return dict(GUIDED_SUPPORTS)

    def shows_expected_state(self, difficulty: str) -> bool:
        return self.supports_for(difficulty)["expected_state"]

    def shows_contextual_feedback(self, difficulty: str) -> bool:
        return self.supports_for(difficulty)["contextual_feedback"]


class FeedbackGenerationService:
    def describe(self, before: dict, after: dict) -> str:
        messages: list[str] = []
        if before.get("head") != after.get("head"):
            messages.append("HEAD moved to a different repository position.")
        if before.get("branches") != after.get("branches"):
            messages.append("One or more branch pointers changed.")
        if len(after.get("commits", [])) > len(before.get("commits", [])):
            messages.append("A new commit node was added to the repository graph.")
        if before.get("staging") != after.get("staging"):
            messages.append("The staging area changed.")
        if before.get("working_tree") != after.get("working_tree"):
            messages.append("The working tree changed.")
        if before.get("conflicts") != after.get("conflicts"):
            messages.append("The conflict state changed.")
        if not messages:
            messages.append("The repository state did not visibly change.")
        return " ".join(messages)
