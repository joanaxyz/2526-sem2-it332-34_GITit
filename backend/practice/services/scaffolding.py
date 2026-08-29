from common.constants import DIFFICULTY_EASY, DIFFICULTY_MEDIUM


class ScaffoldingService:
    def supports_for(self, difficulty: str) -> dict:
        return {
            "live_dag": True,
            "expected_state": difficulty in (DIFFICULTY_EASY, DIFFICULTY_MEDIUM),
            "contextual_feedback": difficulty == DIFFICULTY_EASY,
        }


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
