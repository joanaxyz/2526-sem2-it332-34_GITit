from common.constants import SESSION_MODE_REVIEW
from common.exceptions import Locked
from scenarios.models import CompletionRecord, DifficultyInstance
from scenarios.services import ScenarioSessionService


class ReviewModeService:
    def start_review_session(self, *, user, difficulty_instance: DifficultyInstance):
        if not CompletionRecord.objects.filter(
            user=user,
            difficulty_instance=difficulty_instance,
        ).exists():
            raise Locked("Review Mode is available only after completing this difficulty.")
        return ScenarioSessionService().start_session(
            user=user,
            difficulty_instance=difficulty_instance,
            source_entry_point="review",
            mode=SESSION_MODE_REVIEW,
        )
