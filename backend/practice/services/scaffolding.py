"""The one owner of the fading-scaffold ladders.

Support fades with difficulty, and each ladder is a constant here - never
authored per variant and never re-derived in a payload or command processor.
The live DAG is always available.

Two ladders, one per gameplay surface:

- ``TIER_SCAFFOLDING_LADDER`` (difficulty-tiered adventure levels): the
  per-command contextual feedback goes first, then the Expected State
  diagram. Easy shows both, Medium keeps only the Expected State, Hard neither.
- ``SCAFFOLDING_LADDER`` (challenge trials): the Expected State diagram goes
  first, then the contextual feedback. Easy shows both, Medium keeps only the
  feedback, Hard neither.
"""

from common.constants import DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_MEDIUM

# Challenge trials.
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

# Difficulty-tiered adventure levels.
TIER_SCAFFOLDING_LADDER = {
    DIFFICULTY_EASY: {
        "live_dag": True,
        "expected_state": True,
        "contextual_feedback": True,
    },
    DIFFICULTY_MEDIUM: {
        "live_dag": True,
        "expected_state": True,
        "contextual_feedback": False,
    },
    DIFFICULTY_HARD: {
        "live_dag": True,
        "expected_state": False,
        "contextual_feedback": False,
    },
}



class ScaffoldingService:
    def supports_for(self, difficulty: str) -> dict:
        """Support flags for a challenge trial. Unknown difficulty gets the least support."""
        return dict(SCAFFOLDING_LADDER.get(difficulty, SCAFFOLDING_LADDER[DIFFICULTY_HARD]))

    def supports_for_tier(self, difficulty: str) -> dict:
        """Support flags for an adventure level tier. Unknown difficulty gets the least support."""
        return dict(
            TIER_SCAFFOLDING_LADDER.get(difficulty, TIER_SCAFFOLDING_LADDER[DIFFICULTY_HARD])
        )

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
